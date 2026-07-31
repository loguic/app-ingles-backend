import json

import pytest
from pydantic import ValidationError

from app.services.phonetic_calibration_manifest_service import (
    load_regional_representative_phonetic_calibration_manifest,
)


def payload(**updates):
    sample = {
        "sample_id": "human-001",
        "reference_text": "Hello, I am John.",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "a" * 64,
        "expected_class": "unlabeled",
        "speaker_id": "speaker-001",
        "session_id": "session-001",
        "reference_locale": "en-US",
    }
    sample.update(updates)
    return sample


def test_loads_valid_regional_representative_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps([payload(reference_locale="en-GB")]),
        encoding="utf-8",
    )

    samples = load_regional_representative_phonetic_calibration_manifest(manifest)

    assert len(samples) == 1
    assert samples[0].speaker_id == "speaker-001"
    assert samples[0].session_id == "session-001"
    assert samples[0].reference_locale == "en-GB"


def test_rejects_manifest_without_reference_locale(tmp_path):
    sample = payload()
    sample.pop("reference_locale")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([sample]), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_regional_representative_phonetic_calibration_manifest(manifest)


def test_rejects_unsupported_reference_locale(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps([payload(reference_locale="en-AU")]),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_regional_representative_phonetic_calibration_manifest(manifest)
