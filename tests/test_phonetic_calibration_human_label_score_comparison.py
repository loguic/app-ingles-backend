import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreComparison,
)


def test_accepts_positive_median_difference():
    comparison = PhoneticCalibrationHumanLabelScoreComparison(
        rubric_version="phonetic-rubric/1.0",
        label="acceptable",
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version="wavlm-gop-runner/1.0",
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version="wavlm-gop-runner/2.0",
        left_observation_count=10,
        right_observation_count=10,
        left_median=0.70,
        right_median=0.76,
        median_difference=0.06,
    )

    assert comparison.median_difference == pytest.approx(0.06)


def test_accepts_negative_median_difference():
    comparison = PhoneticCalibrationHumanLabelScoreComparison(
        rubric_version="phonetic-rubric/1.0",
        label="known_error",
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version="wavlm-gop-runner/1.0",
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version="wavlm-gop-runner/2.0",
        left_observation_count=8,
        right_observation_count=8,
        left_median=0.42,
        right_median=0.35,
        median_difference=-0.07,
    )

    assert comparison.median_difference == pytest.approx(-0.07)


def test_rejects_incoherent_median_difference():
    with pytest.raises(
        ValidationError,
        match="Median difference must equal right median minus left median",
    ):
        PhoneticCalibrationHumanLabelScoreComparison(
            rubric_version="phonetic-rubric/1.0",
            label="variant",
            left_analyzer_id="wavlm-gop-phoneme-scorer",
            left_analyzer_version="wavlm-gop-runner/1.0",
            right_analyzer_id="wavlm-gop-phoneme-scorer",
            right_analyzer_version="wavlm-gop-runner/2.0",
            left_observation_count=6,
            right_observation_count=6,
            left_median=0.55,
            right_median=0.60,
            median_difference=0.10,
        )
