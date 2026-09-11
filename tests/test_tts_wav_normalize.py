from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import wave

import pytest
from pydantic import ValidationError

from app.schemas.tts_wav_normalization import (
    TTS_WAV_NORMALIZATION_PROFILE_VERSION,
    TtsWavDescriptiveMetricsV1,
    TtsWavNormalizationResultV1,
    TtsWavProbeV1,
)
from scripts.engineering import tts_wav_normalize as normalizer


FIXED_NOW = datetime(2026, 9, 11, 20, 30, tzinfo=UTC)
GOLDEN_NORMALIZED_SHA256 = (
    "9bb2ce2bc565a7dd28068880e56b222b88970db886e8fb8fa7b0af94d534ac07"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_pcm_wav(
    path: Path,
    *,
    sample_rate: int = 16000,
    channels: int = 1,
) -> None:
    pattern = (0, 900, -900, 1800, -1800, 3200, -3200, 0)
    samples = (0,) * 80 + pattern * 240 + (0,) * 40
    frames = b"".join(
        struct.pack("<" + "h" * channels, *([sample] * channels))
        for sample in samples
    )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(frames)


@pytest.fixture
def raw_mono(tmp_path: Path) -> Path:
    path = tmp_path / "raw-mono.wav"
    _write_pcm_wav(path)
    return path


def _normalize(
    tmp_path: Path,
    raw: Path,
    *,
    output_name: str = "normalized.wav",
    record_name: str = "normalized.json",
) -> tuple[normalizer.TtsWavNormalizationResultV1, Path, Path]:
    output = tmp_path / output_name
    record = tmp_path / record_name
    result = normalizer.normalize_tts_wav(
        sample_id="tts-sample-001",
        raw_path=raw,
        expected_raw_sha256=_sha256(raw),
        normalized_path=output,
        record_path=record,
        now=FIXED_NOW,
    )
    return result, output, record


def _valid_probe() -> TtsWavProbeV1:
    return TtsWavProbeV1(
        container="RIFF/WAVE",
        codec="pcm_s16le",
        sample_format="s16",
        sample_rate=24000,
        channels=1,
        channel_layout="mono",
        bit_depth=16,
        stream_count=1,
        duration_samples=1,
        duration_seconds=1 / 24000,
        decoded_samples=1,
    )


def _valid_metrics() -> TtsWavDescriptiveMetricsV1:
    return TtsWavDescriptiveMetricsV1(
        size_bytes=1,
        sample_peak_linear=0.0,
        true_peak_dbfs=None,
        full_scale_sample_count=0,
        rms_linear=0.0,
        peak_level_dbfs=None,
        integrated_loudness_lufs=None,
        loudness_range_lu=None,
        dc_offset=0.0,
        leading_zero_samples=1,
        trailing_zero_samples=1,
        noise_floor_dbfs=None,
        noise_floor_analyzer_id=None,
        noise_floor_analyzer_version=None,
    )


def test_schema_is_strict_versioned_and_binds_review_to_normalized_identity() -> None:
    result = TtsWavNormalizationResultV1(
        sample_id="tts-sample-001",
        profile_version=TTS_WAV_NORMALIZATION_PROFILE_VERSION,
        raw_sha256="a" * 64,
        normalized_sha256="b" * 64,
        raw_probe=_valid_probe(),
        normalized_probe=_valid_probe(),
        raw_metrics=_valid_metrics(),
        normalized_metrics=_valid_metrics(),
        ffmpeg_version="ffmpeg version 6.1.1-3ubuntu5 full output",
        ffprobe_version="ffprobe version 6.1.1-3ubuntu5 full output",
        normalization_argv=("ffmpeg", "-f", "wav"),
        normalized_at_utc=FIXED_NOW,
    )

    assert result.profile_version == "loguic-tts-wav-normalization/1.0"
    assert result.normalized_sha256 == "b" * 64
    with pytest.raises(ValidationError):
        TtsWavNormalizationResultV1.model_validate(
            {**result.model_dump(mode="json"), "acceptance_threshold": 1}
        )


def test_valid_raw_mono_pcm_is_accepted_and_records_runtime_toolchain(
    tmp_path: Path, raw_mono: Path
) -> None:
    result, output, record = _normalize(tmp_path, raw_mono)

    assert output.is_file()
    assert record.is_file()
    assert result.raw_sha256 == _sha256(raw_mono)
    assert result.normalized_sha256 == _sha256(output)
    assert result.raw_probe.codec == "pcm_s16le"
    assert result.raw_probe.channels == 1
    assert result.ffmpeg_version.startswith(normalizer.EXPECTED_FFMPEG_VERSION)
    assert result.ffprobe_version.startswith(normalizer.EXPECTED_FFPROBE_VERSION)
    persisted = json.loads(record.read_text(encoding="utf-8"))
    assert persisted["normalized_sha256"] == _sha256(output)
    assert persisted["profile_version"] == TTS_WAV_NORMALIZATION_PROFILE_VERSION


def test_runtime_determinism_runs_twice_from_the_same_raw(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_normalize = normalizer._normalize_to_temporary
    calls: list[tuple[Path, Path]] = []

    def record_normalization(
        *,
        raw_path: Path,
        temporary_path: Path,
        ffmpeg: str,
        ffprobe: str,
    ) -> tuple[tuple[str, ...], TtsWavProbeV1, tuple[float, ...]]:
        calls.append((raw_path, temporary_path))
        return original_normalize(
            raw_path=raw_path,
            temporary_path=temporary_path,
            ffmpeg=ffmpeg,
            ffprobe=ffprobe,
        )

    monkeypatch.setattr(normalizer, "_normalize_to_temporary", record_normalization)
    _, output, record = _normalize(tmp_path, raw_mono)

    assert len(calls) == 2
    assert [raw_path for raw_path, _ in calls] == [raw_mono, raw_mono]
    assert calls[0][1] != calls[1][1]
    assert output.is_file()
    assert record.is_file()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.a.tmp").exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.b.tmp").exists()


def test_runtime_determinism_byte_mismatch_publishes_nothing(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(normalizer, "_files_are_byte_identical", lambda *_paths: False)
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"

    with pytest.raises(normalizer.TtsWavNormalizationError, match="bytes are not deterministic"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )

    assert not output.exists()
    assert not record.exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.a.tmp").exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.b.tmp").exists()
    assert not (tmp_path / ".normalized.json.tts-normalizing.record.tmp").exists()


def test_runtime_determinism_hash_mismatch_publishes_nothing(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_sha256 = normalizer._sha256

    def mismatch_second_normalization(path: Path) -> str:
        if path.name.endswith(".tts-normalizing.b.tmp"):
            return "f" * 64
        return original_sha256(path)

    monkeypatch.setattr(normalizer, "_sha256", mismatch_second_normalization)
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"

    with pytest.raises(normalizer.TtsWavNormalizationError, match="hashes are not deterministic"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )

    assert not output.exists()
    assert not record.exists()


def test_raw_hash_mismatch_makes_no_output(tmp_path: Path, raw_mono: Path) -> None:
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"

    with pytest.raises(normalizer.TtsWavNormalizationError, match="SHA-256 mismatch"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256="0" * 64,
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )

    assert not output.exists()
    assert not record.exists()


def test_symlink_raw_is_rejected(tmp_path: Path, raw_mono: Path) -> None:
    link = tmp_path / "raw-link.wav"
    link.symlink_to(raw_mono)
    with pytest.raises(normalizer.TtsWavNormalizationError, match="symlink"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=link,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=tmp_path / "normalized.wav",
            record_path=tmp_path / "normalized.json",
            now=FIXED_NOW,
        )


def test_compressed_wav_is_rejected(tmp_path: Path, raw_mono: Path) -> None:
    compressed = tmp_path / "compressed.wav"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw_mono), "-c:a", "adpcm_ima_wav", str(compressed),
        ],
        check=True,
        shell=False,
    )

    with pytest.raises(normalizer.TtsWavNormalizationError, match="linear uncompressed PCM"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=compressed,
            expected_raw_sha256=_sha256(compressed),
            normalized_path=tmp_path / "normalized.wav",
            record_path=tmp_path / "normalized.json",
            now=FIXED_NOW,
        )


