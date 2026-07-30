from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
    PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification,
)
from app.services.phonetic_calibration_technical_distribution_comparison_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_report_artifact,
)


def verify_phonetic_calibration_technical_distribution_comparison_report_artifact(
    artifact: PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
) -> PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification:
    """Verify a technical comparison report artifact against its current content.

    Verifica un artefacto de informe técnico comparativo contra su contenido actual.
    """
    rebuilt = (
        build_phonetic_calibration_technical_distribution_comparison_report_artifact(
            artifact.report,
            artifact.artifact_version,
        )
    )

    return PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification(
        artifact_version=artifact.artifact_version,
        expected_sha256=artifact.content_sha256,
        computed_sha256=rebuilt.content_sha256,
        matches_content=artifact.content_sha256 == rebuilt.content_sha256,
    )
