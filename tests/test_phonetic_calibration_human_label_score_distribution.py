import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
)


def build_distribution(**updates) -> PhoneticCalibrationHumanLabelScoreDistribution:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "label": "acceptable",
        "observation_count": 4,
        "sample_count": 3,
        "score_q25": 0.42,
        "score_median": 0.61,
        "score_q75": 0.79,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreDistribution(**payload)


def test_accepts_robust_human_label_score_distribution():
    distribution = build_distribution()

    assert distribution.label == "acceptable"
    assert distribution.score_median == 0.61
    assert distribution.analyzer_version == "wavlm-gop-runner/1.0"
    assert distribution.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize("field", ["score_q25", "score_median", "score_q75"])
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_distribution_score_outside_normalized_range(field, value):
    with pytest.raises(ValidationError):
        build_distribution(**{field: value})
