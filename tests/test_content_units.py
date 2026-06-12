from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_existing_unit_returns_unit_data():
    """Verify that an existing unit can be retrieved by its ID."""
    response = client.get("/api/v1/content/units/a1-u1")

    data = response.json()

    assert response.status_code == 200
    assert data["id"] == "a1-u1"
    assert data["title"] == "Basics: Greetings & Introductions"
    assert data["lessons"][0]["id"] == "a1-u1-l1"


def test_get_lessons_by_unit_returns_lessons():
    """Verify that lessons can be retrieved from an existing unit."""
    response = client.get("/api/v1/content/units/a1-u1/lessons")

    data = response.json()

    assert response.status_code == 200
    assert data[0]["id"] == "a1-u1-l1"
    assert data[0]["title"] == "Hello / Goodbye"
