import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    RegionalRepresentativePhoneticCalibrationCoverage,
)


@pytest.mark.parametrize("locale", ["en-US", "en-GB"])
def test_accepts_supported_reference_locale(locale):
    coverage = RegionalRepresentativePhoneticCalibrationCoverage(
        reference_locale=locale,
        sample_count=3,
        speaker_count=2,
        session_count=3,
    )

    assert coverage.reference_locale == locale
    assert coverage.sample_count == 3
    assert coverage.speaker_count == 2
    assert coverage.session_count == 3


def test_rejects_unsupported_reference_locale():
    with pytest.raises(ValidationError):
        RegionalRepresentativePhoneticCalibrationCoverage(
            reference_locale="en-AU",
            sample_count=1,
            speaker_count=1,
            session_count=1,
        )


@pytest.mark.parametrize(
    "field",
    ["sample_count", "speaker_count", "session_count"],
)
def test_rejects_negative_counts(field):
    payload = {
        "reference_locale": "en-US",
        "sample_count": 1,
        "speaker_count": 1,
        "session_count": 1,
    }
    payload[field] = -1

    with pytest.raises(ValidationError):
        RegionalRepresentativePhoneticCalibrationCoverage(**payload)
