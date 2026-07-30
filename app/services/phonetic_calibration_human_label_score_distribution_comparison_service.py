from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalComparisonContext,
)


def compare_phonetic_calibration_human_label_score_distributions(
    context: PhoneticCalibrationTechnicalComparisonContext,
    left: PhoneticCalibrationHumanLabelScoreDistribution,
    right: PhoneticCalibrationHumanLabelScoreDistribution,
) -> PhoneticCalibrationHumanLabelScoreDistributionComparison:
    """Compare robust score distributions inside a validated technical context.

    Compara distribuciones robustas de scores dentro de un contexto técnico validado.
    """
    artifact_comparison = context.comparable_artifact_context.artifact_comparison

    left_expected = (
        artifact_comparison.left_analyzer_id,
        artifact_comparison.left_analyzer_version,
        artifact_comparison.rubric_version,
    )
    left_actual = (
        left.analyzer_id,
        left.analyzer_version,
        left.rubric_version,
    )
    if left_actual != left_expected:
        raise ValueError(
            "Left score distribution must match left technical comparison context"
        )

    right_expected = (
        artifact_comparison.right_analyzer_id,
        artifact_comparison.right_analyzer_version,
        artifact_comparison.rubric_version,
    )
    right_actual = (
        right.analyzer_id,
        right.analyzer_version,
        right.rubric_version,
    )
    if right_actual != right_expected:
        raise ValueError(
            "Right score distribution must match right technical comparison context"
        )

    if left.label != right.label:
        raise ValueError("Score distributions must use the same human label")

    return PhoneticCalibrationHumanLabelScoreDistributionComparison(
        rubric_version=artifact_comparison.rubric_version,
        label=left.label,
        left_analyzer_id=left.analyzer_id,
        left_analyzer_version=left.analyzer_version,
        right_analyzer_id=right.analyzer_id,
        right_analyzer_version=right.analyzer_version,
        left_sample_count=left.sample_count,
        right_sample_count=right.sample_count,
        left_score_q25=left.score_q25,
        right_score_q25=right.score_q25,
        score_q25_difference=right.score_q25 - left.score_q25,
        left_score_median=left.score_median,
        right_score_median=right.score_median,
        score_median_difference=right.score_median - left.score_median,
        left_score_q75=left.score_q75,
        right_score_q75=right.score_q75,
        score_q75_difference=right.score_q75 - left.score_q75,
    )
