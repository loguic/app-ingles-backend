from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistributionComparison,
    PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    PhoneticCalibrationTechnicalDistributionComparisonDeltaReport,
)
from app.services.phonetic_calibration_technical_distribution_comparison_delta_service import (
    compare_phonetic_calibration_technical_distribution_comparison_deltas,
)


def build_phonetic_calibration_technical_distribution_comparison_delta_report(
    artifact_comparison: PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison,
    left_comparisons: list[PhoneticCalibrationHumanLabelScoreDistributionComparison],
    right_comparisons: list[PhoneticCalibrationHumanLabelScoreDistributionComparison],
) -> PhoneticCalibrationTechnicalDistributionComparisonDeltaReport:
    """Build a consolidated descriptive delta report by human label.

    Construye un informe consolidado de deltas descriptivos por etiqueta humana.
    """
    left_by_label = {item.label: item for item in left_comparisons}
    if len(left_by_label) != len(left_comparisons):
        raise ValueError(
            "Left distribution comparisons require unique human labels"
        )

    right_by_label = {item.label: item for item in right_comparisons}
    if len(right_by_label) != len(right_comparisons):
        raise ValueError(
            "Right distribution comparisons require unique human labels"
        )

    if set(left_by_label) != set(right_by_label):
        raise ValueError(
            "Left and right distribution comparisons must use the same human labels"
        )

    deltas = [
        compare_phonetic_calibration_technical_distribution_comparison_deltas(
            artifact_comparison,
            left_by_label[label],
            right_by_label[label],
        )
        for label in sorted(left_by_label)
    ]

    return PhoneticCalibrationTechnicalDistributionComparisonDeltaReport(
        artifact_comparison=artifact_comparison,
        deltas=deltas,
    )
