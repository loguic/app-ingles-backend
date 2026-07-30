from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationModelHumanSummary,
)
from app.services.phonetic_calibration_descriptive_report_artifact_service import (
    build_phonetic_calibration_descriptive_report_artifact,
)
from app.services.phonetic_calibration_descriptive_report_artifact_verification_service import (
    verify_phonetic_calibration_descriptive_report_artifact,
)


def build_report() -> PhoneticCalibrationDescriptiveReport:
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


def test_verifies_matching_artifact_content():
    artifact = build_phonetic_calibration_descriptive_report_artifact(
        build_report(),
        "phonetic-calibration-report/1.0",
    )

    verification = verify_phonetic_calibration_descriptive_report_artifact(artifact)

    assert verification.matches_content is True
    assert verification.expected_sha256 == artifact.content_sha256
    assert verification.computed_sha256 == artifact.content_sha256


def test_detects_altered_expected_hash():
    valid_artifact = build_phonetic_calibration_descriptive_report_artifact(
        build_report(),
        "phonetic-calibration-report/1.0",
    )
    altered_artifact = PhoneticCalibrationDescriptiveReportArtifact(
        report_version=valid_artifact.report_version,
        content_sha256="f" * 64,
        report=valid_artifact.report,
    )

    verification = verify_phonetic_calibration_descriptive_report_artifact(
        altered_artifact
    )

    assert verification.matches_content is False
    assert verification.expected_sha256 == "f" * 64
    assert verification.computed_sha256 == valid_artifact.content_sha256


def test_preserves_report_version_in_verification():
    artifact = build_phonetic_calibration_descriptive_report_artifact(
        build_report(),
        "phonetic-calibration-report/2.0",
    )

    verification = verify_phonetic_calibration_descriptive_report_artifact(artifact)

    assert verification.report_version == "phonetic-calibration-report/2.0"
