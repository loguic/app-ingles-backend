import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationComparableArtifactContext,
    PhoneticCalibrationDescriptiveReportArtifactComparison,
    PhoneticCalibrationHumanEvidenceCompatibility,
    PhoneticCalibrationHumanEvidenceIdentity,
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationTechnicalComparisonContext,
    PhoneticCalibrationTechnicalCoverageCompatibility,
    PhoneticCalibrationTechnicalCoverageIdentity,
)
from app.services.phonetic_calibration_human_label_score_comparison_service import (
    compare_phonetic_calibration_human_label_scores,
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


def distribution(
    analyzer_version: str,
    *,
    label: str = "acceptable",
    analyzer_id: str = "wavlm-gop-phoneme-scorer",
    median: float = 0.70,
):
    return PhoneticCalibrationHumanLabelScoreDistribution(
        analyzer_id=analyzer_id,
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        label=label,
        observation_count=3,
        sample_count=3,
        score_q25=median - 0.05,
        score_median=median,
        score_q75=median + 0.05,
    )


def test_compares_median_scores_for_same_human_label():
    comparison = compare_phonetic_calibration_human_label_scores(
        context(),
        distribution("wavlm-gop-runner/1.0", median=0.70),
        distribution("wavlm-gop-runner/2.0", median=0.76),
    )

    assert comparison.label == "acceptable"
    assert comparison.left_median == pytest.approx(0.70)
    assert comparison.right_median == pytest.approx(0.76)
    assert comparison.median_difference == pytest.approx(0.06)


def test_rejects_left_distribution_outside_context():
    with pytest.raises(
        ValueError,
        match="Left score distribution must match left technical comparison context",
    ):
        compare_phonetic_calibration_human_label_scores(
            context(),
            distribution("unexpected-runner/9.0"),
            distribution("wavlm-gop-runner/2.0"),
        )


def test_rejects_right_distribution_outside_context():
    with pytest.raises(
        ValueError,
        match="Right score distribution must match right technical comparison context",
    ):
        compare_phonetic_calibration_human_label_scores(
            context(),
            distribution("wavlm-gop-runner/1.0"),
            distribution(
                "wavlm-gop-runner/2.0",
                analyzer_id="different-analyzer",
            ),
        )


def test_rejects_different_human_labels():
    with pytest.raises(
        ValueError,
        match="Score distributions must use the same human label",
    ):
        compare_phonetic_calibration_human_label_scores(
            context(),
            distribution("wavlm-gop-runner/1.0", label="acceptable"),
            distribution("wavlm-gop-runner/2.0", label="variant"),
        )
