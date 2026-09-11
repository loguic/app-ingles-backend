"""Strict evidence contracts for the TTS WAV normalization profile v1."""

from datetime import datetime, timedelta
from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TTS_WAV_NORMALIZATION_PROFILE_VERSION = "loguic-tts-wav-normalization/1.0"


class TtsWavProbeV1(BaseModel):
    """Describe one decoded WAV stream without judging its quality."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    container: Literal["RIFF/WAVE"]
    codec: str = Field(min_length=1)
    sample_format: str = Field(min_length=1)
    sample_rate: int = Field(gt=0)
    channels: int = Field(gt=0)
    channel_layout: str | None = None
    bit_depth: int = Field(gt=0)
    stream_count: int = Field(ge=1)
    duration_samples: int = Field(ge=0)
    duration_seconds: float = Field(ge=0.0)
    decoded_samples: int = Field(ge=0)


class TtsWavDescriptiveMetricsV1(BaseModel):
    """Keep technical measurements descriptive, never acceptance thresholds."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    size_bytes: int = Field(ge=0)
    sample_peak_linear: float = Field(ge=0.0)
    true_peak_dbfs: float | None = None
    full_scale_sample_count: int = Field(ge=0)
    rms_linear: float = Field(ge=0.0)
    peak_level_dbfs: float | None = None
    integrated_loudness_lufs: float | None = None
    loudness_range_lu: float | None = None
    dc_offset: float
    leading_zero_samples: int = Field(ge=0)
    trailing_zero_samples: int = Field(ge=0)
    noise_floor_dbfs: float | None = None
    noise_floor_analyzer_id: str | None = None
    noise_floor_analyzer_version: str | None = None

    @model_validator(mode="after")
    def validate_descriptive_values(self) -> "TtsWavDescriptiveMetricsV1":
        numeric_values = (
            self.sample_peak_linear,
            self.rms_linear,
            self.dc_offset,
            self.true_peak_dbfs,
            self.peak_level_dbfs,
            self.integrated_loudness_lufs,
            self.loudness_range_lu,
            self.noise_floor_dbfs,
        )
        if any(value is not None and not isfinite(value) for value in numeric_values):
            raise ValueError("TTS WAV metrics must be finite when present")

        noise_identity = (
            self.noise_floor_analyzer_id,
            self.noise_floor_analyzer_version,
        )
        if self.noise_floor_dbfs is None:
            if noise_identity != (None, None):
                raise ValueError("Noise-floor analyzer requires a noise-floor value")
        elif not all(noise_identity):
            raise ValueError("Noise-floor value requires a versioned analyzer")
        return self


class TtsWavNormalizationResultV1(BaseModel):
    """Record one raw-to-normalized artifact derivation reproducibly."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    sample_id: str = Field(min_length=1)
    profile_version: Literal[TTS_WAV_NORMALIZATION_PROFILE_VERSION]
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    normalized_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    raw_probe: TtsWavProbeV1
    normalized_probe: TtsWavProbeV1
    raw_metrics: TtsWavDescriptiveMetricsV1
    normalized_metrics: TtsWavDescriptiveMetricsV1
    ffmpeg_version: str = Field(min_length=1)
    ffprobe_version: str = Field(min_length=1)
    normalization_argv: tuple[str, ...] = Field(min_length=1)
    normalized_at_utc: datetime

    @model_validator(mode="after")
    def validate_result(self) -> "TtsWavNormalizationResultV1":
        if not self.sample_id.strip():
            raise ValueError("TTS WAV sample_id cannot be blank")
        if (
            self.normalized_at_utc.tzinfo is None
            or self.normalized_at_utc.utcoffset() != timedelta(0)
        ):
            raise ValueError("normalized_at_utc must be UTC")

        normalized = self.normalized_probe
        if (
            normalized.container != "RIFF/WAVE"
            or normalized.codec != "pcm_s16le"
            or normalized.sample_format != "s16"
            or normalized.sample_rate != 24000
            or normalized.channels != 1
            or normalized.bit_depth != 16
            or normalized.stream_count != 1
            or normalized.decoded_samples <= 0
        ):
            raise ValueError("Normalized WAV does not match profile v1")
        return self