def test_stereo_raw_is_rejected_before_normalization(tmp_path: Path) -> None:
    stereo = tmp_path / "stereo.wav"
    _write_pcm_wav(stereo, channels=2)
    with pytest.raises(normalizer.TtsWavNormalizationError, match="downmix is forbidden"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=stereo,
            expected_raw_sha256=_sha256(stereo),
            normalized_path=tmp_path / "normalized.wav",
            record_path=tmp_path / "normalized.json",
            now=FIXED_NOW,
        )


def test_multistream_probe_is_rejected() -> None:
    probe = _valid_probe().model_copy(update={"stream_count": 2})
    with pytest.raises(normalizer.TtsWavNormalizationError, match="exactly one stream"):
        normalizer.validate_raw_probe(probe)


def test_truncated_wav_is_rejected_as_not_fully_decodable(tmp_path: Path) -> None:
    truncated = tmp_path / "truncated.wav"
    truncated.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt ")
    with pytest.raises(normalizer.TtsWavNormalizationError):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=truncated,
            expected_raw_sha256=_sha256(truncated),
            normalized_path=tmp_path / "normalized.wav",
            record_path=tmp_path / "normalized.json",
            now=FIXED_NOW,
        )


def test_golden_normalization_is_deterministic_and_has_canonical_format(
    tmp_path: Path, raw_mono: Path
) -> None:
    first, first_output, _ = _normalize(tmp_path, raw_mono)
    second, second_output, _ = _normalize(
        tmp_path,
        raw_mono,
        output_name="normalized-second.wav",
        record_name="normalized-second.json",
    )

    assert first_output.read_bytes() == second_output.read_bytes()
    assert first.normalized_sha256 == second.normalized_sha256
    assert first.normalized_sha256 == GOLDEN_NORMALIZED_SHA256
    assert first.normalized_probe.container == "RIFF/WAVE"
    assert first.normalized_probe.codec == "pcm_s16le"
    assert first.normalized_probe.sample_format == "s16"
    assert first.normalized_probe.sample_rate == 24000
    assert first.normalized_probe.channels == 1
    assert first.normalized_probe.bit_depth == 16
    assert first.normalized_probe.stream_count == 1
    assert first.normalized_probe.decoded_samples > 0


