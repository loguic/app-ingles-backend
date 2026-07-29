import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import PhoneticCalibrationHumanAgreement


def test_accepts_valid_human_agreement():
    agreement = PhoneticCalibrationHumanAgreement(
        sample_id="human-001",
        rubric_version="phonetic-rubric/1.0",
        label_count=3,
        labeler_count=3,
        label_counts={"acceptable": 2, "variant": 1, "known_error": 0},
        unanimous=False,
    )

    assert agreement.sample_id == "human-001"
    assert agreement.label_count == 3
    assert agreement.labeler_count == 3
    assert agreement.unanimous is False


def test_rejects_zero_human_agreement_label_count():
    with pytest.raises(ValidationError):
        PhoneticCalibrationHumanAgreement(
            sample_id="human-001",
        rubric_version="phonetic-rubric/1.0",
            label_count=0,
            labeler_count=1,
            label_counts={"acceptable": 0, "variant": 0, "known_error": 0},
            unanimous=False,
        )


def test_rejects_zero_human_agreement_labeler_count():
    with pytest.raises(ValidationError):
        PhoneticCalibrationHumanAgreement(
            sample_id="human-001",
        rubric_version="phonetic-rubric/1.0",
            label_count=1,
            labeler_count=0,
            label_counts={"acceptable": 1, "variant": 0, "known_error": 0},
            unanimous=True,
        )
