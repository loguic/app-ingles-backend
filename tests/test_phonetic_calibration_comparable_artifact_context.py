import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationComparableArtifactContext,
    PhoneticCalibrationDescriptiveReportArtifactComparison,
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
)


def comparison() -> PhoneticCalibrationDescriptiveReportArtifactComparison:
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


def identity(
    *,
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationHumanEvidenceIdentity:
    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version=rubric_version,
        sample_count=3,
        evidence_sha256="c" * 64,
    )


def compatibility(
    *,
    left_rubric: str = "phonetic-rubric/1.0",
    right_rubric: str = "phonetic-rubric/1.0",
    same_evidence: bool = True,
) -> PhoneticCalibrationHumanEvidenceCompatibility:
    return PhoneticCalibrationHumanEvidenceCompatibility(
        left=identity(rubric_version=left_rubric),
        right=identity(rubric_version=right_rubric),
        same_evidence=same_evidence,
    )


def test_accepts_comparable_calibration_context():
    context = PhoneticCalibrationComparableArtifactContext(
        artifact_comparison=comparison(),
        human_evidence_compatibility=compatibility(),
    )

    assert context.human_evidence_compatibility.same_evidence is True
    assert context.artifact_comparison.rubric_version == "phonetic-rubric/1.0"


def test_rejects_different_human_evidence():
    with pytest.raises(ValidationError, match="requires the same human evidence"):
        PhoneticCalibrationComparableArtifactContext(
            artifact_comparison=comparison(),
            human_evidence_compatibility=compatibility(same_evidence=False),
        )


def test_rejects_left_human_evidence_rubric_mismatch():
    with pytest.raises(ValidationError, match="Left human evidence rubric"):
        PhoneticCalibrationComparableArtifactContext(
            artifact_comparison=comparison(),
            human_evidence_compatibility=compatibility(
                left_rubric="phonetic-rubric/2.0"
            ),
        )


def test_rejects_right_human_evidence_rubric_mismatch():
    with pytest.raises(ValidationError, match="Right human evidence rubric"):
        PhoneticCalibrationComparableArtifactContext(
            artifact_comparison=comparison(),
            human_evidence_compatibility=compatibility(
                right_rubric="phonetic-rubric/2.0"
            ),
        )
