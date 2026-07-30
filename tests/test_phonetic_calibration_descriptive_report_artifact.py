import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationDescriptiveReportArtifact,
    PhoneticCalibrationModelHumanSummary,
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


def test_accepts_reproducible_descriptive_report_artifact():
    artifact = PhoneticCalibrationDescriptiveReportArtifact(
        report_version="phonetic-calibration-report/1.0",
        content_sha256="a" * 64,
        report=build_report(),
    )

    assert artifact.report_version == "phonetic-calibration-report/1.0"
    assert artifact.content_sha256 == "a" * 64
    assert artifact.report.summary.observation_count == 1


@pytest.mark.parametrize(
    "content_sha256",
    [
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
    ],
)
def test_rejects_invalid_content_sha256(content_sha256):
    with pytest.raises(ValidationError):
        PhoneticCalibrationDescriptiveReportArtifact(
            report_version="phonetic-calibration-report/1.0",
            content_sha256=content_sha256,
            report=build_report(),
        )


def test_rejects_empty_report_version():
    with pytest.raises(ValidationError):
        PhoneticCalibrationDescriptiveReportArtifact(
            report_version="",
            content_sha256="b" * 64,
            report=build_report(),
        )
