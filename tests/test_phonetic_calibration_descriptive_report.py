import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreOverlap,
    PhoneticCalibrationModelHumanSummary,
)


def build_summary(**updates) -> PhoneticCalibrationModelHumanSummary:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "observation_count": 4,
        "sample_count": 4,
        "score_min": 0.20,
        "score_max": 0.90,
        "score_mean": 0.55,
        "label_counts": {
            "acceptable": 2,
            "variant": 1,
            "known_error": 1,
        },
        "unanimous_count": 2,
    }
    payload.update(updates)
    return PhoneticCalibrationModelHumanSummary(**payload)


def build_distribution(**updates) -> PhoneticCalibrationHumanLabelScoreDistribution:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "label": "acceptable",
        "observation_count": 2,
        "sample_count": 2,
        "score_q25": 0.60,
        "score_median": 0.70,
        "score_q75": 0.80,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreDistribution(**payload)


def build_overlap(**updates) -> PhoneticCalibrationHumanLabelScoreOverlap:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "left_label": "acceptable",
        "right_label": "variant",
        "overlap_lower": 0.60,
        "overlap_upper": 0.70,
        "overlap_width": 0.10,
        "overlaps": True,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreOverlap(**payload)


def build_report(**updates) -> PhoneticCalibrationDescriptiveReport:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "summary": build_summary(),
        "score_distributions": [build_distribution()],
        "overlaps": [build_overlap()],
    }
    payload.update(updates)
    return PhoneticCalibrationDescriptiveReport(**payload)


def test_accepts_consistent_versioned_context():
    report = build_report()

    assert report.summary.observation_count == 4
    assert len(report.score_distributions) == 1
    assert len(report.overlaps) == 1


def test_rejects_summary_from_different_context():
    with pytest.raises(ValidationError):
        build_report(summary=build_summary(analyzer_version="wavlm-gop-runner/2.0"))


def test_rejects_distribution_from_different_context():
    with pytest.raises(ValidationError):
        build_report(
            score_distributions=[
                build_distribution(rubric_version="phonetic-rubric/2.0")
            ]
        )


def test_rejects_overlap_from_different_context():
    with pytest.raises(ValidationError):
        build_report(
            overlaps=[
                build_overlap(analyzer_id="different-analyzer")
            ]
        )
