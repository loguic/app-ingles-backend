from app.schemas.phonetic_calibration import (
    PhoneticCalibrationComparableArtifactContext,
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationHumanEvidenceIdentity,
)
from app.services.phonetic_calibration_descriptive_report_artifact_comparison_service import (
    compare_phonetic_calibration_descriptive_report_artifacts,
)
from app.services.phonetic_calibration_human_evidence_compatibility_service import (
    compare_phonetic_calibration_human_evidence,
)


def build_phonetic_calibration_comparable_artifact_context(
    left_artifact: PhoneticCalibrationDescriptiveReportArtifact,
    right_artifact: PhoneticCalibrationDescriptiveReportArtifact,
    left_human_evidence: PhoneticCalibrationHumanEvidenceIdentity,
    right_human_evidence: PhoneticCalibrationHumanEvidenceIdentity,
) -> PhoneticCalibrationComparableArtifactContext:
    """Build a reproducible context for technically comparable calibrations.

    Construye un contexto reproducible para calibraciones técnicamente comparables.
    """
    artifact_comparison = (
        compare_phonetic_calibration_descriptive_report_artifacts(
            left_artifact,
            right_artifact,
        )
    )
    human_evidence_compatibility = compare_phonetic_calibration_human_evidence(
        left_human_evidence,
        right_human_evidence,
    )

    return PhoneticCalibrationComparableArtifactContext(
        artifact_comparison=artifact_comparison,
        human_evidence_compatibility=human_evidence_compatibility,
    )
