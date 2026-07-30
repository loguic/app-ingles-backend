import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReportArtifactComparison,
)


def build_comparison(**updates) -> PhoneticCalibrationDescriptiveReportArtifactComparison:
    payload = {
        "left_report_version": "phonetic-calibration-report/1.0",
        "left_content_sha256": "a" * 64,
        "left_analyzer_id": "wavlm-gop-phoneme-scorer",
        "left_analyzer_version": "wavlm-gop-runner/1.0",
        "right_report_version": "phonetic-calibration-report/1.0",
        "right_content_sha256": "b" * 64,
        "right_analyzer_id": "wavlm-gop-phoneme-scorer",
        "right_analyzer_version": "wavlm-gop-runner/2.0",
        "rubric_version": "phonetic-rubric/1.0",
    }
    payload.update(updates)
    return PhoneticCalibrationDescriptiveReportArtifactComparison(**payload)


def test_accepts_reproducible_artifact_comparison():
    comparison = build_comparison()

    assert comparison.left_content_sha256 == "a" * 64
    assert comparison.right_content_sha256 == "b" * 64
    assert comparison.left_analyzer_version == "wavlm-gop-runner/1.0"
    assert comparison.right_analyzer_version == "wavlm-gop-runner/2.0"
    assert comparison.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize(
    "field",
    ["left_content_sha256", "right_content_sha256"],
)
@pytest.mark.parametrize(
    "value",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64],
)
def test_rejects_invalid_sha256(field, value):
    with pytest.raises(ValidationError):
        build_comparison(**{field: value})


@pytest.mark.parametrize(
    "field",
    [
        "left_report_version",
        "left_analyzer_id",
        "left_analyzer_version",
        "right_report_version",
        "right_analyzer_id",
        "right_analyzer_version",
        "rubric_version",
    ],
)
def test_rejects_empty_versioned_identity(field):
    with pytest.raises(ValidationError):
        build_comparison(**{field: ""})
