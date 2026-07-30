import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_service import (
    compare_phonetic_calibration_technical_distribution_comparison_deltas,
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


def distribution_comparison(
    left_version: str,
    right_version: str,
    *,
    label: str = "acceptable",
    q25_difference: float = 0.04,
    median_difference: float = 0.06,
    q75_difference: float = -0.02,
):
    left_q25 = 0.60
    left_median = 0.70
    left_q75 = 0.80
    return PhoneticCalibrationHumanLabelScoreDistributionComparison(
        rubric_version="phonetic-rubric/1.0",
        label=label,
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version=left_version,
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version=right_version,
        left_sample_count=3,
        right_sample_count=3,
        left_score_q25=left_q25,
        right_score_q25=left_q25 + q25_difference,
        score_q25_difference=q25_difference,
        left_score_median=left_median,
        right_score_median=left_median + median_difference,
        score_median_difference=median_difference,
        left_score_q75=left_q75,
        right_score_q75=left_q75 + q75_difference,
        score_q75_difference=q75_difference,
    )


def test_compares_distribution_comparison_deltas():
    result = compare_phonetic_calibration_technical_distribution_comparison_deltas(
        artifact_comparison(),
        distribution_comparison(
            "wavlm-gop-runner/1.0",
            "wavlm-gop-runner/2.0",
            q25_difference=0.04,
            median_difference=0.06,
            q75_difference=-0.02,
        ),
        distribution_comparison(
            "wavlm-gop-runner/1.1",
            "wavlm-gop-runner/2.1",
            q25_difference=0.07,
            median_difference=0.02,
            q75_difference=0.03,
        ),
    )

    assert result.score_q25_difference_delta == pytest.approx(0.03)
    assert result.score_median_difference_delta == pytest.approx(-0.04)
    assert result.score_q75_difference_delta == pytest.approx(0.05)


def test_rejects_left_distribution_comparison_outside_context():
    with pytest.raises(
        ValueError,
        match="Left distribution comparison must match left technical artifact context",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_deltas(
            artifact_comparison(),
            distribution_comparison(
                "unexpected-runner/9.0",
                "wavlm-gop-runner/2.0",
            ),
            distribution_comparison(
                "wavlm-gop-runner/1.1",
                "wavlm-gop-runner/2.1",
            ),
        )


def test_rejects_right_distribution_comparison_outside_context():
    with pytest.raises(
        ValueError,
        match="Right distribution comparison must match right technical artifact context",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_deltas(
            artifact_comparison(),
            distribution_comparison(
                "wavlm-gop-runner/1.0",
                "wavlm-gop-runner/2.0",
            ),
            distribution_comparison(
                "wavlm-gop-runner/1.1",
                "unexpected-runner/9.0",
            ),
        )


def test_rejects_different_human_labels():
    with pytest.raises(
        ValueError,
        match="Distribution comparisons must use the same human label",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_deltas(
            artifact_comparison(),
            distribution_comparison(
                "wavlm-gop-runner/1.0",
                "wavlm-gop-runner/2.0",
                label="acceptable",
            ),
            distribution_comparison(
                "wavlm-gop-runner/1.1",
                "wavlm-gop-runner/2.1",
                label="variant",
            ),
        )
