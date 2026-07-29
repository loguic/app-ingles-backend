import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import PhoneticCalibrationModelHumanObservation


def build_observation(score: float = 0.72) -> PhoneticCalibrationModelHumanObservation:
    return PhoneticCalibrationModelHumanObservation(
        sample_id="human-001",
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        score=score,
        label_count=2,
        labeler_count=2,
        label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
        unanimous=False,
    )


def test_accepts_descriptive_model_human_observation():
    observation = build_observation()

    assert observation.score == 0.72
    assert observation.analyzer_version == "wavlm-gop-runner/1.0"
    assert observation.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize("score", [-0.01, 1.01])
def test_rejects_score_outside_normalized_range(score):
    with pytest.raises(ValidationError):
        build_observation(score)
