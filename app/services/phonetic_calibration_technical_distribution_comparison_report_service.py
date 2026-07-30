from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationTechnicalComparisonContext,
    PhoneticCalibrationTechnicalDistributionComparisonReport,
)
from app.services.phonetic_calibration_human_label_score_distribution_comparison_service import (
    compare_phonetic_calibration_human_label_score_distributions,
)


def build_phonetic_calibration_technical_distribution_comparison_report(
    context: PhoneticCalibrationTechnicalComparisonContext,
    left_distributions: list[PhoneticCalibrationHumanLabelScoreDistribution],
    right_distributions: list[PhoneticCalibrationHumanLabelScoreDistribution],
) -> PhoneticCalibrationTechnicalDistributionComparisonReport:
    """Build a consolidated robust distribution comparison report.

    Construye un informe consolidado de comparación robusta de distribuciones.
    """
    left_by_label = {item.label: item for item in left_distributions}
    if len(left_by_label) != len(left_distributions):
        raise ValueError("Left score distributions require unique human labels")

    right_by_label = {item.label: item for item in right_distributions}
    if len(right_by_label) != len(right_distributions):
        raise ValueError("Right score distributions require unique human labels")

    if set(left_by_label) != set(right_by_label):
        raise ValueError(
            "Left and right score distributions must use the same human labels"
        )

    comparisons = [
        compare_phonetic_calibration_human_label_score_distributions(
            context,
            left_by_label[label],
            right_by_label[label],
        )
        for label in sorted(left_by_label)
    ]

    return PhoneticCalibrationTechnicalDistributionComparisonReport(
        context=context,
        comparisons=comparisons,
    )
