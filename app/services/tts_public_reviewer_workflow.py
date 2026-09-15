"""Private-authority boundary for the public TTS review workflow."""

from __future__ import annotations

from datetime import datetime
import hashlib
import hmac
import json
from typing import Any, Mapping, Sequence

from app.schemas.tts_engine_benchmark import (
    PUBLIC_REVIEW_ROOT_EVENT_ID,
    PUBLIC_REVIEW_ROOT_EVENT_MAC,
    TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION,
    TTS_PUBLIC_REVIEWER_PACKAGE_VERSION,
    TTS_PUBLIC_REVIEW_SLOT_VERSION,
    TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION,
    BlindReviewManifest,
    HumanReviewRecord,
    LockClaim,
    LockedReviewHandoff,
    PrivateReviewDeliveryBinding,
    PrivateReviewerPackageBinding,
    PublicReviewDisclosure,
    PublicReviewerPackage,
    PublicReviewItem,
    PublicReviewWorkflowEvent,
    PublicReviewWorkflowStage,
    PublicReviewWorkflowState,
    ReviewLabel,
)


_WORKFLOW_KEY_DERIVATION_DOMAIN = (
    "loguic-tts-public-review-workflow-key-derivation/1.0"
)
_WORKFLOW_EVENT_MAC_DOMAIN = "loguic-tts-public-review-workflow-event-mac/1.0"


def build_private_reviewer_package_binding(
    private_manifest: BlindReviewManifest,
    *,
    reviewer_id: str,
) -> PrivateReviewerPackageBinding:
    """Commit one complete private assignment and its normalized audio hashes."""

    if reviewer_id not in {"reviewer_a", "reviewer_b"}:
        raise ValueError("Private package binding requires reviewer_a or reviewer_b")
    samples_by_id = {
        sample.sample_id: sample
        for sample_manifest in private_manifest.sample_manifests
        for sample in sample_manifest.samples
    }
    mappings = sorted(
        (
            mapping
            for mapping in private_manifest.mappings
            if mapping.reviewer_id == reviewer_id
        ),
        key=lambda mapping: mapping.order_position,
    )
    if not mappings:
        raise ValueError("Private manifest has no mappings for the requested reviewer")
    return PrivateReviewerPackageBinding.model_validate(
        {
            "package_version": TTS_PUBLIC_REVIEWER_PACKAGE_VERSION,
            "protocol_version": TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION,
            "reviewer_id": reviewer_id,
            "deliveries": tuple(
                PrivateReviewDeliveryBinding(
                    blind_review_id=mapping.blind_review_id,
                    sample_id=mapping.sample_id,
                    normalized_audio_sha256=samples_by_id[
                        mapping.sample_id
                    ].normalized_sha256,
                    reviewer_id=mapping.reviewer_id,
                    order_position=mapping.order_position,
                )
                for mapping in mappings
            ),
        }
    )


def build_public_reviewer_package(
    private_manifest: BlindReviewManifest,
    *,
    reviewer_id: str,
    private_commitment_key: bytes,
) -> PublicReviewerPackage:
    """Derive one reviewer-safe package committed to the private assignment."""

    binding = build_private_reviewer_package_binding(
        private_manifest,
        reviewer_id=reviewer_id,
    )
    delivery_set_commitment = _private_binding_commitment(
        binding,
        private_commitment_key,
    )
    items = tuple(
        {
            "blind_review_id": delivery.blind_review_id,
            "order_position": delivery.order_position,
            "audio_delivery_id": _audio_delivery_id(
                delivery_set_commitment,
                delivery.blind_review_id,
                delivery.order_position,
            ),
        }
        for delivery in binding.deliveries
    )
    return PublicReviewerPackage.model_validate(
        {
            "package_version": binding.package_version,
            "protocol_version": binding.protocol_version,
            "reviewer_id": binding.reviewer_id,
            "delivery_set_commitment": delivery_set_commitment,
            "items": items,
        }
    )


def deliver_public_review(
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    blind_review_id: str,
    private_commitment_key: bytes,
) -> PublicReviewWorkflowState:
    """Open an authenticated workflow at its explicit root."""

    package = _validated_package(package)
    _require_package_binding(package, private_manifest, private_commitment_key)
    item = _require_package_item(package, blind_review_id)
    event = _issue_event(
        package,
        item,
        stage="delivered",
        predecessor=None,
        private_commitment_key=private_commitment_key,
    )
    return _state_from_events(package, item, (event,))


