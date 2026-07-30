from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationDescriptiveReportArtifactVerification,
)
from app.services.phonetic_calibration_descriptive_report_artifact_service import (
    build_phonetic_calibration_descriptive_report_artifact,
)


def verify_phonetic_calibration_descriptive_report_artifact(
    artifact: PhoneticCalibrationDescriptiveReportArtifact,
) -> PhoneticCalibrationDescriptiveReportArtifactVerification:
    """Verify that an artifact hash matches its current report content.

    Verifica que la huella del artefacto coincida con el contenido actual del informe.
    """
    rebuilt = build_phonetic_calibration_descriptive_report_artifact(
        artifact.report,
        artifact.report_version,
    )

    return PhoneticCalibrationDescriptiveReportArtifactVerification(
        report_version=artifact.report_version,
        expected_sha256=artifact.content_sha256,
        computed_sha256=rebuilt.content_sha256,
        matches_content=artifact.content_sha256 == rebuilt.content_sha256,
    )