def test_metadata_is_eliminated_and_argv_contains_no_forbidden_filter(
    tmp_path: Path, raw_mono: Path
) -> None:
    metadata_raw = tmp_path / "raw-metadata.wav"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw_mono), "-metadata", "title=source title",
            "-c:a", "pcm_s16le", str(metadata_raw),
        ],
        check=True,
        shell=False,
    )
    result, output, _ = _normalize(tmp_path, metadata_raw)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format_tags", "-of", "json", str(output)],
        check=True,
        shell=False,
        capture_output=True,
        text=True,
    )
    assert json.loads(probe.stdout).get("format", {}).get("tags", {}) == {}
    argv_text = " ".join(result.normalization_argv).lower()
    for forbidden in ("loudnorm", "silenceremove", "alimiter", "acompressor", "highpass", "afftdn", "adeesser", "atempo", "asetrate"):
        assert forbidden not in argv_text
    assert "dither_method=none" in argv_text


def test_existing_output_is_never_overwritten(tmp_path: Path, raw_mono: Path) -> None:
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"
    output.write_bytes(b"existing")
    record.write_bytes(b"existing record")
    with pytest.raises(normalizer.TtsWavNormalizationError, match="already exists"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )
    assert output.read_bytes() == b"existing"
    assert record.read_bytes() == b"existing record"


def test_failure_after_normalization_cleans_only_new_artifacts(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("keep", encoding="utf-8")

    def fail_record(*_args: object, **_kwargs: object) -> None:
        raise normalizer.TtsWavNormalizationError("forced record failure")

    monkeypatch.setattr(normalizer, "_write_temporary_json", fail_record)
    with pytest.raises(normalizer.TtsWavNormalizationError, match="forced record failure"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )
    assert not output.exists()
    assert not record.exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.a.tmp").exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.b.tmp").exists()
    assert not (tmp_path / ".normalized.json.tts-normalizing.record.tmp").exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_directory_fsync_failure_after_normalized_link_rolls_back_all_new_outputs(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("keep", encoding="utf-8")
    original_fsync = normalizer.os.fsync
    fsync_calls = 0

    def fail_after_normalized_link(fd: int) -> None:
        nonlocal fsync_calls
        fsync_calls += 1
        if fsync_calls == 2:
            raise OSError("forced normalized directory fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(normalizer.os, "fsync", fail_after_normalized_link)
    with pytest.raises(normalizer.TtsWavNormalizationError, match="normalization failed"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )
    assert fsync_calls == 2
    assert not output.exists()
    assert not record.exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.a.tmp").exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.b.tmp").exists()
    assert not (tmp_path / ".normalized.json.tts-normalizing.record.tmp").exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_directory_fsync_failure_after_record_link_rolls_back_both_new_outputs(
    tmp_path: Path, raw_mono: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "normalized.wav"
    record = tmp_path / "normalized.json"
    unrelated = tmp_path / "unrelated.txt"
    unrelated.write_text("keep", encoding="utf-8")
    original_fsync = normalizer.os.fsync
    fsync_calls = 0

    def fail_after_record_link(fd: int) -> None:
        nonlocal fsync_calls
        fsync_calls += 1
        if fsync_calls == 3:
            raise OSError("forced record directory fsync failure")
        original_fsync(fd)

    monkeypatch.setattr(normalizer.os, "fsync", fail_after_record_link)
    with pytest.raises(normalizer.TtsWavNormalizationError, match="normalization failed"):
        normalizer.normalize_tts_wav(
            sample_id="tts-sample-001",
            raw_path=raw_mono,
            expected_raw_sha256=_sha256(raw_mono),
            normalized_path=output,
            record_path=record,
            now=FIXED_NOW,
        )

    assert fsync_calls == 3
    assert not output.exists()
    assert not record.exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.a.tmp").exists()
    assert not (tmp_path / ".normalized.wav.tts-normalizing.b.tmp").exists()
    assert not (tmp_path / ".normalized.json.tts-normalizing.record.tmp").exists()
    assert unrelated.read_text(encoding="utf-8") == "keep"


def test_metrics_are_descriptive_and_do_not_define_threshold_fields(
    tmp_path: Path, raw_mono: Path
) -> None:
    result, _, _ = _normalize(tmp_path, raw_mono)
    assert result.normalized_metrics.size_bytes > 0
    assert result.normalized_metrics.full_scale_sample_count >= 0
    assert result.normalized_metrics.noise_floor_dbfs is None
    serialized = result.normalized_metrics.model_dump()
    assert not any("threshold" in key or key.startswith("max_") for key in serialized)