def register_first_listen(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    private_commitment_key: bytes,
) -> PublicReviewWorkflowState:
    """Authenticate the prefix and append the first-listen transition."""

    state, item = _require_state(
        state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="delivered",
    )
    return _append_event(
        state,
        package,
        item,
        private_commitment_key=private_commitment_key,
        stage="first_listen",
    )


def capture_initial_review(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    perceived_transcription: str,
    intelligibility: ReviewLabel,
    private_commitment_key: bytes,
) -> PublicReviewWorkflowState:
    """Authenticate the prefix and append pre-disclosure review evidence."""

    state, item = _require_state(
        state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="first_listen",
    )
    return _append_event(
        state,
        package,
        item,
        private_commitment_key=private_commitment_key,
        stage="initial_capture",
        perceived_transcription=perceived_transcription,
        intelligibility=intelligibility,
    )


def disclose_review_context(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    private_commitment_key: bytes,
) -> PublicReviewWorkflowState:
    """Append only the disclosure authorized by the private assignment."""

    state, item = _require_state(
        state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="initial_capture",
    )
    disclosure = _authorized_disclosure(
        package,
        private_manifest,
        reviewer_id=state.reviewer_id,
        blind_review_id=state.blind_review_id,
    )
    return _append_event(
        state,
        package,
        item,
        private_commitment_key=private_commitment_key,
        stage="disclosed",
        disclosure=disclosure,
    )


def complete_review_rubric(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    pronunciation_correctness: ReviewLabel,
    locale_accent_conformance: ReviewLabel,
    naturalness: ReviewLabel,
    prosody_rhythm: ReviewLabel,
    a1_pedagogical_suitability: ReviewLabel,
    private_commitment_key: bytes,
) -> PublicReviewWorkflowState:
    """Authenticate the disclosed prefix and append all remaining dimensions."""

    state, item = _require_state(
        state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="disclosed",
    )
    return _append_event(
        state,
        package,
        item,
        private_commitment_key=private_commitment_key,
        stage="rubric_complete",
        pronunciation_correctness=pronunciation_correctness,
        locale_accent_conformance=locale_accent_conformance,
        naturalness=naturalness,
        prosody_rhythm=prosody_rhythm,
        a1_pedagogical_suitability=a1_pedagogical_suitability,
    )


def lock_public_review(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    locked_at: datetime,
    private_commitment_key: bytes,
) -> LockedReviewHandoff:
    """Authenticate the full prefix and issue one individually valid lock."""

    state, item = _require_state(
        state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="rubric_complete",
    )
    review = _review_from_state(state, locked_at=locked_at)
    locked_state = _append_event(
        state,
        package,
        item,
        private_commitment_key=private_commitment_key,
        stage="locked",
        locked_review_id=review.review_id,
        locked_at=review.locked_at,
        locked_review=review,
    )
    locked_event = locked_state.event_for("locked")
    return LockedReviewHandoff.model_validate(
        {
            "package_id": package.package_id,
            "delivery_set_commitment": package.delivery_set_commitment,
            "lock_transition_id": locked_event.lock_transition_id,
            "workflow_state": locked_state,
            "review": review,
        }
    )


def serialize_locked_review_handoff(
    handoff: LockedReviewHandoff,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    private_commitment_key: bytes,
) -> bytes:
    """Return canonical provenance plus the exact final HumanReviewRecord."""

    handoff = _validated_handoff(
        handoff,
        package,
        private_manifest,
        private_commitment_key,
    )
    return _canonical_json(handoff.model_dump(mode="json")).encode("utf-8")


