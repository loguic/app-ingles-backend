import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison,
)


def artifact_comparison(rubric_version: str = "phonetic-rubric/1.0"):
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
        rubric_version=rubric_version,
    )


def test_accepts_valid_delta_report_artifact_comparison():
    comparison = (
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison(
            left_artifact_version="technical-comparison-delta-report/1.0",
            left_content_sha256="c" * 64,
            left_artifact_comparison=artifact_comparison(),
            right_artifact_version="technical-comparison-delta-report/2.0",
            right_content_sha256="d" * 64,
            right_artifact_comparison=artifact_comparison(),
            rubric_version="phonetic-rubric/1.0",
        )
    )

    assert comparison.rubric_version == "phonetic-rubric/1.0"


def test_rejects_left_context_with_different_rubric():
    with pytest.raises(
        ValidationError,
        match="Left delta report artifact comparison must match rubric version",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison(
            left_artifact_version="technical-comparison-delta-report/1.0",
            left_content_sha256="c" * 64,
            left_artifact_comparison=artifact_comparison("phonetic-rubric/2.0"),
            right_artifact_version="technical-comparison-delta-report/2.0",
            right_content_sha256="d" * 64,
            right_artifact_comparison=artifact_comparison(),
            rubric_version="phonetic-rubric/1.0",
        )


def test_rejects_right_context_with_different_rubric():
    with pytest.raises(
        ValidationError,
        match="Right delta report artifact comparison must match rubric version",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison(
            left_artifact_version="technical-comparison-delta-report/1.0",
            left_content_sha256="c" * 64,
            left_artifact_comparison=artifact_comparison(),
            right_artifact_version="technical-comparison-delta-report/2.0",
            right_content_sha256="d" * 64,
            right_artifact_comparison=artifact_comparison("phonetic-rubric/2.0"),
            rubric_version="phonetic-rubric/1.0",
        )
