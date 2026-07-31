import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_comparison_service import (
    compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts,
)


def report(rubric_version: str = "phonetic-rubric/1.0"):
    artifact_comparison = (
        PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
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
            rubric_version=rubric_version,
        )
    )
    delta = PhoneticCalibrationTechnicalDistributionComparisonDelta(
        rubric_version=rubric_version,
        label="acceptable",
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
    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
        artifact_comparison=artifact_comparison,
        deltas=[delta],
    )


def artifact(
    artifact_version: str = "technical-comparison-delta-report/1.0",
    rubric_version: str = "phonetic-rubric/1.0",
):
    return build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(rubric_version),
        artifact_version,
    )


def test_compares_two_intact_delta_report_artifacts():
    left = artifact()
    right = artifact("technical-comparison-delta-report/2.0")

    comparison = (
        compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts(
            left,
            right,
        )
    )

    assert comparison.left_content_sha256 == left.content_sha256
    assert comparison.right_content_sha256 == right.content_sha256
    assert comparison.left_artifact_comparison == left.report.artifact_comparison
    assert comparison.right_artifact_comparison == right.report.artifact_comparison
    assert comparison.rubric_version == "phonetic-rubric/1.0"


def test_rejects_invalid_left_artifact_integrity():
    left = artifact().model_copy(update={"content_sha256": "f" * 64})
    right = artifact("technical-comparison-delta-report/2.0")

    with pytest.raises(
        ValueError,
        match="Left technical delta report artifact integrity verification failed",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts(
            left,
            right,
        )


def test_rejects_invalid_right_artifact_integrity():
    left = artifact()
    right = artifact("technical-comparison-delta-report/2.0").model_copy(
        update={"content_sha256": "f" * 64}
    )

    with pytest.raises(
        ValueError,
        match="Right technical delta report artifact integrity verification failed",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts(
            left,
            right,
        )


def test_rejects_different_rubric_versions():
    left = artifact()
    right = artifact(
        "technical-comparison-delta-report/2.0",
        "phonetic-rubric/2.0",
    )

    with pytest.raises(
        ValueError,
        match="Technical delta report artifacts must use the same rubric version",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts(
            left,
            right,
        )
