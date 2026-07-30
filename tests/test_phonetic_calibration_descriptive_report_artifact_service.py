from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationModelHumanSummary,
)
from app.services.phonetic_calibration_descriptive_report_artifact_service import (
    build_phonetic_calibration_descriptive_report_artifact,
)


def build_report(
    score_mean: float = 0.70,
) -> PhoneticCalibrationDescriptiveReport:
    return PhoneticCalibrationDescriptiveReport(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        summary=PhoneticCalibrationModelHumanSummary(
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version="wavlm-gop-runner/1.0",
            rubric_version="phonetic-rubric/1.0",
            observation_count=1,
            sample_count=1,
            score_min=score_mean,
            score_max=score_mean,
            score_mean=score_mean,
            label_counts={
                "acceptable": 1,
                "variant": 0,
                "known_error": 0,
            },
            unanimous_count=1,
        ),
    )


def test_same_report_and_version_produce_same_hash():
    report = build_report()

    first = build_phonetic_calibration_descriptive_report_artifact(
        report,
        "phonetic-calibration-report/1.0",
    )
    second = build_phonetic_calibration_descriptive_report_artifact(
        report,
        "phonetic-calibration-report/1.0",
    )

    assert first.content_sha256 == second.content_sha256


def test_report_version_changes_hash():
    report = build_report()

    first = build_phonetic_calibration_descriptive_report_artifact(
        report,
        "phonetic-calibration-report/1.0",
    )
    second = build_phonetic_calibration_descriptive_report_artifact(
        report,
        "phonetic-calibration-report/2.0",
    )

    assert first.content_sha256 != second.content_sha256


def test_report_content_changes_hash():
    first = build_phonetic_calibration_descriptive_report_artifact(
        build_report(0.70),
        "phonetic-calibration-report/1.0",
    )
    second = build_phonetic_calibration_descriptive_report_artifact(
        build_report(0.71),
        "phonetic-calibration-report/1.0",
    )

    assert first.content_sha256 != second.content_sha256


def test_artifact_preserves_original_report():
    report = build_report()

    artifact = build_phonetic_calibration_descriptive_report_artifact(
        report,
        "phonetic-calibration-report/1.0",
    )

    assert artifact.report == report
