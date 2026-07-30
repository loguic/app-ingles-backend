import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
)


def artifact_comparison():
    return PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
        left_artifact_version="technical-comparison-report/1.0",
        left_content_sha256="a" * 64,
        left_left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_left_analyzer_version="wavlm-gop-runner/1.0",
        left_right_analyzer_id="wavlm-gop-phoneme-scorer",
        left_right_analyzer_version="wavlm-gop-runner/2.0",
        right_artifact_version="technical-comparison-report/2.0",
        right_content_sha256="b" * 64,
        right_left_analyzer_id="wavlm-gop-phoneme-scorer",
        right_left_analyzer_version="wavlm-gop-runner/1.1",
        right_right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_right_analyzer_version="wavlm-gop-runner/2.1",
        rubric_version="phonetic-rubric/1.0",
    )


def delta(
    label: str = "acceptable",
    *,
    rubric_version: str = "phonetic-rubric/1.0",
):
    return PhoneticCalibrationTechnicalDistributionComparisonDelta(
        rubric_version=rubric_version,
        label=label,
        left_score_q25_difference=0.04,
        right_score_q25_difference=0.07,
        score_q25_difference_delta=0.03,
        left_score_median_difference=0.06,
        right_score_median_difference=0.02,
        score_median_difference_delta=-0.04,
        left_score_q75_difference=-0.02,
        right_score_q75_difference=0.03,
        score_q75_difference_delta=0.05,
    )


def test_accepts_deltas_matching_artifact_rubric():
    report = PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
        artifact_comparison=artifact_comparison(),
        deltas=[
            delta("acceptable"),
            delta("variant"),
            delta("known_error"),
        ],
    )

    assert len(report.deltas) == 3


def test_rejects_delta_with_different_rubric():
    with pytest.raises(
        ValidationError,
        match="Technical comparison delta must match artifact comparison rubric",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
            artifact_comparison=artifact_comparison(),
            deltas=[
                delta(
                    "acceptable",
                    rubric_version="phonetic-rubric/2.0",
                )
            ],
        )


def test_rejects_duplicate_human_labels():
    with pytest.raises(
        ValidationError,
        match="Technical comparison delta report requires unique human labels",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
            artifact_comparison=artifact_comparison(),
            deltas=[
                delta("acceptable"),
                delta("acceptable"),
            ],
        )
