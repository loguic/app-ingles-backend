from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PhoneticCalibrationSample(BaseModel):
    """Describe one controlled human calibration sample.

    Describe una muestra humana controlada para calibración.
    """

    sample_id: str = Field(min_length=1)
    reference_text: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    audio_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_class: Literal["unlabeled", "acceptable", "variant", "known_error"]


class RepresentativePhoneticCalibrationSample(PhoneticCalibrationSample):
    """Identify a calibration sample by pseudonymous speaker and session.

    Identifica una muestra de calibración por hablante y sesión pseudónimos.
    """

    speaker_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class PhoneticCalibrationHumanLabel(BaseModel):
    """Record one independent human judgment for a calibration sample.

    Registra un juicio humano independiente para una muestra de calibración.
    """

    sample_id: str = Field(min_length=1)
    labeler_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]


class PhoneticCalibrationMeasurement(BaseModel):
    """Represent one reproducible analyzer result for calibration.

    Representa un resultado reproducible del analizador para calibración.
    """

    sample_id: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    analyzed_at: datetime


class RepresentativePhoneticCalibrationCoverage(BaseModel):
    """Describe observable coverage of a representative calibration corpus.

    Describe la cobertura observable de un corpus representativo de calibración.
    """

    sample_count: int = Field(ge=0)
    speaker_count: int = Field(ge=0)
    session_count: int = Field(ge=0)


class RepresentativePhoneticCalibrationObservation(BaseModel):
    """Link a representative human sample to its acoustic measurement.

    Vincula una muestra humana representativa con su medición acústica.
    """

    sample: RepresentativePhoneticCalibrationSample
    measurement: PhoneticCalibrationMeasurement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.sample.sample_id != self.measurement.sample_id:
            raise ValueError("Calibration sample and measurement must share sample_id")
        return self


class PhoneticCalibrationObservation(BaseModel):
    """Link one controlled sample to its acoustic measurement.

    Vincula una muestra controlada con su medición acústica.
    """

    sample: PhoneticCalibrationSample
    measurement: PhoneticCalibrationMeasurement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.sample.sample_id != self.measurement.sample_id:
            raise ValueError("Calibration sample and measurement must share sample_id")
        return self

class PhoneticCalibrationHumanAgreement(BaseModel):
    """Summarize observed human-label agreement without deriving truth.

    Resume el acuerdo observado entre etiquetas humanas sin derivar verdad.
    """

    sample_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label_count: int = Field(ge=1)
    labeler_count: int = Field(ge=1)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous: bool


class PhoneticCalibrationHumanRelationship(BaseModel):
    """Relate technical measurement to descriptive human agreement.

    Relaciona medición técnica con acuerdo humano descriptivo.
    """

    measurement: PhoneticCalibrationMeasurement
    human_labels: list[PhoneticCalibrationHumanLabel] = Field(default_factory=list)
    human_agreement: PhoneticCalibrationHumanAgreement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.measurement.sample_id != self.human_agreement.sample_id:
            raise ValueError("Calibration measurement and human agreement must share sample_id")

        for label in self.human_labels:
            if (
                label.sample_id != self.human_agreement.sample_id
                or label.rubric_version != self.human_agreement.rubric_version
            ):
                raise ValueError(
                    "Human labels and human agreement must share sample_id and rubric_version"
                )

        return self


class PhoneticCalibrationModelHumanObservation(BaseModel):
    """Describe one technical measurement beside human agreement.

    Describe una medición técnica junto al acuerdo humano observado.
    """

    sample_id: str = Field(min_length=1)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    label_count: int = Field(ge=1)
    labeler_count: int = Field(ge=1)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous: bool


