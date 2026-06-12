from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_existing_level_returns_level_data():
    """Verify that an existing level can be retrieved by its code."""
    response = client.get("/api/v1/content/levels/A1")

    data = response.json()

    assert response.status_code == 200
    assert data["code"] == "A1"
    assert data["units"][0]["id"] == "a1-u1"


def test_get_units_by_level_returns_units():
    """Verify that units can be retrieved from an existing level."""
    response = client.get("/api/v1/content/levels/A1/units")

    data = response.json()

    assert response.status_code == 200
    assert data[0]["id"] == "a1-u1"
    assert data[0]["title"] == "Basics: Greetings & Introductions"
