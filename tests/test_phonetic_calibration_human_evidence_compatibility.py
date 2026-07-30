from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
)


def identity(
    evidence_sha256: str,
    *,
    rubric_version: str = "phonetic-rubric/1.0",
    sample_count: int = 3,
) -> PhoneticCalibrationHumanEvidenceIdentity:
    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version=rubric_version,
        sample_count=sample_count,
        evidence_sha256=evidence_sha256,
    )


def test_accepts_matching_human_evidence_compatibility():
    left = identity("a" * 64)
    right = identity("a" * 64)

    compatibility = PhoneticCalibrationHumanEvidenceCompatibility(
        left=left,
        right=right,
        same_evidence=True,
    )

    assert compatibility.left == left
    assert compatibility.right == right
    assert compatibility.same_evidence is True


def test_accepts_non_matching_human_evidence_compatibility():
    left = identity("a" * 64)
    right = identity("b" * 64)

    compatibility = PhoneticCalibrationHumanEvidenceCompatibility(
        left=left,
        right=right,
        same_evidence=False,
    )

    assert compatibility.left.evidence_sha256 == "a" * 64
    assert compatibility.right.evidence_sha256 == "b" * 64
    assert compatibility.same_evidence is False
