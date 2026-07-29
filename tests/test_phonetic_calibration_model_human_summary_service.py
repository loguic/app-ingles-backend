import pytest

from app.schemas.phonetic_calibration import PhoneticCalibrationModelHumanObservation
from app.services.phonetic_calibration_model_human_summary_service import (
    summarize_phonetic_calibration_model_human_observations,
)


def observation(
    sample_id: str,
    score: float,
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
    rubric_version: str = "phonetic-rubric/1.0",
    unanimous: bool = False,
) -> PhoneticCalibrationModelHumanObservation:
    return PhoneticCalibrationModelHumanObservation(
        sample_id=sample_id,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        score=score,
        label_count=2,
        labeler_count=2,
        label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
        unanimous=unanimous,
    )


def test_summarizes_versioned_model_human_observations():
    summaries = summarize_phonetic_calibration_model_human_observations(
        [
            observation("human-001", 0.40, unanimous=True),
            observation("human-002", 0.80),
        ]
    )

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.observation_count == 2
    assert summary.sample_count == 2
    assert summary.score_min == 0.40
    assert summary.score_max == 0.80
    assert summary.score_mean == pytest.approx(0.60)
    assert summary.label_counts == {
        "acceptable": 2,
        "variant": 2,
        "known_error": 0,
    }
    assert summary.unanimous_count == 1


def test_keeps_analyzer_and_rubric_versions_separate():
    summaries = summarize_phonetic_calibration_model_human_observations(
        [
            observation("human-001", 0.40),
            observation(
                "human-002",
                0.80,
                analyzer_version="wavlm-gop-runner/2.0",
            ),
            observation(
                "human-003",
                0.60,
                rubric_version="phonetic-rubric/2.0",
            ),
        ]
    )

    assert len(summaries) == 3
