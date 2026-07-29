from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationModelHumanObservation,
)


def describe_phonetic_calibration_model_human_observations(
    relationships: list[PhoneticCalibrationHumanRelationship],
) -> list[PhoneticCalibrationModelHumanObservation]:
    """Describe technical measurements beside observed human agreement.

    Describe mediciones técnicas junto al acuerdo humano observado.
    """
    return [
        PhoneticCalibrationModelHumanObservation(
            sample_id=item.measurement.sample_id,
            analyzer_id=item.measurement.analyzer_id,
            analyzer_version=item.measurement.analyzer_version,
            rubric_version=item.human_agreement.rubric_version,
            score=item.measurement.score,
            label_count=item.human_agreement.label_count,
            labeler_count=item.human_agreement.labeler_count,
            label_counts=item.human_agreement.label_counts,
            unanimous=item.human_agreement.unanimous,
        )
        for item in relationships
    ]
