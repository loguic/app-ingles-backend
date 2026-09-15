from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.schemas.tts_engine_benchmark import (
    CANDIDATE_V4_CONTENT_DIGEST,
    CANDIDATE_V4_FROZEN_TARGETS,
    PUBLIC_REVIEW_ROOT_EVENT_ID,
    PUBLIC_REVIEW_ROOT_EVENT_MAC,
    TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION,
    TTS_PUBLIC_REVIEWER_PACKAGE_VERSION,
    TTS_PUBLIC_REVIEW_SLOT_VERSION,
    TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION,
    AdjudicationRecord,
    BenchmarkProtocolIdentity,
    BlindReviewManifest,
    BlindReviewMapping,
    DeterminismExecution,
    DeterminismProbe,
    GenerationCase,
    HumanReviewRecord,
    LockClaim,
    LockedReviewHandoff,
    ModelPin,
    PublicReviewerPackage,
    PublicReviewWorkflowEvent,
    PublicReviewWorkflowState,
    ReviewLabel,
    RuntimeEnvironmentPin,
    SampleIdentity,
    SampleManifest,
    validate_private_adjudication_reconciliation,
)
from app.schemas.tts_wav_normalization import TTS_WAV_NORMALIZATION_PROFILE_VERSION
from app.services.pedagogical_candidate_payload_identity import (
    derive_candidate_payload_identity,
)
from app.services.tts_public_reviewer_workflow import (
    build_private_reviewer_package_binding,
    build_public_reviewer_package,
    capture_initial_review,
    complete_review_rubric,
    deliver_public_review,
    disclose_review_context,
    lock_public_review,
    register_first_listen,
    serialize_locked_review_handoff,
    validate_locked_review_handoff,
    validate_nonconflicting_review_locks,
)


CANDIDATE_V4_PATH = (
    Path(__file__).resolve().parents[1]
    / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
)
LOCKED_AT = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
PRIVATE_COMMITMENT_KEY = b"loguic-review-package-test-key-v1"


def _derive_candidate_v4_targets() -> tuple[tuple[str, str, str, str], ...]:
    document: dict[str, Any] = json.loads(CANDIDATE_V4_PATH.read_text("utf-8"))
    lesson = document["candidate_unit"]["lessons"][0]
    occurrences: dict[str, set[tuple[str, str, str]]] = {}

    def collect(text: str, pronunciations: list[dict[str, str]]) -> None:
        for pronunciation in pronunciations:
            occurrences.setdefault(pronunciation["audio_asset"], set()).add(
                (text, pronunciation["ipa"], pronunciation["locale"])
            )

    for support in lesson["experience"]["language_support"]:
        collect(support["en"], support["pronunciations"])
    for conversation in lesson["conversations"]:
        for turn in conversation["turns"]:
            collect(turn["en"], turn["pronunciations"])

    audio_ids = tuple(
        resource_id
        for resource_id in document["required_resource_ids"]
        if resource_id.startswith("audio.")
    )
    assert len(audio_ids) == 12
    assert len(set(audio_ids)) == 12
    assert set(audio_ids) == set(occurrences)
    targets = []
    for resource_id in audio_ids:
        (reference_text, ipa, locale), = occurrences[resource_id]
        targets.append((resource_id, reference_text, ipa, locale))
    return tuple(targets)


def _protocol(**updates: Any) -> BenchmarkProtocolIdentity:
    payload: dict[str, Any] = {
        "protocol_version": TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION,
        "candidate_revision": "a1-u1-candidate-v4",
        "candidate_content_digest": CANDIDATE_V4_CONTENT_DIGEST,
        "normalization_profile_version": TTS_WAV_NORMALIZATION_PROFILE_VERSION,
        "corpus_resource_ids": tuple(
            target[0] for target in CANDIDATE_V4_FROZEN_TARGETS
        ),
    }
    payload.update(updates)
    return BenchmarkProtocolIdentity.model_validate(payload)


def _case(
    *,
    target_index: int = 1,
    engine: str = "kokoro",
    engine_version: str = "0.9.4",
    voice_id: str = "bf_emma",
    **updates: Any,
) -> GenerationCase:
    resource_id, reference_text, ipa, locale = CANDIDATE_V4_FROZEN_TARGETS[
        target_index
    ]
    payload: dict[str, Any] = {
        "protocol_identity": _protocol(),
        "resource_id": resource_id,
        "reference_text": reference_text,
        "ipa": ipa,
        "target_locale": locale,
        "engine": engine,
        "engine_version": engine_version,
        "model_pin": ModelPin(
            model_id=f"{engine}-model",
            revision=engine_version,
            sha256=None,
            status="pending_local_artifact",
        ),
        "voice_id": voice_id,
        "generation_parameters": (("speed", "1.0"),),
        "runtime_environment_pin": RuntimeEnvironmentPin(
            runtime_package=engine,
            runtime_version=engine_version,
            python_version="3.12.3",
            environment_fingerprint_sha256=None,
            status="pending_local_artifact",
        ),
    }
    payload.update(updates)
    return GenerationCase.model_validate(payload)


def _probe(
    case: GenerationCase,
    *,
    hashes: tuple[str, str, str] = ("a", "a", "a"),
    classification: str = "deterministic_for_benchmark",
    replication_count: int = 1,
    executions: tuple[DeterminismExecution, ...] | None = None,
) -> DeterminismProbe:
    records = executions or tuple(
        DeterminismExecution(
            generation_case_id=case.generation_case_id,
            execution_index=index,
            raw_sha256=character * 64,
        )
        for index, character in enumerate(hashes, start=1)
    )
    return DeterminismProbe(
        generation_case=case,
        executions=records,
        classification=classification,
        required_replication_count=replication_count,
    )


def _sample(
    case: GenerationCase,
    probe: DeterminismProbe,
    index: int,
    *,
    raw: str = "d",
    normalized: str = "e",
    **updates: Any,
) -> SampleIdentity:
    payload: dict[str, Any] = {
        "generation_case": case,
        "determinism_probe": probe,
        "replication_index": index,
        "raw_sha256": raw * 64,
        "normalized_sha256": normalized * 64,
        "normalization_profile_version": TTS_WAV_NORMALIZATION_PROFILE_VERSION,
    }
    payload.update(updates)
    return SampleIdentity.model_validate(payload)


def _review(
    reviewer_id: str,
    *,
    blind_review_id: str = "br_0123456789abcdef0123456789abcdef",
    **updates: Any,
) -> HumanReviewRecord:
    payload: dict[str, Any] = {
        "blind_review_id": blind_review_id,
        "reviewer_id": reviewer_id,
        "locked_at": LOCKED_AT,
        "perceived_transcription": "I need water.",
        "first_listen_without_transcript": True,
        "reference_text_revealed_after_first_listen": True,
        "ipa_revealed_after_first_listen": True,
        "target_locale_revealed_after_first_listen": True,
        "intelligibility": "meets",
        "pronunciation_correctness": "meets",
        "locale_accent_conformance": "meets",
        "naturalness": "meets",
        "prosody_rhythm": "meets",
        "a1_pedagogical_suitability": "meets",
    }
    payload.update(updates)
    return HumanReviewRecord.model_validate(payload)


