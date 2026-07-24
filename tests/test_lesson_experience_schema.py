import pytest
from pydantic import ValidationError

from app.schemas.content import Lesson


def build_experience_payload() -> dict:
    return {
        "contract_version": "2.0",
        "mission": {
            "id": "a1-u1-l1-m1",
            "title": "Introduce yourself",
            "situation": "Meet a new colleague.",
            "observable_outcome": "State your name and origin.",
            "success_criteria": [
                "The learner gives a name.",
                "The learner gives an origin.",
            ],
        },
        "skill_ids": ["a1_introduce_yourself"],
        "stages": [
            {
                "id": "a1-u1-l1-s1",
                "type": "encounter",
                "instruction": "Listen to the opening exchange.",
                "activity_ids": ["a1-u1-l1-c1"],
                "mode": "required",
                "completion_condition": "any_activity_completed",
            },
            {
                "id": "a1-u1-l1-s2",
                "type": "evidence",
                "instruction": "Complete the applied check.",
                "activity_ids": ["a1-u1-l1-q1"],
                "mode": "required",
                "completion_condition": "evidence_recorded",
            },
        ],
        "language_support": [
            {
                "id": "a1-u1-l1-ls1",
                "type": "reference_expression",
                "en": "Hello, I am John.",
                "es": "Hola, soy John.",
                "stage_ids": ["a1-u1-l1-s1"],
            },
        ],
        "evidence_definitions": [
            {
                "id": "a1-u1-l1-ev1",
                "skill_ids": ["a1_introduce_yourself"],
                "stage_id": "a1-u1-l1-s2",
                "activity_id": "a1-u1-l1-q1",
                "evidence_type": "exercise_result",
                "measurement_mode": "binary",
                "required": True,
            },
        ],
        "completion_policy": {
            "practiced_stage_ids": ["a1-u1-l1-s1"],
            "required_evidence_ids": ["a1-u1-l1-ev1"],
            "reinforcement_on_failure": True,
            "allow_retry": True,
        },
    }


def test_legacy_lesson_remains_compatible_without_experience():
    lesson = Lesson.model_validate({
        "id": "a1-u1-l1",
        "title": "Legacy lesson",
    })

    assert lesson.experience is None
    assert lesson.examples == []
    assert lesson.conversations == []


def test_lesson_parses_professional_experience_v2():
    lesson = Lesson.model_validate({
        "id": "a1-u1-l1",
        "title": "Introduce yourself",
        "experience": build_experience_payload(),
    })

    assert lesson.experience is not None
    assert lesson.experience.contract_version == "2.0"
    assert lesson.experience.mission.id == "a1-u1-l1-m1"
    assert lesson.experience.skill_ids == ["a1_introduce_yourself"]
    assert len(lesson.experience.stages) == 2


def test_lesson_rejects_unsupported_experience_version():
    payload = build_experience_payload()
    payload["contract_version"] = "3.0"

    with pytest.raises(ValidationError):
        Lesson.model_validate({
            "id": "a1-u1-l1",
            "title": "Unsupported version",
            "experience": payload,
        })


def test_score_evidence_requires_success_threshold():
    payload = build_experience_payload()
    evidence = payload["evidence_definitions"][0]
    evidence["measurement_mode"] = "score"

    with pytest.raises(
        ValidationError,
        match="Score evidence requires success_threshold",
    ):
        Lesson.model_validate({
            "id": "a1-u1-l1",
            "title": "Missing threshold",
            "experience": payload,
        })


def test_non_score_evidence_rejects_success_threshold():
    payload = build_experience_payload()
    evidence = payload["evidence_definitions"][0]
    evidence["success_threshold"] = 0.70

    with pytest.raises(
        ValidationError,
        match="Only score evidence can define success_threshold",
    ):
        Lesson.model_validate({
            "id": "a1-u1-l1",
            "title": "Unexpected threshold",
            "experience": payload,
        })
