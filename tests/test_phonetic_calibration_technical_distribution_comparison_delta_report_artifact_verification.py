import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification,
)


def test_accepts_matching_delta_report_artifact_verification():
    verification = (
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification(
            artifact_version="technical-comparison-delta-report/1.0",
            expected_sha256="a" * 64,
            computed_sha256="a" * 64,
            matches_content=True,
        )
    )

    assert verification.matches_content is True


def test_accepts_non_matching_delta_report_artifact_verification():
    verification = (
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification(
            artifact_version="technical-comparison-delta-report/1.0",
            expected_sha256="a" * 64,
            computed_sha256="b" * 64,
            matches_content=False,
        )
    )

    assert verification.matches_content is False


def test_rejects_invalid_sha256():
    with pytest.raises(ValidationError):
        PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification(
            artifact_version="technical-comparison-delta-report/1.0",
            expected_sha256="invalid",
            computed_sha256="a" * 64,
            matches_content=False,
        )