def test_human_review_requires_a_final_utc_lock_and_canonical_review_id() -> None:
    review = _review("reviewer_a")
    equivalent_offset_review = _review(
        "reviewer_a",
        locked_at=datetime(2026, 9, 14, 13, 0, tzinfo=timezone(timedelta(hours=1))),
    )

    assert review.locked_at == LOCKED_AT
    assert review.locked_at.tzinfo is UTC
    assert equivalent_offset_review.locked_at == LOCKED_AT
    assert equivalent_offset_review.review_id == review.review_id


def test_reject_human_review_without_lock_or_with_naive_lock() -> None:
    review_payload = _review("reviewer_a").model_dump()
    review_payload.pop("locked_at")
    with pytest.raises(ValidationError, match="locked_at"):
        HumanReviewRecord.model_validate(review_payload)

    with pytest.raises(ValidationError, match="timezone-aware"):
        _review("reviewer_a", locked_at=datetime(2026, 9, 14, 12, 0))


def test_reject_stale_review_id_after_changing_locked_payload() -> None:
    review = _review("reviewer_a")
    changed_lock = review.model_dump()
    changed_lock["locked_at"] = LOCKED_AT + timedelta(seconds=1)
    with pytest.raises(ValidationError, match="canonical causal identity"):
        HumanReviewRecord.model_validate(changed_lock)

    changed_label = review.model_dump()
    changed_label["naturalness"] = "minor_issue"
    with pytest.raises(ValidationError, match="canonical causal identity"):
        HumanReviewRecord.model_validate(changed_label)

    with pytest.raises(ValidationError):
        review.locked_at = LOCKED_AT + timedelta(seconds=1)


def _replicated_manifest() -> SampleManifest:
    case = _case()
    probe = _probe(
        case,
        hashes=("a", "b", "c"),
        classification="replicated_for_benchmark",
        replication_count=3,
    )
    samples = tuple(
        _sample(case, probe, index, raw=character, normalized=str(index))
        for index, character in enumerate(("d", "e", "f"), start=1)
    )
    return SampleManifest(determinism_probe=probe, samples=samples)


def _blind_mappings(*manifests: SampleManifest) -> tuple[BlindReviewMapping, ...]:
    mappings = []
    opaque_index = 1
    for reviewer_id in ("reviewer_a", "reviewer_b"):
        samples = tuple(sample for manifest in manifests for sample in manifest.samples)
        for order_position, sample in enumerate(samples, start=1):
            mappings.append(
                BlindReviewMapping(
                    blind_review_id=f"br_{opaque_index:032x}",
                    sample_id=sample.sample_id,
                    reviewer_id=reviewer_id,
                    order_position=order_position,
                    private_mapping=True,
                )
            )
            opaque_index += 1
    return tuple(mappings)


def test_candidate_v4_real_derivation_matches_explicit_frozen_v1_corpus() -> None:
    derived = _derive_candidate_v4_targets()
    candidate = PedagogicalUnitCandidate.model_validate_json(
        CANDIDATE_V4_PATH.read_text("utf-8")
    )
    identity = derive_candidate_payload_identity(
        candidate,
        candidate_revision="a1-u1-candidate-v4",
    )

    assert derived == CANDIDATE_V4_FROZEN_TARGETS
    assert identity.content_digest == CANDIDATE_V4_CONTENT_DIGEST
    assert sum(target[3] == "en-GB" for target in derived) == 7
    assert sum(target[3] == "en-US" for target in derived) == 5


def test_valid_protocol_identity_is_exact() -> None:
    identity = _protocol()
    assert identity.protocol_version == "loguic-tts-engine-benchmark/1.0"
    assert identity.candidate_revision == "a1-u1-candidate-v4"
    assert identity.candidate_content_digest == CANDIDATE_V4_CONTENT_DIGEST


def test_reject_twelve_external_audio_ids() -> None:
    with pytest.raises(ValidationError, match="frozen Candidate v4 corpus"):
        _protocol(corpus_resource_ids=tuple(f"audio.fake.{index}" for index in range(12)))


def test_reject_target_outside_candidate_v4() -> None:
    with pytest.raises(ValidationError, match="not in frozen Candidate v4"):
        _case(resource_id="audio.not-in-candidate")


@pytest.mark.parametrize(
    "updates",
    [
        {"reference_text": "Invented target"},
        {"ipa": "/x/"},
        {"target_locale": "en-US"},
    ],
)
def test_reject_target_text_ipa_or_locale_mismatch(updates: dict[str, str]) -> None:
    with pytest.raises(ValidationError, match="does not match Candidate v4"):
        _case(**updates)


def test_reject_generation_case_without_exact_protocol_candidate_and_profile() -> None:
    payload = _case().model_dump()
    payload.pop("generation_case_id")
    payload.pop("protocol_identity")
    with pytest.raises(ValidationError, match="protocol_identity"):
        GenerationCase.model_validate(payload)

    for field, value in (
        ("protocol_version", "loguic-tts-engine-benchmark/2.0"),
        ("candidate_revision", "a1-u1-candidate-v5"),
        ("candidate_content_digest", "sha256:" + "0" * 64),
        ("normalization_profile_version", "other-profile/1.0"),
    ):
        with pytest.raises(ValidationError):
            _protocol(**{field: value})


def test_generation_case_id_is_canonical_and_rejects_payload_reuse() -> None:
    original = _case()
    changed = original.model_dump()
    changed["generation_parameters"] = (("speed", "0.9"),)
    with pytest.raises(ValidationError, match="canonical causal identity"):
        GenerationCase.model_validate(changed)
    assert _case().generation_case_id == original.generation_case_id


def test_model_and_environment_pins_distinguish_pending_and_verified() -> None:
    with pytest.raises(ValidationError, match="machine-specific absolute path"):
        ModelPin(
            model_id="/home/user/model.bin",
            revision=None,
            sha256=None,
            status="pending_local_artifact",
        )
    with pytest.raises(ValidationError, match="pending model pin"):
        ModelPin(
            model_id="model",
            revision=None,
            sha256="a" * 64,
            status="pending_local_artifact",
        )
    with pytest.raises(ValidationError, match="verified model pin"):
        ModelPin(model_id="model", revision=None, sha256=None, status="verified")
    with pytest.raises(ValidationError, match="requires a lock fingerprint"):
        RuntimeEnvironmentPin(
            runtime_package="kokoro",
            runtime_version="0.9.4",
            python_version="3.12.3",
            environment_fingerprint_sha256=None,
            status="verified",
        )
    mismatched_runtime = RuntimeEnvironmentPin(
        runtime_package="piper",
        runtime_version="1.8.0",
        python_version="3.12.3",
        environment_fingerprint_sha256=None,
        status="pending_local_artifact",
    )
    with pytest.raises(ValidationError, match="Runtime pin must match"):
        _case(runtime_environment_pin=mismatched_runtime)


@pytest.mark.parametrize(
    "revision",
    [
        "models/voice.bin",
        "model/revision.json",
        "tmp/model-revision",
        "home/user/model.bin",
        "~",
        "~/model",
        "/home/user/model.bin",
        "/tmp/model-revision",
        "../model",
        "./model",
        r"C:\models\voice.bin",
        "C:/models/voice.bin",
        "file:///tmp/model",
        r".\model",
        r"..\model",
        r"\\server\share\model.bin",
        "refs/other/v1.0",
        "refs/tags/",
        "refs/heads/",
        "refs/tags/../v1",
        "refs/heads/.local",
        "refs/tags/release//v1.0",
    ],
)
def test_reject_local_path_as_model_revision(revision: str) -> None:
    with pytest.raises(ValidationError, match="portable revision identifier"):
        ModelPin(
            model_id="portable-model-id",
            revision=revision,
            sha256=None,
            status="pending_local_artifact",
        )


