import pytest

from datetime import UTC, datetime

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationMeasurement,
)
from app.services.phonetic_calibration_human_label_score_summary_service import (
    summarize_phonetic_calibration_scores_by_human_label,
)


def relationship(
    sample_id: str,
    score: float,
    labels: list[PhoneticCalibrationHumanLabel],
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationHumanRelationship:
    return PhoneticCalibrationHumanRelationship(
        measurement=PhoneticCalibrationMeasurement(
            sample_id=sample_id,
            score=score,
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version=analyzer_version,
            analyzed_at=datetime.now(UTC),
        ),
        human_labels=labels,
        human_agreement=PhoneticCalibrationHumanAgreement(
            sample_id=sample_id,
            rubric_version=rubric_version,
            label_count=len(labels),
            labeler_count=len({label.labeler_id for label in labels}),
            label_counts={
                "acceptable": sum(label.label == "acceptable" for label in labels),
                "variant": sum(label.label == "variant" for label in labels),
                "known_error": sum(label.label == "known_error" for label in labels),
            },
            unanimous=len({label.label for label in labels}) == 1,
        ),
    )


def label(
    sample_id: str,
    labeler_id: str,
    value: str,
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationHumanLabel:
    return PhoneticCalibrationHumanLabel(
        sample_id=sample_id,
        labeler_id=labeler_id,
        rubric_version=rubric_version,
        label=value,
    )


def test_preserves_human_disagreement_across_label_summaries():
    summaries = summarize_phonetic_calibration_scores_by_human_label([
        relationship(
            "human-001",
            0.72,
            [
                label("human-001", "labeler-001", "acceptable"),
                label("human-001", "labeler-002", "variant"),
            ],
        )
    ])

    assert [item.label for item in summaries] == ["acceptable", "variant"]
    assert all(item.sample_count == 1 for item in summaries)
    assert all(item.score_mean == pytest.approx(0.72) for item in summaries)


def test_summarizes_scores_within_same_human_label():
    summaries = summarize_phonetic_calibration_scores_by_human_label([
        relationship(
            "human-001",
            0.40,
            [label("human-001", "labeler-001", "acceptable")],
        ),
        relationship(
            "human-002",
            0.80,
            [label("human-002", "labeler-002", "acceptable")],
        ),
    ])

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.observation_count == 2
    assert summary.sample_count == 2
    assert summary.score_min == 0.40
    assert summary.score_max == 0.80
    assert summary.score_mean == pytest.approx(0.60)


def test_keeps_analyzer_and_rubric_versions_separate():
    summaries = summarize_phonetic_calibration_scores_by_human_label([
        relationship(
            "human-001",
            0.40,
            [label("human-001", "labeler-001", "acceptable")],
        ),
        relationship(
            "human-002",
            0.80,
            [label("human-002", "labeler-002", "acceptable")],
            analyzer_version="wavlm-gop-runner/2.0",
        ),
        relationship(
            "human-003",
            0.60,
            [label("human-003", "labeler-003", "acceptable", "phonetic-rubric/2.0")],
            rubric_version="phonetic-rubric/2.0",
        ),
    ])

    assert len(summaries) == 3
