"""Strict, human-governed evidence contracts for the TTS benchmark v1."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Annotated, Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.tts_wav_normalization import TTS_WAV_NORMALIZATION_PROFILE_VERSION


TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION = "loguic-tts-engine-benchmark/1.0"
CANDIDATE_V4_CONTENT_DIGEST = (
    "sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d"
)

EngineId = Literal["kokoro", "piper"]
TargetLocale = Literal["en-GB", "en-US"]
PinStatus = Literal["pending_local_artifact", "verified"]
ReviewLabel = Literal["meets", "minor_issue", "major_issue", "not_assessable"]
ReviewDimension = Literal[
    "intelligibility",
    "pronunciation_correctness",
    "locale_accent_conformance",
    "naturalness",
    "prosody_rhythm",
    "a1_pedagogical_suitability",
]
DeterminismClassification = Literal[
    "deterministic_for_benchmark",
    "replicated_for_benchmark",
]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
_PORTABLE_REVISION_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_EXPLICIT_GIT_REF_PREFIXES = ("refs/tags/", "refs/heads/")

# Explicit v1 freeze. The focal test derives this tuple from authoritative
# Candidate v4, including text, IPA and locale, so any Candidate drift fails closed.
CANDIDATE_V4_FROZEN_TARGETS: tuple[tuple[str, str, str, TargetLocale], ...] = (
    ("audio.a1-u1-l1.i-need-water.en-us.v1", "I need water.", "/aɪ niːd ˈwɔːtɚ/", "en-US"),
    ("audio.a1-u1-l1.i-need-water.en-gb.v1", "I need water.", "/aɪ niːd ˈwɔːtə/", "en-GB"),
    ("audio.a1-u1-l1.i-need-help.en-gb.v1", "I need help.", "/aɪ niːd help/", "en-GB"),
    ("audio.a1-u1-l1.i-need-food.en-gb.v1", "I need food.", "/aɪ niːd fuːd/", "en-GB"),
    ("audio.a1-u1-l1.water.en-us.v1", "water", "/ˈwɔːtɚ/", "en-US"),
    ("audio.a1-u1-l1.water.en-gb.v1", "water", "/ˈwɔːtə/", "en-GB"),
    ("audio.a1-u1-l1.help.en-us.v1", "help", "/hɛlp/", "en-US"),
    ("audio.a1-u1-l1.help.en-gb.v1", "help", "/help/", "en-GB"),
    ("audio.a1-u1-l1.food.en-us.v1", "food", "/fuːd/", "en-US"),
    ("audio.a1-u1-l1.food.en-gb.v1", "food", "/fuːd/", "en-GB"),
    ("audio.a1-u1-l1.okay.en-us.v1", "Okay.", "/oʊˈkeɪ/", "en-US"),
    ("audio.a1-u1-l1.okay.en-gb.v1", "Okay.", "/əʊˈkeɪ/", "en-GB"),
)
_FROZEN_TARGET_BY_RESOURCE_ID = {
    resource_id: (reference_text, ipa, locale)
    for resource_id, reference_text, ipa, locale in CANDIDATE_V4_FROZEN_TARGETS
}
_FROZEN_CORPUS_RESOURCE_IDS = tuple(
    resource_id for resource_id, _, _, _ in CANDIDATE_V4_FROZEN_TARGETS
)


def _json_value(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _causal_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        _json_value(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return prefix + hashlib.sha256(encoded).hexdigest()


def _derive_or_validate_id(
    values: Any,
    *,
    field_name: str,
    prefix: str,
) -> Any:
    if not isinstance(values, Mapping):
        return values
    data = dict(values)
    payload = {key: value for key, value in data.items() if key != field_name}
    expected = _causal_id(prefix, payload)
    supplied = data.get(field_name)
    if supplied is not None and supplied != expected:
        raise ValueError(f"{field_name} does not match canonical causal identity")
    data[field_name] = expected
    return data


class _StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ModelPin(_StrictFrozenModel):
    """Identify a model pin while distinguishing pending and verified state."""

    model_id: str = Field(min_length=1)
    revision: str | None = None
    sha256: Sha256 | None = None
    status: PinStatus

    @model_validator(mode="after")
    def validate_pin_state(self) -> "ModelPin":
        if not self.model_id.strip():
            raise ValueError("model_id cannot be blank")
        if self.model_id.startswith(("/", "~/")) or (
            len(self.model_id) >= 3
            and self.model_id[1:3] in {":/", ":\\"}
        ):
            raise ValueError("model_id cannot be a machine-specific absolute path")
        if self.revision is not None:
            if not self.revision.strip():
                raise ValueError("model revision cannot be blank")
            revision = self.revision
            if revision.casefold().startswith("file:"):
                raise ValueError("model revision must be a portable revision identifier, not a local path")
            explicit_prefix = next(
                (prefix for prefix in _EXPLICIT_GIT_REF_PREFIXES if revision.startswith(prefix)),
                None,
            )
            if explicit_prefix is not None:
                components = revision.removeprefix(explicit_prefix).split("/")
                is_portable = bool(components) and all(
                    _PORTABLE_REVISION_COMPONENT.fullmatch(component)
                    for component in components
                )
            else:
                is_portable = "/" not in revision and bool(
                    _PORTABLE_REVISION_COMPONENT.fullmatch(revision)
                )
            if not is_portable:
                raise ValueError("model revision must be a portable revision identifier, not a local path")
        if self.status == "pending_local_artifact" and self.sha256 is not None:
            raise ValueError("pending model pin cannot declare a verified sha256")
        if self.status == "verified" and self.revision is None and self.sha256 is None:
            raise ValueError("verified model pin requires revision or sha256")
        return self


class RuntimeEnvironmentPin(_StrictFrozenModel):
    """Identify engine runtime, Python and the reproducible environment lock."""

    runtime_package: EngineId
    runtime_version: str = Field(min_length=1)
    python_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+._a-zA-Z0-9]*)?$")
    environment_fingerprint_sha256: Sha256 | None = None
    status: PinStatus

    @model_validator(mode="after")
    def validate_pin_state(self) -> "RuntimeEnvironmentPin":
        if not self.runtime_version.strip():
            raise ValueError("runtime_version cannot be blank")
        fingerprint = self.environment_fingerprint_sha256
        if self.status == "pending_local_artifact" and fingerprint is not None:
            raise ValueError("pending environment pin cannot declare a verified fingerprint")
        if self.status == "verified" and fingerprint is None:
            raise ValueError("verified environment pin requires a lock fingerprint")
        return self


class BenchmarkProtocolIdentity(_StrictFrozenModel):
    """Freeze the approved protocol, Candidate v4 corpus and WAV profile."""

    protocol_version: Literal[TTS_ENGINE_BENCHMARK_PROTOCOL_VERSION]
    candidate_revision: Literal["a1-u1-candidate-v4"]
    candidate_content_digest: Literal[CANDIDATE_V4_CONTENT_DIGEST]
    normalization_profile_version: Literal[TTS_WAV_NORMALIZATION_PROFILE_VERSION]
    corpus_resource_ids: tuple[str, ...] = Field(min_length=12, max_length=12)

    @model_validator(mode="after")
    def validate_frozen_candidate_corpus(self) -> "BenchmarkProtocolIdentity":
        if self.corpus_resource_ids != _FROZEN_CORPUS_RESOURCE_IDS:
            raise ValueError("Benchmark corpus must equal the frozen Candidate v4 corpus")
        return self


class GenerationCase(_StrictFrozenModel):
    """Identify one complete causal rendering configuration without timestamps."""

    generation_case_id: str = Field(pattern=r"^gcase_[0-9a-f]{64}$")
    protocol_identity: BenchmarkProtocolIdentity
    resource_id: str = Field(pattern=r"^audio\.")
    reference_text: str = Field(min_length=1)
    ipa: str | None
    target_locale: TargetLocale
    engine: EngineId
    engine_version: str = Field(min_length=1)
    model_pin: ModelPin
    voice_id: str = Field(min_length=1)
    generation_parameters: tuple[tuple[str, str], ...] = Field(min_length=1)
    runtime_environment_pin: RuntimeEnvironmentPin

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="generation_case_id", prefix="gcase_")

    @model_validator(mode="after")
    def validate_generation_case(self) -> "GenerationCase":
        frozen_target = _FROZEN_TARGET_BY_RESOURCE_ID.get(self.resource_id)
        if frozen_target is None:
            raise ValueError("Generation target is not in frozen Candidate v4 corpus")
        if (self.reference_text, self.ipa, self.target_locale) != frozen_target:
            raise ValueError("Generation target text/IPA/locale does not match Candidate v4")
        approved_configurations = {
            ("kokoro", "0.9.4", "af_heart", "en-US"),
            ("kokoro", "0.9.4", "af_bella", "en-US"),
            ("kokoro", "0.9.4", "bf_emma", "en-GB"),
            ("kokoro", "0.9.4", "bf_isabella", "en-GB"),
            ("piper", "1.8.0", "en_GB-cori-medium", "en-GB"),
            ("piper", "1.8.0", "en_GB-alba-medium", "en-GB"),
            ("piper", "1.8.0", "en_US-kristin-medium", "en-US"),
            ("piper", "1.8.0", "en_US-joe-medium", "en-US"),
        }
        if (self.engine, self.engine_version, self.voice_id, self.target_locale) not in approved_configurations:
            raise ValueError("Generation case engine/version/voice/locale is not approved")
        runtime_pin = self.runtime_environment_pin
        if runtime_pin.runtime_package != self.engine or runtime_pin.runtime_version != self.engine_version:
            raise ValueError("Runtime pin must match generation engine and version")
        parameter_names = tuple(name for name, _ in self.generation_parameters)
        if any(not name.strip() for name in parameter_names):
            raise ValueError("Generation parameter names cannot be blank")
        if any(not value.strip() for _, value in self.generation_parameters):
            raise ValueError("Generation parameter values cannot be blank")
        if len(set(parameter_names)) != len(parameter_names):
            raise ValueError("Generation parameter names must be unique")
        return self


def _determinism_applicability_scope(
    generation_case: GenerationCase,
) -> tuple[Any, ...]:
    """Return the target-independent configuration authorized by a probe."""

    return (
        generation_case.protocol_identity,
        generation_case.engine,
        generation_case.engine_version,
        generation_case.model_pin,
        generation_case.voice_id,
        generation_case.target_locale,
        generation_case.generation_parameters,
        generation_case.runtime_environment_pin,
    )


class DeterminismExecution(_StrictFrozenModel):
    """Identify one of three distinct executions of one generation case."""

    execution_id: str = Field(pattern=r"^dexec_[0-9a-f]{64}$")
    generation_case_id: str = Field(pattern=r"^gcase_[0-9a-f]{64}$")
    execution_index: Literal[1, 2, 3]
    raw_sha256: Sha256

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="execution_id", prefix="dexec_")


class DeterminismProbe(_StrictFrozenModel):
    """Validate three distinct executions and the adaptive classification."""

    probe_id: str = Field(pattern=r"^dprobe_[0-9a-f]{64}$")
    generation_case: GenerationCase
    executions: tuple[DeterminismExecution, DeterminismExecution, DeterminismExecution]
    classification: DeterminismClassification
    required_replication_count: Literal[1, 3]

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="probe_id", prefix="dprobe_")

    @model_validator(mode="after")
    def validate_probe(self) -> "DeterminismProbe":
        if len({execution.execution_id for execution in self.executions}) != 3:
            raise ValueError("Determinism execution_id values must be unique")
        if {execution.execution_index for execution in self.executions} != {1, 2, 3}:
            raise ValueError("Determinism executions must use indexes 1, 2 and 3")
        if any(execution.generation_case_id != self.generation_case.generation_case_id for execution in self.executions):
            raise ValueError("Determinism executions must share one generation case")
        all_raw_hashes_identical = len({execution.raw_sha256 for execution in self.executions}) == 1
        expected = (
            ("deterministic_for_benchmark", 1)
            if all_raw_hashes_identical
            else ("replicated_for_benchmark", 3)
        )
        if (self.classification, self.required_replication_count) != expected:
            raise ValueError("Determinism classification contradicts execution hashes")
        return self


class SampleIdentity(_StrictFrozenModel):
    """Bind one artifact identity to its generation case and authorized probe."""

    sample_id: str = Field(pattern=r"^sample_[0-9a-f]{64}$")
    generation_case: GenerationCase
    determinism_probe: DeterminismProbe
    replication_index: Literal[1, 2, 3]
    raw_sha256: Sha256
    normalized_sha256: Sha256
    normalization_profile_version: Literal[TTS_WAV_NORMALIZATION_PROFILE_VERSION]

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="sample_id", prefix="sample_")

    @model_validator(mode="after")
    def validate_sample(self) -> "SampleIdentity":
        if _determinism_applicability_scope(
            self.determinism_probe.generation_case
        ) != _determinism_applicability_scope(self.generation_case):
            raise ValueError("Sample generation configuration must match determinism probe scope")
        if self.normalization_profile_version != self.generation_case.protocol_identity.normalization_profile_version:
            raise ValueError("Sample normalization profile must match generation protocol")
        if self.determinism_probe.classification == "deterministic_for_benchmark" and self.replication_index != 1:
            raise ValueError("Deterministic benchmark samples use replication_index 1")
        return self


class SampleManifest(_StrictFrozenModel):
    """Enforce complete 1-or-3 sample coverage and cross-record uniqueness."""

    determinism_probe: DeterminismProbe
    samples: tuple[SampleIdentity, ...] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def validate_samples(self) -> "SampleManifest":
        if any(sample.determinism_probe != self.determinism_probe for sample in self.samples):
            raise ValueError("All samples must share the manifest determinism probe")
        generation_case = self.samples[0].generation_case
        if any(sample.generation_case != generation_case for sample in self.samples[1:]):
            raise ValueError("All samples must share one complete target-specific generation case")
        expected_indexes = {1} if self.determinism_probe.classification == "deterministic_for_benchmark" else {1, 2, 3}
        if (
            len(self.samples) != len(expected_indexes)
            or {sample.replication_index for sample in self.samples} != expected_indexes
        ):
            raise ValueError("Sample manifest must contain the complete 1-or-3 index set")
        if len({sample.sample_id for sample in self.samples}) != len(self.samples):
            raise ValueError("Sample manifest sample_id values must be unique")
        return self


class BlindReviewMapping(_StrictFrozenModel):
    """Keep one private reviewer-specific opaque mapping entry."""

    blind_review_id: str = Field(pattern=r"^br_[0-9a-f]{32}$")
    sample_id: str = Field(pattern=r"^sample_[0-9a-f]{64}$")
    reviewer_id: Literal["reviewer_a", "reviewer_b"]
    order_position: int = Field(ge=1)
    private_mapping: Literal[True]


class BlindReviewManifest(_StrictFrozenModel):
    """Enforce a private bijective review mapping and reviewer-specific order."""

    sample_manifests: tuple[SampleManifest, ...] = Field(min_length=1)
    mappings: tuple[BlindReviewMapping, ...] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_mapping(self) -> "BlindReviewManifest":
        samples = tuple(
            sample
            for manifest in self.sample_manifests
            for sample in manifest.samples
        )
        if len({sample.sample_id for sample in samples}) != len(samples):
            raise ValueError("Blind manifest sample_id values must be unique")
        if len({mapping.blind_review_id for mapping in self.mappings}) != len(self.mappings):
            raise ValueError("blind_review_id values must be unique")
        reviewer_positions = {(mapping.reviewer_id, mapping.order_position) for mapping in self.mappings}
        if len(reviewer_positions) != len(self.mappings):
            raise ValueError("Reviewer order positions must be unique per reviewer")
        actual_coverage = {(mapping.reviewer_id, mapping.sample_id) for mapping in self.mappings}
        if len(actual_coverage) != len(self.mappings):
            raise ValueError("Each reviewer may receive each sample only once")
        expected_coverage = {
            (reviewer_id, sample.sample_id)
            for reviewer_id in ("reviewer_a", "reviewer_b")
            for sample in samples
        }
        if actual_coverage != expected_coverage:
            raise ValueError("Blind mapping must cover every sample for both reviewers")
        return self


class HumanReviewRecord(_StrictFrozenModel):
    """Preserve one independent original human review without automatic judgment."""

    review_id: str = Field(pattern=r"^review_[0-9a-f]{64}$")
    blind_review_id: str = Field(pattern=r"^br_[0-9a-f]{32}$")
    reviewer_id: Literal["reviewer_a", "reviewer_b"]
    perceived_transcription: str = Field(min_length=1)
    first_listen_without_transcript: Literal[True]
    reference_text_revealed_after_first_listen: Literal[True]
    ipa_revealed_after_first_listen: Literal[True]
    target_locale_revealed_after_first_listen: Literal[True]
    intelligibility: ReviewLabel
    pronunciation_correctness: ReviewLabel
    locale_accent_conformance: ReviewLabel
    naturalness: ReviewLabel
    prosody_rhythm: ReviewLabel
    a1_pedagogical_suitability: ReviewLabel

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="review_id", prefix="review_")


class AdjudicationRecord(_StrictFrozenModel):
    """Keep factual disagreement adjudication separate from original reviews."""

    adjudication_id: str = Field(pattern=r"^adjudication_[0-9a-f]{64}$")
    blind_review_id: str = Field(pattern=r"^br_[0-9a-f]{32}$")
    review_a: HumanReviewRecord
    review_b: HumanReviewRecord
    adjudicator_id: str = Field(min_length=1)
    relevant_disagreement_dimensions: tuple[ReviewDimension, ...] = Field(min_length=1)
    adjudicated_labels: dict[ReviewDimension, ReviewLabel] = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def bind_causal_id(cls, values: Any) -> Any:
        return _derive_or_validate_id(values, field_name="adjudication_id", prefix="adjudication_")

    @model_validator(mode="after")
    def validate_adjudication(self) -> "AdjudicationRecord":
        if self.review_a.reviewer_id != "reviewer_a" or self.review_b.reviewer_id != "reviewer_b":
            raise ValueError("Adjudication requires original reviewer A and reviewer B records")
        if self.review_a.blind_review_id != self.review_b.blind_review_id:
            raise ValueError("Adjudication reviews must share blind_review_id")
        if self.blind_review_id != self.review_a.blind_review_id:
            raise ValueError("Adjudication must share the original reviews blind_review_id")
        dimensions = self.relevant_disagreement_dimensions
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("Relevant disagreement dimensions must be unique")
        factual_disagreements = {
            dimension
            for dimension in (
                "intelligibility",
                "pronunciation_correctness",
                "locale_accent_conformance",
                "naturalness",
                "prosody_rhythm",
                "a1_pedagogical_suitability",
            )
            if getattr(self.review_a, dimension) != getattr(self.review_b, dimension)
        }
        if not set(dimensions).issubset(factual_disagreements):
            raise ValueError("Adjudication dimensions must contain factual label disagreement")
        if set(self.adjudicated_labels) != set(dimensions):
            raise ValueError("Adjudicated labels must cover only relevant disagreements")
        return self
