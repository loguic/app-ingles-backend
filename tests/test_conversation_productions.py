import pytest
from fastapi.testclient import TestClient

from app.db.database import SessionLocal
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
)
from app.main import app
from app.schemas.content import Conversation
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
)
from app.services.conversation_production_persistence_service import (
    save_conversation_production_submission,
)
from app.services.production_audio_storage_service import (
    read_production_audio,
)


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_conversation_productions():
    """Clean B124 API records before and after each test.

    Limpia registros API de B124 antes y después de cada prueba.
    """
    db = SessionLocal()
    try:
        db.query(SubmissionModel).filter(
            SubmissionModel.user_id.like("test-user-b124-%")
        ).delete(synchronize_session=False)
        db.commit()
        yield
        db.query(SubmissionModel).filter(
            SubmissionModel.user_id.like("test-user-b124-%")
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def build_active_conversation() -> Conversation:
    """Build one synthetic active conversation for API tests.

    Construye una conversación activa sintética para pruebas de API.
    """
    return Conversation.model_validate(
        {
            "id": "a1-u1-l1-c3",
            "title": "Synthetic active production",
            "mode": "free",
            "turns": [
                {
                    "id": "a1-u1-l1-c3-t2",
                    "speaker": "learner",
                    "en": "Say your name.",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p1",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t4",
                    "speaker": "learner",
                    "en": "Say where you are from.",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p2",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t6",
                    "speaker": "learner",
                    "en": "Respond politely.",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p3",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
            ],
        }
    )

def build_payload():
    """Build one complete production payload for API tests.

    Construye una entrega completa para pruebas de API.
    """
    return {
        "user_id": "test-user-b124-isolated",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "conversation_id": "a1-u1-l1-c3",
        "productions": [
            {
                "prompt_id": "a1-u1-l1-c3-p1",
                "turn_id": "a1-u1-l1-c3-t2",
                "modality": "text",
                "response_text": "My name is Ana.",
            },
            {
                "prompt_id": "a1-u1-l1-c3-p2",
                "turn_id": "a1-u1-l1-c3-t4",
                "modality": "text",
                "response_text": "I am from Ecuador.",
            },
            {
                "prompt_id": "a1-u1-l1-c3-p3",
                "turn_id": "a1-u1-l1-c3-t6",
                "modality": "text",
                "response_text": "Nice to meet you too.",
            },
        ],
    }


def test_post_rejects_production_outside_active_content():
    """Reject candidate production through the public API.

    Rechaza producción candidata mediante la API pública.
    """
    payload = build_payload()

    response = client.post(
        "/api/v1/conversation-productions",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Conversation does not exist"

    db = SessionLocal()
    try:
        count = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == payload["user_id"]
        ).count()
    finally:
        db.close()

    assert count == 0

def test_save_and_read_active_conversation_production(
    monkeypatch,
):
    """Save and read production exposed through active content.

    Guarda y lee producción expuesta mediante contenido activo.
    """
    monkeypatch.setattr(
        "app.services.conversation_production_persistence_service."
        "get_conversation_context_by_id",
        lambda conversation_id: (
            "A1",
            "a1-u1",
            "a1-u1-l1",
            build_active_conversation(),
        ),
    )

    payload = build_payload()
    payload["user_id"] = "test-user-b124-active"

    create_response = client.post(
        "/api/v1/conversation-productions",
        json=payload,
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["submission_id"] > 0
    assert created["submitted_at"]
    assert created["user_id"] == payload["user_id"]
    assert created["conversation_id"] == payload["conversation_id"]
    assert len(created["productions"]) == 3
    assert all(
        item["production_id"] > 0
        for item in created["productions"]
    )

    read_response = client.get(
        "/api/v1/conversation-productions/"
        + payload["user_id"]
    )

    assert read_response.status_code == 200
    assert read_response.json() == [created]

def test_post_rejects_mismatched_active_hierarchy(
    monkeypatch,
):
    """Reject production assigned to a wrong active hierarchy.

    Rechaza producción asociada a una jerarquía activa incorrecta.
    """
    monkeypatch.setattr(
        "app.services.conversation_production_persistence_service."
        "get_conversation_context_by_id",
        lambda conversation_id: (
            "A1",
            "a1-u1",
            "a1-u1-l1",
            build_active_conversation(),
        ),
    )

    payload = build_payload()
    payload["user_id"] = "test-user-b124-wrong-hierarchy"
    payload["lesson_id"] = "a1-u1-l2"

    response = client.post(
        "/api/v1/conversation-productions",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Conversation hierarchy does not match the content tree"
    )

    db = SessionLocal()
    try:
        count = db.query(SubmissionModel).filter(
            SubmissionModel.user_id == payload["user_id"]
        ).count()
    finally:
        db.close()

    assert count == 0

def test_get_hides_persisted_non_active_production():
    """Hide internal production absent from active content.

    Oculta producción interna ausente del contenido activo.
    """
    payload = build_payload()
    payload["user_id"] = "test-user-b124-hidden"
    submission = ConversationProductionSubmission.model_validate(
        payload
    )

    db = SessionLocal()
    try:
        save_conversation_production_submission(
            submission,
            build_active_conversation(),
            db,
        )
    finally:
        db.close()

    response = client.get(
        "/api/v1/conversation-productions/"
        + payload["user_id"]
    )

    assert response.status_code == 200
    assert response.json() == []

def build_wav_payload(extra=b"learner-audio"):
    # Build minimal WAV-like bytes accepted by the storage boundary.
    # Construye bytes WAV mínimos aceptados por la frontera.
    return (
        b"RIFF"
        + (36 + len(extra)).to_bytes(4, "little")
        + b"WAVE"
        + extra
    )


def test_upload_production_audio_returns_resolvable_reference(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    payload = build_wav_payload()

    response = client.post(
        "/api/v1/conversation-production-audio",
        files={
            "audio": (
                "learner.wav",
                payload,
                "audio/wav",
            )
        },
    )

    assert response.status_code == 200
    record = response.json()
    assert record["audio_reference"].startswith(
        "production-audio://"
    )
    assert record["media_type"] == "audio/wav"
    assert record["size_bytes"] == len(payload)
    assert read_production_audio(
        record["audio_reference"],
        storage_dir=tmp_path,
    ) == payload


def test_upload_production_audio_rejects_non_wav(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))

    response = client.post(
        "/api/v1/conversation-production-audio",
        files={
            "audio": (
                "fake.wav",
                b"not-a-wave-file",
                "audio/wav",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Production audio must be WAV"
    )


def test_upload_production_audio_requires_storage_configuration(
    monkeypatch,
):
    monkeypatch.delenv("PRODUCTION_AUDIO_DIR", raising=False)

    response = client.post(
        "/api/v1/conversation-production-audio",
        files={
            "audio": (
                "learner.wav",
                build_wav_payload(),
                "audio/wav",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "PRODUCTION_AUDIO_DIR is not configured"
    )
