import pytest

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
from app.services.phonetic_calibration_technical_distribution_comparison_report_artifact_service import (
    build_phonetic_calibration_technical_distribution_comparison_report_artifact,
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


def comparison(median_difference: float = 0.05):
    left_median = 0.70
    right_median = left_median + median_difference
    return PhoneticCalibrationHumanLabelScoreDistributionComparison(
        rubric_version="phonetic-rubric/1.0",
        label="acceptable",
        left_analyzer_id="wavlm-gop-phoneme-scorer",
        left_analyzer_version="wavlm-gop-runner/1.0",
        right_analyzer_id="wavlm-gop-phoneme-scorer",
        right_analyzer_version="wavlm-gop-runner/2.0",
        left_sample_count=3,
        right_sample_count=3,
        left_score_q25=0.60,
        right_score_q25=0.65,
        score_q25_difference=0.05,
        left_score_median=left_median,
        right_score_median=right_median,
        score_median_difference=median_difference,
        left_score_q75=0.80,
        right_score_q75=0.82,
        score_q75_difference=0.02,
    )


def report(median_difference: float = 0.05):
    return PhoneticCalibrationTechnicalDistributionComparisonReport(
        context=context(),
        comparisons=[comparison(median_difference)],
    )


from app.services.phonetic_calibration_technical_distribution_comparison_artifact_comparison_service import (
    compare_phonetic_calibration_technical_distribution_comparison_report_artifacts,
)


def artifact(version: str = "technical-comparison-report/1.0"):
    return build_phonetic_calibration_technical_distribution_comparison_report_artifact(
        report(),
        version,
    )


def test_compares_two_intact_technical_artifacts():
    left = artifact()
    right = artifact("technical-comparison-report/2.0")

    comparison = (
        compare_phonetic_calibration_technical_distribution_comparison_report_artifacts(
            left,
            right,
        )
    )

    assert comparison.left_content_sha256 == left.content_sha256
    assert comparison.right_content_sha256 == right.content_sha256
    assert comparison.rubric_version == "phonetic-rubric/1.0"


def test_rejects_invalid_left_artifact_integrity():
    left = artifact().model_copy(update={"content_sha256": "f" * 64})
    right = artifact("technical-comparison-report/2.0")

    with pytest.raises(
        ValueError,
        match="Left technical comparison artifact integrity verification failed",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_report_artifacts(
            left,
            right,
        )


def test_rejects_invalid_right_artifact_integrity():
    left = artifact()
    right = artifact("technical-comparison-report/2.0").model_copy(
        update={"content_sha256": "f" * 64}
    )

    with pytest.raises(
        ValueError,
        match="Right technical comparison artifact integrity verification failed",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_report_artifacts(
            left,
            right,
        )


def test_rejects_different_rubric_versions():
    left = artifact()
    payload = report().model_dump(mode="python")

    def replace_rubric(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "rubric_version":
                    value[key] = "phonetic-rubric/2.0"
                else:
                    replace_rubric(item)
        elif isinstance(value, list):
            for item in value:
                replace_rubric(item)

    replace_rubric(payload)
    right_report = PhoneticCalibrationTechnicalDistributionComparisonReport.model_validate(
        payload
    )
    right = build_phonetic_calibration_technical_distribution_comparison_report_artifact(
        right_report,
        "technical-comparison-report/2.0",
    )

    with pytest.raises(
        ValueError,
        match="Technical comparison artifacts must use the same rubric version",
    ):
        compare_phonetic_calibration_technical_distribution_comparison_report_artifacts(
            left,
            right,
        )