class PhoneticCalibrationModelHumanSummary(BaseModel):
    """Summarize descriptive model-human observations by versioned context.

    Resume observaciones descriptivas modelo-humano por contexto versionado.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    observation_count: int = Field(ge=1)
    sample_count: int = Field(ge=1)
    score_min: float = Field(ge=0.0, le=1.0)
    score_max: float = Field(ge=0.0, le=1.0)
    score_mean: float = Field(ge=0.0, le=1.0)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous_count: int = Field(ge=0)


class PhoneticCalibrationHumanLabelScoreSummary(BaseModel):
    """Describe technical scores observed beside one human label.

    Describe scores técnicos observados junto a una etiqueta humana.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]
    observation_count: int = Field(ge=1)
    sample_count: int = Field(ge=1)
    score_min: float = Field(ge=0.0, le=1.0)
    score_max: float = Field(ge=0.0, le=1.0)
    score_mean: float = Field(ge=0.0, le=1.0)


class PhoneticCalibrationHumanLabelScoreDistribution(BaseModel):
    """Describe robust technical-score distribution beside one human label.

    Describe la distribución robusta de scores técnicos junto a una etiqueta humana.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]
    observation_count: int = Field(ge=1)
    sample_count: int = Field(ge=1)
    score_q25: float = Field(ge=0.0, le=1.0)
    score_median: float = Field(ge=0.0, le=1.0)
    score_q75: float = Field(ge=0.0, le=1.0)


class PhoneticCalibrationHumanLabelScoreOverlap(BaseModel):
    """Describe observed IQR overlap between two human-label score distributions.

    Describe el solapamiento IQR observado entre dos distribuciones por etiqueta humana.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    left_label: Literal["acceptable", "variant", "known_error"]
    right_label: Literal["acceptable", "variant", "known_error"]
    overlap_lower: float | None = Field(default=None, ge=0.0, le=1.0)
    overlap_upper: float | None = Field(default=None, ge=0.0, le=1.0)
    overlap_width: float = Field(ge=0.0, le=1.0)
    overlaps: bool

    @model_validator(mode="after")
    def validate_overlap_shape(self):
        if self.overlaps:
            if self.overlap_lower is None or self.overlap_upper is None:
                raise ValueError("Overlapping distributions require overlap bounds")
        else:
            if self.overlap_lower is not None or self.overlap_upper is not None:
                raise ValueError("Non-overlapping distributions must not define overlap bounds")
            if self.overlap_width != 0.0:
                raise ValueError("Non-overlapping distributions must have zero overlap width")
        return self


class PhoneticCalibrationDescriptiveReport(BaseModel):
    """Consolidate descriptive model-human calibration evidence.

    Consolida evidencia descriptiva de calibración modelo-humano.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    summary: PhoneticCalibrationModelHumanSummary
    score_distributions: list[PhoneticCalibrationHumanLabelScoreDistribution] = Field(
        default_factory=list
    )
    overlaps: list[PhoneticCalibrationHumanLabelScoreOverlap] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_versioned_context(self):
        expected = (
            self.analyzer_id,
            self.analyzer_version,
            self.rubric_version,
        )

        summary_context = (
            self.summary.analyzer_id,
            self.summary.analyzer_version,
            self.summary.rubric_version,
        )
        if summary_context != expected:
            raise ValueError("Report summary must share the report versioned context")

        for distribution in self.score_distributions:
            distribution_context = (
                distribution.analyzer_id,
                distribution.analyzer_version,
                distribution.rubric_version,
            )
            if distribution_context != expected:
                raise ValueError(
                    "Report score distributions must share the report versioned context"
                )

        for overlap in self.overlaps:
            overlap_context = (
                overlap.analyzer_id,
                overlap.analyzer_version,
                overlap.rubric_version,
            )
            if overlap_context != expected:
                raise ValueError(
                    "Report overlaps must share the report versioned context"
                )

        return self

class PhoneticCalibrationDescriptiveReportArtifact(BaseModel):
    """Identify a reproducible descriptive calibration report artifact.

    Identifica un artefacto reproducible del informe descriptivo de calibración.
    """

    report_version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report: PhoneticCalibrationDescriptiveReport

class PhoneticCalibrationDescriptiveReportArtifactVerification(BaseModel):
    """Describe integrity verification of a descriptive report artifact.

    Describe la verificación de integridad de un artefacto de informe descriptivo.
    """

    report_version: str = Field(min_length=1)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    computed_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    matches_content: bool
