from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_existing_lesson_returns_lesson_data():
    """Verify that an existing lesson can be retrieved by its lesson ID."""
    response = client.get("/api/v1/content/lessons/a1-u1-l1")

    assert response.status_code == 200
    assert response.json()["id"] == "a1-u1-l1"
    assert response.json()["title"] == "Hello / Goodbye"
