from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
)
from app.services.phonetic_calibration_technical_distribution_comparison_report_artifact_verification_service import (
    verify_phonetic_calibration_technical_distribution_comparison_report_artifact,
)


def compare_phonetic_calibration_technical_distribution_comparison_report_artifacts(
    left: PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
    right: PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
) -> PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison:
    """Compare two intact technical comparison report artifacts reproducibly.

    Compara reproduciblemente dos artefactos íntegros de informes técnicos comparativos.
    """
    left_verification = (
        verify_phonetic_calibration_technical_distribution_comparison_report_artifact(
            left
        )
    )
    if not left_verification.matches_content:
        raise ValueError("Left technical comparison artifact integrity verification failed")

    right_verification = (
        verify_phonetic_calibration_technical_distribution_comparison_report_artifact(
            right
        )
    )
    if not right_verification.matches_content:
        raise ValueError("Right technical comparison artifact integrity verification failed")

    left_comparison = (
        left.report.context.comparable_artifact_context.artifact_comparison
    )
    right_comparison = (
        right.report.context.comparable_artifact_context.artifact_comparison
    )

    if left_comparison.rubric_version != right_comparison.rubric_version:
        raise ValueError(
            "Technical comparison artifacts must use the same rubric version"
        )

    return PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
        left_artifact_version=left.artifact_version,
        left_content_sha256=left.content_sha256,
        left_left_analyzer_id=left_comparison.left_analyzer_id,
        left_left_analyzer_version=left_comparison.left_analyzer_version,
        left_right_analyzer_id=left_comparison.right_analyzer_id,
        left_right_analyzer_version=left_comparison.right_analyzer_version,
        right_artifact_version=right.artifact_version,
        right_content_sha256=right.content_sha256,
        right_left_analyzer_id=right_comparison.left_analyzer_id,
        right_left_analyzer_version=right_comparison.left_analyzer_version,
        right_right_analyzer_id=right_comparison.right_analyzer_id,
        right_right_analyzer_version=right_comparison.right_analyzer_version,
        rubric_version=left_comparison.rubric_version,
    )
