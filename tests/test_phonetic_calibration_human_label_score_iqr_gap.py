import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreIqrGap,
)


def build_gap(**updates) -> PhoneticCalibrationHumanLabelScoreIqrGap:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "left_label": "known_error",
        "right_label": "acceptable",
        "gap_width": 0.30,
        "separated": True,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreIqrGap(**payload)


def test_accepts_positive_gap_for_separated_iqrs():
    gap = build_gap()

    assert gap.gap_width == pytest.approx(0.30)
    assert gap.separated is True


def test_accepts_zero_gap_for_non_separated_iqrs():
    gap = build_gap(
        gap_width=0.0,
        separated=False,
    )

    assert gap.gap_width == 0.0
    assert gap.separated is False


def test_rejects_zero_gap_for_separated_iqrs():
    with pytest.raises(
        ValidationError,
        match="Separated IQRs require a positive gap width",
    ):
        build_gap(gap_width=0.0)


def test_rejects_positive_gap_for_non_separated_iqrs():
    with pytest.raises(
        ValidationError,
        match="Non-separated IQRs must have zero gap width",
    ):
        build_gap(separated=False)
