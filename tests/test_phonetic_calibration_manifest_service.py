import json

import pytest
from pydantic import ValidationError

from app.services.phonetic_calibration_manifest_service import (
    load_phonetic_calibration_manifest,
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
