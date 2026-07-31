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


class RegionalRepresentativePhoneticCalibrationSample(
    RepresentativePhoneticCalibrationSample
):
    """Identify the pronunciation reference locale used for one human sample.

    Identifica la variante regional de referencia usada para una muestra humana.
    """

    reference_locale: Literal["en-US", "en-GB"]


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


class RegionalRepresentativePhoneticCalibrationCoverage(BaseModel):
    """Describe observable representative corpus coverage by reference locale.

    Describe la cobertura observable del corpus representativo por variante de referencia.
    """

    reference_locale: Literal["en-US", "en-GB"]
    sample_count: int = Field(ge=0)
    speaker_count: int = Field(ge=0)
    session_count: int = Field(ge=0)


class RegionalPhoneticCalibrationHumanEvidenceCoverage(BaseModel):
    """Describe regional coverage of independently reviewed human evidence.

    Describe la cobertura regional de evidencia humana revisada independientemente.
    """

    reference_locale: Literal["en-US", "en-GB"]
    rubric_version: str = Field(min_length=1)
    sample_count: int = Field(ge=0)
    speaker_count: int = Field(ge=0)
    session_count: int = Field(ge=0)
    label_count: int = Field(ge=0)
    labeler_count: int = Field(ge=0)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous_sample_count: int = Field(ge=0)


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


class PhoneticCalibrationHumanLabelScoreIqrGap(BaseModel):
    """Describe the observed gap between two human-label score IQRs.

    Describe la distancia observada entre dos IQR de scores por etiqueta humana.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    left_label: Literal["acceptable", "variant", "known_error"]
    right_label: Literal["acceptable", "variant", "known_error"]
    gap_width: float = Field(ge=0.0, le=1.0)
    separated: bool

    @model_validator(mode="after")
    def validate_iqr_gap(self):
        if self.separated and self.gap_width <= 0.0:
            raise ValueError("Separated IQRs require a positive gap width")
        if not self.separated and self.gap_width != 0.0:
            raise ValueError("Non-separated IQRs must have zero gap width")
        return self


class PhoneticCalibrationHumanLabelScoreIqrRelationship(BaseModel):
    """Combine descriptive overlap and gap evidence for one human-label IQR pair.

    Combina evidencia descriptiva de solapamiento y distancia para un par de IQR humanos.
    """

    overlap: PhoneticCalibrationHumanLabelScoreOverlap
    gap: PhoneticCalibrationHumanLabelScoreIqrGap

    @model_validator(mode="after")
    def validate_iqr_relationship(self):
        overlap_key = (
            self.overlap.analyzer_id,
            self.overlap.analyzer_version,
            self.overlap.rubric_version,
            self.overlap.left_label,
            self.overlap.right_label,
        )
        gap_key = (
            self.gap.analyzer_id,
            self.gap.analyzer_version,
            self.gap.rubric_version,
            self.gap.left_label,
            self.gap.right_label,
        )
        if overlap_key != gap_key:
            raise ValueError(
                "IQR overlap and gap must describe the same versioned label pair"
            )

        if self.overlap.overlaps == self.gap.separated:
            raise ValueError(
                "IQR overlap and separation states must be complementary"
            )

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

class PhoneticCalibrationDescriptiveReportArtifactComparison(BaseModel):
    """Describe a reproducible comparison between calibration report artifacts.

    Describe una comparación reproducible entre artefactos de informes de calibración.
    """

    left_report_version: str = Field(min_length=1)
    left_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    left_analyzer_id: str = Field(min_length=1)
    left_analyzer_version: str = Field(min_length=1)
    right_report_version: str = Field(min_length=1)
    right_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    right_analyzer_id: str = Field(min_length=1)
    right_analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)

class PhoneticCalibrationHumanEvidenceIdentity(BaseModel):
    """Identify reproducibly the human evidence used for calibration comparison.

    Identifica reproduciblemente la evidencia humana usada para comparar calibraciones.
    """

    rubric_version: str = Field(min_length=1)
    sample_count: int = Field(ge=1)
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

class PhoneticCalibrationHumanEvidenceCompatibility(BaseModel):
    """Describe reproducible compatibility between two human evidence identities.

    Describe la compatibilidad reproducible entre dos identidades de evidencia humana.
    """

    left: PhoneticCalibrationHumanEvidenceIdentity
    right: PhoneticCalibrationHumanEvidenceIdentity
    same_evidence: bool

class PhoneticCalibrationComparableArtifactContext(BaseModel):
    """Combine artifact comparison with reproducible human evidence compatibility.

    Combina la comparación de artefactos con compatibilidad reproducible de evidencia humana.
    """

    artifact_comparison: PhoneticCalibrationDescriptiveReportArtifactComparison
    human_evidence_compatibility: PhoneticCalibrationHumanEvidenceCompatibility

    @model_validator(mode="after")
    def validate_comparable_context(self):
        compatibility = self.human_evidence_compatibility
        if not compatibility.same_evidence:
            raise ValueError(
                "Comparable calibration context requires the same human evidence"
            )

        expected_rubric = self.artifact_comparison.rubric_version
        if compatibility.left.rubric_version != expected_rubric:
            raise ValueError(
                "Left human evidence rubric must match artifact comparison rubric"
            )
        if compatibility.right.rubric_version != expected_rubric:
            raise ValueError(
                "Right human evidence rubric must match artifact comparison rubric"
            )

        return self

class PhoneticCalibrationTechnicalCoverageIdentity(BaseModel):
    """Identify reproducibly the sample coverage of a technical calibration.

    Identifica reproduciblemente la cobertura de muestras de una calibración técnica.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    sample_count: int = Field(ge=1)
    sample_ids_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

