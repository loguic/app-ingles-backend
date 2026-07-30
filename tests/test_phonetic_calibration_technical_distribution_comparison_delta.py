import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
)


def delta(**overrides):
    values = {
        "rubric_version": "phonetic-rubric/1.0",
        "label": "acceptable",
        "left_score_q25_difference": 0.04,
        "right_score_q25_difference": 0.07,
        "score_q25_difference_delta": 0.03,
        "left_score_median_difference": 0.06,
        "right_score_median_difference": 0.02,
        "score_median_difference_delta": -0.04,
        "left_score_q75_difference": -0.02,
        "right_score_q75_difference": 0.03,
        "score_q75_difference_delta": 0.05,
    }
    values.update(overrides)
    return PhoneticCalibrationTechnicalDistributionComparisonDelta(**values)


def test_accepts_coherent_distribution_comparison_deltas():
    result = delta()

    assert result.score_q25_difference_delta == pytest.approx(0.03)
    assert result.score_median_difference_delta == pytest.approx(-0.04)
    assert result.score_q75_difference_delta == pytest.approx(0.05)


def test_rejects_incoherent_q25_comparison_delta():
    with pytest.raises(
        ValidationError,
        match="Q25 comparison delta must equal right difference minus left difference",
    ):
        delta(score_q25_difference_delta=0.10)


def test_rejects_incoherent_median_comparison_delta():
    with pytest.raises(
        ValidationError,
        match="Median comparison delta must equal right difference minus left difference",
    ):
        delta(score_median_difference_delta=0.10)


def test_rejects_incoherent_q75_comparison_delta():
    with pytest.raises(
        ValidationError,
        match="Q75 comparison delta must equal right difference minus left difference",
    ):
        delta(score_q75_difference_delta=0.10)
