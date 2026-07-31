from collections import defaultdict
from itertools import combinations

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreIqrGap,
)


def describe_phonetic_calibration_human_label_score_iqr_gaps(
    distributions: list[PhoneticCalibrationHumanLabelScoreDistribution],
) -> list[PhoneticCalibrationHumanLabelScoreIqrGap]:
    """Describe IQR gaps between version-compatible human-label distributions.

    Describe distancias entre IQR de distribuciones humanas versionadas compatibles.
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

    gaps: list[PhoneticCalibrationHumanLabelScoreIqrGap] = []

    for (analyzer_id, analyzer_version, rubric_version), group in sorted(
        grouped.items()
    ):
        ordered = sorted(group, key=lambda item: item.label)

        for left, right in combinations(ordered, 2):
            if left.score_q75 < right.score_q25:
                gap_width = right.score_q25 - left.score_q75
            elif right.score_q75 < left.score_q25:
                gap_width = left.score_q25 - right.score_q75
            else:
                gap_width = 0.0

            gaps.append(
                PhoneticCalibrationHumanLabelScoreIqrGap(
                    analyzer_id=analyzer_id,
                    analyzer_version=analyzer_version,
                    rubric_version=rubric_version,
                    left_label=left.label,
                    right_label=right.label,
                    gap_width=gap_width,
                    separated=gap_width > 0.0,
                )
            )

    return gaps
