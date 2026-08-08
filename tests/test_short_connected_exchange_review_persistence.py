from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

import app.services.short_connected_exchange_review_persistence_service as service
from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    ConversationalDiagnosticObservation,
    DirectEnglishConstructionProductionOrientation,
    LearnerProduction as ProductionModel,
    ProductionEvaluationResult,
    ProductionFeedback,
    ShortConnectedExchangeProductionReview as ReviewModel,
)
from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReviewBatch,
)
from app.services.content_service import get_lesson_by_id
from app.services.short_connected_exchange_review_persistence_service import (
    ShortConnectedExchangeReviewInvariantError,
    ShortConnectedExchangeReviewPersistenceError,
    ShortConnectedExchangeReviewReferenceError,
    get_short_connected_exchange_reviews_by_submission,
    save_short_connected_exchange_production_reviews,
)


NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)
PROMPTS = (
    ("a1-u1-l2-p-place", "a1-u1-l2-c1-t2"),
    ("a1-u1-l2-p-interest", "a1-u1-l2-c1-t4"),
    ("a1-u1-l2-p-unexpected-where", "a1-u1-l2-c1-t6"),
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def create_submission(db, *, conversation_id="a1-u1-l2-c1"):
    lesson_id = "a1-u1-l2" if conversation_id == "a1-u1-l2-c1" else "a1-u1-l1"
    submission = SubmissionModel(
        user_id="b181-review-user",
        level_id="A1",
        unit_id="a1-u1",
        lesson_id=lesson_id,
        conversation_id=conversation_id,
    )
    db.add(submission)
    db.flush()
    productions = []
    for prompt_id, turn_id in PROMPTS:
        production = ProductionModel(
            submission_id=submission.id,
            prompt_id=prompt_id,
            turn_id=turn_id,
            modality="voice",
            response_text=None,
            audio_reference="production-audio://test",
        )
        db.add(production)
        productions.append(production)
    db.commit()
    for production in productions:
        db.refresh(production)
    return submission, productions


def build_batch(productions, *, prefix="review", reviewed_at=NOW):
    reviews = []
    results = ("positive", "negative", "pending")
    for index, production in enumerate(productions):
        for dimension_index, dimension in enumerate(
            ("intention_understanding", "contingent_response")
        ):
            reviews.append(
                {
                    "review_id": f"{prefix}-{index}-{dimension_index}",
                    "production_id": production.id,
                    "dimension": dimension,
                    "result": results[index],
                    "source_type": "external",
                    "source_id": "review-system",
                    "source_version": "1.0",
                    "reviewed_at": reviewed_at
                    + timedelta(seconds=index + dimension_index),
                }
            )
    return ShortConnectedExchangeProductionReviewBatch.model_validate(
        {"reviews": reviews}
    )


def test_review_model_has_exact_append_only_metadata():
    table = ReviewModel.__table__
    assert table.name == "short_connected_exchange_production_reviews"
    assert set(table.columns) == {
        table.c.review_id,
        table.c.production_id,
        table.c.dimension,
        table.c.result,
        table.c.source_type,
        table.c.source_id,
        table.c.source_version,
        table.c.reviewed_at,
    }
    foreign_key = next(iter(table.c.production_id.foreign_keys))
    assert foreign_key.target_fullname == "learner_productions.id"
    assert foreign_key.ondelete == "CASCADE"
    assert table.c.production_id.index is True
    assert "ix_short_exchange_review_history" in {
        index.name for index in table.indexes
    }
    unique_sets = {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }
    assert ("production_id", "dimension") not in unique_sets


def test_persists_six_reviews_atomically_and_reads_complete_history(db):
    submission, productions = create_submission(db)
    commits = []

    @event.listens_for(db, "after_commit")
    def count_commit(_session):
        commits.append(True)

    records = save_short_connected_exchange_production_reviews(
        build_batch(productions),
        db,
    )
    assert len(records) == 6
    assert len(commits) == 1
    assert {record.production_id for record in records} == {
        production.id for production in productions
    }
    history = get_short_connected_exchange_reviews_by_submission(
        submission.id,
        db,
    )
    assert len(history.productions) == 3
    assert [len(item.reviews) for item in history.productions] == [2, 2, 2]
    assert {
        review.result
        for item in history.productions
        for review in item.reviews
    } == {"positive", "negative", "pending"}
    for item in history.productions:
        ordered = [
            (review.reviewed_at, review.review_id)
            for review in item.reviews
        ]
        assert ordered == sorted(ordered)
    assert db.query(ProductionEvaluationResult).count() == 0
    assert db.query(ProductionFeedback).count() == 0
    assert db.query(ConversationalDiagnosticObservation).count() == 0
    assert db.query(DirectEnglishConstructionProductionOrientation).count() == 0


def test_multiple_batches_preserve_same_dimension_history(db):
    submission, productions = create_submission(db)
    first = ShortConnectedExchangeProductionReviewBatch.model_validate(
        {"reviews": [build_batch(productions).reviews[0]]}
    )
    later_review = first.reviews[0].model_copy(
        update={
            "review_id": "later-review",
            "result": "pending",
            "reviewed_at": NOW + timedelta(hours=1),
        }
    )
    save_short_connected_exchange_production_reviews(first, db)
    save_short_connected_exchange_production_reviews(
        ShortConnectedExchangeProductionReviewBatch(reviews=[later_review]),
        db,
    )
    history = get_short_connected_exchange_reviews_by_submission(
        submission.id,
        db,
    )
    reviews = history.productions[0].reviews
    assert [review.result for review in reviews] == ["positive", "pending"]
    assert [review.review_id for review in reviews] == ["review-0-0", "later-review"]


def test_rejects_unknown_or_out_of_scope_production(db):
    _, productions = create_submission(db)
    unknown = build_batch(productions).reviews[0].model_copy(
        update={"production_id": 999999}
    )
    with pytest.raises(ShortConnectedExchangeReviewReferenceError):
        save_short_connected_exchange_production_reviews(
            ShortConnectedExchangeProductionReviewBatch(reviews=[unknown]),
            db,
        )
    _, other_productions = create_submission(
        db,
        conversation_id="a1-u1-l1-c3",
    )
    other = build_batch(other_productions).reviews[0]
    with pytest.raises(ShortConnectedExchangeReviewReferenceError):
        save_short_connected_exchange_production_reviews(
            ShortConnectedExchangeProductionReviewBatch(reviews=[other]),
            db,
        )


def test_rejects_prompt_without_evidence_and_undeclared_dimension(db, monkeypatch):
    _, productions = create_submission(db)
    lesson = get_lesson_by_id("a1-u1-l2").model_copy(deep=True)
    lesson.experience.evidence_definitions[0].production_prompt_id = None
    monkeypatch.setattr(service, "get_lesson_by_id", lambda _lesson_id: lesson)
    with pytest.raises(ShortConnectedExchangeReviewInvariantError, match="exactly one"):
        save_short_connected_exchange_production_reviews(
            ShortConnectedExchangeProductionReviewBatch(
                reviews=[build_batch(productions).reviews[0]]
            ),
            db,
        )

    lesson = get_lesson_by_id("a1-u1-l2").model_copy(deep=True)
    lesson.experience.evidence_definitions[0].external_review_requirements = [
        lesson.experience.evidence_definitions[0].external_review_requirements[0]
    ]
    monkeypatch.setattr(service, "get_lesson_by_id", lambda _lesson_id: lesson)
    contingent = build_batch(productions).reviews[1]
    with pytest.raises(ShortConnectedExchangeReviewInvariantError, match="dimension"):
        save_short_connected_exchange_production_reviews(
            ShortConnectedExchangeProductionReviewBatch(reviews=[contingent]),
            db,
        )


def test_conflicting_review_id_rolls_back_entire_batch(db):
    _, productions = create_submission(db)
    existing = ShortConnectedExchangeProductionReviewBatch(
        reviews=[build_batch(productions).reviews[0]]
    )
    save_short_connected_exchange_production_reviews(existing, db)
    conflict = build_batch(productions, prefix="new")
    conflict.reviews[0] = conflict.reviews[0].model_copy(
        update={"review_id": existing.reviews[0].review_id}
    )
    with pytest.raises(ShortConnectedExchangeReviewInvariantError):
        save_short_connected_exchange_production_reviews(conflict, db)
    assert db.query(ReviewModel).count() == 1


def test_sql_error_rolls_back_without_partial_reviews(db, monkeypatch):
    _, productions = create_submission(db)
    rollbacks = []
    original_rollback = db.rollback

    def tracked_rollback():
        rollbacks.append(True)
        original_rollback()

    monkeypatch.setattr(db, "rollback", tracked_rollback)
    monkeypatch.setattr(
        db,
        "flush",
        lambda: (_ for _ in ()).throw(SQLAlchemyError("forced")),
    )
    with pytest.raises(ShortConnectedExchangeReviewPersistenceError):
        save_short_connected_exchange_production_reviews(
            build_batch(productions),
            db,
        )
    assert rollbacks == [True]
    monkeypatch.undo()
    assert db.query(ReviewModel).count() == 0


def test_database_rejects_invalid_fk_and_checks(db):
    invalid_fk = ReviewModel(
        review_id="invalid-fk",
        production_id=999999,
        dimension="intention_understanding",
        result="pending",
        source_type="human",
        source_id="reviewer",
        source_version=None,
        reviewed_at=NOW,
    )
    db.add(invalid_fk)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    _, productions = create_submission(db)
    invalid_dimension = ReviewModel(
        review_id="invalid-dimension",
        production_id=productions[0].id,
        dimension="semantic",
        result="pending",
        source_type="human",
        source_id="reviewer",
        source_version=None,
        reviewed_at=NOW,
    )
    db.add(invalid_dimension)
    with pytest.raises(IntegrityError):
        db.commit()
