import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReportArtifactVerification,
)


def build_verification(**updates) -> PhoneticCalibrationDescriptiveReportArtifactVerification:
    payload = {
        "report_version": "phonetic-calibration-report/1.0",
        "expected_sha256": "a" * 64,
        "computed_sha256": "a" * 64,
        "matches_content": True,
    }
    payload.update(updates)
    return PhoneticCalibrationDescriptiveReportArtifactVerification(**payload)


def test_accepts_integrity_verification():
    verification = build_verification()

    assert verification.report_version == "phonetic-calibration-report/1.0"
    assert verification.expected_sha256 == "a" * 64
    assert verification.computed_sha256 == "a" * 64
    assert verification.matches_content is True


@pytest.mark.parametrize(
    "field",
    ["expected_sha256", "computed_sha256"],
)
@pytest.mark.parametrize(
    "value",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64],
)
def test_rejects_invalid_sha256(field, value):
    with pytest.raises(ValidationError):
        build_verification(**{field: value})


def test_rejects_empty_report_version():
    with pytest.raises(ValidationError):
        build_verification(report_version="")
