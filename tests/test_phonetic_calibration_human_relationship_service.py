from datetime import UTC, datetime

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationMeasurement,
)
from app.services.phonetic_calibration_human_relationship_service import (
    relate_phonetic_calibration_measurements_to_human_agreements,
)


def measurement(sample_id: str) -> PhoneticCalibrationMeasurement:
    return PhoneticCalibrationMeasurement(
        sample_id=sample_id,
        score=0.72,
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version="wavlm-gop-runner/1.0",
        analyzed_at=datetime.now(UTC),
    )


def agreement(sample_id: str, rubric_version: str) -> PhoneticCalibrationHumanAgreement:
    return PhoneticCalibrationHumanAgreement(
        sample_id=sample_id,
        rubric_version=rubric_version,
        label_count=2,
        labeler_count=2,
        label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
        unanimous=False,
    )


def test_relates_measurement_to_matching_human_agreement():
    relationships = relate_phonetic_calibration_measurements_to_human_agreements(
        [measurement("human-001")],
        [agreement("human-001", "phonetic-rubric/1.0")],
    )

    assert len(relationships) == 1
    assert relationships[0].measurement.sample_id == "human-001"
    assert relationships[0].human_agreement.rubric_version == "phonetic-rubric/1.0"


def test_preserves_separate_rubric_versions_for_same_sample():
    relationships = relate_phonetic_calibration_measurements_to_human_agreements(
        [measurement("human-001")],
        [
            agreement("human-001", "phonetic-rubric/1.0"),
            agreement("human-001", "phonetic-rubric/2.0"),
        ],
    )

    assert [item.human_agreement.rubric_version for item in relationships] == [
        "phonetic-rubric/1.0",
        "phonetic-rubric/2.0",
    ]


def test_ignores_agreement_without_matching_measurement():
    relationships = relate_phonetic_calibration_measurements_to_human_agreements(
        [measurement("human-001")],
        [agreement("human-002", "phonetic-rubric/1.0")],
    )

    assert relationships == []


def test_preserves_multiple_measurements_for_same_sample():
    first = measurement("human-001")
    second = first.model_copy(update={"analyzer_version": "wavlm-gop-runner/2.0"})

    relationships = relate_phonetic_calibration_measurements_to_human_agreements(
        [first, second],
        [agreement("human-001", "phonetic-rubric/1.0")],
    )

    assert [item.measurement.analyzer_version for item in relationships] == [
        "wavlm-gop-runner/1.0",
        "wavlm-gop-runner/2.0",
    ]


def test_preserves_matching_independent_human_labels():
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
            rubric_version="phonetic-rubric/2.0",
            label="known_error",
        ),
    ]

    relationships = relate_phonetic_calibration_measurements_to_human_agreements(
        [measurement("human-001")],
        [agreement("human-001", "phonetic-rubric/1.0")],
        labels,
    )

    assert [(item.labeler_id, item.label) for item in relationships[0].human_labels] == [
        ("labeler-001", "acceptable"),
    ]
