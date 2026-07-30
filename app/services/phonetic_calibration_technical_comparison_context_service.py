from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationHumanEvidenceIdentity,
    PhoneticCalibrationTechnicalComparisonContext,
    PhoneticCalibrationTechnicalCoverageIdentity,
)
from app.services.phonetic_calibration_comparable_artifact_context_service import (
    build_phonetic_calibration_comparable_artifact_context,
)
from app.services.phonetic_calibration_technical_coverage_compatibility_service import (
    compare_phonetic_calibration_technical_coverage,
)


def build_phonetic_calibration_technical_comparison_context(
    left_artifact: PhoneticCalibrationDescriptiveReportArtifact,
    right_artifact: PhoneticCalibrationDescriptiveReportArtifact,
    left_human_evidence: PhoneticCalibrationHumanEvidenceIdentity,
    right_human_evidence: PhoneticCalibrationHumanEvidenceIdentity,
    left_technical_coverage: PhoneticCalibrationTechnicalCoverageIdentity,
    right_technical_coverage: PhoneticCalibrationTechnicalCoverageIdentity,
) -> PhoneticCalibrationTechnicalComparisonContext:
    """Build a fully comparable reproducible technical calibration context.

    Construye un contexto técnico reproducible de calibraciones completamente comparables.
    """
    comparable_artifact_context = (
        build_phonetic_calibration_comparable_artifact_context(
            left_artifact,
            right_artifact,
            left_human_evidence,
            right_human_evidence,
        )
    )
    technical_coverage_compatibility = (
        compare_phonetic_calibration_technical_coverage(
            left_technical_coverage,
            right_technical_coverage,
        )
    )

    return PhoneticCalibrationTechnicalComparisonContext(
        comparable_artifact_context=comparable_artifact_context,
        technical_coverage_compatibility=technical_coverage_compatibility,
    )
