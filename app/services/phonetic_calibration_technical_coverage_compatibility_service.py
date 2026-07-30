from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalCoverageCompatibility,
    PhoneticCalibrationTechnicalCoverageIdentity,
)


def compare_phonetic_calibration_technical_coverage(
    left: PhoneticCalibrationTechnicalCoverageIdentity,
    right: PhoneticCalibrationTechnicalCoverageIdentity,
) -> PhoneticCalibrationTechnicalCoverageCompatibility:
    """Compare reproducible technical calibration coverage identities.

    Compara identidades reproducibles de cobertura técnica de calibración.
    """
    same_coverage = (
        left.rubric_version == right.rubric_version
        and left.sample_count == right.sample_count
        and left.sample_ids_sha256 == right.sample_ids_sha256
    )

    return PhoneticCalibrationTechnicalCoverageCompatibility(
        left=left,
        right=right,
        same_coverage=same_coverage,
    )
