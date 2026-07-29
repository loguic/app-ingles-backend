from datetime import UTC, datetime

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanRelationship,
    PhoneticCalibrationMeasurement,
)
from app.services.phonetic_calibration_model_human_observation_service import (
    describe_phonetic_calibration_model_human_observations,
)


def test_describes_model_human_relationship_without_deriving_truth():
    relationship = PhoneticCalibrationHumanRelationship(
        measurement=PhoneticCalibrationMeasurement(
            sample_id="human-001",
            score=0.72,
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version="wavlm-gop-runner/1.0",
            analyzed_at=datetime.now(UTC),
        ),
        human_agreement=PhoneticCalibrationHumanAgreement(
            sample_id="human-001",
            rubric_version="phonetic-rubric/1.0",
            label_count=2,
            labeler_count=2,
            label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
            unanimous=False,
        ),
    )

    observations = describe_phonetic_calibration_model_human_observations(
        [relationship]
    )

    assert len(observations) == 1
    observation = observations[0]
    assert observation.sample_id == "human-001"
    assert observation.score == 0.72
    assert observation.analyzer_version == "wavlm-gop-runner/1.0"
    assert observation.rubric_version == "phonetic-rubric/1.0"
    assert observation.label_counts == {
        "acceptable": 1,
        "variant": 1,
        "known_error": 0,
    }
    assert observation.unanimous is False