class PhoneticCalibrationTechnicalCoverageCompatibility(BaseModel):
    """Describe reproducible compatibility between two technical coverage identities.

    Describe la compatibilidad reproducible entre dos identidades de cobertura técnica.
    """

    left: PhoneticCalibrationTechnicalCoverageIdentity
    right: PhoneticCalibrationTechnicalCoverageIdentity
    same_coverage: bool

class PhoneticCalibrationTechnicalComparisonContext(BaseModel):
    """Combine comparable artifacts with reproducible technical coverage compatibility.

    Combina artefactos comparables con compatibilidad reproducible de cobertura técnica.
    """

    comparable_artifact_context: PhoneticCalibrationComparableArtifactContext
    technical_coverage_compatibility: PhoneticCalibrationTechnicalCoverageCompatibility

    @model_validator(mode="after")
    def validate_technical_comparison_context(self):
        artifact_comparison = self.comparable_artifact_context.artifact_comparison
        coverage = self.technical_coverage_compatibility

        if not coverage.same_coverage:
            raise ValueError(
                "Technical comparison context requires the same technical coverage"
            )

        left_expected = (
            artifact_comparison.left_analyzer_id,
            artifact_comparison.left_analyzer_version,
            artifact_comparison.rubric_version,
        )
        left_actual = (
            coverage.left.analyzer_id,
            coverage.left.analyzer_version,
            coverage.left.rubric_version,
        )
        if left_actual != left_expected:
            raise ValueError(
                "Left technical coverage must match left artifact comparison context"
            )

        right_expected = (
            artifact_comparison.right_analyzer_id,
            artifact_comparison.right_analyzer_version,
            artifact_comparison.rubric_version,
        )
        right_actual = (
            coverage.right.analyzer_id,
            coverage.right.analyzer_version,
            coverage.right.rubric_version,
        )
        if right_actual != right_expected:
            raise ValueError(
                "Right technical coverage must match right artifact comparison context"
            )

        return self

class PhoneticCalibrationHumanLabelScoreComparison(BaseModel):
    """Describe score differences for one human label across comparable calibrations.

    Describe diferencias de score para una etiqueta humana entre calibraciones comparables.
    """

    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]
    left_analyzer_id: str = Field(min_length=1)
    left_analyzer_version: str = Field(min_length=1)
    right_analyzer_id: str = Field(min_length=1)
    right_analyzer_version: str = Field(min_length=1)
    left_observation_count: int = Field(ge=1)
    right_observation_count: int = Field(ge=1)
    left_median: float = Field(ge=0.0, le=1.0)
    right_median: float = Field(ge=0.0, le=1.0)
    median_difference: float = Field(ge=-1.0, le=1.0)

    @model_validator(mode="after")
    def validate_median_difference(self):
        expected = self.right_median - self.left_median
        if abs(self.median_difference - expected) > 1e-12:
            raise ValueError(
                "Median difference must equal right median minus left median"
            )
        return self

