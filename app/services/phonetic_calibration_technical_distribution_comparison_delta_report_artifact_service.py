import hashlib
import json

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
)


def build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
    report: PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
    artifact_version: str,
) -> PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact:
    """Build a reproducibly identified technical comparison delta report artifact.

    Construye un artefacto reproducible del informe de deltas de comparación técnica.
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

    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact(
        artifact_version=artifact_version,
        content_sha256=content_sha256,
        report=report,
    )
