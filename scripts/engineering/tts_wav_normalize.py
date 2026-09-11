"""Normalize one approved TTS raw WAV with LOGUIC profile v1.

This engineering tool does not generate speech, assess speech quality, or make
pedagogical decisions. It derives one reproducible normalized WAV and a
machine-readable technical record from an already-produced raw WAV.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas.tts_wav_normalization import (
    TTS_WAV_NORMALIZATION_PROFILE_VERSION,
    TtsWavDescriptiveMetricsV1,
    TtsWavNormalizationResultV1,
    TtsWavProbeV1,
)


CANONICAL_SAMPLE_RATE = 24000
EXPECTED_FFMPEG_VERSION = "ffmpeg version 6.1.1-3ubuntu5"
EXPECTED_FFPROBE_VERSION = "ffprobe version 6.1.1-3ubuntu5"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_LINEAR_PCM_EXCLUSIONS = {"pcm_alaw", "pcm_mulaw"}
_LOUDNESS_PATTERN = re.compile(r"^\s*I:\s+([^\s]+)\s+LUFS\s*$", re.MULTILINE)
_LRA_PATTERN = re.compile(r"^\s*LRA:\s+([^\s]+)\s+LU\s*$", re.MULTILINE)
_TRUE_PEAK_PATTERN = re.compile(r"^\s*Peak:\s+([^\s]+)\s+dBFS\s*$", re.MULTILINE)


class TtsWavNormalizationError(RuntimeError):
    """Describe one fail-closed TTS WAV normalization failure."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_regular_not_symlink(path: Path, *, label: str) -> None:
    if path.is_symlink():
        raise TtsWavNormalizationError(label + " must not be a symlink")
    if not path.is_file():
        raise TtsWavNormalizationError(label + " must be a regular file")


def _validate_sha256(value: str) -> str:
    if SHA256_PATTERN.fullmatch(value) is None:
        raise TtsWavNormalizationError("expected raw SHA-256 must be lowercase hex")
    return value


def _run(
    argv: Sequence[str],
    *,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(argv),
            check=False,
            shell=False,
            capture_output=capture_output,
            text=True,
        )
    except OSError as exc:
        raise TtsWavNormalizationError("required audio tool is unavailable") from exc


def _tool_version(tool: str, expected_prefix: str) -> str:
    completed = _run([tool, "-version"])
    version = completed.stdout.strip()
    if completed.returncode != 0 or not version.startswith(expected_prefix):
        raise TtsWavNormalizationError(
            "unexpected audio toolchain version: " + tool
        )
    return version


def validate_toolchain(ffmpeg: str, ffprobe: str) -> tuple[str, str]:
    """Require the Human-Gate-approved initial FFmpeg/FFprobe release."""
    return (
        _tool_version(ffmpeg, EXPECTED_FFMPEG_VERSION),
        _tool_version(ffprobe, EXPECTED_FFPROBE_VERSION),
    )


def _parse_positive_int(value: object, *, field: str) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if not isinstance(value, str) or not value.isdigit() or int(value) <= 0:
        raise TtsWavNormalizationError("ffprobe returned invalid " + field)
    return int(value)


def inspect_wav(path: Path, *, ffprobe: str) -> TtsWavProbeV1:
    """Inspect container and stream shape without accepting it yet."""
    _require_regular_not_symlink(path, label="raw WAV")
    completed = _run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            (
                "format=format_name:stream=codec_type,codec_name,sample_fmt,"
                "sample_rate,channels,channel_layout,bits_per_raw_sample,"
                "bits_per_sample"
            ),
            "-of",
            "json",
            str(path),
        ]
    )
    if completed.returncode != 0:
        raise TtsWavNormalizationError("ffprobe could not inspect WAV")
    try:
        payload = json.loads(completed.stdout)
        format_name = payload["format"]["format_name"]
        streams = payload["streams"]
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise TtsWavNormalizationError("ffprobe returned invalid WAV metadata") from exc

    if format_name != "wav" or not isinstance(streams, list):
        raise TtsWavNormalizationError("raw audio must use RIFF/WAVE")
    if len(streams) != 1:
        raise TtsWavNormalizationError("raw WAV must contain exactly one stream")
    stream = streams[0]
    if not isinstance(stream, dict) or stream.get("codec_type") != "audio":
        raise TtsWavNormalizationError("raw WAV must contain one audio stream")

    codec = stream.get("codec_name")
    sample_format = stream.get("sample_fmt")
    if not isinstance(codec, str) or not isinstance(sample_format, str):
        raise TtsWavNormalizationError("ffprobe returned incomplete audio metadata")
    bit_depth_raw = stream.get("bits_per_raw_sample") or stream.get("bits_per_sample")
    bit_depth = _parse_positive_int(bit_depth_raw, field="bit depth")
    return TtsWavProbeV1(
        container="RIFF/WAVE",
        codec=codec,
        sample_format=sample_format,
        sample_rate=_parse_positive_int(stream.get("sample_rate"), field="sample rate"),
        channels=_parse_positive_int(stream.get("channels"), field="channels"),
        channel_layout=(
            stream.get("channel_layout")
            if isinstance(stream.get("channel_layout"), str)
            else None
        ),
        bit_depth=bit_depth,
        stream_count=1,
        duration_samples=0,
        duration_seconds=0.0,
        decoded_samples=0,
    )


