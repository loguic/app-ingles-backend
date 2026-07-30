import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanEvidenceIdentity,
)


def build_identity(**updates) -> PhoneticCalibrationHumanEvidenceIdentity:
    payload = {
        "rubric_version": "phonetic-rubric/1.0",
        "sample_count": 3,
        "evidence_sha256": "a" * 64,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanEvidenceIdentity(**payload)


def test_accepts_reproducible_human_evidence_identity():
    identity = build_identity()

    assert identity.rubric_version == "phonetic-rubric/1.0"
    assert identity.sample_count == 3
    assert identity.evidence_sha256 == "a" * 64


def test_rejects_empty_rubric_version():
    with pytest.raises(ValidationError):
        build_identity(rubric_version="")


@pytest.mark.parametrize("sample_count", [0, -1])
def test_rejects_non_positive_sample_count(sample_count):
    with pytest.raises(ValidationError):
        build_identity(sample_count=sample_count)


@pytest.mark.parametrize(
    "evidence_sha256",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64],
)
def test_rejects_invalid_evidence_sha256(evidence_sha256):
    with pytest.raises(ValidationError):
        build_identity(evidence_sha256=evidence_sha256)
