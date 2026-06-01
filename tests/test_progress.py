from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_progress_saves_record():
    """Verify that a progress record can be saved through the API."""
    payload = {
        "user_id": "test-user-b29",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    response = client.post("/api/v1/progress", json=payload)

    assert response.status_code == 200
    assert response.json() == payload
