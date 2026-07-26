import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
)

from app.schemas.content import Conversation
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
)
from app.services.conversation_production_persistence_service import (
    get_conversation_production_submissions_by_user,
    save_conversation_production_submission,
)


def build_conversation() -> Conversation:
    """Build a free conversation requiring three personal productions.

    Construye una conversación libre con tres producciones personales.
    """
    return Conversation.model_validate(
        {
            "id": "a1-u1-l1-c3",
            "title": "Applied introduction",
            "mode": "free",
            "start_turn_id": "a1-u1-l1-c3-t1",
            "turns": [
                {
                    "id": "a1-u1-l1-c3-t1",
                    "speaker": "partner",
                    "en": "What is your name?",
                    "next_turn_id": "a1-u1-l1-c3-t2",
                },
                {
                    "id": "a1-u1-l1-c3-t2",
                    "speaker": "learner",
                    "en": "Say your name.",
                    "next_turn_id": "a1-u1-l1-c3-t3",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p1",
                        "accepted_modalities": ["text", "voice"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t3",
                    "speaker": "partner",
                    "en": "Where are you from?",
                    "next_turn_id": "a1-u1-l1-c3-t4",
                },
                {
                    "id": "a1-u1-l1-c3-t4",
                    "speaker": "learner",
                    "en": "Say where you are from.",
                    "next_turn_id": "a1-u1-l1-c3-t5",
                    "production_prompt": {
                        "id": "a1-u1-l1-c3-p2",
                        "accepted_modalities": ["text"],
                        "required": True,
                    },
                },
                {
                    "id": "a1-u1-l1-c3-t5",
                    "speaker": "partner",
                    "en": "Nice to meet you.",
                    "next_turn_id": "a1-u1-l1-c3-t6",
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


def build_submission() -> ConversationProductionSubmission:
    """Build one structurally complete personal-production submission.

    Construye un envío estructuralmente completo.
    """
    return ConversationProductionSubmission.model_validate(
        {
            "user_id": "test-user-b123-service",
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
    )


def _delete_test_production_records(db):
    # Delete only records created by B123 tests.
    # Elimina únicamente registros creados por las pruebas de B123.
    submission_ids = [
        row[0]
        for row in db.query(SubmissionModel.id)
        .filter(
            SubmissionModel.user_id.like("test-user-b123-%")
        )
        .all()
    ]

    if submission_ids:
        db.query(ProductionModel).filter(
            ProductionModel.submission_id.in_(submission_ids)
        ).delete(synchronize_session=False)

    db.query(SubmissionModel).filter(
        SubmissionModel.user_id.like("test-user-b123-%")
    ).delete(synchronize_session=False)
    db.commit()


@pytest.fixture(autouse=True)
def clean_test_production_submissions():
    """Clean B123 database records before and after each test.

    Limpia los registros de B123 antes y después de cada prueba.
    """
    db = SessionLocal()
    try:
        _delete_test_production_records(db)
        yield
        _delete_test_production_records(db)
    finally:
        db.close()

def test_save_and_read_complete_production_submission():
    """Persist and reconstruct one complete learner submission.

    Persiste y reconstruye una entrega completa del estudiante.
    """
    db = SessionLocal()
    try:
        created = save_conversation_production_submission(
            build_submission(),
            build_conversation(),
            db,
        )
        recovered = (
            get_conversation_production_submissions_by_user(
                "test-user-b123-service",
                db,
            )
        )
    finally:
        db.close()

    assert created.submission_id > 0
    assert created.submitted_at is not None
    assert len(created.productions) == 3
    assert all(
        item.production_id > 0
        for item in created.productions
    )
    assert recovered == [created]

def test_invalid_submission_is_not_persisted():
    """Reject invalid content before database writes.

    Rechaza contenido inválido antes de escribir.
    """
    submission = build_submission().model_copy(
        update={
            "productions": build_submission().productions[:-1]
        }
    )

    db = SessionLocal()
    try:
        with pytest.raises(
            ValueError,
            match="missing required production",
        ):
            save_conversation_production_submission(
                submission,
                build_conversation(),
                db,
            )

        submission_count = db.query(SubmissionModel).filter(
            SubmissionModel.user_id
            == "test-user-b123-service"
        ).count()
        production_count = db.query(ProductionModel).filter(
            ProductionModel.submission_id.in_(
                db.query(SubmissionModel.id).filter(
                    SubmissionModel.user_id
                    == "test-user-b123-service"
                )
            )
        ).count()
    finally:
        db.close()

    assert submission_count == 0
    assert production_count == 0

def test_database_failure_rolls_back_complete_submission(
    monkeypatch,
):
    """Rollback parent and child rows when commit fails.

    Revierte entrega y producciones cuando falla el commit.
    """
    db = SessionLocal()
    original_commit = db.commit

    def fail_commit():
        raise SQLAlchemyError(
            "forced B123 commit failure"
        )

    monkeypatch.setattr(db, "commit", fail_commit)

    try:
        with pytest.raises(
            SQLAlchemyError,
            match="forced B123 commit failure",
        ):
            save_conversation_production_submission(
                build_submission(),
                build_conversation(),
                db,
            )

        monkeypatch.setattr(db, "commit", original_commit)

        submission_ids = db.query(SubmissionModel.id).filter(
            SubmissionModel.user_id
            == "test-user-b123-service"
        )
        submission_count = submission_ids.count()
        production_count = db.query(ProductionModel).filter(
            ProductionModel.submission_id.in_(submission_ids)
        ).count()
    finally:
        db.close()

    assert submission_count == 0
    assert production_count == 0
