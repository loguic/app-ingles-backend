import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact,
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


def test_accepts_valid_delta_report_artifact():
    source_report = report()

    artifact = (
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact(
            artifact_version="technical-comparison-delta-report/1.0",
            content_sha256="c" * 64,
            report=source_report,
        )
    )

    assert artifact.artifact_version == "technical-comparison-delta-report/1.0"
    assert artifact.report == source_report


def test_rejects_empty_artifact_version():
    with pytest.raises(ValidationError):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact(
            artifact_version="",
            content_sha256="c" * 64,
            report=report(),
        )


def test_rejects_invalid_content_sha256():
    with pytest.raises(ValidationError):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact(
            artifact_version="technical-comparison-delta-report/1.0",
            content_sha256="invalid",
            report=report(),
        )
