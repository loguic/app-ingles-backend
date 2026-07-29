import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import PhoneticCalibrationModelHumanSummary


def build_summary(**updates) -> PhoneticCalibrationModelHumanSummary:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "observation_count": 3,
        "sample_count": 2,
        "score_min": 0.42,
        "score_max": 0.81,
        "score_mean": 0.63,
        "label_counts": {"acceptable": 2, "variant": 3, "known_error": 1},
        "unanimous_count": 1,
    }
    payload.update(updates)
    return PhoneticCalibrationModelHumanSummary(**payload)


def test_accepts_descriptive_model_human_summary():
    summary = build_summary()

    assert summary.observation_count == 3
    assert summary.sample_count == 2
    assert summary.analyzer_version == "wavlm-gop-runner/1.0"
    assert summary.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize("field", ["score_min", "score_max", "score_mean"])
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_summary_score_outside_normalized_range(field, value):
    with pytest.raises(ValidationError):
        build_summary(**{field: value})
