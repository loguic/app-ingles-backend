import hashlib
import json

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationModelHumanObservation,
    PhoneticCalibrationTechnicalCoverageIdentity,
)


def build_phonetic_calibration_technical_coverage_identity(
    observations: list[PhoneticCalibrationModelHumanObservation],
    analyzer_id: str,
    analyzer_version: str,
    rubric_version: str,
) -> PhoneticCalibrationTechnicalCoverageIdentity:
    """Build a reproducible identity for technical calibration sample coverage.

    Construye una identidad reproducible de la cobertura de muestras de calibración técnica.
    """
    sample_ids = sorted(
        {
            observation.sample_id
            for observation in observations
            if observation.analyzer_id == analyzer_id
            and observation.analyzer_version == analyzer_version
            and observation.rubric_version == rubric_version
        }
    )
    if not sample_ids:
        raise ValueError("Technical coverage identity requires matching observations")

    canonical_json = json.dumps(
        sample_ids,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    sample_ids_sha256 = hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

    return PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id=analyzer_id,
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        sample_count=len(sample_ids),
        sample_ids_sha256=sample_ids_sha256,
    )
