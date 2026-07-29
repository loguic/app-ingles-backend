import pytest

from datetime import UTC, datetime

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationMeasurement,
)
from app.services.phonetic_calibration_human_label_score_distribution_service import (
    describe_phonetic_calibration_score_distributions_by_human_label,
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


def relationship(
    sample_id: str,
    score: float,
    human_label: PhoneticCalibrationHumanLabel,
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
) -> PhoneticCalibrationHumanRelationship:
    return PhoneticCalibrationHumanRelationship(
        measurement=PhoneticCalibrationMeasurement(
            sample_id=sample_id,
            score=score,
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version=analyzer_version,
            analyzed_at=datetime.now(UTC),
        ),
        human_labels=[human_label],
        human_agreement=PhoneticCalibrationHumanAgreement(
            sample_id=sample_id,
            rubric_version=human_label.rubric_version,
            label_count=1,
            labeler_count=1,
            label_counts={
                "acceptable": int(human_label.label == "acceptable"),
                "variant": int(human_label.label == "variant"),
                "known_error": int(human_label.label == "known_error"),
            },
            unanimous=True,
        ),
    )


def test_describes_quartiles_for_human_label():
    distributions = describe_phonetic_calibration_score_distributions_by_human_label([
        relationship("human-001", 0.20, label("human-001", "labeler-001", "acceptable")),
        relationship("human-002", 0.40, label("human-002", "labeler-002", "acceptable")),
        relationship("human-003", 0.60, label("human-003", "labeler-003", "acceptable")),
        relationship("human-004", 0.80, label("human-004", "labeler-004", "acceptable")),
    ])

    assert len(distributions) == 1
    distribution = distributions[0]
    assert distribution.observation_count == 4
    assert distribution.sample_count == 4
    assert distribution.score_q25 == pytest.approx(0.35)
    assert distribution.score_median == pytest.approx(0.50)
    assert distribution.score_q75 == pytest.approx(0.65)


def test_handles_single_observation():
    distributions = describe_phonetic_calibration_score_distributions_by_human_label([
        relationship("human-001", 0.72, label("human-001", "labeler-001", "variant"))
    ])

    distribution = distributions[0]
    assert distribution.score_q25 == pytest.approx(0.72)
    assert distribution.score_median == pytest.approx(0.72)
    assert distribution.score_q75 == pytest.approx(0.72)


def test_keeps_versioned_contexts_separate():
    distributions = describe_phonetic_calibration_score_distributions_by_human_label([
        relationship("human-001", 0.40, label("human-001", "labeler-001", "acceptable")),
        relationship(
            "human-002",
            0.60,
            label("human-002", "labeler-002", "acceptable"),
            analyzer_version="wavlm-gop-runner/2.0",
        ),
        relationship(
            "human-003",
            0.80,
            label("human-003", "labeler-003", "acceptable", "phonetic-rubric/2.0"),
        ),
    ])

    assert len(distributions) == 3
