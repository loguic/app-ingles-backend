from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_submit_exercise_with_correct_answer_returns_true():
    """Verify that submitting the correct answer returns correct=True."""
    response = client.post(
        "/api/v1/exercises/a1-u1-l1-q1/submit",
        json={"selected_index": 1},
    )

    assert response.status_code == 200
    assert response.json() == {"correct": True}
