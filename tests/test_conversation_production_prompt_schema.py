import pytest
from pydantic import ValidationError

from app.schemas.content import Conversation, LearnerProductionPrompt


def build_prompt() -> dict:
    """Return one valid personal-production prompt.

    Devuelve una instrucción válida de producción personal.
    """
    return {
        "id": "a1-u1-l1-c3-p1",
        "accepted_modalities": ["text", "voice"],
        "required": True,
    }


def build_free_conversation() -> dict:
    """Return one valid free conversation with personal production.

    Devuelve una conversación libre válida con producción personal.
    """
    return {
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
                "production_prompt": build_prompt(),
            },
        ],
    }


def test_valid_learner_production_prompt_supports_text_and_voice():
    """Represent accepted capture modalities without claiming correctness.

    Representa modalidades de captura sin afirmar corrección.
    """
    prompt = LearnerProductionPrompt.model_validate(build_prompt())

    assert prompt.id == "a1-u1-l1-c3-p1"
    assert prompt.accepted_modalities == ["text", "voice"]
    assert prompt.required is True


def test_learner_turn_can_request_personal_production():
    """Attach one production prompt only to a learner turn.

    Asocia una instrucción de producción a un turno del estudiante.
    """
    conversation = Conversation.model_validate(build_free_conversation())

    prompt = conversation.turns[1].production_prompt
    assert prompt is not None
    assert prompt.id == "a1-u1-l1-c3-p1"


@pytest.mark.parametrize(
    "modalities",
    [
        [],
        ["text", "text"],
        ["voice", "voice"],
    ],
)
def test_production_prompt_rejects_empty_or_duplicate_modalities(modalities):
    """Require at least one unique supported capture modality.

    Exige al menos una modalidad de captura válida y única.
    """
    payload = build_prompt()
    payload["accepted_modalities"] = modalities

    with pytest.raises(ValidationError):
        LearnerProductionPrompt.model_validate(payload)


def test_partner_turn_cannot_request_learner_production():
    """Keep personal production prompts exclusive to learner turns.

    Mantiene las instrucciones de producción exclusivas del estudiante.
    """
    payload = build_free_conversation()
    payload["turns"][0]["production_prompt"] = build_prompt()

    with pytest.raises(
        ValidationError,
        match="production prompt.*learner turn",
    ):
        Conversation.model_validate(payload)


def test_existing_conversation_remains_valid_without_production_prompt():
    """Preserve backward compatibility for existing conversations.

    Conserva la compatibilidad con conversaciones existentes.
    """
    conversation = Conversation.model_validate(
        {
            "id": "guided-legacy",
            "title": "Existing guided conversation",
            "mode": "guided",
            "turns": [
                {
                    "id": "guided-legacy-t1",
                    "speaker": "partner",
                    "en": "Hello.",
                },
                {
                    "id": "guided-legacy-t2",
                    "speaker": "learner",
                    "en": "Hello.",
                },
            ],
        }
    )

    assert conversation.turns[0].production_prompt is None
    assert conversation.turns[1].production_prompt is None

def test_conversation_rejects_duplicate_production_prompt_ids():
    """Require production prompt IDs to be unique per conversation.

    Exige identificadores de producción únicos por conversación.
    """
    payload = build_free_conversation()
    payload["turns"].append(
        {
            "id": "a1-u1-l1-c3-t3",
            "speaker": "learner",
            "en": "Say where you are from.",
            "production_prompt": build_prompt(),
        }
    )

    with pytest.raises(
        ValidationError,
        match="production prompt IDs must be unique",
    ):
        Conversation.model_validate(payload)
