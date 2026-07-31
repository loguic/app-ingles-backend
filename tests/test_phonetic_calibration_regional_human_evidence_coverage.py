import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    RegionalPhoneticCalibrationHumanEvidenceCoverage,
)


def build_coverage(**updates) -> RegionalPhoneticCalibrationHumanEvidenceCoverage:
    payload = {
        "reference_locale": "en-US",
        "rubric_version": "phonetic-rubric/1.0",
        "sample_count": 3,
        "speaker_count": 2,
        "session_count": 3,
        "label_count": 6,
        "labeler_count": 2,
        "label_counts": {
            "acceptable": 3,
            "variant": 2,
            "known_error": 1,
        },
        "unanimous_sample_count": 1,
    }
    payload.update(updates)
    return RegionalPhoneticCalibrationHumanEvidenceCoverage(**payload)


def test_accepts_regional_human_evidence_coverage():
    coverage = build_coverage()

    assert coverage.reference_locale == "en-US"
    assert coverage.rubric_version == "phonetic-rubric/1.0"
    assert coverage.sample_count == 3
    assert coverage.label_counts["variant"] == 2


@pytest.mark.parametrize("reference_locale", ["en-US", "en-GB"])
def test_accepts_supported_reference_locales(reference_locale):
    assert build_coverage(reference_locale=reference_locale).reference_locale == reference_locale


def test_rejects_unsupported_reference_locale():
    with pytest.raises(ValidationError):
        build_coverage(reference_locale="en-AU")


@pytest.mark.parametrize(
    "field",
    [
        "sample_count",
        "speaker_count",
        "session_count",
        "label_count",
        "labeler_count",
        "unanimous_sample_count",
    ],
)
def test_rejects_negative_counts(field):
    with pytest.raises(ValidationError):
        build_coverage(**{field: -1})