@pytest.mark.parametrize(
    "revision",
    [
        "v1.0",
        "main",
        "c3327e9bac3dbe55779397bfa82de0f8806fb3bc",
        "refs/tags/v1.0",
        "refs/heads/main",
        "0.9.4",
    ],
)
def test_accept_portable_model_revision_identifiers(revision: str) -> None:
    pin = ModelPin(
        model_id="portable-model-id",
        revision=revision,
        sha256=None,
        status="pending_local_artifact",
    )
    assert pin.revision == revision


@pytest.mark.parametrize(
    ("target_index", "engine", "version", "voice"),
    [
        (0, "kokoro", "0.9.4", "af_heart"),
        (0, "kokoro", "0.9.4", "af_bella"),
        (1, "kokoro", "0.9.4", "bf_emma"),
        (1, "kokoro", "0.9.4", "bf_isabella"),
        (1, "piper", "1.8.0", "en_GB-cori-medium"),
        (1, "piper", "1.8.0", "en_GB-alba-medium"),
        (0, "piper", "1.8.0", "en_US-kristin-medium"),
        (0, "piper", "1.8.0", "en_US-joe-medium"),
    ],
)
def test_approved_engine_voice_locale_matrix_is_unchanged(
    target_index: int,
    engine: str,
    version: str,
    voice: str,
) -> None:
    assert _case(
        target_index=target_index,
        engine=engine,
        engine_version=version,
        voice_id=voice,
    ).voice_id == voice


def test_valid_deterministic_and_replicated_probes() -> None:
    case = _case()
    deterministic = _probe(case)
    replicated = _probe(
        case,
        hashes=("a", "b", "c"),
        classification="replicated_for_benchmark",
        replication_count=3,
    )
    assert deterministic.required_replication_count == 1
    assert replicated.required_replication_count == 3
    assert len({execution.execution_id for execution in replicated.executions}) == 3


def test_reject_probe_with_repeated_execution_id() -> None:
    case = _case()
    first = DeterminismExecution(
        generation_case_id=case.generation_case_id,
        execution_index=1,
        raw_sha256="a" * 64,
    )
    third = DeterminismExecution(
        generation_case_id=case.generation_case_id,
        execution_index=3,
        raw_sha256="a" * 64,
    )
    with pytest.raises(ValidationError, match="execution_id values must be unique"):
        _probe(case, executions=(first, first, third))


def test_reject_probe_with_different_generation_configurations() -> None:
    case = _case()
    changed_case = _case(generation_parameters=(("speed", "0.9"),))
    executions = tuple(
        DeterminismExecution(
            generation_case_id=(
                changed_case.generation_case_id if index == 2 else case.generation_case_id
            ),
            execution_index=index,
            raw_sha256="a" * 64,
        )
        for index in (1, 2, 3)
    )
    with pytest.raises(ValidationError, match="share one generation case"):
        _probe(case, executions=executions)


def test_reject_replicated_classification_for_identical_hashes() -> None:
    with pytest.raises(ValidationError, match="classification contradicts"):
        _probe(
            _case(),
            classification="replicated_for_benchmark",
            replication_count=3,
        )


def test_reject_deterministic_classification_for_different_hashes() -> None:
    with pytest.raises(ValidationError, match="classification contradicts"):
        _probe(_case(), hashes=("a", "b", "c"))


def test_valid_deterministic_sample_and_manifest() -> None:
    case = _case()
    probe = _probe(case)
    sample = _sample(case, probe, 1)
    manifest = SampleManifest(determinism_probe=probe, samples=(sample,))
    assert manifest.samples == (sample,)


def test_valid_sample_for_different_target_with_matching_probe_scope() -> None:
    probe_case = _case(target_index=1)
    sample_case = _case(target_index=2)
    probe = _probe(
        probe_case,
        hashes=("a", "b", "c"),
        classification="replicated_for_benchmark",
        replication_count=3,
    )
    samples = tuple(
        _sample(sample_case, probe, index, raw=raw, normalized=normalized)
        for index, (raw, normalized) in enumerate(
            (("d", "7"), ("e", "8"), ("f", "9")), start=1
        )
    )

    manifest = SampleManifest(determinism_probe=probe, samples=samples)

    assert probe_case.generation_case_id != sample_case.generation_case_id
    assert probe_case.resource_id != sample_case.resource_id
    assert probe_case.reference_text != sample_case.reference_text
    assert probe_case.ipa != sample_case.ipa
    assert {sample.replication_index for sample in manifest.samples} == {1, 2, 3}


def test_valid_three_replication_sample_manifest() -> None:
    manifest = _replicated_manifest()
    assert tuple(sample.replication_index for sample in manifest.samples) == (1, 2, 3)
    assert len({sample.sample_id for sample in manifest.samples}) == 3


@pytest.mark.parametrize(
    "target_indexes",
    ((1, 2, 2), (1, 1, 2), (1, 2, 3)),
    ids=("first-target-differs", "last-target-differs", "three-targets-differ"),
)
def test_reject_replicated_manifest_with_mixed_target_generation_cases(
    target_indexes: tuple[int, int, int],
) -> None:
    probe_case = _case(target_index=1)
    probe = _probe(
        probe_case,
        hashes=("a", "b", "c"),
        classification="replicated_for_benchmark",
        replication_count=3,
    )
    samples = tuple(
        _sample(_case(target_index=target_index), probe, index, raw=raw, normalized=normalized)
        for index, (target_index, raw, normalized) in enumerate(
            zip(target_indexes, ("d", "e", "f"), ("7", "8", "9")), start=1
        )
    )

    with pytest.raises(ValidationError, match="one complete target-specific generation case"):
        SampleManifest(determinism_probe=probe, samples=samples)


def test_reject_multiple_samples_for_deterministic_probe() -> None:
    case = _case()
    probe = _probe(case)
    first = _sample(case, probe, 1, raw="a", normalized="b")
    second = _sample(case, probe, 1, raw="c", normalized="d")
    with pytest.raises(ValidationError, match="complete 1-or-3 index set"):
        SampleManifest(determinism_probe=probe, samples=(first, second))


