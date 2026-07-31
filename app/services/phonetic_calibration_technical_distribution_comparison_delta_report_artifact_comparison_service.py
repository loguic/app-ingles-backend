from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_verification_service import (
    verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)


def compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts(
    left: PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
    right: PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
) -> PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison:
    """Compare two intact technical delta report artifacts reproducibly.

    Compara reproduciblemente dos artefactos íntegros de informes de deltas técnicos.
    """
    left_verification = (
        verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
            left
        )
    )
    if not left_verification.matches_content:
        raise ValueError(
            "Left technical delta report artifact integrity verification failed"
        )

    right_verification = (
        verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
            right
        )
    )
    if not right_verification.matches_content:
        raise ValueError(
            "Right technical delta report artifact integrity verification failed"
        )

    left_context = left.report.artifact_comparison
    right_context = right.report.artifact_comparison

    if left_context.rubric_version != right_context.rubric_version:
        raise ValueError(
            "Technical delta report artifacts must use the same rubric version"
        )

    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison(
        left_artifact_version=left.artifact_version,
        left_content_sha256=left.content_sha256,
        left_artifact_comparison=left_context,
        right_artifact_version=right.artifact_version,
        right_content_sha256=right.content_sha256,
        right_artifact_comparison=right_context,
        rubric_version=left_context.rubric_version,
    )
