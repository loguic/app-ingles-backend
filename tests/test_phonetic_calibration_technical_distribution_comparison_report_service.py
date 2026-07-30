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
from app.services.phonetic_calibration_technical_distribution_comparison_report_service import (
    build_phonetic_calibration_technical_distribution_comparison_report,
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


def distribution(analyzer_version: str, label: str, median: float):
    return PhoneticCalibrationHumanLabelScoreDistribution(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        label=label,
        observation_count=3,
        sample_count=3,
        score_q25=median - 0.05,
        score_median=median,
        score_q75=median + 0.05,
    )


def test_builds_deterministic_consolidated_report():
    report = build_phonetic_calibration_technical_distribution_comparison_report(
        context(),
        [
            distribution("wavlm-gop-runner/1.0", "variant", 0.60),
            distribution("wavlm-gop-runner/1.0", "acceptable", 0.75),
        ],
        [
            distribution("wavlm-gop-runner/2.0", "acceptable", 0.80),
            distribution("wavlm-gop-runner/2.0", "variant", 0.64),
        ],
    )

    assert [item.label for item in report.comparisons] == [
        "acceptable",
        "variant",
    ]
    assert report.comparisons[0].score_median_difference == pytest.approx(0.05)
    assert report.comparisons[1].score_median_difference == pytest.approx(0.04)


def test_rejects_duplicate_left_labels():
    with pytest.raises(
        ValueError,
        match="Left score distributions require unique human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_report(
            context(),
            [
                distribution("wavlm-gop-runner/1.0", "acceptable", 0.70),
                distribution("wavlm-gop-runner/1.0", "acceptable", 0.72),
            ],
            [
                distribution("wavlm-gop-runner/2.0", "acceptable", 0.75),
            ],
        )


def test_rejects_duplicate_right_labels():
    with pytest.raises(
        ValueError,
        match="Right score distributions require unique human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_report(
            context(),
            [
                distribution("wavlm-gop-runner/1.0", "acceptable", 0.70),
            ],
            [
                distribution("wavlm-gop-runner/2.0", "acceptable", 0.75),
                distribution("wavlm-gop-runner/2.0", "acceptable", 0.77),
            ],
        )


def test_rejects_different_label_sets():
    with pytest.raises(
        ValueError,
        match="must use the same human labels",
    ):
        build_phonetic_calibration_technical_distribution_comparison_report(
            context(),
            [
                distribution("wavlm-gop-runner/1.0", "acceptable", 0.70),
            ],
            [
                distribution("wavlm-gop-runner/2.0", "variant", 0.60),
            ],
        )
