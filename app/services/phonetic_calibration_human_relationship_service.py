from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationMeasurement,
)


def relate_phonetic_calibration_measurements_to_human_agreements(
    measurements: list[PhoneticCalibrationMeasurement],
    agreements: list[PhoneticCalibrationHumanAgreement],
    labels: list[PhoneticCalibrationHumanLabel] | None = None,
) -> list[PhoneticCalibrationHumanRelationship]:
    """Relate technical measurements to descriptive human agreements.

    Relaciona mediciones técnicas con acuerdos humanos descriptivos.
    """
    labels = labels or []

    return [
        PhoneticCalibrationHumanRelationship(
            measurement=measurement,
            human_labels=[
                label
                for label in labels
                if label.sample_id == agreement.sample_id
                and label.rubric_version == agreement.rubric_version
            ],
            human_agreement=agreement,
        )
        for agreement in agreements
        for measurement in measurements
        if measurement.sample_id == agreement.sample_id
    ]
