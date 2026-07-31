import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreIqrGap,
    PhoneticCalibrationHumanLabelScoreIqrRelationship,
    PhoneticCalibrationHumanLabelScoreOverlap,
)


def build_overlap(
    *,
    overlaps: bool = True,
    right_label: str = "variant",
) -> PhoneticCalibrationHumanLabelScoreOverlap:
    return PhoneticCalibrationHumanLabelScoreOverlap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        left_label="acceptable",
        right_label=right_label,
        overlap_lower=0.60 if overlaps else None,
        overlap_upper=0.70 if overlaps else None,
        overlap_width=0.10 if overlaps else 0.0,
        overlaps=overlaps,
    )


def build_gap(
    *,
    separated: bool = False,
    right_label: str = "variant",
) -> PhoneticCalibrationHumanLabelScoreIqrGap:
    return PhoneticCalibrationHumanLabelScoreIqrGap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        left_label="acceptable",
        right_label=right_label,
        gap_width=0.20 if separated else 0.0,
        separated=separated,
    )


def test_accepts_overlapping_relationship():
    relationship = PhoneticCalibrationHumanLabelScoreIqrRelationship(
        overlap=build_overlap(overlaps=True),
        gap=build_gap(separated=False),
    )

    assert relationship.overlap.overlaps is True
    assert relationship.gap.separated is False


def test_accepts_separated_relationship():
    relationship = PhoneticCalibrationHumanLabelScoreIqrRelationship(
        overlap=build_overlap(overlaps=False),
        gap=build_gap(separated=True),
    )

    assert relationship.overlap.overlaps is False
    assert relationship.gap.separated is True


def test_rejects_different_versioned_label_pairs():
    with pytest.raises(ValidationError):
        PhoneticCalibrationHumanLabelScoreIqrRelationship(
            overlap=build_overlap(right_label="variant"),
            gap=build_gap(right_label="known_error"),
        )


def test_rejects_non_complementary_states():
    with pytest.raises(ValidationError):
        PhoneticCalibrationHumanLabelScoreIqrRelationship(
            overlap=build_overlap(overlaps=True),
            gap=build_gap(separated=True),
        )

def test_accepts_touching_iqr_relationship():
    overlap = PhoneticCalibrationHumanLabelScoreOverlap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        left_label="acceptable",
        right_label="variant",
        overlap_lower=0.60,
        overlap_upper=0.60,
        overlap_width=0.0,
        overlaps=True,
    )
    gap = build_gap(separated=False)

    relationship = PhoneticCalibrationHumanLabelScoreIqrRelationship(
        overlap=overlap,
        gap=gap,
    )

    assert relationship.overlap.overlaps is True
    assert relationship.overlap.overlap_width == 0.0
    assert relationship.gap.separated is False
    assert relationship.gap.gap_width == 0.0

