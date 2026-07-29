import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
)
from app.services.phonetic_calibration_human_label_score_overlap_service import (
    describe_phonetic_calibration_human_label_score_overlaps,
)


def distribution(
    label: str,
    q25: float,
    q75: float,
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationHumanLabelScoreDistribution:
    return PhoneticCalibrationHumanLabelScoreDistribution(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        label=label,
        observation_count=4,
        sample_count=4,
        score_q25=q25,
        score_median=(q25 + q75) / 2,
        score_q75=q75,
    )


def test_describes_iqr_overlap_between_human_labels():
    overlaps = describe_phonetic_calibration_human_label_score_overlaps([
        distribution("acceptable", 0.50, 0.80),
        distribution("variant", 0.65, 0.90),
    ])

    assert len(overlaps) == 1
    overlap = overlaps[0]
    assert {overlap.left_label, overlap.right_label} == {"acceptable", "variant"}
    assert overlap.overlap_lower == pytest.approx(0.65)
    assert overlap.overlap_upper == pytest.approx(0.80)
    assert overlap.overlap_width == pytest.approx(0.15)
    assert overlap.overlaps is True


def test_describes_non_overlapping_human_labels():
    overlaps = describe_phonetic_calibration_human_label_score_overlaps([
        distribution("known_error", 0.10, 0.30),
        distribution("acceptable", 0.60, 0.90),
    ])

    overlap = overlaps[0]
    assert overlap.overlap_lower is None
    assert overlap.overlap_upper is None
    assert overlap.overlap_width == 0.0
    assert overlap.overlaps is False


def test_does_not_compare_incompatible_versioned_contexts():
    overlaps = describe_phonetic_calibration_human_label_score_overlaps([
        distribution("acceptable", 0.50, 0.80),
        distribution(
            "variant",
            0.60,
            0.90,
            analyzer_version="wavlm-gop-runner/2.0",
        ),
        distribution(
            "known_error",
            0.20,
            0.40,
            rubric_version="phonetic-rubric/2.0",
        ),
    ])

    assert overlaps == []
