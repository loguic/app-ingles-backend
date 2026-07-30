import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
)


def comparison(**overrides):
    values = {
        "rubric_version": "phonetic-rubric/1.0",
        "label": "acceptable",
        "left_analyzer_id": "wavlm-gop-phoneme-scorer",
        "left_analyzer_version": "wavlm-gop-runner/1.0",
        "right_analyzer_id": "wavlm-gop-phoneme-scorer",
        "right_analyzer_version": "wavlm-gop-runner/2.0",
        "left_sample_count": 10,
        "right_sample_count": 10,
        "left_score_q25": 0.60,
        "right_score_q25": 0.65,
        "score_q25_difference": 0.05,
        "left_score_median": 0.70,
        "right_score_median": 0.76,
        "score_median_difference": 0.06,
        "left_score_q75": 0.80,
        "right_score_q75": 0.78,
        "score_q75_difference": -0.02,
    }
    values.update(overrides)
    return PhoneticCalibrationHumanLabelScoreDistributionComparison(**values)


def test_accepts_coherent_robust_distribution_differences():
    result = comparison()

    assert result.score_q25_difference == pytest.approx(0.05)
    assert result.score_median_difference == pytest.approx(0.06)
    assert result.score_q75_difference == pytest.approx(-0.02)


def test_rejects_incoherent_q25_difference():
    with pytest.raises(
        ValidationError,
        match="Q25 difference must equal right Q25 minus left Q25",
    ):
        comparison(score_q25_difference=0.10)


def test_rejects_incoherent_median_difference():
    with pytest.raises(
        ValidationError,
        match="Median difference must equal right median minus left median",
    ):
        comparison(score_median_difference=0.10)


def test_rejects_incoherent_q75_difference():
    with pytest.raises(
        ValidationError,
        match="Q75 difference must equal right Q75 minus left Q75",
    ):
        comparison(score_q75_difference=0.10)