@pytest.mark.parametrize(
    ("updates", "error_pattern"),
    (
        (
            {
                "engine": "piper",
                "engine_version": "1.8.0",
                "voice_id": "en_GB-cori-medium",
                "model_pin": ModelPin(
                    model_id="piper-model",
                    revision="1.8.0",
                    sha256=None,
                    status="pending_local_artifact",
                ),
                "runtime_environment_pin": RuntimeEnvironmentPin(
                    runtime_package="piper",
                    runtime_version="1.8.0",
                    python_version="3.12.3",
                    environment_fingerprint_sha256=None,
                    status="pending_local_artifact",
                ),
            },
            "configuration must match determinism probe scope",
        ),
        ({"engine_version": "0.9.5"}, "engine/version/voice/locale is not approved"),
        ({"voice_id": "bf_isabella"}, "configuration must match determinism probe scope"),
        (
            {
                "model_pin": ModelPin(
                    model_id="kokoro-model",
                    revision="alternate",
                    sha256=None,
                    status="pending_local_artifact",
                )
            },
            "configuration must match determinism probe scope",
        ),
        ({"generation_parameters": (("speed", "0.9"),)}, "configuration must match determinism probe scope"),
        (
            {
                "runtime_environment_pin": RuntimeEnvironmentPin(
                    runtime_package="kokoro",
                    runtime_version="0.9.4",
                    python_version="3.11.9",
                    environment_fingerprint_sha256=None,
                    status="pending_local_artifact",
                )
            },
            "configuration must match determinism probe scope",
        ),
        ({"target_locale": "en-US"}, "text/IPA/locale does not match Candidate v4"),
        (
            {
                "protocol_identity": _protocol().model_copy(
                    update={"candidate_content_digest": "sha256:" + "0" * 64}
                )
            },
            "configuration must match determinism probe scope",
        ),
    ),
    ids=(
        "engine",
        "engine_version",
        "voice_id",
        "model_pin",
        "generation_parameters",
        "runtime_environment_pin",
        "target_locale",
        "protocol_identity",
    ),
)
def test_reject_sample_that_contradicts_probe_applicability_scope(
    updates: dict[str, Any], error_pattern: str,
) -> None:
    case = _case()
    probe = _probe(case)
    different_case = case.model_copy(update=updates)
    with pytest.raises(ValidationError, match=error_pattern):
        _sample(different_case, probe, 1)


def test_reject_sample_id_reuse_for_different_replica_or_hash() -> None:
    manifest = _replicated_manifest()
    original = manifest.samples[0]
    changed = original.model_dump()
    changed["replication_index"] = 2
    changed["raw_sha256"] = "9" * 64
    with pytest.raises(ValidationError, match="canonical causal identity"):
        SampleIdentity.model_validate(changed)


def test_reject_invalid_replication_index() -> None:
    case = _case()
    probe = _probe(
        case,
        hashes=("a", "b", "c"),
        classification="replicated_for_benchmark",
        replication_count=3,
    )
    with pytest.raises(ValidationError):
        _sample(case, probe, 4)


def test_valid_blind_manifest_for_independent_reviewers() -> None:
    sample_manifest = _replicated_manifest()
    blind_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    assert len(blind_manifest.mappings) == 6
    assert "engine" not in BlindReviewMapping.model_fields
    assert "voice_id" not in BlindReviewMapping.model_fields


def test_blind_manifest_preserves_288_unique_reviewer_specific_ids() -> None:
    source_manifest = _replicated_manifest()
    sample_manifests = tuple(
        SampleManifest(
            determinism_probe=source_manifest.determinism_probe,
            samples=tuple(
                sample.model_copy(
                    update={"sample_id": f"sample_{sample_index:064x}"}
                )
                for sample_index, sample in enumerate(
                    source_manifest.samples,
                    start=manifest_index * len(source_manifest.samples) + 1,
                )
            ),
        )
        for manifest_index in range(48)
    )
    blind_manifest = BlindReviewManifest(
        sample_manifests=sample_manifests,
        mappings=_blind_mappings(*sample_manifests),
    )

    assert len(blind_manifest.mappings) == 288
    assert len({mapping.blind_review_id for mapping in blind_manifest.mappings}) == 288
    mappings_by_reviewer_and_sample = {
        (mapping.reviewer_id, mapping.sample_id): mapping.blind_review_id
        for mapping in blind_manifest.mappings
    }
    assert len(mappings_by_reviewer_and_sample) == 288
    assert all(
        mappings_by_reviewer_and_sample[("reviewer_a", sample.sample_id)]
        != mappings_by_reviewer_and_sample[("reviewer_b", sample.sample_id)]
        for manifest in sample_manifests
        for sample in manifest.samples
    )


def test_reject_blind_id_reused_for_different_sample() -> None:
    sample_manifest = _replicated_manifest()
    mappings = [mapping.model_dump() for mapping in _blind_mappings(sample_manifest)]
    mappings[1]["blind_review_id"] = mappings[0]["blind_review_id"]
    with pytest.raises(ValidationError, match="blind_review_id values must be unique"):
        BlindReviewManifest(sample_manifests=(sample_manifest,), mappings=tuple(mappings))


def test_reject_sample_reused_across_blind_manifest_slices() -> None:
    sample_manifest = _replicated_manifest()
    with pytest.raises(ValidationError, match="sample_id values must be unique"):
        BlindReviewManifest(
            sample_manifests=(sample_manifest, sample_manifest),
            mappings=_blind_mappings(sample_manifest),
        )


def test_reject_duplicate_reviewer_order_position() -> None:
    sample_manifest = _replicated_manifest()
    mappings = [mapping.model_dump() for mapping in _blind_mappings(sample_manifest)]
    mappings[1]["order_position"] = mappings[0]["order_position"]
    with pytest.raises(ValidationError, match="order positions must be unique"):
        BlindReviewManifest(sample_manifests=(sample_manifest,), mappings=tuple(mappings))


def _public_review_setup(
    *,
    reviewer_id: str = "reviewer_a",
    item_index: int = 0,
    private_commitment_key: bytes = PRIVATE_COMMITMENT_KEY,
) -> tuple[
    BlindReviewManifest,
    PublicReviewerPackage,
    PublicReviewWorkflowState,
]:
    sample_manifest = _replicated_manifest()
    private_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    package = build_public_reviewer_package(
        private_manifest,
        reviewer_id=reviewer_id,
        private_commitment_key=private_commitment_key,
    )
    delivered = deliver_public_review(
        package,
        private_manifest,
        blind_review_id=package.items[item_index].blind_review_id,
        private_commitment_key=private_commitment_key,
    )
    return private_manifest, package, delivered


def _complete_public_review(
    *,
    reviewer_id: str = "reviewer_a",
    item_index: int = 0,
    naturalness: ReviewLabel = "meets",
    private_commitment_key: bytes = PRIVATE_COMMITMENT_KEY,
) -> tuple[
    BlindReviewManifest,
    PublicReviewerPackage,
    PublicReviewWorkflowState,
]:
    private_manifest, package, state = _public_review_setup(
        reviewer_id=reviewer_id,
        item_index=item_index,
        private_commitment_key=private_commitment_key,
    )
    state = register_first_listen(
        state,
        package,
        private_manifest,
        private_commitment_key=private_commitment_key,
    )
    state = capture_initial_review(
        state,
        package,
        private_manifest,
        perceived_transcription="I need water.",
        intelligibility="meets",
        private_commitment_key=private_commitment_key,
    )
    state = disclose_review_context(
        state,
        package,
        private_manifest,
        private_commitment_key=private_commitment_key,
    )
    state = complete_review_rubric(
        state,
        package,
        private_manifest,
        pronunciation_correctness="meets",
        locale_accent_conformance="meets",
        naturalness=naturalness,
        prosody_rhythm="meets",
        a1_pedagogical_suitability="meets",
        private_commitment_key=private_commitment_key,
    )
    return private_manifest, package, state


def _public_causal_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return prefix + hashlib.sha256(encoded).hexdigest()


