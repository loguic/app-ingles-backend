from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationDescriptiveReportArtifactComparison,
)
from app.services.phonetic_calibration_descriptive_report_artifact_verification_service import (
    verify_phonetic_calibration_descriptive_report_artifact,
)


def compare_phonetic_calibration_descriptive_report_artifacts(
    left: PhoneticCalibrationDescriptiveReportArtifact,
    right: PhoneticCalibrationDescriptiveReportArtifact,
) -> PhoneticCalibrationDescriptiveReportArtifactComparison:
    """Compare two intact descriptive calibration report artifacts.

    Compara dos artefactos íntegros de informes descriptivos de calibración.
    """
    left_verification = verify_phonetic_calibration_descriptive_report_artifact(left)
    right_verification = verify_phonetic_calibration_descriptive_report_artifact(right)

    if not left_verification.matches_content:
        raise ValueError("Left calibration report artifact failed integrity verification")
    if not right_verification.matches_content:
        raise ValueError("Right calibration report artifact failed integrity verification")
    if left.report.rubric_version != right.report.rubric_version:
        raise ValueError("Calibration report artifacts must share rubric_version")

    return PhoneticCalibrationDescriptiveReportArtifactComparison(
        left_report_version=left.report_version,
        left_content_sha256=left.content_sha256,
        left_analyzer_id=left.report.analyzer_id,
        left_analyzer_version=left.report.analyzer_version,
        right_report_version=right.report_version,
        right_content_sha256=right.content_sha256,
        right_analyzer_id=right.report.analyzer_id,
        right_analyzer_version=right.report.analyzer_version,
        rubric_version=left.report.rubric_version,
    )
