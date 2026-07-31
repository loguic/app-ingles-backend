from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_report_artifact_verification_service import (
    verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact,
)


def report():
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
    delta = PhoneticCalibrationTechnicalDistributionComparisonDelta(
        rubric_version="phonetic-rubric/1.0",
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


def test_verifies_intact_delta_report_artifact():
    artifact = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/1.0",
    )

    verification = (
        verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
            artifact
        )
    )

    assert verification.matches_content is True
    assert verification.expected_sha256 == artifact.content_sha256
    assert verification.computed_sha256 == artifact.content_sha256


def test_detects_stored_hash_mismatch():
    artifact = build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
        report(),
        "technical-comparison-delta-report/1.0",
    )
    tampered = artifact.model_copy(update={"content_sha256": "f" * 64})

    verification = (
        verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact(
            tampered
        )
    )

    assert verification.matches_content is False
    assert verification.expected_sha256 == "f" * 64
    assert verification.computed_sha256 == artifact.content_sha256
