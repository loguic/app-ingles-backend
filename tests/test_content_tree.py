from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_content_tree_returns_levels():
    """Verify that the content tree returns available levels and units."""
    response = client.get("/api/v1/content/tree")

    data = response.json()

    assert response.status_code == 200
    assert "levels" in data
    assert data["levels"][0]["code"] == "A1"
    assert data["levels"][0]["units"][0]["id"] == "a1-u1"
