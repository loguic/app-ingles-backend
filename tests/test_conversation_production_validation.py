import pytest

from app.schemas.content import Conversation
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
)
from app.services.conversation_production_validation import (
    validate_conversation_production_submission,
)


def build_conversation() -> Conversation:
    """Build a free conversation requiring three personal productions.

    Construye una conversación libre con tres producciones personales.
    """
    return Conversation.model_validate(
        {
            "id": "a1-u1-l1-c3",
            "title": "Applied introduction",
            "mode": "free",
            "start_turn_id": "a1-u1-l1-c3-t1",
            "turns": [
                {
                    "id": "a1-u1-l1-c3-t1",
                    "speaker": "partner",
                    "en": "What is your name?",
                    "next_turn_id": "a1-u1-l1-c3-t2",
                },
                {
                    "id": "a1-u1-l1-c3-t2",
                    "speaker": "learner",
                    "en": "Say your name.",
                    "next_turn_id": "a1-u1-l1-c3-t3",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p1",
                        "accepted_modalities": ["text", "voice"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t3",
                    "speaker": "partner",
                    "en": "Where are you from?",
                    "next_turn_id": "a1-u1-l1-c3-t4",
                },
                {
                    "id": "a1-u1-l1-c3-t4",
                    "speaker": "learner",
                    "en": "Say where you are from.",
                    "next_turn_id": "a1-u1-l1-c3-t5",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p2",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t5",
                    "speaker": "partner",
                    "en": "Nice to meet you.",
                    "next_turn_id": "a1-u1-l1-c3-t6",
                },
                {
                    "id": "a1-u1-l1-c3-t6",
                    "speaker": "learner",
                    "en": "Respond politely.",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p3",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
            ],
        }
    )


def build_submission() -> ConversationProductionSubmission:
    """Build one structurally complete personal-production submission.

    Construye un envío estructuralmente completo.
    """
    return ConversationProductionSubmission.model_validate(
        {
            "user_id": "learner-1",
            "level_id": "A1",
            "unit_id": "a1-u1",
            "lesson_id": "a1-u1-l1",
            "conversation_id": "a1-u1-l1-c3",
            "productions": [
                {
                    "prompt_id": "a1-u1-l1-c3-p1",
                    "turn_id": "a1-u1-l1-c3-t2",
                    "modality": "text",
                    "response_text": "My name is Ana.",
                },
                {
                    "prompt_id": "a1-u1-l1-c3-p2",
                    "turn_id": "a1-u1-l1-c3-t4",
                    "modality": "text",
                    "response_text": "I am from Ecuador.",
                },
                {
                    "prompt_id": "a1-u1-l1-c3-p3",
                    "turn_id": "a1-u1-l1-c3-t6",
                    "modality": "text",
                    "response_text": "Nice to meet you too.",
                },
            ],
        }
    )


def test_valid_submission_matches_conversation_prompts():
    validate_conversation_production_submission(
        build_submission(),
        build_conversation(),
    )


def test_submission_rejects_wrong_conversation_id():
    submission = build_submission().model_copy(
        update={"conversation_id": "a1-u1-l1-c99"}
    )

    with pytest.raises(ValueError, match="conversation ID"):
        validate_conversation_production_submission(
            submission,
            build_conversation(),
        )


def test_submission_rejects_unknown_prompt_or_turn():
    submission = build_submission()
    submission.productions[0].prompt_id = "a1-u1-l1-c3-p99"

    with pytest.raises(ValueError, match="unknown production prompt"):
        validate_conversation_production_submission(
            submission,
            build_conversation(),
        )


def test_submission_rejects_modality_not_accepted_by_prompt():
    submission = build_submission()
    submission.productions[1] = submission.productions[1].model_copy(
        update={
            "modality": "voice",
            "response_text": None,
            "audio_reference": "recordings/origin.wav",
        }
    )

    with pytest.raises(ValueError, match="modality is not accepted"):
        validate_conversation_production_submission(
            submission,
            build_conversation(),
        )


def test_submission_requires_every_required_prompt():
    submission = build_submission().model_copy(
        update={"productions": build_submission().productions[:-1]}
    )

    with pytest.raises(ValueError, match="missing required production"):
        validate_conversation_production_submission(
            submission,
            build_conversation(),
        )
