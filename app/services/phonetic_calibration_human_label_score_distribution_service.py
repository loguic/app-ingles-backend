from collections import defaultdict

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanRelationship,
)


def _percentile(sorted_scores: list[float], fraction: float) -> float:
    """Calculate one deterministic linearly interpolated percentile.

    Calcula un percentil determinista mediante interpolación lineal.
    """
    if len(sorted_scores) == 1:
        return sorted_scores[0]

    position = fraction * (len(sorted_scores) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_scores) - 1)
    weight = position - lower_index

    return (
        sorted_scores[lower_index] * (1.0 - weight)
        + sorted_scores[upper_index] * weight
    )


def describe_phonetic_calibration_score_distributions_by_human_label(
    relationships: list[PhoneticCalibrationHumanRelationship],
) -> list[PhoneticCalibrationHumanLabelScoreDistribution]:
    """Describe robust score distributions beside independent human labels.

    Describe distribuciones robustas de scores junto a etiquetas humanas independientes.
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

    distributions: list[PhoneticCalibrationHumanLabelScoreDistribution] = []

    for (analyzer_id, analyzer_version, rubric_version, label), group in sorted(
        grouped.items()
    ):
        scores = sorted(score for _, score in group)

        distributions.append(
            PhoneticCalibrationHumanLabelScoreDistribution(
                analyzer_id=analyzer_id,
                analyzer_version=analyzer_version,
                rubric_version=rubric_version,
                label=label,
                observation_count=len(group),
                sample_count=len({sample_id for sample_id, _ in group}),
                score_q25=_percentile(scores, 0.25),
                score_median=_percentile(scores, 0.50),
                score_q75=_percentile(scores, 0.75),
            )
        )

    return distributions