class PhoneticCalibrationHumanLabelScoreDistributionComparison(BaseModel):
    """Describe robust score distribution differences for one human label.

    Describe diferencias robustas de distribución de scores para una etiqueta humana.
    """

    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]
    left_analyzer_id: str = Field(min_length=1)
    left_analyzer_version: str = Field(min_length=1)
    right_analyzer_id: str = Field(min_length=1)
    right_analyzer_version: str = Field(min_length=1)
    left_sample_count: int = Field(ge=1)
    right_sample_count: int = Field(ge=1)
    left_score_q25: float = Field(ge=0.0, le=1.0)
    right_score_q25: float = Field(ge=0.0, le=1.0)
    score_q25_difference: float = Field(ge=-1.0, le=1.0)
    left_score_median: float = Field(ge=0.0, le=1.0)
    right_score_median: float = Field(ge=0.0, le=1.0)
    score_median_difference: float = Field(ge=-1.0, le=1.0)
    left_score_q75: float = Field(ge=0.0, le=1.0)
    right_score_q75: float = Field(ge=0.0, le=1.0)
    score_q75_difference: float = Field(ge=-1.0, le=1.0)

    @model_validator(mode="after")
    def validate_distribution_differences(self):
        expected_q25 = self.right_score_q25 - self.left_score_q25
        expected_median = self.right_score_median - self.left_score_median
        expected_q75 = self.right_score_q75 - self.left_score_q75

        if abs(self.score_q25_difference - expected_q25) > 1e-12:
            raise ValueError(
                "Q25 difference must equal right Q25 minus left Q25"
            )
        if abs(self.score_median_difference - expected_median) > 1e-12:
            raise ValueError(
                "Median difference must equal right median minus left median"
            )
        if abs(self.score_q75_difference - expected_q75) > 1e-12:
            raise ValueError(
                "Q75 difference must equal right Q75 minus left Q75"
            )
        return self

class PhoneticCalibrationTechnicalDistributionComparisonReport(BaseModel):
    """Consolidate robust human-label score comparisons in one technical context.

    Consolida comparaciones robustas por etiqueta humana en un contexto técnico.
    """

    context: PhoneticCalibrationTechnicalComparisonContext
    comparisons: list[
        PhoneticCalibrationHumanLabelScoreDistributionComparison
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_comparison_report(self):
        artifact_comparison = (
            self.context.comparable_artifact_context.artifact_comparison
        )
        expected = (
            artifact_comparison.left_analyzer_id,
            artifact_comparison.left_analyzer_version,
            artifact_comparison.right_analyzer_id,
            artifact_comparison.right_analyzer_version,
            artifact_comparison.rubric_version,
        )

        labels = set()
        for comparison in self.comparisons:
            actual = (
                comparison.left_analyzer_id,
                comparison.left_analyzer_version,
                comparison.right_analyzer_id,
                comparison.right_analyzer_version,
                comparison.rubric_version,
            )
            if actual != expected:
                raise ValueError(
                    "Distribution comparison must match technical comparison context"
                )

            if comparison.label in labels:
                raise ValueError(
                    "Technical distribution comparison report requires unique human labels"
                )
            labels.add(comparison.label)

        return self

class PhoneticCalibrationTechnicalDistributionComparisonReportArtifact(BaseModel):
    """Version a technical distribution comparison report with reproducible identity.

    Versiona un informe de comparación técnica de distribuciones con identidad reproducible.
    """

    artifact_version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report: PhoneticCalibrationTechnicalDistributionComparisonReport

class PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification(BaseModel):
    """Describe integrity verification for a technical comparison report artifact.

    Describe la verificación de integridad de un artefacto de informe técnico comparativo.
    """

    artifact_version: str = Field(min_length=1)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    computed_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    matches_content: bool

class PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(BaseModel):
    """Describe a reproducible comparison between two technical report artifacts.

    Describe una comparación reproducible entre dos artefactos de informes técnicos.
    """

    left_artifact_version: str = Field(min_length=1)
    left_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    left_left_analyzer_id: str = Field(min_length=1)
    left_left_analyzer_version: str = Field(min_length=1)
    left_right_analyzer_id: str = Field(min_length=1)
    left_right_analyzer_version: str = Field(min_length=1)
    right_artifact_version: str = Field(min_length=1)
    right_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    right_left_analyzer_id: str = Field(min_length=1)
    right_left_analyzer_version: str = Field(min_length=1)
    right_right_analyzer_id: str = Field(min_length=1)
    right_right_analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)

