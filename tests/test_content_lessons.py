import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.content import Conversation


client = TestClient(app)


def test_get_existing_lesson_returns_lesson_data():
    """Verify that an existing lesson can be retrieved by its lesson ID."""
    response = client.get("/api/v1/content/lessons/a1-u1-l1")

    assert response.status_code == 200
    assert response.json()["id"] == "a1-u1-l1"
    assert response.json()["title"] == "Hello / Goodbye"

    # Verify both regional pronunciation variants and their audio assets.
    # Verifica ambas variantes regionales de pronunciación y sus audios.
    pronunciations = response.json()["examples"][0]["pronunciations"]
    assert [item["locale"] for item in pronunciations] == ["en-US", "en-GB"]
    assert pronunciations[0]["ipa"] == "/həˈloʊ, aɪ æm dʒɑːn/"
    assert pronunciations[0]["audio_asset"] == "audio/a1_u1_l1_hello_us.wav"
    assert pronunciations[1]["ipa"] == "/həˈləʊ, aɪ æm dʒɒn/"
    assert pronunciations[1]["audio_asset"] == "audio/a1_u1_l1_hello_uk.wav"
    # Verify the first scalable guided conversation contract.
    # Verifica el primer contrato escalable de conversación guiada.
    conversation = response.json()["conversations"][0]

    assert conversation["id"] == "a1-u1-l1-c1"
    assert conversation["mode"] == "guided"
    assert [turn["speaker"] for turn in conversation["turns"]] == [
        "partner",
        "learner",
        "partner",
        "learner",
    ]
    assert conversation["turns"][1]["en"] == "Hello, I am John."
    assert len(conversation["turns"][1]["pronunciations"]) == 2
    # Verify that partner turns include playable regional audio references.
    # Verifica que los turnos del interlocutor incluyan audios regionales.
    first_partner_pronunciations = conversation["turns"][0]["pronunciations"]
    second_partner_pronunciations = conversation["turns"][2]["pronunciations"]

    assert [item["locale"] for item in first_partner_pronunciations] == [
        "en-US",
        "en-GB",
    ]
    assert [
        item["audio_asset"] for item in first_partner_pronunciations
    ] == [
        "audio/a1_u1_l1_c1_t1_us.wav",
        "audio/a1_u1_l1_c1_t1_uk.wav",
    ]
    assert all(item["ipa"] for item in first_partner_pronunciations)

    assert [item["locale"] for item in second_partner_pronunciations] == [
        "en-US",
        "en-GB",
    ]
    assert [
        item["audio_asset"] for item in second_partner_pronunciations
    ] == [
        "audio/a1_u1_l1_c1_t3_us.wav",
        "audio/a1_u1_l1_c1_t3_uk.wav",
    ]
    assert all(item["ipa"] for item in second_partner_pronunciations)


def test_lesson_without_conversations_remains_compatible():
    """Verify that older lessons return an empty conversation list."""
    response = client.get("/api/v1/content/lessons/a1-u1-l2")

    assert response.status_code == 200
    assert response.json()["conversations"] == []


def test_branching_conversation_exposes_professional_graph_contract():
    """Verify split, merge and terminal routes from the content API.

    Verifica separación, unión y cierre de rutas desde la API de contenido.
    """
    response = client.get("/api/v1/content/lessons/a1-u1-l1")

    assert response.status_code == 200
    conversations = {
        conversation["id"]: conversation
        for conversation in response.json()["conversations"]
    }
    conversation = conversations["a1-u1-l1-c2"]

    assert conversation["mode"] == "branching"
    assert conversation["start_turn_id"] == "a1-u1-l1-c2-t1"

    turns = {turn["id"]: turn for turn in conversation["turns"]}
    learner_choices = turns["a1-u1-l1-c2-t2"]["choices"]

    assert [choice["id"] for choice in learner_choices] == [
        "a1-u1-l1-c2-choice-fine",
        "a1-u1-l1-c2-choice-tired",
    ]
    assert [choice["next_turn_id"] for choice in learner_choices] == [
        "a1-u1-l1-c2-t3",
        "a1-u1-l1-c2-t4",
    ]
    assert turns["a1-u1-l1-c2-t3"]["next_turn_id"] == "a1-u1-l1-c2-t5"
    assert turns["a1-u1-l1-c2-t4"]["next_turn_id"] == "a1-u1-l1-c2-t5"
    assert turns["a1-u1-l1-c2-t5"]["next_turn_id"] is None

def _validate_branching_test_graph(turns):
    """Build a branching conversation for schema integrity tests.

    Construye una conversación ramificada para pruebas de integridad.
    """
    return Conversation.model_validate(
        {
            "id": "branching-schema-test",
            "title": "Branching schema test",
            "mode": "branching",
            "start_turn_id": "t1",
            "turns": turns,
        }
    )


def test_branching_conversation_rejects_unknown_transition():
    """Reject a choice that points to a turn outside the conversation."""
    with pytest.raises(
        ValueError,
        match="transitions reference unknown turns: missing-turn",
    ):
        _validate_branching_test_graph(
            [
                {
                    "id": "t1",
                    "speaker": "learner",
                    "en": "Choose.",
                    "choices": [
                        {"id": "c1", "en": "Missing", "next_turn_id": "missing-turn"},
                        {"id": "c2", "en": "Finish", "next_turn_id": None},
                    ],
                }
            ]
        )


def test_branching_conversation_rejects_cycle_with_terminal_branch():
    """Reject a reachable cycle even when another branch can finish."""
    with pytest.raises(ValueError, match="contains a reachable cycle"):
        _validate_branching_test_graph(
            [
                {
                    "id": "t1",
                    "speaker": "learner",
                    "en": "Choose.",
                    "choices": [
                        {"id": "c1", "en": "Finish", "next_turn_id": "t2"},
                        {"id": "c2", "en": "Loop", "next_turn_id": "t3"},
                    ],
                },
                {"id": "t2", "speaker": "partner", "en": "Finished."},
                {
                    "id": "t3",
                    "speaker": "partner",
                    "en": "Continue.",
                    "next_turn_id": "t4",
                },
                {
                    "id": "t4",
                    "speaker": "learner",
                    "en": "Return.",
                    "next_turn_id": "t3",
                },
            ]
        )
