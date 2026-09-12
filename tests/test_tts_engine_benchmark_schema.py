from __future__ import annotations

import json
from pathlib import Path
from typing import Any, get_args

import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.schemas.tts_engine_benchmark import (
    CANDIDATE_V4_CONTENT_DIGEST,
    CANDIDATE_V4_FROZEN_TARGETS,
    TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION,
    AdjudicationRecord,
    BenchmarkProtocolIdentity,
    BlindReviewManifest,
    BlindReviewMapping,
    DeterminismExecution,
    DeterminismProbe,
    GenerationCase,
    HumanReviewRecord,
    ModelPin,
    ReviewLabel,
    RuntimeEnvironmentPin,
    SampleIdentity,
    SampleManifest,
)
from app.schemas.tts_wav_normalization import TTS_WAV_NORMALIZATION_PROFILE_VERSION
from app.services.pedagogical_candidate_payload_identity import (
    derive_candidate_payload_identity,
)


CANDIDATE_V4_PATH = (
    Path(__file__).resolve().parents[1]
    / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
)


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


def _blind_mappings(manifest: SampleManifest) -> tuple[BlindReviewMapping, ...]:
    mappings = []
    opaque_index = 1
    for reviewer_id in ("reviewer_a", "reviewer_b"):
        for order_position, sample in enumerate(manifest.samples, start=1):
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


def test_valid_adjudication_for_factual_disagreement() -> None:
    review_a = _review("reviewer_a")
    review_b = _review("reviewer_b", naturalness="minor_issue")
    adjudication = AdjudicationRecord(
        blind_review_id=review_a.blind_review_id,
        review_a=review_a,
        review_b=review_b,
        adjudicator_id="adjudicator-human-001",
        relevant_disagreement_dimensions=("naturalness",),
        adjudicated_labels={"naturalness": "minor_issue"},
    )
    assert adjudication.review_a is review_a
    assert adjudication.review_b is review_b


def test_reject_adjudication_with_different_blind_ids() -> None:
    with pytest.raises(ValidationError, match="must share blind_review_id"):
        AdjudicationRecord(
            blind_review_id="br_0123456789abcdef0123456789abcdef",
            review_a=_review("reviewer_a"),
            review_b=_review(
                "reviewer_b",
                blind_review_id="br_ffffffffffffffffffffffffffffffff",
                naturalness="minor_issue",
            ),
            adjudicator_id="human",
            relevant_disagreement_dimensions=("naturalness",),
            adjudicated_labels={"naturalness": "minor_issue"},
        )


def test_reject_adjudication_with_identical_labels() -> None:
    review_a = _review("reviewer_a")
    review_b = _review("reviewer_b")
    with pytest.raises(ValidationError, match="factual label disagreement"):
        AdjudicationRecord(
            blind_review_id=review_a.blind_review_id,
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
            blind_review_id=review_a.blind_review_id,
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
            blind_review_id=review_a.blind_review_id,
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
