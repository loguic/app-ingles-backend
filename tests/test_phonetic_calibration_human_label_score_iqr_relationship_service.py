import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreIqrGap,
    PhoneticCalibrationHumanLabelScoreOverlap,
)
from app.services.phonetic_calibration_human_label_score_iqr_relationship_service import (
    relate_phonetic_calibration_human_label_score_iqr_evidence,
)


def overlap(
    left_label: str,
    right_label: str,
    *,
    overlaps: bool,
) -> PhoneticCalibrationHumanLabelScoreOverlap:
    return PhoneticCalibrationHumanLabelScoreOverlap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        left_label=left_label,
        right_label=right_label,
        overlap_lower=0.60 if overlaps else None,
        overlap_upper=0.70 if overlaps else None,
        overlap_width=0.10 if overlaps else 0.0,
        overlaps=overlaps,
    )


def gap(
    left_label: str,
    right_label: str,
    *,
    separated: bool,
) -> PhoneticCalibrationHumanLabelScoreIqrGap:
    return PhoneticCalibrationHumanLabelScoreIqrGap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        rubric_version="phonetic-rubric/1.0",
        left_label=left_label,
        right_label=right_label,
        gap_width=0.20 if separated else 0.0,
        separated=separated,
    )


def test_relates_matching_evidence_in_deterministic_order():
    relationships = relate_phonetic_calibration_human_label_score_iqr_evidence(
        overlaps=[
            overlap("acceptable", "variant", overlaps=True),
            overlap("acceptable", "known_error", overlaps=False),
        ],
        gaps=[
            gap("acceptable", "known_error", separated=True),
            gap("acceptable", "variant", separated=False),
        ],
    )

    assert [
        (item.overlap.left_label, item.overlap.right_label)
        for item in relationships
    ] == [
        ("acceptable", "known_error"),
        ("acceptable", "variant"),
    ]


def test_rejects_missing_gap_counterpart():
    with pytest.raises(ValueError, match="same versioned label pairs"):
        relate_phonetic_calibration_human_label_score_iqr_evidence(
            overlaps=[overlap("acceptable", "variant", overlaps=True)],
            gaps=[],
        )


def test_rejects_missing_overlap_counterpart():
    with pytest.raises(ValueError, match="same versioned label pairs"):
        relate_phonetic_calibration_human_label_score_iqr_evidence(
            overlaps=[],
            gaps=[gap("acceptable", "variant", separated=False)],
        )


def test_rejects_duplicate_overlap_key():
    duplicated = overlap("acceptable", "variant", overlaps=True)

    with pytest.raises(ValueError, match="Duplicate overlap evidence"):
        relate_phonetic_calibration_human_label_score_iqr_evidence(
            overlaps=[duplicated, duplicated],
            gaps=[gap("acceptable", "variant", separated=False)],
        )


def test_rejects_duplicate_gap_key():
    duplicated = gap("acceptable", "variant", separated=False)

    with pytest.raises(ValueError, match="Duplicate gap evidence"):
        relate_phonetic_calibration_human_label_score_iqr_evidence(
            overlaps=[overlap("acceptable", "variant", overlaps=True)],
            gaps=[duplicated, duplicated],
        )
