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
