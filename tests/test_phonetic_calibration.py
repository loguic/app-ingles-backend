from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationMeasurement,
    PhoneticCalibrationObservation,
    PhoneticCalibrationSample,
)


def test_accepts_valid_human_calibration_sample():
    sample = PhoneticCalibrationSample(
        sample_id="human-001",
        reference_text="Hello, I am John.",
        audio_path="samples/human-001.wav",
        audio_sha256="a" * 64,
        expected_class="acceptable",
    )

    assert sample.sample_id == "human-001"
    assert sample.expected_class == "acceptable"


def test_rejects_invalid_audio_sha256():
    with pytest.raises(ValidationError):
        PhoneticCalibrationSample(
            sample_id="human-001",
            reference_text="Hello, I am John.",
            audio_path="samples/human-001.wav",
            audio_sha256="not-a-sha256",
            expected_class="acceptable",
        )


def test_rejects_unknown_expected_class():
    with pytest.raises(ValidationError):
        PhoneticCalibrationSample(
            sample_id="human-001",
            reference_text="Hello, I am John.",
            audio_path="samples/human-001.wav",
            audio_sha256="b" * 64,
            expected_class="perfect",
        )


def test_accepts_reproducible_calibration_measurement():
    measured_at = datetime.now(UTC)
    measurement = PhoneticCalibrationMeasurement(
        sample_id="human-001",
        score=0.884,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0|pipeline-sha256:test",
        analyzed_at=measured_at,
    )

    assert measurement.score == 0.884
    assert measurement.analyzed_at == measured_at


@pytest.mark.parametrize("score", [-0.01, 1.01])
def test_rejects_measurement_score_outside_normalized_range(score):
    with pytest.raises(ValidationError):
        PhoneticCalibrationMeasurement(
            sample_id="human-001",
            score=score,
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version="wavlm-gop-runner/1.0",
            analyzed_at=datetime.now(UTC),
        )


def test_accepts_observation_with_matching_sample_identity():
    sample = PhoneticCalibrationSample(
        sample_id="human-001",
        reference_text="Hello, I am John.",
        audio_path="samples/human-001.wav",
        audio_sha256="c" * 64,
        expected_class="acceptable",
    )
    measurement = PhoneticCalibrationMeasurement(
        sample_id="human-001",
        score=0.884,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        analyzed_at=datetime.now(UTC),
    )

    observation = PhoneticCalibrationObservation(
        sample=sample,
        measurement=measurement,
    )

    assert observation.sample.expected_class == "acceptable"


def test_rejects_observation_with_mismatched_sample_identity():
    sample = PhoneticCalibrationSample(
        sample_id="human-001",
        reference_text="Hello, I am John.",
        audio_path="samples/human-001.wav",
        audio_sha256="d" * 64,
        expected_class="known_error",
    )
    measurement = PhoneticCalibrationMeasurement(
        sample_id="human-002",
        score=0.4,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        analyzed_at=datetime.now(UTC),
    )

    with pytest.raises(ValidationError, match="share sample_id"):
        PhoneticCalibrationObservation(
            sample=sample,
            measurement=measurement,
        )
