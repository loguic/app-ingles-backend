import json

import pytest
from pydantic import ValidationError

from app.services.phonetic_calibration_manifest_service import (
    load_phonetic_calibration_manifest,
    load_representative_phonetic_calibration_manifest,
)


def test_loads_valid_calibration_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{
        "sample_id": "human-001",
        "reference_text": "Hello, I am John.",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "a" * 64,
        "expected_class": "acceptable",
    }]), encoding="utf-8")

    samples = load_phonetic_calibration_manifest(manifest)

    assert len(samples) == 1
    assert samples[0].sample_id == "human-001"


def test_rejects_invalid_manifest_json(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON"):
        load_phonetic_calibration_manifest(manifest)


def test_rejects_invalid_manifest_sample(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{
        "sample_id": "human-001",
        "reference_text": "Hello",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "invalid",
        "expected_class": "acceptable",
    }]), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_phonetic_calibration_manifest(manifest)


def test_loads_valid_representative_calibration_manifest(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([{
        "sample_id": "human-001",
        "reference_text": "Hello, I am John.",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "b" * 64,
        "expected_class": "unlabeled",
        "speaker_id": "speaker-001",
        "session_id": "session-001",
    }]), encoding="utf-8")

    samples = load_representative_phonetic_calibration_manifest(manifest)

    assert samples[0].speaker_id == "speaker-001"
    assert samples[0].session_id == "session-001"


@pytest.mark.parametrize("missing_field", ["speaker_id", "session_id"])
def test_rejects_representative_manifest_without_identity(tmp_path, missing_field):
    payload = {
        "sample_id": "human-001",
        "reference_text": "Hello, I am John.",
        "audio_path": "audio/human-001.wav",
        "audio_sha256": "c" * 64,
        "expected_class": "unlabeled",
        "speaker_id": "speaker-001",
        "session_id": "session-001",
    }
    payload.pop(missing_field)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([payload]), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_representative_phonetic_calibration_manifest(manifest)
