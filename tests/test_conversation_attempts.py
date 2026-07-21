import pytest
from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.db.models import ConversationAttempt
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_conversation_attempts():
    """Clean B101 test records before and after every test.
    Limpia los registros de prueba de B101 antes y después de cada prueba.
    """
    db = SessionLocal()
    try:
        db.query(ConversationAttempt).filter(
            ConversationAttempt.user_id.like("test-user-b101-%")
        ).delete(synchronize_session=False)
        db.commit()

        yield

        db.query(ConversationAttempt).filter(
            ConversationAttempt.user_id.like("test-user-b101-%")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_save_and_read_completed_guided_attempt():
    """Save and recover one complete guided conversation attempt.
    Guarda y recupera un intento completo de conversación guiada.
    """
    payload = {
        "user_id": "test-user-b101-guided",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c1",
        "mode": "guided",
        "visited_turn_ids": [
            "a1-u1-l1-c1-t1",
            "a1-u1-l1-c1-t2",
            "a1-u1-l1-c1-t3",
            "a1-u1-l1-c1-t4",
        ],
        "selected_choice_ids": [],
    }

    create_response = client.post("/api/v1/conversation-attempts", json=payload)

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["completed_at"]
    assert {key: created[key] for key in payload} == payload

    read_response = client.get(
        "/api/v1/conversation-attempts/test-user-b101-guided"
    )

    assert read_response.status_code == 200
    assert read_response.json() == [created]


def test_save_completed_branching_attempt():
    """Save one valid completed branching route.
    Guarda una ruta ramificada válida y completada.
    """
    payload = {
        "user_id": "test-user-b101-branching",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c2",
        "mode": "branching",
        "visited_turn_ids": [
            "a1-u1-l1-c2-t1",
            "a1-u1-l1-c2-t2",
            "a1-u1-l1-c2-t4",
            "a1-u1-l1-c2-t5",
        ],
        "selected_choice_ids": [
            "a1-u1-l1-c2-choice-tired",
        ],
    }

    response = client.post("/api/v1/conversation-attempts", json=payload)

    assert response.status_code == 200
    created = response.json()
    assert created["completed_at"]
    assert created["visited_turn_ids"] == payload["visited_turn_ids"]
    assert created["selected_choice_ids"] == payload["selected_choice_ids"]


def test_reject_branching_attempt_with_mismatched_route():
    """Reject a route that does not match the selected choice.
    Rechaza una ruta que no coincide con la opción seleccionada.
    """
    payload = {
        "user_id": "test-user-b101-invalid-route",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c2",
        "mode": "branching",
        "visited_turn_ids": [
            "a1-u1-l1-c2-t1",
            "a1-u1-l1-c2-t2",
            "a1-u1-l1-c2-t3",
            "a1-u1-l1-c2-t5",
        ],
        "selected_choice_ids": [
            "a1-u1-l1-c2-choice-tired",
        ],
    }

    response = client.post("/api/v1/conversation-attempts", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Visited turns do not match the completed route"
    )


def test_reject_incomplete_guided_attempt():
    """Reject and do not persist an incomplete guided attempt.
    Rechaza y no persiste un intento guiado incompleto.
    """
    user_id = "test-user-b101-incomplete-guided"
    payload = {
        "user_id": user_id,
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c1",
        "mode": "guided",
        "visited_turn_ids": [
            "a1-u1-l1-c1-t1",
            "a1-u1-l1-c1-t2",
        ],
        "selected_choice_ids": [],
    }

    create_response = client.post("/api/v1/conversation-attempts", json=payload)

    assert create_response.status_code == 400
    assert create_response.json()["detail"] == (
        "Guided attempt must visit every turn in order"
    )

    read_response = client.get(f"/api/v1/conversation-attempts/{user_id}")
    assert read_response.status_code == 200
    assert read_response.json() == []


def test_reject_attempt_with_mismatched_hierarchy():
    """Reject a conversation assigned to the wrong lesson hierarchy.
    Rechaza una conversación asociada a una jerarquía de lección incorrecta.
    """
    payload = {
        "user_id": "test-user-b101-invalid-hierarchy",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l2",
        "conversation_id": "a1-u1-l1-c1",
        "mode": "guided",
        "visited_turn_ids": [
            "a1-u1-l1-c1-t1",
            "a1-u1-l1-c1-t2",
            "a1-u1-l1-c1-t3",
            "a1-u1-l1-c1-t4",
        ],
        "selected_choice_ids": [],
    }

    response = client.post("/api/v1/conversation-attempts", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Conversation hierarchy does not match the content tree"
    )


def test_conversation_attempt_does_not_change_exercise_stats():
    """Keep conversation attempts separate from exercise statistics.
    Mantiene los intentos conversacionales separados de las estadísticas de ejercicios.
    """
    user_id = "test-user-b101-separated-stats"
    payload = {
        "user_id": user_id,
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c1",
        "mode": "guided",
        "visited_turn_ids": [
            "a1-u1-l1-c1-t1",
            "a1-u1-l1-c1-t2",
            "a1-u1-l1-c1-t3",
            "a1-u1-l1-c1-t4",
        ],
        "selected_choice_ids": [],
    }

    create_response = client.post("/api/v1/conversation-attempts", json=payload)
    stats_response = client.get(f"/api/v1/progress/{user_id}/stats")

    assert create_response.status_code == 200
    assert stats_response.status_code == 200
    assert stats_response.json() == {
        "user_id": user_id,
        "total_attempts": 0,
        "correct_attempts": 0,
        "accuracy": 0.0,
    }


def test_repeated_completions_create_separate_attempts():
    """Store repeated completions as separate conversation attempts.
    Guarda las repeticiones como intentos conversacionales independientes.
    """
    user_id = "test-user-b101-repeated"
    payload = {
        "user_id": user_id,
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c1",
        "mode": "guided",
        "visited_turn_ids": [
            "a1-u1-l1-c1-t1",
            "a1-u1-l1-c1-t2",
            "a1-u1-l1-c1-t3",
            "a1-u1-l1-c1-t4",
        ],
        "selected_choice_ids": [],
    }

    first_response = client.post("/api/v1/conversation-attempts", json=payload)
    second_response = client.post("/api/v1/conversation-attempts", json=payload)
    read_response = client.get(f"/api/v1/conversation-attempts/{user_id}")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert read_response.status_code == 200
    attempts = read_response.json()
    assert len(attempts) == 2
    assert attempts[0]["conversation_id"] == payload["conversation_id"]
    assert attempts[1]["conversation_id"] == payload["conversation_id"]
