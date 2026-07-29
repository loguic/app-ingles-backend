from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreOverlap,
    PhoneticCalibrationModelHumanSummary,
)


def build_phonetic_calibration_descriptive_reports(
    summaries: list[PhoneticCalibrationModelHumanSummary],
    distributions: list[PhoneticCalibrationHumanLabelScoreDistribution],
    overlaps: list[PhoneticCalibrationHumanLabelScoreOverlap],
) -> list[PhoneticCalibrationDescriptiveReport]:
    """Consolidate descriptive calibration evidence by versioned context.

    Consolida evidencia descriptiva de calibración por contexto versionado.
    """
    reports: list[PhoneticCalibrationDescriptiveReport] = []

    for summary in summaries:
        context = (
            summary.analyzer_id,
            summary.analyzer_version,
            summary.rubric_version,
        )

        matching_distributions = [
            distribution
            for distribution in distributions
            if (
                distribution.analyzer_id,
                distribution.analyzer_version,
                distribution.rubric_version,
            )
            == context
        ]
        matching_overlaps = [
            overlap
            for overlap in overlaps
            if (
                overlap.analyzer_id,
                overlap.analyzer_version,
                overlap.rubric_version,
            )
            == context
        ]

        reports.append(
            PhoneticCalibrationDescriptiveReport(
                analyzer_id=summary.analyzer_id,
                analyzer_version=summary.analyzer_version,
                rubric_version=summary.rubric_version,
                summary=summary,
                score_distributions=sorted(
                    matching_distributions,
                    key=lambda item: item.label,
                ),
                overlaps=sorted(
                    matching_overlaps,
                    key=lambda item: (item.left_label, item.right_label),
                ),
            )
        )

    return sorted(
        reports,
        key=lambda item: (
            item.analyzer_id,
            item.analyzer_version,
            item.rubric_version,
        ),
    )
