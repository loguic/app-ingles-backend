import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationComparableArtifactContext,
    PhoneticCalibrationDescriptiveReportArtifactComparison,
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
    PhoneticCalibrationTechnicalComparisonContext,
    PhoneticCalibrationTechnicalCoverageCompatibility,
    PhoneticCalibrationTechnicalCoverageIdentity,
)


def artifact_comparison():
    return PhoneticCalibrationDescriptiveReportArtifactComparison(
        left_report_version="phonetic-calibration-report/1.0",
        left_content_sha256="a" * 64,
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version="wavlm-gop-runner/1.0",
        right_report_version="phonetic-calibration-report/1.0",
        right_content_sha256="b" * 64,
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version="wavlm-gop-runner/2.0",
        rubric_version="phonetic-rubric/1.0",
    )


def human_identity():
    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        evidence_sha256="c" * 64,
    )


def comparable_context():
    return PhoneticCalibrationComparableArtifactContext(
        artifact_comparison=artifact_comparison(),
        human_evidence_compatibility=PhoneticCalibrationHumanEvidenceCompatibility(
            left=human_identity(),
            right=human_identity(),
            same_evidence=True,
        ),
    )


def technical_identity(
    analyzer_version: str,
    *,
    analyzer_id: str = "wavlm-gop-phoneme-scorer",
):
    return PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id=analyzer_id,
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        sample_ids_sha256="d" * 64,
    )


def technical_compatibility(
    *,
    left=None,
    right=None,
    same_coverage=True,
):
    return PhoneticCalibrationTechnicalCoverageCompatibility(
        left=left or technical_identity("wavlm-gop-runner/1.0"),
        right=right or technical_identity("wavlm-gop-runner/2.0"),
        same_coverage=same_coverage,
    )


def test_accepts_complete_technical_comparison_context():
    context = PhoneticCalibrationTechnicalComparisonContext(
        comparable_artifact_context=comparable_context(),
        technical_coverage_compatibility=technical_compatibility(),
    )

    assert context.technical_coverage_compatibility.same_coverage is True


def test_rejects_different_technical_coverage():
    with pytest.raises(
        ValidationError,
        match="requires the same technical coverage",
    ):
        PhoneticCalibrationTechnicalComparisonContext(
            comparable_artifact_context=comparable_context(),
            technical_coverage_compatibility=technical_compatibility(
                same_coverage=False
            ),
        )


def test_rejects_left_technical_context_mismatch():
    with pytest.raises(
        ValidationError,
        match="Left technical coverage",
    ):
        PhoneticCalibrationTechnicalComparisonContext(
            comparable_artifact_context=comparable_context(),
            technical_coverage_compatibility=technical_compatibility(
                left=technical_identity("unexpected-runner/9.0")
            ),
        )


def test_rejects_right_technical_context_mismatch():
    with pytest.raises(
        ValidationError,
        match="Right technical coverage",
    ):
        PhoneticCalibrationTechnicalComparisonContext(
            comparable_artifact_context=comparable_context(),
            technical_coverage_compatibility=technical_compatibility(
                right=technical_identity(
                    "wavlm-gop-runner/2.0",
                    analyzer_id="different-analyzer",
                )
            ),
        )
