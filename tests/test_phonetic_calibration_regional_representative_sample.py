import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    RegionalRepresentativePhoneticCalibrationSample,
)


def build_sample(**updates) -> RegionalRepresentativePhoneticCalibrationSample:
    payload = {
        "sample_id": "human-001",
        "reference_text": "Hello, I am John.",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "a" * 64,
        "expected_class": "unlabeled",
        "speaker_id": "speaker-001",
        "session_id": "session-001",
        "reference_locale": "en-US",
    }
    payload.update(updates)
    return RegionalRepresentativePhoneticCalibrationSample(**payload)


@pytest.mark.parametrize("locale", ["en-US", "en-GB"])
def test_accepts_supported_reference_locale(locale):
    sample = build_sample(reference_locale=locale)

    assert sample.reference_locale == locale


def test_rejects_unsupported_reference_locale():
    with pytest.raises(ValidationError):
        build_sample(reference_locale="en-AU")


@pytest.mark.parametrize("field", ["speaker_id", "session_id"])
def test_preserves_representative_identity_requirements(field):
    payload = {
        "speaker_id": "speaker-001",
        "session_id": "session-001",
    }
    payload.pop(field)

    with pytest.raises(ValidationError):
        build_sample(**{field: None})