def validate_raw_probe(probe: TtsWavProbeV1) -> None:
    """Apply the raw-input contract before creating any output file."""
    if probe.container != "RIFF/WAVE":
        raise TtsWavNormalizationError("raw audio must use RIFF/WAVE")
    if (
        not probe.codec.startswith("pcm_")
        or probe.codec in _LINEAR_PCM_EXCLUSIONS
    ):
        raise TtsWavNormalizationError("raw WAV must use linear uncompressed PCM")
    if probe.channels != 1:
        raise TtsWavNormalizationError("raw WAV must be mono; downmix is forbidden")
    if probe.stream_count != 1:
        raise TtsWavNormalizationError("raw WAV must contain exactly one stream")


def _decode_mono_samples(path: Path, *, ffmpeg: str) -> tuple[float, ...]:
    completed = subprocess.run(
        [
            ffmpeg,
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-xerror",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-vn",
            "-sn",
            "-dn",
            "-f",
            "f64le",
            "-acodec",
            "pcm_f64le",
            "-",
        ],
        check=False,
        shell=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise TtsWavNormalizationError("WAV is not completely decodable")
    if len(completed.stdout) % 8 != 0:
        raise TtsWavNormalizationError("decoded WAV samples are malformed")
    samples = tuple(value[0] for value in struct.iter_unpack("<d", completed.stdout))
    if not samples:
        raise TtsWavNormalizationError("decoded WAV must contain audio samples")
    if any(not math.isfinite(value) for value in samples):
        raise TtsWavNormalizationError("decoded WAV contains non-finite samples")
    return samples


def _with_decoded_duration(
    probe: TtsWavProbeV1,
    samples: tuple[float, ...],
) -> TtsWavProbeV1:
    count = len(samples)
    return probe.model_copy(
        update={
            "duration_samples": count,
            "duration_seconds": count / probe.sample_rate,
            "decoded_samples": count,
        }
    )


def _parse_ebu_value(pattern: re.Pattern[str], output: str) -> float | None:
    matches = pattern.findall(output)
    if not matches:
        return None
    try:
        value = float(matches[-1])
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _ebu_metrics(path: Path, *, ffmpeg: str) -> tuple[float | None, float | None, float | None]:
    """Measure EBU R128 descriptively; absent values remain descriptive nulls."""
    completed = _run(
        [
            ffmpeg,
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "info",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            "ebur128=peak=true:framelog=quiet",
            "-f",
            "null",
            "-",
        ]
    )
    if completed.returncode != 0:
        return None, None, None
    output = completed.stderr
    return (
        _parse_ebu_value(_LOUDNESS_PATTERN, output),
        _parse_ebu_value(_LRA_PATTERN, output),
        _parse_ebu_value(_TRUE_PEAK_PATTERN, output),
    )


def descriptive_metrics(
    path: Path,
    samples: tuple[float, ...],
    *,
    ffmpeg: str,
) -> TtsWavDescriptiveMetricsV1:
    """Measure technical properties without deriving an acceptance threshold."""
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    leading = next((index for index, value in enumerate(samples) if value != 0.0), len(samples))
    trailing = next(
        (index for index, value in enumerate(reversed(samples)) if value != 0.0),
        len(samples),
    )
    integrated_lufs, loudness_range_lu, true_peak_dbfs = _ebu_metrics(
        path,
        ffmpeg=ffmpeg,
    )
    return TtsWavDescriptiveMetricsV1(
        size_bytes=path.stat().st_size,
        sample_peak_linear=peak,
        true_peak_dbfs=true_peak_dbfs,
        full_scale_sample_count=sum(abs(value) >= 1.0 for value in samples),
        rms_linear=rms,
        peak_level_dbfs=(20.0 * math.log10(peak) if peak > 0.0 else None),
        integrated_loudness_lufs=integrated_lufs,
        loudness_range_lu=loudness_range_lu,
        dc_offset=sum(samples) / len(samples),
        leading_zero_samples=leading,
        trailing_zero_samples=trailing,
        noise_floor_dbfs=None,
        noise_floor_analyzer_id=None,
        noise_floor_analyzer_version=None,
    )


def normalization_argv(
    *,
    ffmpeg: str,
    raw_path: Path,
    normalized_path: Path,
) -> tuple[str, ...]:
    """Build the approved v1 argv without a shell or hidden processing."""
    return (
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-xerror",
        "-i",
        str(raw_path),
        "-map",
        "0:a:0",
        "-vn",
        "-sn",
        "-dn",
        "-map_metadata",
        "-1",
        "-map_chapters",
        "-1",
        "-af",
        (
            "aresample=24000:resampler=swr:osf=s16:dither_method=none:"
            "filter_size=32:phase_shift=10:linear_interp=1:exact_rational=1"
        ),
        "-c:a",
        "pcm_s16le",
        "-ac",
        "1",
        "-threads",
        "1",
        "-fflags",
        "+bitexact",
        "-flags:a",
        "+bitexact",
        "-write_bext",
        "0",
        "-write_peak",
        "off",
        "-rf64",
        "never",
        "-f",
        "wav",
        "-n",
        str(normalized_path),
    )


def validate_normalized_probe(probe: TtsWavProbeV1) -> None:
    """Require the exact technical output shape fixed by profile v1."""
    if (
        probe.container != "RIFF/WAVE"
        or probe.codec != "pcm_s16le"
        or probe.sample_format != "s16"
        or probe.sample_rate != CANONICAL_SAMPLE_RATE
        or probe.channels != 1
        or probe.bit_depth != 16
        or probe.stream_count != 1
        or probe.decoded_samples <= 0
    ):
        raise TtsWavNormalizationError(
            "normalized WAV does not match profile v1"
        )


def _files_are_byte_identical(first: Path, second: Path) -> bool:
    """Compare complete files without treating matching hashes as sufficient."""
    if first.stat().st_size != second.stat().st_size:
        return False
    with first.open("rb") as first_handle, second.open("rb") as second_handle:
        while True:
            first_chunk = first_handle.read(1024 * 1024)
            second_chunk = second_handle.read(1024 * 1024)
            if first_chunk != second_chunk:
                return False
            if not first_chunk:
                return True


def _require_new_output(path: Path, *, label: str) -> None:
    if path.exists() or path.is_symlink():
        raise TtsWavNormalizationError(label + " already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise TtsWavNormalizationError(label + " parent must be a regular directory")


def _temporary_path(path: Path, *, role: str) -> Path:
    return path.with_name("." + path.name + ".tts-normalizing." + role + ".tmp")


def _publish_no_overwrite(
    temporary: Path,
    destination: Path,
    *,
    created_final_paths: list[Path],
) -> None:
    try:
        os.link(temporary, destination)
    except FileExistsError as exc:
        raise TtsWavNormalizationError("output already exists") from exc
    created_final_paths.append(destination)
    temporary.unlink(missing_ok=True)
    directory_fd = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _normalize_to_temporary(
    *,
    raw_path: Path,
    temporary_path: Path,
    ffmpeg: str,
    ffprobe: str,
) -> tuple[tuple[str, ...], TtsWavProbeV1, tuple[float, ...]]:
    """Run one independent normalization from the original raw WAV."""
    argv = normalization_argv(
        ffmpeg=ffmpeg,
        raw_path=raw_path,
        normalized_path=temporary_path,
    )
    completed = _run(argv)
    if completed.returncode != 0 or not temporary_path.is_file():
        raise TtsWavNormalizationError("FFmpeg normalization failed")

    probe = inspect_wav(temporary_path, ffprobe=ffprobe)
    samples = _decode_mono_samples(temporary_path, ffmpeg=ffmpeg)
    probe = _with_decoded_duration(probe, samples)
    validate_normalized_probe(probe)
    return argv, probe, samples


def _write_temporary_json(path: Path, result: TtsWavNormalizationResultV1) -> None:
    payload = (
        json.dumps(
            result.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def normalize_tts_wav(
    *,
    sample_id: str,
    raw_path: Path,
    expected_raw_sha256: str,
    normalized_path: Path,
    record_path: Path,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    now: datetime | None = None,
) -> TtsWavNormalizationResultV1:
    """Create normalized bytes and record, or leave no new output on failure."""
    if not sample_id.strip():
        raise TtsWavNormalizationError("sample_id cannot be blank")
    expected_raw_sha256 = _validate_sha256(expected_raw_sha256)
    _require_regular_not_symlink(raw_path, label="raw WAV")
    _require_new_output(normalized_path, label="normalized WAV")
    _require_new_output(record_path, label="normalization record")
    if normalized_path.parent != record_path.parent:
        raise TtsWavNormalizationError("output and record must share one directory")

    temporary_wav_a = _temporary_path(normalized_path, role="a")
    temporary_wav_b = _temporary_path(normalized_path, role="b")
    temporary_record = _temporary_path(record_path, role="record")
    temporary_paths = (temporary_wav_a, temporary_wav_b, temporary_record)
    if any(path.exists() for path in temporary_paths):
        raise TtsWavNormalizationError("normalization temporary path already exists")

    created_final_paths: list[Path] = []
    try:
        ffmpeg_version, ffprobe_version = validate_toolchain(ffmpeg, ffprobe)
        actual_raw_sha256 = _sha256(raw_path)
        if actual_raw_sha256 != expected_raw_sha256:
            raise TtsWavNormalizationError("raw WAV SHA-256 mismatch")

        raw_probe = inspect_wav(raw_path, ffprobe=ffprobe)
        validate_raw_probe(raw_probe)
        raw_samples = _decode_mono_samples(raw_path, ffmpeg=ffmpeg)
        raw_probe = _with_decoded_duration(raw_probe, raw_samples)
        raw_metrics = descriptive_metrics(raw_path, raw_samples, ffmpeg=ffmpeg)

        argv, normalized_probe, normalized_samples = _normalize_to_temporary(
            raw_path=raw_path,
            temporary_path=temporary_wav_a,
            ffmpeg=ffmpeg,
            ffprobe=ffprobe,
        )
        _, repeated_probe, _ = _normalize_to_temporary(
            raw_path=raw_path,
            temporary_path=temporary_wav_b,
            ffmpeg=ffmpeg,
            ffprobe=ffprobe,
        )
        first_normalized_sha256 = _sha256(temporary_wav_a)
        repeated_normalized_sha256 = _sha256(temporary_wav_b)
        if first_normalized_sha256 != repeated_normalized_sha256:
            raise TtsWavNormalizationError("normalization hashes are not deterministic")
        if not _files_are_byte_identical(temporary_wav_a, temporary_wav_b):
            raise TtsWavNormalizationError("normalization bytes are not deterministic")
        if repeated_probe != normalized_probe:
            raise TtsWavNormalizationError("normalization probes are not deterministic")

        # A published result is reachable only after the independent second
        # derivation agrees. The existing normalized SHA-256 is therefore the
        # sole review identity; recording a duplicate SHA would add no evidence.
        normalized_metrics = descriptive_metrics(
            temporary_wav_a,
            normalized_samples,
            ffmpeg=ffmpeg,
        )
        result = TtsWavNormalizationResultV1(
            sample_id=sample_id,
            profile_version=TTS_WAV_NORMALIZATION_PROFILE_VERSION,
            raw_sha256=actual_raw_sha256,
            normalized_sha256=first_normalized_sha256,
            raw_probe=raw_probe,
            normalized_probe=normalized_probe,
            raw_metrics=raw_metrics,
            normalized_metrics=normalized_metrics,
            ffmpeg_version=ffmpeg_version,
            ffprobe_version=ffprobe_version,
            normalization_argv=argv,
            normalized_at_utc=(now or datetime.now(UTC)),
        )
        _write_temporary_json(temporary_record, result)
        temporary_wav_b.unlink(missing_ok=True)
        _publish_no_overwrite(
            temporary_wav_a,
            normalized_path,
            created_final_paths=created_final_paths,
        )
        _publish_no_overwrite(
            temporary_record,
            record_path,
            created_final_paths=created_final_paths,
        )
        return result
    except Exception as exc:
        for path in temporary_paths:
            path.unlink(missing_ok=True)
        for path in reversed(created_final_paths):
            path.unlink(missing_ok=True)
        if isinstance(exc, TtsWavNormalizationError):
            raise
        raise TtsWavNormalizationError("TTS WAV normalization failed") from exc


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize one existing TTS WAV with LOGUIC profile v1."
    )
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--expected-raw-sha256", required=True)
    parser.add_argument("--normalized", required=True, type=Path)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    result = normalize_tts_wav(
        sample_id=args.sample_id,
        raw_path=args.raw,
        expected_raw_sha256=args.expected_raw_sha256,
        normalized_path=args.normalized,
        record_path=args.record,
        ffmpeg=args.ffmpeg,
        ffprobe=args.ffprobe,
    )
    print(
        json.dumps(
            result.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
