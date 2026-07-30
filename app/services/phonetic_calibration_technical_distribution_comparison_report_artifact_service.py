import hashlib
import json

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonReport,
    PhoneticCalibrationTechnicalDistributionComparisonReportArtifact,
)


def build_phonetic_calibration_technical_distribution_comparison_report_artifact(
    report: PhoneticCalibrationTechnicalDistributionComparisonReport,
    artifact_version: str,
) -> PhoneticCalibrationTechnicalDistributionComparisonReportArtifact:
    """Build a reproducibly identified technical comparison report artifact.

    Construye un artefacto de informe de comparación técnica con identidad reproducible.
    """
    payload = {
        "artifact_version": artifact_version,
        "report": report.model_dump(mode="json"),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    content_sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return PhoneticCalibrationTechnicalDistributionComparisonReportArtifact(
        artifact_version=artifact_version,
        content_sha256=content_sha256,
        report=report,
    )
