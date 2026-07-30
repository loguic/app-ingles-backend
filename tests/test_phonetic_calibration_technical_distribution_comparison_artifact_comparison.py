import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
)


def test_accepts_valid_technical_artifact_comparison():
    comparison = PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
        left_artifact_version="technical-comparison-report/1.0",
        left_content_sha256="a" * 64,
        left_left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_left_analyzer_version="wavlm-gop-runner/1.0",
        left_right_analyzer_id="wavlm-gop-phoneme-scorer",
        left_right_analyzer_version="wavlm-gop-runner/2.0",
        right_artifact_version="technical-comparison-report/1.0",
        right_content_sha256="b" * 64,
        right_left_analyzer_id="wavlm-gop-phoneme-scorer",
        right_left_analyzer_version="wavlm-gop-runner/1.0",
        right_right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_right_analyzer_version="wavlm-gop-runner/3.0",
        rubric_version="phonetic-rubric/1.0",
    )

    assert comparison.left_content_sha256 == "a" * 64
    assert comparison.right_content_sha256 == "b" * 64


def test_preserves_both_analyzer_comparison_contexts():
    comparison = PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
        left_artifact_version="technical-comparison-report/1.0",
        left_content_sha256="a" * 64,
        left_left_analyzer_id="analyzer-a",
        left_left_analyzer_version="1.0",
        left_right_analyzer_id="analyzer-b",
        left_right_analyzer_version="2.0",
        right_artifact_version="technical-comparison-report/2.0",
        right_content_sha256="b" * 64,
        right_left_analyzer_id="analyzer-a",
        right_left_analyzer_version="1.1",
        right_right_analyzer_id="analyzer-b",
        right_right_analyzer_version="2.1",
        rubric_version="phonetic-rubric/1.0",
    )

    assert comparison.left_left_analyzer_version == "1.0"
    assert comparison.right_right_analyzer_version == "2.1"


def test_rejects_invalid_content_sha256():
    with pytest.raises(ValidationError):
        PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison(
            left_artifact_version="technical-comparison-report/1.0",
            left_content_sha256="invalid",
            left_left_analyzer_id="analyzer-a",
            left_left_analyzer_version="1.0",
            left_right_analyzer_id="analyzer-b",
            left_right_analyzer_version="2.0",
            right_artifact_version="technical-comparison-report/1.0",
            right_content_sha256="b" * 64,
            right_left_analyzer_id="analyzer-a",
            right_left_analyzer_version="1.0",
            right_right_analyzer_id="analyzer-b",
            right_right_analyzer_version="2.0",
            rubric_version="phonetic-rubric/1.0",
        )
