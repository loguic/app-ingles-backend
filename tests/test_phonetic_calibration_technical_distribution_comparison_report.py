import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationComparableArtifactContext,
    PhoneticCalibrationDescriptiveReportArtifactComparison,
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalComparisonContext,
    PhoneticCalibrationTechnicalCoverageCompatibility,
    PhoneticCalibrationTechnicalCoverageIdentity,
    PhoneticCalibrationTechnicalDistributionComparisonReport,
)


def context():
    artifact_comparison = PhoneticCalibrationDescriptiveReportArtifactComparison(
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
    human_identity = PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        evidence_sha256="c" * 64,
    )
    comparable = PhoneticCalibrationComparableArtifactContext(
        artifact_comparison=artifact_comparison,
        human_evidence_compatibility=PhoneticCalibrationHumanEvidenceCompatibility(
            left=human_identity,
            right=human_identity,
            same_evidence=True,
        ),
    )
    left_coverage = PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        sample_ids_sha256="d" * 64,
    )
    right_coverage = PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/2.0",
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        sample_ids_sha256="d" * 64,
    )
    return PhoneticCalibrationTechnicalComparisonContext(
        comparable_artifact_context=comparable,
        technical_coverage_compatibility=PhoneticCalibrationTechnicalCoverageCompatibility(
            left=left_coverage,
            right=right_coverage,
            same_coverage=True,
        ),
    )


def comparison(
    label: str = "acceptable",
    *,
    left_analyzer_version: str = "wavlm-gop-runner/1.0",
):
    return PhoneticCalibrationHumanLabelScoreDistributionComparison(
        rubric_version="phonetic-rubric/1.0",
        label=label,
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version=left_analyzer_version,
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version="wavlm-gop-runner/2.0",
        left_sample_count=3,
        right_sample_count=3,
        left_score_q25=0.60,
        right_score_q25=0.65,
        score_q25_difference=0.05,
        left_score_median=0.70,
        right_score_median=0.76,
        score_median_difference=0.06,
        left_score_q75=0.80,
        right_score_q75=0.78,
        score_q75_difference=-0.02,
    )


def test_accepts_comparisons_matching_context():
    report = PhoneticCalibrationTechnicalDistributionComparisonReport(
        context=context(),
        comparisons=[
            comparison("acceptable"),
            comparison("variant"),
            comparison("known_error"),
        ],
    )

    assert len(report.comparisons) == 3


def test_rejects_comparison_outside_context():
    with pytest.raises(
        ValidationError,
        match="Distribution comparison must match technical comparison context",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonReport(
            context=context(),
            comparisons=[
                comparison(
                    "acceptable",
                    left_analyzer_version="unexpected-runner/9.0",
                )
            ],
        )


def test_rejects_duplicate_human_labels():
    with pytest.raises(
        ValidationError,
        match="requires unique human labels",
    ):
        PhoneticCalibrationTechnicalDistributionComparisonReport(
            context=context(),
            comparisons=[
                comparison("acceptable"),
                comparison("acceptable"),
            ],
        )
