import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalCoverageIdentity,
)


def build_identity(**updates) -> PhoneticCalibrationTechnicalCoverageIdentity:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "sample_count": 3,
        "sample_ids_sha256": "a" * 64,
    }
    payload.update(updates)
    return PhoneticCalibrationTechnicalCoverageIdentity(**payload)


def test_accepts_reproducible_technical_coverage_identity():
    identity = build_identity()

    assert identity.analyzer_id == "wavlm-gop-phoneme-scorer"
    assert identity.analyzer_version == "wavlm-gop-runner/1.0"
    assert identity.rubric_version == "phonetic-rubric/1.0"
    assert identity.sample_count == 3
    assert identity.sample_ids_sha256 == "a" * 64


@pytest.mark.parametrize(
    "field",
    ["analyzer_id", "analyzer_version", "rubric_version"],
)
def test_rejects_empty_versioned_identity(field):
    with pytest.raises(ValidationError):
        build_identity(**{field: ""})


@pytest.mark.parametrize("sample_count", [0, -1])
def test_rejects_non_positive_sample_count(sample_count):
    with pytest.raises(ValidationError):
        build_identity(sample_count=sample_count)


@pytest.mark.parametrize(
    "sample_ids_sha256",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64],
)
def test_rejects_invalid_sample_ids_sha256(sample_ids_sha256):
    with pytest.raises(ValidationError):
        build_identity(sample_ids_sha256=sample_ids_sha256)
