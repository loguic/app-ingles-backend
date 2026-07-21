import pytest
from pydantic import ValidationError

from app.schemas.content import Conversation


def build_valid_branching_conversation() -> dict:
    """Return a reusable valid branching graph.

    Devuelve un grafo ramificado válido y reutilizable.
    """
    return {
        "id": "conversation-1",
        "title": "Professional branching contract",
        "mode": "branching",
        "start_turn_id": "turn-1",
        "turns": [
            {
                "id": "turn-1",
                "speaker": "partner",
                "en": "How are you?",
                "next_turn_id": "turn-2",
            },
            {
                "id": "turn-2",
                "speaker": "learner",
                "en": "Choose a response.",
                "choices": [
                    {
                        "id": "choice-1",
                        "en": "I'm fine.",
                        "next_turn_id": "turn-3",
                    },
                    {
                        "id": "choice-2",
                        "en": "I'm tired.",
                        "next_turn_id": "turn-4",
                    },
                ],
            },
            {
                "id": "turn-3",
                "speaker": "partner",
                "en": "Great.",
                "next_turn_id": "turn-5",
            },
            {
                "id": "turn-4",
                "speaker": "partner",
                "en": "Get some rest.",
                "next_turn_id": "turn-5",
            },
            {
                "id": "turn-5",
                "speaker": "learner",
                "en": "Thank you.",
            },
        ],
    }


def test_valid_branching_graph_supports_split_merge_and_terminal_turn():
    """Accept branching routes that split, merge and finish.

    Acepta rutas que se separan, se unen y finalizan.
    """
    conversation = Conversation.model_validate(
        build_valid_branching_conversation()
    )

    assert conversation.start_turn_id == "turn-1"
    assert conversation.turns[1].choices[1].next_turn_id == "turn-4"


def test_guided_conversation_remains_backward_compatible():
    """Keep existing ordered guided conversations valid.

    Mantiene válidas las conversaciones guiadas ordenadas existentes.
    """
    conversation = Conversation.model_validate(
        {
            "id": "guided-1",
            "title": "Existing guided conversation",
            "mode": "guided",
            "turns": [
                {
                    "id": "guided-turn-1",
                    "speaker": "partner",
                    "en": "Hello.",
                },
                {
                    "id": "guided-turn-2",
                    "speaker": "learner",
                    "en": "Hi.",
                },
            ],
        }
    )

    assert conversation.start_turn_id is None
    assert conversation.turns[0].choices == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda payload: payload["turns"][1]["choices"][0].update(
                next_turn_id="missing-turn"
            ),
            "unknown turns",
        ),
        (
            lambda payload: payload["turns"][4].update(id="turn-4"),
            "turn IDs must be unique",
        ),
        (
            lambda payload: payload["turns"].append(
                {
                    "id": "unreachable-turn",
                    "speaker": "partner",
                    "en": "Unused.",
                }
            ),
            "unreachable turns",
        ),
        (
            lambda payload: payload["turns"][4].update(next_turn_id="turn-1"),
            "reachable cycle",
        ),
        (
            lambda payload: payload["turns"][0].update(
                next_turn_id=None,
                choices=[
                    {
                        "id": "invalid-partner-choice-1",
                        "en": "Option one.",
                        "next_turn_id": "turn-2",
                    },
                    {
                        "id": "invalid-partner-choice-2",
                        "en": "Option two.",
                        "next_turn_id": "turn-2",
                    },
                ],
            ),
            "not a learner turn",
        ),
    ],
)
def test_invalid_branching_graphs_are_rejected(mutation, message):
    """Reject broken branching graph definitions.

    Rechaza definiciones rotas del grafo ramificado.
    """
    payload = build_valid_branching_conversation()
    mutation(payload)

    with pytest.raises(ValidationError, match=message):
        Conversation.model_validate(payload)