def _recalculate_public_state_ids(raw_state: dict[str, Any]) -> dict[str, Any]:
    events = raw_state["events"]
    for index, event in enumerate(events):
        event["predecessor_event_id"] = (
            PUBLIC_REVIEW_ROOT_EVENT_ID
            if index == 0
            else events[index - 1]["event_id"]
        )
        event["predecessor_event_mac"] = (
            PUBLIC_REVIEW_ROOT_EVENT_MAC
            if index == 0
            else events[index - 1]["event_mac"]
        )
        if event["stage"] == "locked":
            event["lock_transition_id"] = _public_causal_id(
                "review_lock_",
                {
                    "package_id": event["package_id"],
                    "reviewer_id": event["reviewer_id"],
                    "blind_review_id": event["blind_review_id"],
                    "rubric_complete_event_id": event["predecessor_event_id"],
                },
            )
        event_identity = {
            key: value
            for key, value in event.items()
            if key not in {"event_id", "event_mac"}
        }
        event["event_id"] = _public_causal_id("review_event_", event_identity)
    state_identity = {
        key: value for key, value in raw_state.items() if key != "workflow_state_id"
    }
    raw_state["workflow_state_id"] = _public_causal_id(
        "review_state_",
        state_identity,
    )
    return raw_state


def _authenticate_public_state_for_test(
    raw_state: dict[str, Any],
    package: PublicReviewerPackage,
) -> dict[str, Any]:
    key_context = {
        "domain": "loguic-tts-public-review-workflow-key-derivation/1.0",
        "authentication_version": TTS_PUBLIC_REVIEW_WORKFLOW_AUTH_VERSION,
        "package_version": package.package_version,
        "protocol_version": package.protocol_version,
        "package_id": package.package_id,
        "delivery_set_commitment": package.delivery_set_commitment,
    }
    workflow_key = hmac.new(
        PRIVATE_COMMITMENT_KEY,
        json.dumps(
            key_context,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8"),
        hashlib.sha256,
    ).digest()
    events = raw_state["events"]
    for index, event in enumerate(events):
        event["predecessor_event_id"] = (
            PUBLIC_REVIEW_ROOT_EVENT_ID
            if index == 0
            else events[index - 1]["event_id"]
        )
        event["predecessor_event_mac"] = (
            PUBLIC_REVIEW_ROOT_EVENT_MAC
            if index == 0
            else events[index - 1]["event_mac"]
        )
        event_identity = {
            key: value
            for key, value in event.items()
            if key not in {"event_id", "event_mac"}
        }
        event["event_id"] = _public_causal_id("review_event_", event_identity)
        mac_content = {
            "domain": "loguic-tts-public-review-workflow-event-mac/1.0",
            "event": {key: value for key, value in event.items() if key != "event_mac"},
        }
        event["event_mac"] = "review_event_mac_" + hmac.new(
            workflow_key,
            json.dumps(
                mac_content,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
    return _recalculate_public_state_ids(raw_state)


def _recalculate_public_handoff_ids(raw_handoff: dict[str, Any]) -> dict[str, Any]:
    _recalculate_public_state_ids(raw_handoff["workflow_state"])
    locked = raw_handoff["workflow_state"]["events"][-1]
    raw_handoff["lock_transition_id"] = locked["lock_transition_id"]
    handoff_identity = {
        key: value for key, value in raw_handoff.items() if key != "handoff_id"
    }
    raw_handoff["handoff_id"] = _public_causal_id(
        "review_handoff_",
        handoff_identity,
    )
    return raw_handoff


def _canonical_payload(raw_handoff: dict[str, Any]) -> bytes:
    return json.dumps(
        raw_handoff,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def test_public_package_is_deterministic_frozen_assigned_and_ordered() -> None:
    private_manifest, package, _ = _public_review_setup()
    repeated = build_public_reviewer_package(
        private_manifest,
        reviewer_id="reviewer_a",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    reviewer_b = build_public_reviewer_package(
        private_manifest,
        reviewer_id="reviewer_b",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    different_private_key = build_public_reviewer_package(
        private_manifest,
        reviewer_id="reviewer_a",
        private_commitment_key=b"different-private-commitment-key-v1",
    )

    assert package == repeated
    assert package.package_id == repeated.package_id
    assert package.package_version == TTS_PUBLIC_REVIEWER_PACKAGE_VERSION
    assert package.reviewer_id == "reviewer_a"
    assert package.package_id != reviewer_b.package_id
    assert package.package_id != different_private_key.package_id
    assert tuple(item.order_position for item in package.items) == (1, 2, 3)
    assert tuple(item.blind_review_id for item in package.items) == tuple(
        mapping.blind_review_id
        for mapping in private_manifest.mappings
        if mapping.reviewer_id == "reviewer_a"
    )
    with pytest.raises(ValidationError):
        package.reviewer_id = "reviewer_b"
    with pytest.raises(ValueError, match="at least 32 bytes"):
        build_public_reviewer_package(
            private_manifest,
            reviewer_id="reviewer_a",
            private_commitment_key=b"too-short",
        )
    incompatible_version = package.model_dump(mode="json")
    incompatible_version["package_version"] = "loguic-tts-public-reviewer-package/2.0"
    incompatible_version.pop("package_id")
    with pytest.raises(ValidationError, match="package_version"):
        PublicReviewerPackage.model_validate(incompatible_version)


def test_private_remapping_changes_package_and_every_audio_delivery_identity() -> None:
    private_manifest, package, _ = _public_review_setup()
    remapped = [mapping.model_dump() for mapping in private_manifest.mappings]
    remapped[0]["sample_id"], remapped[1]["sample_id"] = (
        remapped[1]["sample_id"],
        remapped[0]["sample_id"],
    )
    remapped[3]["sample_id"], remapped[4]["sample_id"] = (
        remapped[4]["sample_id"],
        remapped[3]["sample_id"],
    )
    altered_manifest = BlindReviewManifest(
        sample_manifests=private_manifest.sample_manifests,
        mappings=tuple(remapped),
    )
    altered = build_public_reviewer_package(
        altered_manifest,
        reviewer_id="reviewer_a",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    assert altered.delivery_set_commitment != package.delivery_set_commitment
    assert altered.package_id != package.package_id
    assert tuple(item.audio_delivery_id for item in altered.items) != tuple(
        item.audio_delivery_id for item in package.items
    )


def test_normalized_audio_change_changes_private_binding_and_delivery_identity() -> None:
    private_manifest, package, _ = _public_review_setup()
    sample_manifest = private_manifest.sample_manifests[0]
    changed_payload = sample_manifest.samples[0].model_dump()
    changed_payload.pop("sample_id")
    changed_payload["normalized_sha256"] = "9" * 64
    changed_sample = SampleIdentity.model_validate(changed_payload)
    changed_sample_manifest = SampleManifest(
        determinism_probe=sample_manifest.determinism_probe,
        samples=(changed_sample, *sample_manifest.samples[1:]),
    )
    changed_manifest = BlindReviewManifest(
        sample_manifests=(changed_sample_manifest,),
        mappings=_blind_mappings(changed_sample_manifest),
    )
    changed_package = build_public_reviewer_package(
        changed_manifest,
        reviewer_id="reviewer_a",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    assert build_private_reviewer_package_binding(
        changed_manifest,
        reviewer_id="reviewer_a",
    ).binding_id != build_private_reviewer_package_binding(
        private_manifest,
        reviewer_id="reviewer_a",
    ).binding_id
    assert changed_package.package_id != package.package_id
    assert changed_package.items[0].audio_delivery_id != package.items[0].audio_delivery_id


def test_public_package_and_disclosure_never_expose_private_technical_identity() -> None:
    private_manifest, package, state = _public_review_setup()
    serialized_package = package.model_dump_json()
    sample = private_manifest.sample_manifests[0].samples[0]

    assert not {
        "sample_id",
        "engine",
        "engine_version",
        "model_pin",
        "voice_id",
        "private_mapping",
    }.intersection(PublicReviewerPackage.model_fields)
    assert all(
        not {
            "sample_id",
            "engine",
            "engine_version",
            "model_pin",
            "voice_id",
            "private_mapping",
        }.intersection(type(item).model_fields)
        for item in package.items
    )
    assert sample.sample_id not in serialized_package
    assert sample.normalized_sha256 not in serialized_package
    assert sample.generation_case.engine not in serialized_package
    assert sample.generation_case.voice_id not in serialized_package

    state = register_first_listen(
        state,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    state = capture_initial_review(
        state,
        package,
        private_manifest,
        perceived_transcription="I need water.",
        intelligibility="meets",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    disclosed = disclose_review_context(
        state,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    disclosure = disclosed.event_for("disclosed").disclosure
    assert disclosure is not None
    assert set(type(disclosure).model_fields) == {
        "package_id",
        "blind_review_id",
        "reference_text",
        "ipa",
        "target_locale",
    }
    assert sample.sample_id not in disclosure.model_dump_json()


def test_public_workflow_rejects_premature_disclosure_and_rubric() -> None:
    private_manifest, package, delivered = _public_review_setup()
    with pytest.raises(ValueError, match="requires initial_capture"):
        disclose_review_context(
            delivered,
            package,
            private_manifest,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    first_listen = register_first_listen(
        delivered,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    with pytest.raises(ValueError, match="requires initial_capture"):
        disclose_review_context(
            first_listen,
            package,
            private_manifest,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )
    initial_capture = capture_initial_review(
        first_listen,
        package,
        private_manifest,
        perceived_transcription="I need water.",
        intelligibility="meets",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    with pytest.raises(ValueError, match="requires disclosed"):
        complete_review_rubric(
            initial_capture,
            package,
            private_manifest,
            pronunciation_correctness="meets",
            locale_accent_conformance="meets",
            naturalness="meets",
            prosody_rhythm="meets",
            a1_pedagogical_suitability="meets",
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_public_workflow_rejects_lock_before_complete_rubric() -> None:
    private_manifest, package, state = _public_review_setup()
    state = register_first_listen(
        state,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    state = capture_initial_review(
        state,
        package,
        private_manifest,
        perceived_transcription="I need water.",
        intelligibility="meets",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    disclosed = disclose_review_context(
        state,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    with pytest.raises(ValueError, match="requires rubric_complete"):
        lock_public_review(
            disclosed,
            package,
            private_manifest,
            locked_at=LOCKED_AT,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_event_mac_is_mandatory_and_model_validation_never_repairs_it() -> None:
    private_manifest, package, delivered = _public_review_setup()
    missing = delivered.events[0].model_dump(mode="json")
    missing.pop("event_mac")
    with pytest.raises(ValidationError, match="event_mac"):
        PublicReviewWorkflowEvent.model_validate(missing)

    invented = delivered.model_dump(mode="json")
    invented["events"][0]["event_mac"] = "review_event_mac_" + "0" * 64
    invented = _recalculate_public_state_ids(invented)
    structurally_valid = PublicReviewWorkflowState.model_validate(invented)
    with pytest.raises(ValueError, match="MAC authentication failed"):
        register_first_listen(
            structurally_valid,
            package,
            private_manifest,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    with pytest.raises(ValueError, match="private delivery binding"):
        register_first_listen(
            delivered,
            package,
            private_manifest,
            private_commitment_key=b"different-private-commitment-key-v1",
        )


def test_workflow_rejects_missing_altered_and_wrong_predecessor_lineage() -> None:
    private_manifest, package, complete = _complete_public_review()
    missing = complete.model_dump()
    missing.pop("workflow_state_id")
    missing["events"] = list(missing["events"])
    missing["events"].pop(1)
    with pytest.raises(ValidationError, match="complete ordered stage prefix"):
        PublicReviewWorkflowState.model_validate(missing)

    altered = complete.model_dump(mode="json")
    altered["events"][2]["perceived_transcription"] = "altered"
    altered = _recalculate_public_state_ids(altered)
    altered_state = PublicReviewWorkflowState.model_validate(altered)
    with pytest.raises(ValueError, match="MAC authentication failed"):
        lock_public_review(
            altered_state,
            package,
            private_manifest,
            locked_at=LOCKED_AT,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    wrong_predecessor = complete.model_dump()
    wrong_predecessor.pop("workflow_state_id")
    wrong_predecessor["events"][1].pop("event_id")
    wrong_predecessor["events"][1]["predecessor_event_id"] = (
        "review_event_" + "f" * 64
    )
    with pytest.raises(ValidationError, match="predecessor does not match"):
        PublicReviewWorkflowState.model_validate(wrong_predecessor)

    changed_stage = complete.model_dump(mode="json")
    changed_stage["events"][1]["stage"] = "initial_capture"
    changed_stage["events"][1].pop("event_id")
    changed_stage.pop("workflow_state_id")
    with pytest.raises(ValidationError):
        PublicReviewWorkflowState.model_validate(changed_stage)

    changed_context = complete.model_dump(mode="json")
    changed_context["events"][2]["reviewer_id"] = "reviewer_b"
    changed_context["events"][2].pop("event_id")
    changed_context.pop("workflow_state_id")
    with pytest.raises(ValidationError, match="different package or item"):
        PublicReviewWorkflowState.model_validate(changed_context)


def test_complete_chain_with_all_public_hashes_recalculated_is_rejected() -> None:
    private_manifest, package, complete = _complete_public_review()
    handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    fabricated = handoff.model_dump(mode="json")
    for index, event in enumerate(fabricated["workflow_state"]["events"]):
        event["event_mac"] = "review_event_mac_" + hashlib.sha256(
            f"fabricated-{index}".encode("ascii")
        ).hexdigest()
    fabricated = _recalculate_public_handoff_ids(fabricated)
    LockedReviewHandoff.model_validate(fabricated)

    with pytest.raises(ValueError, match="MAC authentication failed"):
        validate_locked_review_handoff(
            package,
            private_manifest,
            _canonical_payload(fabricated),
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_valid_public_sequence_produces_exact_locked_review_and_canonical_handoff() -> None:
    private_manifest, package, complete = _complete_public_review()
    assert not isinstance(complete, HumanReviewRecord)
    assert complete.stage == "rubric_complete"

    handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    expected = _review(
        "reviewer_a",
        blind_review_id=package.items[0].blind_review_id,
    )
    assert isinstance(handoff, LockedReviewHandoff)
    assert handoff.workflow_state.stage == "locked"
    assert handoff.review == expected

    payload = serialize_locked_review_handoff(
        handoff,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    serialized = json.loads(payload)
    assert serialized["review"] == expected.model_dump(mode="json")
    assert set(serialized["review"]) == set(HumanReviewRecord.model_fields)
    claim = validate_locked_review_handoff(
        package,
        private_manifest,
        payload,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    assert isinstance(claim, LockClaim)
    assert claim.review_slot_version == TTS_PUBLIC_REVIEW_SLOT_VERSION
    assert claim.package_id == package.package_id
    assert claim.lock_transition_id == handoff.lock_transition_id
    assert claim.handoff_id == handoff.handoff_id
    assert claim.review == expected
    with pytest.raises(ValueError, match="not canonical JSON"):
        validate_locked_review_handoff(
            package,
            private_manifest,
            payload + b"\n",
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    serialized_text = payload.decode("utf-8")
    for forbidden_field in (
        "sample_id",
        "engine",
        "engine_version",
        "model_pin",
        "voice_id",
        "private_mapping",
    ):
        assert f'"{forbidden_field}"' not in serialized_text
    for sample_manifest in private_manifest.sample_manifests:
        for sample in sample_manifest.samples:
            assert sample.sample_id not in serialized_text
            assert sample.normalized_sha256 not in serialized_text
            assert sample.generation_case.engine not in serialized_text
            assert sample.generation_case.model_pin.model_id not in serialized_text
            assert sample.generation_case.voice_id not in serialized_text
    assert PRIVATE_COMMITMENT_KEY.decode("ascii") not in serialized_text
    reviewer_b_package = build_public_reviewer_package(
        private_manifest,
        reviewer_id="reviewer_b",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    with pytest.raises(ValueError, match="different package"):
        validate_locked_review_handoff(
            reviewer_b_package,
            private_manifest,
            payload,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_handoff_rejects_bare_or_incomplete_fabricated_provenance() -> None:
    private_manifest, package, complete = _complete_public_review()
    direct_review = _review(
        "reviewer_a",
        blind_review_id=package.items[0].blind_review_id,
    )
    bare_payload = json.dumps(
        direct_review.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    with pytest.raises(ValidationError):
        validate_locked_review_handoff(
            package,
            private_manifest,
            bare_payload,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    fabricated = handoff.model_dump(mode="json")
    fabricated.pop("handoff_id")
    fabricated["workflow_state"].pop("workflow_state_id")
    fabricated["workflow_state"]["events"] = list(
        fabricated["workflow_state"]["events"]
    )
    fabricated["workflow_state"]["events"].pop(1)
    fabricated_payload = json.dumps(
        fabricated,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    with pytest.raises(ValidationError, match="complete ordered stage prefix"):
        validate_locked_review_handoff(
            package,
            private_manifest,
            fabricated_payload,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_events_from_other_packages_reviewers_and_items_cannot_be_mixed() -> None:
    _, package, complete = _complete_public_review()
    _, _, other_item = _complete_public_review(item_index=1)
    _, _, reviewer_b = _complete_public_review(reviewer_id="reviewer_b")
    other_key = b"different-private-commitment-key-v1"
    _, _, other_package = _complete_public_review(private_commitment_key=other_key)

    for foreign_state in (other_item, reviewer_b, other_package):
        mixed = complete.model_dump(mode="json")
        mixed["events"][2] = foreign_state.events[2].model_dump(mode="json")
        mixed.pop("workflow_state_id")
        with pytest.raises(ValidationError):
            PublicReviewWorkflowState.model_validate(mixed)


def test_fabricated_root_and_lock_are_rejected() -> None:
    private_manifest, package, delivered = _public_review_setup()
    false_root = delivered.model_dump(mode="json")
    false_root["events"][0]["predecessor_event_mac"] = (
        "review_event_mac_" + "0" * 64
    )
    false_root["events"][0].pop("event_id")
    false_root.pop("workflow_state_id")
    with pytest.raises(ValidationError, match="explicit workflow root"):
        PublicReviewWorkflowState.model_validate(false_root)

    _, _, complete = _complete_public_review()
    handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    false_lock = handoff.model_dump(mode="json")
    false_lock["workflow_state"]["events"][-1]["event_mac"] = (
        "review_event_mac_" + "f" * 64
    )
    false_lock = _recalculate_public_handoff_ids(false_lock)
    with pytest.raises(ValueError, match="MAC authentication failed"):
        validate_locked_review_handoff(
            package,
            private_manifest,
            _canonical_payload(false_lock),
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_disclosure_must_match_the_private_assignment() -> None:
    private_manifest, package, complete = _complete_public_review()
    wrong_disclosure = complete.model_dump(mode="json")
    wrong_disclosure["events"][3]["disclosure"]["reference_text"] = "wrong"
    wrong_disclosure = _authenticate_public_state_for_test(
        wrong_disclosure,
        package,
    )
    wrong_state = PublicReviewWorkflowState.model_validate(wrong_disclosure)
    with pytest.raises(ValueError, match="not authorized by the private assignment"):
        lock_public_review(
            wrong_state,
            package,
            private_manifest,
            locked_at=LOCKED_AT,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )


def test_locked_public_workflow_rejects_mutation_reopen_and_stale_id() -> None:
    private_manifest, package, complete = _complete_public_review()
    handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    with pytest.raises(ValidationError):
        handoff.workflow_state.events = complete.events
    with pytest.raises(ValidationError):
        handoff.review.naturalness = "minor_issue"
    with pytest.raises(ValueError, match="requires delivered"):
        register_first_listen(
            handoff.workflow_state,
            package,
            private_manifest,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )

    stale_package = package.model_dump()
    stale_package["items"][0]["order_position"] = 2
    with pytest.raises(ValidationError, match="canonical causal identity"):
        PublicReviewerPackage.model_validate(stale_package)

    stale_state = handoff.workflow_state.model_dump()
    stale_state["events"][4]["naturalness"] = "minor_issue"
    with pytest.raises(ValidationError, match="canonical causal identity"):
        PublicReviewWorkflowState.model_validate(stale_state)


def test_retry_and_timestamp_branch_produce_stable_slot_and_distinct_handoffs() -> None:
    private_manifest, package, complete = _complete_public_review()
    first = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    identical = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    conflicting = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=LOCKED_AT + timedelta(seconds=1),
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    first_payload = serialize_locked_review_handoff(
        first,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    identical_payload = serialize_locked_review_handoff(
        identical,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    conflicting_payload = serialize_locked_review_handoff(
        conflicting,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    first_claim = validate_locked_review_handoff(
        package,
        private_manifest,
        first_payload,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    identical_claim = validate_locked_review_handoff(
        package,
        private_manifest,
        identical_payload,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    conflicting_claim = validate_locked_review_handoff(
        package,
        private_manifest,
        conflicting_payload,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    assert identical == first
    assert identical_claim == first_claim
    assert conflicting.lock_transition_id == first.lock_transition_id
    assert conflicting_claim.review_slot_id == first_claim.review_slot_id
    assert conflicting_claim.handoff_id != first_claim.handoff_id
    validate_nonconflicting_review_locks((first_claim, identical_claim))
    with pytest.raises(ValueError, match="Conflicting handoffs"):
        validate_nonconflicting_review_locks((first_claim, conflicting_claim))


def test_authenticated_divergent_branches_are_individually_valid_conflicts() -> None:
    private_manifest, package, disclosed = _public_review_setup()
    disclosed = register_first_listen(
        disclosed,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    disclosed = capture_initial_review(
        disclosed,
        package,
        private_manifest,
        perceived_transcription="I need water.",
        intelligibility="meets",
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )
    disclosed = disclose_review_context(
        disclosed,
        package,
        private_manifest,
        private_commitment_key=PRIVATE_COMMITMENT_KEY,
    )

    claims = []
    for naturalness in ("meets", "minor_issue"):
        completed = complete_review_rubric(
            disclosed,
            package,
            private_manifest,
            pronunciation_correctness="meets",
            locale_accent_conformance="meets",
            naturalness=naturalness,
            prosody_rhythm="meets",
            a1_pedagogical_suitability="meets",
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )
        handoff = lock_public_review(
            completed,
            package,
            private_manifest,
            locked_at=LOCKED_AT,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )
        payload = serialize_locked_review_handoff(
            handoff,
            package,
            private_manifest,
            private_commitment_key=PRIVATE_COMMITMENT_KEY,
        )
        claims.append(
            validate_locked_review_handoff(
                package,
                private_manifest,
                payload,
                private_commitment_key=PRIVATE_COMMITMENT_KEY,
            )
        )

    assert claims[0].review_slot_id == claims[1].review_slot_id
    assert claims[0].lock_transition_id != claims[1].lock_transition_id
    assert claims[0].handoff_id != claims[1].handoff_id
    assert not {
        "accepted",
        "acceptance_id",
        "consumed",
        "append_only_position",
    }.intersection(LockClaim.model_fields)
    with pytest.raises(ValueError, match="Conflicting handoffs"):
        validate_nonconflicting_review_locks(claims)


def test_valid_adjudication_for_factual_disagreement() -> None:
    sample_manifest = _replicated_manifest()
    blind_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    mapping_a, mapping_b = blind_manifest.mappings[0], blind_manifest.mappings[3]
    review_a = _review("reviewer_a", blind_review_id=mapping_a.blind_review_id)
    review_b = _review(
        "reviewer_b",
        blind_review_id=mapping_b.blind_review_id,
        naturalness="minor_issue",
    )
    adjudication = AdjudicationRecord(
        review_a=review_a,
        review_b=review_b,
        adjudicator_id="adjudicator-human-001",
        relevant_disagreement_dimensions=("naturalness",),
        adjudicated_labels={"naturalness": "minor_issue"},
    )
    assert adjudication.review_a is review_a
    assert adjudication.review_b is review_b
    assert "blind_review_id" not in AdjudicationRecord.model_fields
    assert review_a.blind_review_id != review_b.blind_review_id
    validate_private_adjudication_reconciliation(adjudication, blind_manifest)


def test_adjudication_rejects_a_review_without_the_required_lock() -> None:
    review_a_payload = _review("reviewer_a").model_dump()
    review_a_payload.pop("locked_at")
    review_b = _review("reviewer_b", naturalness="minor_issue")
    with pytest.raises(ValidationError, match="locked_at"):
        AdjudicationRecord.model_validate(
            {
                "review_a": review_a_payload,
                "review_b": review_b.model_dump(),
                "adjudicator_id": "human",
                "relevant_disagreement_dimensions": ("naturalness",),
                "adjudicated_labels": {"naturalness": "minor_issue"},
            }
        )


def test_reject_reconciliation_for_reviews_resolving_to_different_samples() -> None:
    sample_manifest = _replicated_manifest()
    blind_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    adjudication = AdjudicationRecord(
        review_a=_review("reviewer_a", blind_review_id=blind_manifest.mappings[0].blind_review_id),
        review_b=_review(
            "reviewer_b",
            blind_review_id=blind_manifest.mappings[4].blind_review_id,
            naturalness="minor_issue",
        ),
        adjudicator_id="human",
        relevant_disagreement_dimensions=("naturalness",),
        adjudicated_labels={"naturalness": "minor_issue"},
    )
    with pytest.raises(ValueError, match="resolve to the same sample_id"):
        validate_private_adjudication_reconciliation(adjudication, blind_manifest)


def test_reject_reconciliation_for_missing_blind_mapping() -> None:
    sample_manifest = _replicated_manifest()
    blind_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    adjudication = AdjudicationRecord(
        review_a=_review("reviewer_a", blind_review_id="br_ffffffffffffffffffffffffffffffff"),
        review_b=_review(
            "reviewer_b",
            blind_review_id=blind_manifest.mappings[3].blind_review_id,
            naturalness="minor_issue",
        ),
        adjudicator_id="human",
        relevant_disagreement_dimensions=("naturalness",),
        adjudicated_labels={"naturalness": "minor_issue"},
    )
    with pytest.raises(ValueError, match="must resolve exactly once"):
        validate_private_adjudication_reconciliation(adjudication, blind_manifest)


def test_reject_reconciliation_for_reviewer_mapping_mismatch() -> None:
    sample_manifest = _replicated_manifest()
    blind_manifest = BlindReviewManifest(
        sample_manifests=(sample_manifest,),
        mappings=_blind_mappings(sample_manifest),
    )
    adjudication = AdjudicationRecord(
        review_a=_review("reviewer_a", blind_review_id=blind_manifest.mappings[3].blind_review_id),
        review_b=_review(
            "reviewer_b",
            blind_review_id=blind_manifest.mappings[3].blind_review_id,
            naturalness="minor_issue",
        ),
        adjudicator_id="human",
        relevant_disagreement_dimensions=("naturalness",),
        adjudicated_labels={"naturalness": "minor_issue"},
    )
    with pytest.raises(ValueError, match="must belong to its reviewer"):
        validate_private_adjudication_reconciliation(adjudication, blind_manifest)


def test_reject_adjudication_with_identical_labels() -> None:
    review_a = _review("reviewer_a")
    review_b = _review("reviewer_b")
    with pytest.raises(ValidationError, match="factual label disagreement"):
        AdjudicationRecord(
            review_a=review_a,
            review_b=review_b,
            adjudicator_id="human",
            relevant_disagreement_dimensions=("naturalness",),
            adjudicated_labels={"naturalness": "meets"},
        )


def test_reject_adjudication_for_dimension_without_disagreement() -> None:
    review_a = _review("reviewer_a")
    review_b = _review("reviewer_b", naturalness="minor_issue")
    with pytest.raises(ValidationError, match="factual label disagreement"):
        AdjudicationRecord(
            review_a=review_a,
            review_b=review_b,
            adjudicator_id="human",
            relevant_disagreement_dimensions=("intelligibility",),
            adjudicated_labels={"intelligibility": "meets"},
        )


def test_reject_adjudication_with_same_reviewer_twice() -> None:
    review_a = _review("reviewer_a")
    second_a = _review("reviewer_a", naturalness="minor_issue")
    with pytest.raises(ValidationError, match="reviewer A and reviewer B"):
        AdjudicationRecord(
            review_a=review_a,
            review_b=second_a,
            adjudicator_id="human",
            relevant_disagreement_dimensions=("naturalness",),
            adjudicated_labels={"naturalness": "minor_issue"},
        )


def test_exact_review_scale_and_automatic_acceptance_fields_are_forbidden() -> None:
    assert set(get_args(ReviewLabel)) == {
        "meets",
        "minor_issue",
        "major_issue",
        "not_assessable",
    }
    review = _review("reviewer_a")
    with pytest.raises(ValidationError):
        HumanReviewRecord.model_validate(
            review.model_dump() | {"automatic_acceptance_threshold": 0.9}
        )
    assert not {
        "sample_id",
        "engine",
        "model",
        "model_id",
        "voice",
        "voice_id",
        "private_mapping",
    }.intersection(HumanReviewRecord.model_fields)
    for model in (
        GenerationCase,
        DeterminismProbe,
        SampleIdentity,
        HumanReviewRecord,
        AdjudicationRecord,
    ):
        assert not {
            "automatic_accept",
            "automatic_reject",
            "wer_threshold",
            "gop_threshold",
            "wavlm_threshold",
            "average_score",
            "mastery",
            "progress",
            "best_replica",
            "preferred_replica",
            "selected_replica",
        }.intersection(model.model_fields)
