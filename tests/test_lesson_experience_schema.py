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


def build_support_timing_lesson_payload(
    contract_version: str = "3.0",
) -> dict:
    payload = build_experience_payload()
    payload["contract_version"] = contract_version
    payload["stages"][1].update({
        "type": "comprehension",
        "activity_ids": ["a1-u1-l1-c1"],
    })
    payload["evidence_definitions"] = [
        {
            "id": "a1-u1-l1-ev-comprehension",
            "skill_ids": ["a1_introduce_yourself"],
            "stage_id": "a1-u1-l1-s2",
            "activity_id": "a1-u1-l1-c1",
            "comprehension_exercise_id": "a1-u1-l1-q1",
            "evidence_type": "comprehension_result",
            "measurement_mode": "binary",
            "required": True,
        },
    ]
    payload["completion_policy"]["required_evidence_ids"] = [
        "a1-u1-l1-ev-comprehension"
    ]
    payload["language_support"][0][
        "spanish_reveal_after_first_response_to_exercise_id"
    ] = "a1-u1-l1-q1"
    return {
        "id": "a1-u1-l1",
        "title": "Support timing",
        "experience": payload,
        "conversations": [
            {
                "id": "a1-u1-l1-c1",
                "title": "Audio-first context",
                "mode": "guided",
                "audio_first_policy": {
                    "primary_presentation": "audio",
                    "audio_replay_allowed": True,
                    "transcript_initially_hidden": True,
                    "transcript_access": "contingency_accessibility",
                    "transcript_use_interpretation": (
                        "assisted_not_exclusively_auditory"
                    ),
                    "transcript_is_answer_model": False,
                    "transcript_reveal_after_first_response_to_exercise_id": (
                        "a1-u1-l1-q1"
                    ),
                },
                "turns": [
                    {
                        "id": "a1-u1-l1-c1-t1",
                        "speaker": "partner",
                        "en": "What is your name?",
                    }
                ],
            }
        ],
        "exercises": [
            {
                "id": "a1-u1-l1-q1",
                "type": "mcq",
                "prompt": "What does the speaker ask?",
                "options": ["Your name", "Your age"],
                "answer_index": 0,
                "skill_ids": ["a1_introduce_yourself"],
            }
        ],
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
        "exercises": [
            {
                "id": "a1-u1-l1-q1",
                "type": "mcq",
                "prompt": "Complete the introduction.",
                "options": ["Hello.", "Goodbye."],
                "answer_index": 0,
                "skill_ids": ["a1_introduce_yourself"],
            }
        ],
    })

    assert lesson.experience is not None
    assert lesson.experience.contract_version == "2.0"
    assert lesson.experience.mission.id == "a1-u1-l1-m1"
    assert lesson.experience.skill_ids == ["a1_introduce_yourself"]
    assert len(lesson.experience.stages) == 2


@pytest.mark.parametrize("contract_version", ["2.0", "3.0"])
def test_lesson_accepts_declared_experience_versions(contract_version):
    payload = build_experience_payload()
    payload["contract_version"] = contract_version

    lesson = Lesson.model_validate({
        "id": "a1-u1-l1",
        "title": "Declared version",
        "experience": payload,
        "exercises": [
            {
                "id": "a1-u1-l1-q1",
                "type": "mcq",
                "prompt": "Complete the introduction.",
                "options": ["Hello.", "Goodbye."],
                "answer_index": 0,
                "skill_ids": ["a1_introduce_yourself"],
            }
        ],
    })

    assert lesson.experience is not None
    assert lesson.experience.contract_version == contract_version


def test_lesson_rejects_unsupported_experience_version():
    payload = build_experience_payload()
    payload["contract_version"] = "2.1"

    with pytest.raises(ValidationError):
        Lesson.model_validate({
            "id": "a1-u1-l1",
            "title": "Unsupported version",
            "experience": payload,
        })


@pytest.mark.parametrize("field", ["spanish", "transcript"])
def test_v2_rejects_populated_support_timing_metadata(field):
    payload = build_support_timing_lesson_payload("2.0")
    if field == "spanish":
        payload["conversations"][0]["audio_first_policy"].pop(
            "transcript_reveal_after_first_response_to_exercise_id"
        )
    else:
        payload["experience"]["language_support"][0].pop(
            "spanish_reveal_after_first_response_to_exercise_id"
        )

    with pytest.raises(
        ValidationError,
        match="requires contract version 3.0",
    ):
        Lesson.model_validate(payload)


def test_v3_accepts_optional_support_timing_metadata():
    lesson = Lesson.model_validate(build_support_timing_lesson_payload())

    assert lesson.experience is not None
    assert (
        lesson.conversations[0]
        .audio_first_policy
        .transcript_reveal_after_first_response_to_exercise_id
        == "a1-u1-l1-q1"
    )
    assert (
        lesson.experience.language_support[0]
        .spanish_reveal_after_first_response_to_exercise_id
        == "a1-u1-l1-q1"
    )


def test_v3_without_support_timing_metadata_preserves_existing_behavior():
    payload = build_support_timing_lesson_payload()
    payload["experience"]["language_support"][0].pop(
        "spanish_reveal_after_first_response_to_exercise_id"
    )
    payload["conversations"][0]["audio_first_policy"].pop(
        "transcript_reveal_after_first_response_to_exercise_id"
    )

    lesson = Lesson.model_validate(payload)

    assert lesson.conversations[0].audio_first_policy is not None
    assert (
        lesson.conversations[0]
        .audio_first_policy
        .transcript_reveal_after_first_response_to_exercise_id
        is None
    )


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
