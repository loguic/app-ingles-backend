import os

import pytest

from app.services.production_audio_storage_service import (
    MAX_PRODUCTION_AUDIO_BYTES,
    get_production_audio_storage_dir,
    read_production_audio,
    resolve_production_audio_path,
    store_production_audio,
)


def wav_payload(extra=b""):
    return (
        b"RIFF"
        + (36 + len(extra)).to_bytes(4, "little")
        + b"WAVE"
        + extra
    )


def test_store_audio_returns_opaque_reference_and_private_file(tmp_path):
    payload = wav_payload(b"learner-audio")

    record = store_production_audio(
        payload,
        storage_dir=tmp_path,
    )

    assert record.audio_reference.startswith(
        "production-audio://"
    )
    assert record.size_bytes == len(payload)
    assert record.media_type == "audio/wav"
    assert str(tmp_path) not in record.audio_reference

    path = resolve_production_audio_path(
        record.audio_reference,
        storage_dir=tmp_path,
    )

    assert path.read_bytes() == payload
    assert path.suffix == ".wav"
    assert os.stat(tmp_path).st_mode & 0o777 == 0o700
    assert os.stat(path).st_mode & 0o777 == 0o600


def test_read_audio_returns_original_bytes(tmp_path):
    payload = wav_payload(b"phonetic-input")
    record = store_production_audio(
        payload,
        storage_dir=tmp_path,
    )

    assert read_production_audio(
        record.audio_reference,
        storage_dir=tmp_path,
    ) == payload


def test_store_audio_rejects_non_wav(tmp_path):
    with pytest.raises(
        ValueError,
        match="must be WAV",
    ):
        store_production_audio(
            b"not-a-wave-file",
            storage_dir=tmp_path,
        )


def test_store_audio_rejects_oversized_payload(tmp_path):
    payload = wav_payload(
        b"x" * MAX_PRODUCTION_AUDIO_BYTES
    )

    with pytest.raises(
        ValueError,
        match="exceeds maximum size",
    ):
        store_production_audio(
            payload,
            storage_dir=tmp_path,
        )


def test_resolver_rejects_malformed_reference(tmp_path):
    with pytest.raises(
        ValueError,
        match="Invalid production audio reference",
    ):
        resolve_production_audio_path(
            "production-audio://../../etc/passwd",
            storage_dir=tmp_path,
        )


def test_resolver_rejects_unsupported_reference(tmp_path):
    with pytest.raises(
        ValueError,
        match="Unsupported production audio reference",
    ):
        resolve_production_audio_path(
            "file:///tmp/audio.wav",
            storage_dir=tmp_path,
        )


def test_resolver_reports_missing_audio(tmp_path):
    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        resolve_production_audio_path(
            "production-audio://"
            "00000000-0000-0000-0000-000000000001",
            storage_dir=tmp_path,
        )


def test_storage_dir_requires_explicit_configuration(monkeypatch):
    monkeypatch.delenv("PRODUCTION_AUDIO_DIR", raising=False)

    with pytest.raises(
        RuntimeError,
        match="PRODUCTION_AUDIO_DIR is not configured",
    ):
        get_production_audio_storage_dir()
