from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreComparison,
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationTechnicalComparisonContext,
)


def compare_phonetic_calibration_human_label_scores(
    context: PhoneticCalibrationTechnicalComparisonContext,
    left: PhoneticCalibrationHumanLabelScoreDistribution,
    right: PhoneticCalibrationHumanLabelScoreDistribution,
) -> PhoneticCalibrationHumanLabelScoreComparison:
    """Compare median scores for one human label in a validated technical context.

    Compara medianas para una etiqueta humana dentro de un contexto técnico validado.
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

    return PhoneticCalibrationHumanLabelScoreComparison(
        rubric_version=artifact_comparison.rubric_version,
        label=left.label,
        left_analyzer_id=left.analyzer_id,
        left_analyzer_version=left.analyzer_version,
        right_analyzer_id=right.analyzer_id,
        right_analyzer_version=right.analyzer_version,
        left_observation_count=left.observation_count,
        right_observation_count=right.observation_count,
        left_median=left.score_median,
        right_median=right.score_median,
        median_difference=right.score_median - left.score_median,
    )
