from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
)


def compare_phonetic_calibration_human_evidence(
    left: PhoneticCalibrationHumanEvidenceIdentity,
    right: PhoneticCalibrationHumanEvidenceIdentity,
) -> PhoneticCalibrationHumanEvidenceCompatibility:
    """Compare two reproducible human evidence identities.

    Compara dos identidades reproducibles de evidencia humana.
    """
    return PhoneticCalibrationHumanEvidenceCompatibility(
        left=left,
        right=right,
        same_evidence=left == right,
    )
