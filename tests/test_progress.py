import pytest
from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.db.models import UserProgress
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_progress_records():
    """Clean test progress records before and after each test."""
    db = SessionLocal()
    try:
        db.query(UserProgress).filter(
            UserProgress.user_id.like("test-user-%")
        ).delete(synchronize_session=False)
        db.commit()

        yield

        db.query(UserProgress).filter(
            UserProgress.user_id.like("test-user-%")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_create_progress_saves_record():
    """Verify that a progress record can be saved through the API."""
    payload = {
        "user_id": "test-user-b29",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    response = client.post("/api/v1/progress", json=payload)

    assert response.status_code == 200
    assert response.json() == payload


def test_read_progress_returns_user_records():
    """Verify that saved progress records can be read by user ID."""
    payload = {
        "user_id": "test-user-b30",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get("/api/v1/progress/test-user-b30")

    assert response.status_code == 200
    assert payload in response.json()


def test_read_progress_stats_returns_user_statistics():
    """Verify that progress statistics are calculated from saved records."""
    payload = {
        "user_id": "test-user-b31",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get("/api/v1/progress/test-user-b31/stats")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "test-user-b31",
        "total_attempts": 1,
        "correct_attempts": 1,
        "accuracy": 1.0,
    }
