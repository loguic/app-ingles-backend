from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)


def verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
    artifact: PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
) -> PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification:
    """Verify a technical comparison delta report artifact against its content.

    Verifica un artefacto de informe de deltas técnicos contra su contenido actual.
    """
    rebuilt = (
        build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
            artifact.report,
            artifact.artifact_version,
        )
    )

    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification(
        artifact_version=artifact.artifact_version,
        expected_sha256=artifact.content_sha256,
        computed_sha256=rebuilt.content_sha256,
        matches_content=artifact.content_sha256 == rebuilt.content_sha256,
    )
