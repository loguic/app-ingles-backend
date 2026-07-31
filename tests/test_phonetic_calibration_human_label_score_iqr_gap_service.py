import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
)
from app.services.phonetic_calibration_human_label_score_iqr_gap_service import (
    describe_phonetic_calibration_human_label_score_iqr_gaps,
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


def test_describes_positive_gap_between_separated_iqrs():
    gaps = describe_phonetic_calibration_human_label_score_iqr_gaps([
        distribution("known_error", 0.10, 0.30),
        distribution("acceptable", 0.60, 0.90),
    ])

    assert len(gaps) == 1
    gap = gaps[0]
    assert {gap.left_label, gap.right_label} == {
        "acceptable",
        "known_error",
    }
    assert gap.gap_width == pytest.approx(0.30)
    assert gap.separated is True


def test_describes_zero_gap_when_iqrs_overlap():
    gaps = describe_phonetic_calibration_human_label_score_iqr_gaps([
        distribution("acceptable", 0.50, 0.80),
        distribution("variant", 0.65, 0.90),
    ])

    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.gap_width == 0.0
    assert gap.separated is False


def test_does_not_compare_incompatible_versioned_contexts():
    gaps = describe_phonetic_calibration_human_label_score_iqr_gaps([
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

    assert gaps == []
