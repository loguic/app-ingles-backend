from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)


def report(median_delta: float = -0.04):
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
            rubric_version="phonetic-rubric/1.0",
        )
    )
    left_median_difference = 0.06
    right_median_difference = left_median_difference + median_delta
    delta = PhoneticCalibrationTechnicalDistributionComparisonDelta(
        rubric_version="phonetic-rubric/1.0",
        label="acceptable",
        left_score_q25_difference=0.04,
        right_score_q25_difference=0.07,
        score_q25_difference_delta=0.03,
        left_score_median_difference=left_median_difference,
        right_score_median_difference=right_median_difference,
        score_median_difference_delta=median_delta,
        left_score_q75_difference=-0.02,
        right_score_q75_difference=0.03,
        score_q75_difference_delta=0.05,
    )
    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
        artifact_comparison=artifact_comparison,
        deltas=[delta],
    )


def test_build_is_reproducible_for_same_content():
    left = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/1.0",
    )
    right = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/1.0",
    )

    assert left.content_sha256 == right.content_sha256


def test_artifact_version_changes_identity():
    left = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/1.0",
    )
    right = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/2.0",
    )

    assert left.content_sha256 != right.content_sha256


def test_report_content_changes_identity():
    left = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(-0.04),
        "technical-comparison-delta-report/1.0",
    )
    right = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(-0.03),
        "technical-comparison-delta-report/1.0",
    )

    assert left.content_sha256 != right.content_sha256
