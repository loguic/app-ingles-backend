import pytest

from app.schemas.content import Lesson
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.services.production_evaluation_validation_service import (
    validate_production_evaluation_criteria,
)


def build_lesson() -> Lesson:
    """Build one evaluable conversation. / Construye una conversación evaluable."""
    return Lesson.model_validate(
        {
            "id": "a1-u1-l1",
            "title": "Introduce yourself",
            "experience": {
                "contract_version": "2.0",
                "mission": {
                    "id": "a1-u1-l1-m1",
                    "title": "Introduce yourself",
                    "situation": "Meet someone.",
                    "observable_outcome": "State your name.",
                    "success_criteria": ["The learner states a name."],
                },
                "skill_ids": ["a1_introduce_yourself"],
                "stages": [
                    {
                        "id": "a1-u1-l1-s1",
                        "type": "evidence",
                        "instruction": "Provide evidence.",
                        "activity_ids": ["a1-u1-l1-c1"],
                        "mode": "required",
                        "completion_condition": "evidence_recorded",
                    }
                ],
                "language_support": [],
                "evidence_definitions": [
                    {
                        "id": "a1-u1-l1-ev1",
                        "skill_ids": ["a1_introduce_yourself"],
                        "stage_id": "a1-u1-l1-s1",
                        "activity_id": "a1-u1-l1-c1",
                        "evidence_type": "contextual_response",
                        "measurement_mode": "completion",
                        "required": True,
                    }
                ],
                "completion_policy": {
                    "practiced_stage_ids": ["a1-u1-l1-s1"],
                    "required_evidence_ids": ["a1-u1-l1-ev1"],
                    "reinforcement_on_failure": True,
                    "allow_retry": True,
                },
            },
            "conversations": [
                {
                    "id": "a1-u1-l1-c1",
                    "title": "Introduction",
                    "mode": "free",
                    "start_turn_id": "a1-u1-l1-c1-t1",
                    "turns": [
                        {
                            "id": "a1-u1-l1-c1-t1",
                            "speaker": "learner",
                            "en": "Say your name.",
                            "next_turn_id": None,
                            "choices": [],
                            "production_prompt": {
                                "id": "a1-u1-l1-c1-p1",
                                "accepted_modalities": ["text", "voice"],
                                "required": True,
                            },
                        }
                    ],
                }
            ],
        }
    )


def build_criterion() -> ProductionEvaluationCriterion:
    return ProductionEvaluationCriterion.model_validate(
        {
            "id": "a1-u1-l1-c1-p1-semantic",
            "evidence_definition_id": "a1-u1-l1-ev1",
            "conversation_id": "a1-u1-l1-c1",
            "prompt_id": "a1-u1-l1-c1-p1",
            "dimension": "semantic",
            "description": "The learner states a name.",
            "measurement_mode": "binary",
            "applicable_modalities": ["text", "voice"],
        }
    )


def test_valid_criterion_matches_lesson_context():
    validate_production_evaluation_criteria(
        build_lesson(),
        [build_criterion()],
    )


def test_duplicate_criterion_ids_are_rejected():
    criterion = build_criterion()

    with pytest.raises(
        ValueError,
        match="criterion IDs must be unique",
    ):
        validate_production_evaluation_criteria(
            build_lesson(),
            [criterion, criterion],
        )


def test_unknown_evidence_is_rejected():
    criterion = build_criterion().model_copy(
        update={"evidence_definition_id": "a1-u1-l1-ev9"}
    )

    with pytest.raises(ValueError, match="unknown evidence"):
        validate_production_evaluation_criteria(
            build_lesson(),
            [criterion],
        )


def test_evidence_activity_must_match_conversation():
    criterion = build_criterion().model_copy(
        update={"conversation_id": "a1-u1-l1-c9"}
    )

    with pytest.raises(
        ValueError,
        match="conversation must match evidence activity",
    ):
        validate_production_evaluation_criteria(
            build_lesson(),
            [criterion],
        )


def test_unknown_prompt_is_rejected():
    criterion = build_criterion().model_copy(
        update={"prompt_id": "a1-u1-l1-c1-p9"}
    )

    with pytest.raises(
        ValueError,
        match="unknown production prompt",
    ):
        validate_production_evaluation_criteria(
            build_lesson(),
            [criterion],
        )


def test_unsupported_prompt_modality_is_rejected():
    criterion = build_criterion().model_copy(
        update={"applicable_modalities": ["text", "voice"]}
    )
    lesson = build_lesson()
    lesson.conversations[0].turns[
        0
    ].production_prompt.accepted_modalities = ["text"]

    with pytest.raises(
        ValueError,
        match="modalities not accepted by prompt",
    ):
        validate_production_evaluation_criteria(
            lesson,
            [criterion],
        )