def validate_locked_review_handoff(
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    payload: bytes,
    *,
    private_commitment_key: bytes,
) -> LockClaim:
    """Replay all private authority and return B's deterministic lock claim."""

    package = _validated_package(package)
    _require_package_binding(package, private_manifest, private_commitment_key)
    try:
        decoded = payload.decode("utf-8")
        raw = json.loads(decoded, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("Locked review handoff must be canonical UTF-8 JSON") from error
    if not isinstance(raw, Mapping):
        raise ValueError("Locked review handoff must contain one JSON object")
    handoff = LockedReviewHandoff.model_validate(raw)
    if decoded != _canonical_json(handoff.model_dump(mode="json")):
        raise ValueError("Locked review handoff is not canonical JSON")
    handoff = _validated_handoff(
        handoff,
        package,
        private_manifest,
        private_commitment_key,
    )
    return _lock_claim(handoff)


def validate_nonconflicting_review_locks(claims: Sequence[LockClaim]) -> None:
    """Detect divergent validated handoffs for a review slot without persisting."""

    seen: dict[str, str] = {}
    for claim in claims:
        claim = LockClaim.model_validate(claim.model_dump(mode="python"))
        previous_handoff_id = seen.get(claim.review_slot_id)
        if previous_handoff_id is not None and previous_handoff_id != claim.handoff_id:
            raise ValueError("Conflicting handoffs for one review slot")
        seen[claim.review_slot_id] = claim.handoff_id


def _validated_handoff(
    handoff: LockedReviewHandoff,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    private_commitment_key: bytes,
) -> LockedReviewHandoff:
    package = _validated_package(package)
    _require_package_binding(package, private_manifest, private_commitment_key)
    handoff = LockedReviewHandoff.model_validate(handoff.model_dump(mode="python"))
    if (
        handoff.package_id != package.package_id
        or not hmac.compare_digest(
            handoff.delivery_set_commitment,
            package.delivery_set_commitment,
        )
        or handoff.workflow_state.package_id != package.package_id
        or handoff.workflow_state.reviewer_id != package.reviewer_id
    ):
        raise ValueError("Locked review handoff belongs to a different package")
    state, item = _require_state(
        handoff.workflow_state,
        package,
        private_manifest,
        private_commitment_key,
        expected_stage="locked",
    )
    if (
        handoff.review.reviewer_id != package.reviewer_id
        or handoff.review.blind_review_id != item.blind_review_id
        or handoff.review != state.event_for("locked").locked_review
    ):
        raise ValueError("Locked review handoff does not match its authenticated lock")
    expected_review = _review_from_state(state, locked_at=handoff.review.locked_at)
    if handoff.review != expected_review:
        raise ValueError("Locked review does not match authenticated workflow evidence")
    return handoff


def _validated_package(package: PublicReviewerPackage) -> PublicReviewerPackage:
    return PublicReviewerPackage.model_validate(package.model_dump(mode="python"))


def _require_package_binding(
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    private_commitment_key: bytes,
) -> None:
    expected = build_public_reviewer_package(
        private_manifest,
        reviewer_id=package.reviewer_id,
        private_commitment_key=private_commitment_key,
    )
    if not hmac.compare_digest(
        expected.delivery_set_commitment,
        package.delivery_set_commitment,
    ) or expected != package:
        raise ValueError("Public package does not match its private delivery binding")


def _require_package_item(
    package: PublicReviewerPackage,
    blind_review_id: str,
) -> PublicReviewItem:
    items = tuple(
        item for item in package.items if item.blind_review_id == blind_review_id
    )
    if len(items) != 1:
        raise ValueError("blind_review_id must belong exactly once to the public package")
    return items[0]


def _require_state(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    private_commitment_key: bytes,
    *,
    expected_stage: PublicReviewWorkflowStage,
) -> tuple[PublicReviewWorkflowState, PublicReviewItem]:
    package = _validated_package(package)
    _require_package_binding(package, private_manifest, private_commitment_key)
    state = PublicReviewWorkflowState.model_validate(state.model_dump(mode="python"))
    item = _require_package_item(package, state.blind_review_id)
    if (
        state.package_id != package.package_id
        or state.package_version != package.package_version
        or state.protocol_version != package.protocol_version
        or not hmac.compare_digest(
            state.delivery_set_commitment,
            package.delivery_set_commitment,
        )
        or state.reviewer_id != package.reviewer_id
        or state.audio_delivery_id != item.audio_delivery_id
        or state.order_position != item.order_position
    ):
        raise ValueError("Workflow state does not belong to the public package item")
    _verify_workflow_prefix(state, package, item, private_commitment_key)
    if any(event.stage == "disclosed" for event in state.events):
        expected_disclosure = _authorized_disclosure(
            package,
            private_manifest,
            reviewer_id=state.reviewer_id,
            blind_review_id=state.blind_review_id,
        )
        if state.event_for("disclosed").disclosure != expected_disclosure:
            raise ValueError("Workflow disclosure is not authorized by the private assignment")
    if state.stage != expected_stage:
        raise ValueError(
            f"Workflow transition requires {expected_stage}, got {state.stage}"
        )
    return state, item


def _verify_workflow_prefix(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    item: PublicReviewItem,
    private_commitment_key: bytes,
) -> None:
    workflow_key = _workflow_authentication_key(package, private_commitment_key)
    predecessor_id = PUBLIC_REVIEW_ROOT_EVENT_ID
    predecessor_mac = PUBLIC_REVIEW_ROOT_EVENT_MAC
    for event in state.events:
        if (
            event.authentication_version != TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION
            or event.package_version != package.package_version
            or event.protocol_version != package.protocol_version
            or event.package_id != package.package_id
            or not hmac.compare_digest(
                event.delivery_set_commitment,
                package.delivery_set_commitment,
            )
            or event.audio_delivery_id != item.audio_delivery_id
            or event.order_position != item.order_position
            or event.reviewer_id != package.reviewer_id
            or event.blind_review_id != item.blind_review_id
            or event.predecessor_event_id != predecessor_id
            or not hmac.compare_digest(event.predecessor_event_mac, predecessor_mac)
        ):
            raise ValueError("Workflow event context or predecessor is incompatible")
        expected_mac = _event_mac(event, workflow_key)
        if not hmac.compare_digest(event.event_mac, expected_mac):
            raise ValueError("Workflow event MAC authentication failed")
        predecessor_id = event.event_id
        predecessor_mac = event.event_mac


def _state_from_events(
    package: PublicReviewerPackage,
    item: PublicReviewItem,
    events: tuple[PublicReviewWorkflowEvent, ...],
) -> PublicReviewWorkflowState:
    return PublicReviewWorkflowState.model_validate(
        {
            "package_id": package.package_id,
            "package_version": package.package_version,
            "protocol_version": package.protocol_version,
            "delivery_set_commitment": package.delivery_set_commitment,
            "reviewer_id": package.reviewer_id,
            "blind_review_id": item.blind_review_id,
            "audio_delivery_id": item.audio_delivery_id,
            "order_position": item.order_position,
            "events": events,
        }
    )


def _append_event(
    state: PublicReviewWorkflowState,
    package: PublicReviewerPackage,
    item: PublicReviewItem,
    *,
    private_commitment_key: bytes,
    stage: PublicReviewWorkflowStage,
    **evidence: Any,
) -> PublicReviewWorkflowState:
    event = _issue_event(
        package,
        item,
        stage=stage,
        predecessor=state.events[-1],
        private_commitment_key=private_commitment_key,
        **evidence,
    )
    return _state_from_events(package, item, (*state.events, event))


def _issue_event(
    package: PublicReviewerPackage,
    item: PublicReviewItem,
    *,
    stage: PublicReviewWorkflowStage,
    predecessor: PublicReviewWorkflowEvent | None,
    private_commitment_key: bytes,
    **evidence: Any,
) -> PublicReviewWorkflowEvent:
    raw = {
        "authentication_version": TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION,
        "package_version": package.package_version,
        "protocol_version": package.protocol_version,
        "package_id": package.package_id,
        "delivery_set_commitment": package.delivery_set_commitment,
        "audio_delivery_id": item.audio_delivery_id,
        "order_position": item.order_position,
        "reviewer_id": package.reviewer_id,
        "blind_review_id": item.blind_review_id,
        "stage": stage,
        "predecessor_event_id": (
            PUBLIC_REVIEW_ROOT_EVENT_ID
            if predecessor is None
            else predecessor.event_id
        ),
        "predecessor_event_mac": (
            PUBLIC_REVIEW_ROOT_EVENT_MAC
            if predecessor is None
            else predecessor.event_mac
        ),
        **evidence,
        "event_mac": "review_event_mac_" + "0" * 64,
    }
    unsigned = PublicReviewWorkflowEvent.model_validate(raw)
    workflow_key = _workflow_authentication_key(package, private_commitment_key)
    authenticated = unsigned.model_dump(mode="python")
    authenticated["event_mac"] = _event_mac(unsigned, workflow_key)
    return PublicReviewWorkflowEvent.model_validate(authenticated)


def _event_mac(event: PublicReviewWorkflowEvent, workflow_key: bytes) -> str:
    event_content = event.model_dump(mode="json")
    event_content.pop("event_mac")
    payload = _canonical_json(
        {
            "domain": _WORKFLOW_EVENT_MAC_DOMAIN,
            "event": event_content,
        }
    ).encode("utf-8")
    return "review_event_mac_" + hmac.new(
        workflow_key,
        payload,
        hashlib.sha256,
    ).hexdigest()


def _workflow_authentication_key(
    package: PublicReviewerPackage,
    private_commitment_key: bytes,
) -> bytes:
    if len(private_commitment_key) < 32:
        raise ValueError("Private commitment key must contain at least 32 bytes")
    context = _canonical_json(
        {
            "domain": _WORKFLOW_KEY_DERIVATION_DOMAIN,
            "authentication_version": TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION,
            "package_version": package.package_version,
            "protocol_version": package.protocol_version,
            "package_id": package.package_id,
            "delivery_set_commitment": package.delivery_set_commitment,
        }
    ).encode("utf-8")
    return hmac.new(private_commitment_key, context, hashlib.sha256).digest()


def _authorized_disclosure(
    package: PublicReviewerPackage,
    private_manifest: BlindReviewManifest,
    *,
    reviewer_id: str,
    blind_review_id: str,
) -> PublicReviewDisclosure:
    mappings = tuple(
        mapping
        for mapping in private_manifest.mappings
        if mapping.reviewer_id == reviewer_id
        and mapping.blind_review_id == blind_review_id
    )
    if len(mappings) != 1:
        raise ValueError("Public review item has no unique private mapping")
    samples = tuple(
        sample
        for sample_manifest in private_manifest.sample_manifests
        for sample in sample_manifest.samples
        if sample.sample_id == mappings[0].sample_id
    )
    if len(samples) != 1:
        raise ValueError("Public review item must resolve to exactly one private sample")
    generation_case = samples[0].generation_case
    return PublicReviewDisclosure.model_validate(
        {
            "package_id": package.package_id,
            "blind_review_id": blind_review_id,
            "reference_text": generation_case.reference_text,
            "ipa": generation_case.ipa,
            "target_locale": generation_case.target_locale,
        }
    )


def _review_from_state(
    state: PublicReviewWorkflowState,
    *,
    locked_at: datetime,
) -> HumanReviewRecord:
    initial = state.event_for("initial_capture")
    rubric = state.event_for("rubric_complete")
    return HumanReviewRecord.model_validate(
        {
            "blind_review_id": state.blind_review_id,
            "reviewer_id": state.reviewer_id,
            "locked_at": locked_at,
            "perceived_transcription": initial.perceived_transcription,
            "first_listen_without_transcript": True,
            "reference_text_revealed_after_first_listen": True,
            "ipa_revealed_after_first_listen": True,
            "target_locale_revealed_after_first_listen": True,
            "intelligibility": initial.intelligibility,
            "pronunciation_correctness": rubric.pronunciation_correctness,
            "locale_accent_conformance": rubric.locale_accent_conformance,
            "naturalness": rubric.naturalness,
            "prosody_rhythm": rubric.prosody_rhythm,
            "a1_pedagogical_suitability": rubric.a1_pedagogical_suitability,
        }
    )


def _lock_claim(handoff: LockedReviewHandoff) -> LockClaim:
    review_slot_id = _causal_id(
        "review_slot_",
        {
            "domain": TTS_PUBLIC_REVIEW_SLOT_VERSION,
            "package_id": handoff.package_id,
            "reviewer_id": handoff.review.reviewer_id,
            "blind_review_id": handoff.review.blind_review_id,
        },
    )
    return LockClaim.model_validate(
        {
            "review_slot_version": TTS_PUBLIC_REVIEW_SLOT_VERSION,
            "review_slot_id": review_slot_id,
            "package_id": handoff.package_id,
            "lock_transition_id": handoff.lock_transition_id,
            "handoff_id": handoff.handoff_id,
            "review": handoff.review,
        }
    )


def _audio_delivery_id(
    delivery_set_commitment: str,
    blind_review_id: str,
    order_position: int,
) -> str:
    return _causal_id(
        "review_audio_",
        {
            "delivery_set_commitment": delivery_set_commitment,
            "blind_review_id": blind_review_id,
            "order_position": order_position,
        },
    )


def _private_binding_commitment(
    binding: PrivateReviewerPackageBinding,
    private_commitment_key: bytes,
) -> str:
    if len(private_commitment_key) < 32:
        raise ValueError("Private commitment key must contain at least 32 bytes")
    payload = _canonical_json(binding.model_dump(mode="json")).encode("utf-8")
    return "review_binding_" + hmac.new(
        private_commitment_key,
        payload,
        hashlib.sha256,
    ).hexdigest()


def _causal_id(prefix: str, payload: Mapping[str, Any]) -> str:
    return prefix + hashlib.sha256(
        _canonical_json(payload).encode("utf-8")
    ).hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=_json_default,
    )


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Value of type {type(value).__name__} is not JSON serializable")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Locked review handoff cannot contain duplicate JSON keys")
        result[key] = value
    return result
