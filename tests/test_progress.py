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


def test_read_progress_recommendation_returns_message():
    """Verify that a basic learning recommendation is returned for a user."""
    payload = {
        "user_id": "test-user-b44",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get("/api/v1/progress/test-user-b44/recommendation")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "test-user-b44",
        "accuracy": 1.0,
        "message": "Good progress. Continue with the next lesson.",
    }


def test_read_skill_mastery_returns_score():
    """Verify that mastery score is calculated for a specific skill."""
    payload = {
        "user_id": "test-user-b47",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get(
        "/api/v1/progress/test-user-b47/skills/a1_greetings_basic/mastery"
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "test-user-b47",
        "skill_id": "a1_greetings_basic",
        "total_attempts": 1,
        "correct_attempts": 1,
        "mastery_score": 1.0,
    }


def test_read_review_recommendation_returns_decision():
    """Verify that review recommendation is generated for a specific skill."""
    payload = {
        "user_id": "test-user-b49",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 0,
        "correct": False,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get(
        "/api/v1/progress/test-user-b49/skills/a1_greetings_basic/review"
    )

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "test-user-b49",
        "skill_id": "a1_greetings_basic",
        "mastery_score": 0.0,
        "should_review": True,
        "message": "Review this skill before moving forward.",
    }


def test_read_student_dashboard_returns_summary():
    """Verify that the student dashboard returns progress summary data."""
    payload = {
        "user_id": "test-user-b52",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "exercise_id": "a1-u1-l1-q1",
        "selected_index": 1,
        "correct": True,
    }

    client.post("/api/v1/progress", json=payload)

    response = client.get("/api/v1/progress/test-user-b52/dashboard")

    assert response.status_code == 200
    assert response.json() == {
        "user_id": "test-user-b52",
        "total_attempts": 1,
        "correct_attempts": 1,
        "accuracy": 1.0,
        "recommendation": "Good progress. Continue with the next lesson.",
    }
