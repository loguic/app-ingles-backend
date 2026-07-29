from collections import defaultdict
from itertools import combinations

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreOverlap,
)


def describe_phonetic_calibration_human_label_score_overlaps(
    distributions: list[PhoneticCalibrationHumanLabelScoreDistribution],
) -> list[PhoneticCalibrationHumanLabelScoreOverlap]:
    """Describe IQR overlap between version-compatible human-label distributions.

    Describe el solapamiento IQR entre distribuciones humanas versionadas compatibles.
    """
    grouped: dict[
        tuple[str, str, str],
        list[PhoneticCalibrationHumanLabelScoreDistribution],
    ] = defaultdict(list)

    for distribution in distributions:
        grouped[
            (
                distribution.analyzer_id,
                distribution.analyzer_version,
                distribution.rubric_version,
            )
        ].append(distribution)

    overlaps: list[PhoneticCalibrationHumanLabelScoreOverlap] = []

    for (analyzer_id, analyzer_version, rubric_version), group in sorted(
        grouped.items()
    ):
        ordered = sorted(group, key=lambda item: item.label)

        for left, right in combinations(ordered, 2):
            lower = max(left.score_q25, right.score_q25)
            upper = min(left.score_q75, right.score_q75)

            if lower <= upper:
                overlaps.append(
                    PhoneticCalibrationHumanLabelScoreOverlap(
                        analyzer_id=analyzer_id,
                        analyzer_version=analyzer_version,
                        rubric_version=rubric_version,
                        left_label=left.label,
                        right_label=right.label,
                        overlap_lower=lower,
                        overlap_upper=upper,
                        overlap_width=upper - lower,
                        overlaps=True,
                    )
                )
            else:
                overlaps.append(
                    PhoneticCalibrationHumanLabelScoreOverlap(
                        analyzer_id=analyzer_id,
                        analyzer_version=analyzer_version,
                        rubric_version=rubric_version,
                        left_label=left.label,
                        right_label=right.label,
                        overlap_lower=None,
                        overlap_upper=None,
                        overlap_width=0.0,
                        overlaps=False,
                    )
                )

    return overlaps
