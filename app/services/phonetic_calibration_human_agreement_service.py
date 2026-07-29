from collections import defaultdict

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
)


def summarize_phonetic_calibration_human_agreements(
    labels: list[PhoneticCalibrationHumanLabel],
) -> list[PhoneticCalibrationHumanAgreement]:
    """Summarize observed human agreement by sample and rubric.

    Resume el acuerdo humano observado por muestra y rúbrica.
    """
    grouped: dict[tuple[str, str], list[PhoneticCalibrationHumanLabel]] = defaultdict(list)
    for label in labels:
        grouped[(label.sample_id, label.rubric_version)].append(label)

    agreements: list[PhoneticCalibrationHumanAgreement] = []
    for (sample_id, rubric_version), group in sorted(grouped.items()):
        counts = {"acceptable": 0, "variant": 0, "known_error": 0}
        for label in group:
            counts[label.label] += 1

        agreements.append(
            PhoneticCalibrationHumanAgreement(
                sample_id=sample_id,
                rubric_version=rubric_version,
                label_count=len(group),
                labeler_count=len({label.labeler_id for label in group}),
                label_counts=counts,
                unanimous=sum(count > 0 for count in counts.values()) == 1,
            )
        )

    return agreements
