from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreIqrGap,
    PhoneticCalibrationHumanLabelScoreIqrRelationship,
    PhoneticCalibrationHumanLabelScoreOverlap,
)


def _evidence_key(item) -> tuple[str, str, str, str, str]:
    return (
        item.analyzer_id,
        item.analyzer_version,
        item.rubric_version,
        item.left_label,
        item.right_label,
    )


def relate_phonetic_calibration_human_label_score_iqr_evidence(
    overlaps: list[PhoneticCalibrationHumanLabelScoreOverlap],
    gaps: list[PhoneticCalibrationHumanLabelScoreIqrGap],
) -> list[PhoneticCalibrationHumanLabelScoreIqrRelationship]:
    """Relate descriptive overlap and gap evidence for the same IQR pairs.

    Relaciona evidencia descriptiva de solapamiento y distancia para los mismos pares IQR.
    """
    overlap_by_key: dict[
        tuple[str, str, str, str, str],
        PhoneticCalibrationHumanLabelScoreOverlap,
    ] = {}

    for overlap in overlaps:
        key = _evidence_key(overlap)
        if key in overlap_by_key:
            raise ValueError("Duplicate overlap evidence for versioned label pair")
        overlap_by_key[key] = overlap

    gap_by_key: dict[
        tuple[str, str, str, str, str],
        PhoneticCalibrationHumanLabelScoreIqrGap,
    ] = {}

    for gap in gaps:
        key = _evidence_key(gap)
        if key in gap_by_key:
            raise ValueError("Duplicate gap evidence for versioned label pair")
        gap_by_key[key] = gap

    if set(overlap_by_key) != set(gap_by_key):
        raise ValueError(
            "IQR overlap and gap evidence must describe the same versioned label pairs"
        )

    return [
        PhoneticCalibrationHumanLabelScoreIqrRelationship(
            overlap=overlap_by_key[key],
            gap=gap_by_key[key],
        )
        for key in sorted(overlap_by_key)
    ]
