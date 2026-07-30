import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_service import (
    build_phonetic_calibration_technical_distribution_comparison_delta_report,
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


def comparison(
    left_version: str,
    right_version: str,
    label: str,
    median_difference: float,
):
    left_median = 0.70
    return PhoneticCalibrationHumanLabelScoreDistributionComparison(
        rubric_version="phonetic-rubric/1.0",
        label=label,
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version=left_version,
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version=right_version,
        left_sample_count=3,
        right_sample_count=3,
        left_score_q25=0.60,
        right_score_q25=0.65,
        score_q25_difference=0.05,
        left_score_median=left_median,
        right_score_median=left_median + median_difference,
        score_median_difference=median_difference,
        left_score_q75=0.80,
        right_score_q75=0.82,
        score_q75_difference=0.02,
    )


def test_builds_deterministic_delta_report():
    report = build_phonetic_calibration_technical_distribution_comparison_delta_report(
        artifact_comparison(),
        [
            comparison(
                "wavlm-gop-runner/1.0",
                "wavlm-gop-runner/2.0",
                "variant",
                0.04,
            ),
            comparison(
                "wavlm-gop-runner/1.0",
                "wavlm-gop-runner/2.0",
                "acceptable",
                0.06,
            ),
        ],
        [
            comparison(
                "wavlm-gop-runner/1.1",
                "wavlm-gop-runner/2.1",
                "acceptable",
                0.02,
            ),
            comparison(
                "wavlm-gop-runner/1.1",
                "wavlm-gop-runner/2.1",
                "variant",
                0.07,
            ),
        ],
    )

    assert [item.label for item in report.deltas] == [
        "acceptable",
        "variant",
    ]
    assert report.deltas[0].score_median_difference_delta == pytest.approx(-0.04)
    assert report.deltas[1].score_median_difference_delta == pytest.approx(0.03)


def test_rejects_duplicate_left_labels():
    with pytest.raises(
        ValueError,
        match="Left distribution comparisons require unique human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_delta_report(
            artifact_comparison(),
            [
                comparison(
                    "wavlm-gop-runner/1.0",
                    "wavlm-gop-runner/2.0",
                    "acceptable",
                    0.06,
                ),
                comparison(
                    "wavlm-gop-runner/1.0",
                    "wavlm-gop-runner/2.0",
                    "acceptable",
                    0.05,
                ),
            ],
            [
                comparison(
                    "wavlm-gop-runner/1.1",
                    "wavlm-gop-runner/2.1",
                    "acceptable",
                    0.02,
                )
            ],
        )


def test_rejects_duplicate_right_labels():
    with pytest.raises(
        ValueError,
        match="Right distribution comparisons require unique human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_delta_report(
            artifact_comparison(),
            [
                comparison(
                    "wavlm-gop-runner/1.0",
                    "wavlm-gop-runner/2.0",
                    "acceptable",
                    0.06,
                )
            ],
            [
                comparison(
                    "wavlm-gop-runner/1.1",
                    "wavlm-gop-runner/2.1",
                    "acceptable",
                    0.02,
                ),
                comparison(
                    "wavlm-gop-runner/1.1",
                    "wavlm-gop-runner/2.1",
                    "acceptable",
                    0.03,
                ),
            ],
        )


def test_rejects_different_label_sets():
    with pytest.raises(
        ValueError,
        match="must use the same human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_delta_report(
            artifact_comparison(),
            [
                comparison(
                    "wavlm-gop-runner/1.0",
                    "wavlm-gop-runner/2.0",
                    "acceptable",
                    0.06,
                )
            ],
            [
                comparison(
                    "wavlm-gop-runner/1.1",
                    "wavlm-gop-runner/2.1",
                    "variant",
                    0.02,
                )
            ],
        )
