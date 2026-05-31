from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_levels_endpoint_returns_expected_levels():
    """Verify that the levels endpoint returns the expected CEFR levels."""
    response = client.get("/api/v1/levels")

    assert response.status_code == 200
    assert response.json() == {
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
    }
