from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationMeasurement,
)


def build_measurement(sample_id: str = "human-001") -> PhoneticCalibrationMeasurement:
    return PhoneticCalibrationMeasurement(
        sample_id=sample_id,
        score=0.72,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        analyzed_at=datetime.now(UTC),
    )


def build_agreement(sample_id: str = "human-001") -> PhoneticCalibrationHumanAgreement:
    return PhoneticCalibrationHumanAgreement(
        sample_id=sample_id,
        rubric_version="phonetic-rubric/1.0",
        label_count=2,
        labeler_count=2,
        label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
        unanimous=False,
    )


def test_accepts_matching_measurement_and_human_agreement():
    relationship = PhoneticCalibrationHumanRelationship(
        measurement=build_measurement(),
        human_agreement=build_agreement(),
    )

    assert relationship.measurement.score == 0.72
    assert relationship.human_agreement.rubric_version == "phonetic-rubric/1.0"


def test_rejects_mismatched_sample_identity():
    with pytest.raises(ValidationError, match="share sample_id"):
        PhoneticCalibrationHumanRelationship(
            measurement=build_measurement("human-001"),
            human_agreement=build_agreement("human-002"),
        )


def test_preserves_independent_human_labels():
    labels = [
        PhoneticCalibrationHumanLabel(
            sample_id="human-001",
            labeler_id="labeler-001",
            rubric_version="phonetic-rubric/1.0",
            label="acceptable",
        ),
        PhoneticCalibrationHumanLabel(
            sample_id="human-001",
            labeler_id="labeler-002",
            rubric_version="phonetic-rubric/1.0",
            label="variant",
        ),
    ]

    relationship = PhoneticCalibrationHumanRelationship(
        measurement=build_measurement(),
        human_labels=labels,
        human_agreement=build_agreement(),
    )

    assert [label.labeler_id for label in relationship.human_labels] == [
        "labeler-001",
        "labeler-002",
    ]


def test_rejects_human_label_from_other_rubric():
    label = PhoneticCalibrationHumanLabel(
        sample_id="human-001",
        labeler_id="labeler-001",
        rubric_version="phonetic-rubric/2.0",
        label="acceptable",
    )

    with pytest.raises(ValidationError, match="share sample_id and rubric_version"):
        PhoneticCalibrationHumanRelationship(
            measurement=build_measurement(),
            human_labels=[label],
            human_agreement=build_agreement(),
        )
