import hashlib
import json

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationDescriptiveReportArtifact,
)


def build_phonetic_calibration_descriptive_report_artifact(
    report: PhoneticCalibrationDescriptiveReport,
    report_version: str,
) -> PhoneticCalibrationDescriptiveReportArtifact:
    """Build a reproducibly identified descriptive calibration report artifact.

    Construye un artefacto de informe descriptivo identificado reproduciblemente.
    """
    canonical_payload = {
        "report_version": report_version,
        "report": report.model_dump(mode="json"),
    }
    canonical_json = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    content_sha256 = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    return PhoneticCalibrationDescriptiveReportArtifact(
        report_version=report_version,
        content_sha256=content_sha256,
        report=report,
    )
