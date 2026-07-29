import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreOverlap,
)


def build_overlap(**updates) -> PhoneticCalibrationHumanLabelScoreOverlap:
    payload = {
        "analyzer_id": "wavlm-gop-phoneme-scorer",
        "analyzer_version": "wavlm-gop-runner/1.0",
        "rubric_version": "phonetic-rubric/1.0",
        "left_label": "acceptable",
        "right_label": "variant",
        "overlap_lower": 0.55,
        "overlap_upper": 0.70,
        "overlap_width": 0.15,
        "overlaps": True,
    }
    payload.update(updates)
    return PhoneticCalibrationHumanLabelScoreOverlap(**payload)


def test_accepts_descriptive_iqr_overlap():
    overlap = build_overlap()

    assert overlap.left_label == "acceptable"
    assert overlap.right_label == "variant"
    assert overlap.overlaps is True
    assert overlap.analyzer_version == "wavlm-gop-runner/1.0"
    assert overlap.rubric_version == "phonetic-rubric/1.0"


@pytest.mark.parametrize(
    "field",
    ["overlap_lower", "overlap_upper", "overlap_width"],
)
@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_overlap_value_outside_normalized_range(field, value):
    with pytest.raises(ValidationError):
        build_overlap(**{field: value})


def test_accepts_non_overlapping_distribution_pair():
    overlap = build_overlap(
        overlap_lower=None,
        overlap_upper=None,
        overlap_width=0.0,
        overlaps=False,
    )

    assert overlap.overlap_lower is None
    assert overlap.overlap_upper is None
    assert overlap.overlap_width == 0.0
    assert overlap.overlaps is False

