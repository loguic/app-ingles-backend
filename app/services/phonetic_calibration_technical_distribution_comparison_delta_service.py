from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDelta,
)


def compare_phonetic_calibration_technical_distribution_comparison_deltas(
    artifact_comparison: PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    left: PhoneticCalibrationHumanLabelScoreDistributionComparison,
    right: PhoneticCalibrationHumanLabelScoreDistributionComparison,
) -> PhoneticCalibrationTechnicalDistributionComparisonDelta:
    """Describe changes between two robust technical distribution comparisons.

    Describe cambios entre dos comparaciones técnicas robustas de distribución.
    """
    left_expected = (
        artifact_comparison.left_left_analyzer_id,
        artifact_comparison.left_left_analyzer_version,
        artifact_comparison.left_right_analyzer_id,
        artifact_comparison.left_right_analyzer_version,
        artifact_comparison.rubric_version,
    )
    left_actual = (
        left.left_analyzer_id,
        left.left_analyzer_version,
        left.right_analyzer_id,
        left.right_analyzer_version,
        left.rubric_version,
    )
    if left_actual != left_expected:
        raise ValueError(
            "Left distribution comparison must match left technical artifact context"
        )

    right_expected = (
        artifact_comparison.right_left_analyzer_id,
        artifact_comparison.right_left_analyzer_version,
        artifact_comparison.right_right_analyzer_id,
        artifact_comparison.right_right_analyzer_version,
        artifact_comparison.rubric_version,
    )
    right_actual = (
        right.left_analyzer_id,
        right.left_analyzer_version,
        right.right_analyzer_id,
        right.right_analyzer_version,
        right.rubric_version,
    )
    if right_actual != right_expected:
        raise ValueError(
            "Right distribution comparison must match right technical artifact context"
        )

    if left.label != right.label:
        raise ValueError(
            "Distribution comparisons must use the same human label"
        )

    return PhoneticCalibrationTechnicalDistributionComparisonDelta(
        rubric_version=artifact_comparison.rubric_version,
        label=left.label,
        left_score_q25_difference=left.score_q25_difference,
        right_score_q25_difference=right.score_q25_difference,
        score_q25_difference_delta=(
            right.score_q25_difference - left.score_q25_difference
        ),
        left_score_median_difference=left.score_median_difference,
        right_score_median_difference=right.score_median_difference,
        score_median_difference_delta=(
            right.score_median_difference - left.score_median_difference
        ),
        left_score_q75_difference=left.score_q75_difference,
        right_score_q75_difference=right.score_q75_difference,
        score_q75_difference_delta=(
            right.score_q75_difference - left.score_q75_difference
        ),
    )