class PhoneticCalibrationTechnicalDistributionComparisonDelta(BaseModel):
    """Describe changes between two robust technical distribution comparisons.

    Describe cambios entre dos comparaciones técnicas robustas de distribución.
    """

    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]
    left_score_q25_difference: float = Field(ge=-1.0, le=1.0)
    right_score_q25_difference: float = Field(ge=-1.0, le=1.0)
    score_q25_difference_delta: float = Field(ge=-2.0, le=2.0)
    left_score_median_difference: float = Field(ge=-1.0, le=1.0)
    right_score_median_difference: float = Field(ge=-1.0, le=1.0)
    score_median_difference_delta: float = Field(ge=-2.0, le=2.0)
    left_score_q75_difference: float = Field(ge=-1.0, le=1.0)
    right_score_q75_difference: float = Field(ge=-1.0, le=1.0)
    score_q75_difference_delta: float = Field(ge=-2.0, le=2.0)

    @model_validator(mode="after")
    def validate_distribution_comparison_deltas(self):
        expected_q25 = (
            self.right_score_q25_difference - self.left_score_q25_difference
        )
        expected_median = (
            self.right_score_median_difference
            - self.left_score_median_difference
        )
        expected_q75 = (
            self.right_score_q75_difference - self.left_score_q75_difference
        )

        if abs(self.score_q25_difference_delta - expected_q25) > 1e-12:
            raise ValueError(
                "Q25 comparison delta must equal right difference minus left difference"
            )
        if abs(self.score_median_difference_delta - expected_median) > 1e-12:
            raise ValueError(
                "Median comparison delta must equal right difference minus left difference"
            )
        if abs(self.score_q75_difference_delta - expected_q75) > 1e-12:
            raise ValueError(
                "Q75 comparison delta must equal right difference minus left difference"
            )
        return self

class PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(BaseModel):
    """Consolidate descriptive technical comparison deltas by human label.

    Consolida deltas descriptivos de comparación técnica por etiqueta humana.
    """

    artifact_comparison: PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison
    deltas: list[
        PhoneticCalibrationTechnicalDistributionComparisonDelta
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_delta_report(self):
        expected_rubric = self.artifact_comparison.rubric_version
        labels = set()

        for delta in self.deltas:
            if delta.rubric_version != expected_rubric:
                raise ValueError(
                    "Technical comparison delta must match artifact comparison rubric"
                )

            if delta.label in labels:
                raise ValueError(
                    "Technical comparison delta report requires unique human labels"
                )
            labels.add(delta.label)

        return self


class PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact(BaseModel):
    """Version a technical comparison delta report with reproducible identity.

    Versiona un informe de deltas de comparación técnica con identidad reproducible.
    """

    artifact_version: str = Field(min_length=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    report: PhoneticCalibrationTechnicalDistributionComparisonDeltaReport


class PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification(BaseModel):
    """Describe integrity verification for a technical comparison delta report artifact.

    Describe la verificación de integridad de un artefacto de informe de deltas técnicos.
    """

    artifact_version: str = Field(min_length=1)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    computed_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    matches_content: bool


class PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison(BaseModel):
    """Describe a reproducible comparison between two delta report artifacts.

    Describe una comparación reproducible entre dos artefactos de informes de deltas.
    """

    left_artifact_version: str = Field(min_length=1)
    left_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    left_artifact_comparison: PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison
    right_artifact_version: str = Field(min_length=1)
    right_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    right_artifact_comparison: PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison
    rubric_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_delta_artifact_comparison(self):
        if self.left_artifact_comparison.rubric_version != self.rubric_version:
            raise ValueError(
                "Left delta report artifact comparison must match rubric version"
            )
        if self.right_artifact_comparison.rubric_version != self.rubric_version:
            raise ValueError(
                "Right delta report artifact comparison must match rubric version"
            )
        return self
