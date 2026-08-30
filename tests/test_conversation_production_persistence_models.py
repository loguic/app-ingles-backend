from sqlalchemy import UniqueConstraint

from app.db.models import (
    ConversationProductionSubmission,
    LearnerProduction,
)


def test_conversation_production_persistence_metadata():
    """Protect normalized capture persistence without evaluation.

    Protege la persistencia normalizada sin añadir evaluación.
    """
    submission = ConversationProductionSubmission.__table__
    production = LearnerProduction.__table__

    assert submission.name == (
        "conversation_production_submissions"
    )
    assert production.name == "learner_productions"

    assert set(submission.columns.keys()) == {
        "id",
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "conversation_id",
        "experience_attempt_id",
        "submitted_at",
    }
    assert set(production.columns.keys()) == {
        "id",
        "submission_id",
        "prompt_id",
        "turn_id",
        "modality",
        "response_text",
        "audio_reference",
    }

    foreign_key = next(
        iter(production.c.submission_id.foreign_keys)
    )
    assert foreign_key.target_fullname == (
        "conversation_production_submissions.id"
    )
    assert foreign_key.ondelete == "CASCADE"

    unique_constraints = [
        constraint
        for constraint in production.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert any(
        constraint.name
        == "uq_learner_production_submission_prompt"
        and tuple(
            column.name for column in constraint.columns
        )
        == ("submission_id", "prompt_id")
        for constraint in unique_constraints
    )

    forbidden_columns = {
        "score",
        "correct",
        "mastered",
        "retained",
        "phonetic_score",
    }
    assert forbidden_columns.isdisjoint(
        production.columns.keys()
    )
