import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationSample,
)
from app.services.phonetic_calibration_human_label_service import (
    validate_phonetic_calibration_human_labels,
)


def build_sample() -> PhoneticCalibrationSample:
    return PhoneticCalibrationSample(
        sample_id="human-001",
        reference_text="Hello, I am John.",
        audio_path="audio/human-001.wav",
        audio_sha256="a" * 64,
        expected_class="unlabeled",
    )


def build_label(sample_id: str = "human-001") -> PhoneticCalibrationHumanLabel:
    return PhoneticCalibrationHumanLabel(
        sample_id=sample_id,
        labeler_id="labeler-001",
        rubric_version="phonetic-rubric/1.0",
        label="acceptable",
    )


def test_accepts_valid_human_label_references():
    validate_phonetic_calibration_human_labels(
        [build_sample()],
        [build_label()],
    )


def test_rejects_human_label_for_unknown_sample():
    with pytest.raises(ValueError, match="unknown calibration sample"):
        validate_phonetic_calibration_human_labels(
            [build_sample()],
            [build_label("human-999")],
        )


def test_rejects_duplicate_human_label_identity():
    label = build_label()

    with pytest.raises(ValueError, match="must be unique"):
        validate_phonetic_calibration_human_labels(
            [build_sample()],
            [label, label],
        )
