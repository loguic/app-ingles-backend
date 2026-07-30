from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanEvidenceIdentity,
)
from app.services.phonetic_calibration_human_evidence_compatibility_service import (
    compare_phonetic_calibration_human_evidence,
)


def identity(
    evidence_sha256: str = "a" * 64,
    *,
    rubric_version: str = "phonetic-rubric/1.0",
    sample_count: int = 3,
) -> PhoneticCalibrationHumanEvidenceIdentity:
    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version=rubric_version,
        sample_count=sample_count,
        evidence_sha256=evidence_sha256,
    )


def test_same_identity_is_compatible():
    compatibility = compare_phonetic_calibration_human_evidence(
        identity(),
        identity(),
    )

    assert compatibility.same_evidence is True


def test_different_hash_is_not_same_evidence():
    compatibility = compare_phonetic_calibration_human_evidence(
        identity(),
        identity("b" * 64),
    )

    assert compatibility.same_evidence is False


def test_different_sample_count_is_not_same_evidence():
    compatibility = compare_phonetic_calibration_human_evidence(
        identity(),
        identity(sample_count=4),
    )

    assert compatibility.same_evidence is False


def test_different_rubric_is_not_same_evidence():
    compatibility = compare_phonetic_calibration_human_evidence(
        identity(),
        identity(rubric_version="phonetic-rubric/2.0"),
    )

    assert compatibility.same_evidence is False
