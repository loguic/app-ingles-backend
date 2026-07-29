from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationSample,
)


def validate_phonetic_calibration_human_labels(
    samples: list[PhoneticCalibrationSample],
    labels: list[PhoneticCalibrationHumanLabel],
) -> None:
    """Validate human-label references without deriving consensus.

    Valida referencias de etiquetas humanas sin derivar consenso.
    """
    sample_ids = {sample.sample_id for sample in samples}
    seen_labels: set[tuple[str, str, str]] = set()

    for label in labels:
        if label.sample_id not in sample_ids:
            raise ValueError("Human label references unknown calibration sample")

        identity = (label.sample_id, label.labeler_id, label.rubric_version)
        if identity in seen_labels:
            raise ValueError("Human calibration label must be unique per sample, labeler and rubric")
        seen_labels.add(identity)
