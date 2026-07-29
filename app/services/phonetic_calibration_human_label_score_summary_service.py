from collections import defaultdict

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreSummary,
    PhoneticCalibrationHumanRelationship,
)


def summarize_phonetic_calibration_scores_by_human_label(
    relationships: list[PhoneticCalibrationHumanRelationship],
) -> list[PhoneticCalibrationHumanLabelScoreSummary]:
    """Summarize technical scores beside independent human labels.

    Resume scores técnicos junto a etiquetas humanas independientes.
    """
    grouped: dict[tuple[str, str, str, str], list[tuple[str, float]]] = defaultdict(list)

    for relationship in relationships:
        measurement = relationship.measurement
        for human_label in relationship.human_labels:
            grouped[
                (
                    measurement.analyzer_id,
                    measurement.analyzer_version,
                    human_label.rubric_version,
                    human_label.label,
                )
            ].append((measurement.sample_id, measurement.score))

    summaries: list[PhoneticCalibrationHumanLabelScoreSummary] = []

    for (analyzer_id, analyzer_version, rubric_version, label), group in sorted(
        grouped.items()
    ):
        scores = [score for _, score in group]

        summaries.append(
            PhoneticCalibrationHumanLabelScoreSummary(
                analyzer_id=analyzer_id,
                analyzer_version=analyzer_version,
                rubric_version=rubric_version,
                label=label,
                observation_count=len(group),
                sample_count=len({sample_id for sample_id, _ in group}),
                score_min=min(scores),
                score_max=max(scores),
                score_mean=sum(scores) / len(scores),
            )
        )

    return summaries
