import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationModelHumanSummary,
)
from app.services.phonetic_calibration_descriptive_report_artifact_comparison_service import (
    compare_phonetic_calibration_descriptive_report_artifacts,
)
from app.services.phonetic_calibration_descriptive_report_artifact_service import (
    build_phonetic_calibration_descriptive_report_artifact,
)


def build_report(
    analyzer_version: str,
    *,
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationDescriptiveReport:
    return PhoneticCalibrationDescriptiveReport(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        summary=PhoneticCalibrationModelHumanSummary(
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version=analyzer_version,
            rubric_version=rubric_version,
            observation_count=1,
            sample_count=1,
            score_min=0.70,
            score_max=0.70,
            score_mean=0.70,
            label_counts={
                "acceptable": 1,
                "variant": 0,
                "known_error": 0,
            },
            unanimous_count=1,
        ),
    )


def build_artifact(
    analyzer_version: str,
    *,
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationDescriptiveReportArtifact:
    return build_phonetic_calibration_descriptive_report_artifact(
        build_report(
            analyzer_version,
            rubric_version=rubric_version,
        ),
        "phonetic-calibration-report/1.0",
    )


def test_compares_two_intact_artifacts():
    left = build_artifact("wavlm-gop-runner/1.0")
    right = build_artifact("wavlm-gop-runner/2.0")

    comparison = compare_phonetic_calibration_descriptive_report_artifacts(
        left,
        right,
    )

    assert comparison.left_content_sha256 == left.content_sha256
    assert comparison.right_content_sha256 == right.content_sha256
    assert comparison.left_analyzer_version == "wavlm-gop-runner/1.0"
    assert comparison.right_analyzer_version == "wavlm-gop-runner/2.0"
    assert comparison.rubric_version == "phonetic-rubric/1.0"


def test_rejects_left_artifact_with_failed_integrity():
    left = build_artifact("wavlm-gop-runner/1.0")
    altered_left = left.model_copy(update={"content_sha256": "f" * 64})
    right = build_artifact("wavlm-gop-runner/2.0")

    with pytest.raises(ValueError, match="Left calibration report artifact"):
        compare_phonetic_calibration_descriptive_report_artifacts(
            altered_left,
            right,
        )


def test_rejects_right_artifact_with_failed_integrity():
    left = build_artifact("wavlm-gop-runner/1.0")
    right = build_artifact("wavlm-gop-runner/2.0")
    altered_right = right.model_copy(update={"content_sha256": "f" * 64})

    with pytest.raises(ValueError, match="Right calibration report artifact"):
        compare_phonetic_calibration_descriptive_report_artifacts(
            left,
            altered_right,
        )


def test_rejects_different_rubric_versions():
    left = build_artifact("wavlm-gop-runner/1.0")
    right = build_artifact(
        "wavlm-gop-runner/2.0",
        rubric_version="phonetic-rubric/2.0",
    )

    with pytest.raises(ValueError, match="share rubric_version"):
        compare_phonetic_calibration_descriptive_report_artifacts(
            left,
            right,
        )
