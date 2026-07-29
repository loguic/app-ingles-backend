import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import PhoneticCalibrationHumanLabelScoreSummary


def build_summary(**updates) -> PhoneticCalibrationHumanLabelScoreSummary:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "label": "acceptable",
        "observation_count": 3,
        "sample_count": 2,
        "score_min": 0.41,
        "score_max": 0.82,
        "score_mean": 0.63,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreSummary(**payload)


def test_accepts_human_label_score_summary():
    summary = build_summary()

    assert summary.label == "acceptable"
    assert summary.analyzer_version == "wavlm-gop-runner/1.0"
    assert summary.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize("field", ["score_min", "score_max", "score_mean"])
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_score_outside_normalized_range(field, value):
    with pytest.raises(ValidationError):
        build_summary(**{field: value})
