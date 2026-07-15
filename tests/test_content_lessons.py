from fastapi.testclient import TestClient

from app.main import app


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
