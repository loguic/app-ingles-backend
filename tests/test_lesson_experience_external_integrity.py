import pytest
from pydantic import ValidationError

from app.schemas.content import Lesson
from tests.test_lesson_experience_schema import build_experience_payload


def build_lesson_payload() -> dict:
    experience = build_experience_payload()
    experience["skill_ids"] = [
        "a1_greetings_basic",
        "a1_vocabulary_greetings",
    ]
    experience["evidence_definitions"][0]["skill_ids"] = [
        "a1_greetings_basic"
    ]

    return {
        "id": "a1-u1-l1",
        "title": "Greeting mission",
        "experience": experience,
        "conversations": [
            {
                "id": "a1-u1-l1-c1",
                "title": "Greeting conversation",
                "mode": "guided",
                "turns": [
                    {
                        "id": "turn-1",
                        "speaker": "partner",
                        "en": "Hello.",
                    }
                ],
            }
        ],
        "exercises": [
            {
                "id": "a1-u1-l1-q1",
                "type": "mcq",
                "prompt": "Choose the best greeting:",
                "options": [
                    "Goodbye",
                    "Hello",
                    "Thanks",
                    "Sorry",
                ],
                "answer_index": 1,
                "skill_ids": [
                    "a1_greetings_basic",
                    "a1_vocabulary_greetings",
                ],
            }
        ],
    }


def assert_invalid(payload: dict, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Lesson.model_validate(payload)


def test_accepts_consistent_external_references():
    lesson = Lesson.model_validate(build_lesson_payload())

    assert lesson.experience is not None
    assert lesson.conversations[0].id == "a1-u1-l1-c1"
    assert lesson.exercises[0].id == "a1-u1-l1-q1"


def test_rejects_duplicate_conversation_ids():
    payload = build_lesson_payload()
    payload["conversations"].append(
        dict(payload["conversations"][0])
    )

    assert_invalid(payload, "Lesson conversation IDs must be unique")


def test_rejects_duplicate_exercise_ids():
    payload = build_lesson_payload()
    payload["exercises"].append(
        dict(payload["exercises"][0])
    )

    assert_invalid(payload, "Lesson exercise IDs must be unique")


def test_rejects_collision_between_conversation_and_exercise_ids():
    payload = build_lesson_payload()
    payload["exercises"][0]["id"] = "a1-u1-l1-c1"

    assert_invalid(
        payload,
        "Lesson activity IDs must be unique across resources",
    )


def test_exercise_result_requires_existing_exercise():
    payload = build_lesson_payload()
    evidence = payload["experience"]["evidence_definitions"][0]
    evidence["activity_id"] = "a1-u1-l1-q999"
    payload["experience"]["stages"][1]["activity_ids"] = [
        "a1-u1-l1-q999"
    ]

    assert_invalid(payload, "references unknown exercise")


def test_exercise_result_skills_must_belong_to_exercise():
    payload = build_lesson_payload()
    experience = payload["experience"]
    experience["skill_ids"].append("a1_introduce_yourself")
    experience["evidence_definitions"][0]["skill_ids"] = [
        "a1_introduce_yourself"
    ]

    assert_invalid(
        payload,
        "Skills must be declared by exercise",
    )


def test_conversation_completion_requires_existing_conversation():
    payload = build_lesson_payload()
    evidence = payload["experience"]["evidence_definitions"][0]
    evidence["evidence_type"] = "conversation_completion"
    evidence["measurement_mode"] = "completion"
    evidence["activity_id"] = "a1-u1-l1-c999"
    payload["experience"]["stages"][1]["activity_ids"] = [
        "a1-u1-l1-c999"
    ]

    assert_invalid(payload, "references unknown conversation")

def test_contextual_response_requires_existing_conversation():
    payload = build_lesson_payload()
    evidence = payload["experience"]["evidence_definitions"][0]
    evidence["evidence_type"] = "contextual_response"
    evidence["measurement_mode"] = "completion"
    evidence["activity_id"] = "a1-u1-l1-c999"
    payload["experience"]["stages"][1]["activity_ids"] = [
        "a1-u1-l1-c999"
    ]

    assert_invalid(
        payload,
        "Contextual response references unknown conversation",
    )


def test_contextual_response_requires_production_prompt():
    payload = build_lesson_payload()
    evidence = payload["experience"]["evidence_definitions"][0]
    evidence["evidence_type"] = "contextual_response"
    evidence["measurement_mode"] = "completion"
    evidence["activity_id"] = "a1-u1-l1-c1"
    payload["experience"]["stages"][1]["activity_ids"] = [
        "a1-u1-l1-c1"
    ]

    assert_invalid(
        payload,
        "Contextual response requires at least one production prompt",
    )


def test_contextual_response_requires_completion_measurement():
    payload = build_lesson_payload()
    payload["conversations"][0]["turns"].append(
        {
            "id": "turn-2",
            "speaker": "learner",
            "en": "Respond personally.",
            "production_prompt": {
                "id": "a1-u1-l1-c1-p1",
                "accepted_modalities": ["text"],
                "required": True,
            },
        }
    )

    evidence = payload["experience"]["evidence_definitions"][0]
    evidence["evidence_type"] = "contextual_response"
    evidence["measurement_mode"] = "binary"
    evidence["activity_id"] = "a1-u1-l1-c1"
    payload["experience"]["stages"][1]["activity_ids"] = [
        "a1-u1-l1-c1"
    ]

    assert_invalid(
        payload,
        "Contextual response must use completion measurement",
    )
