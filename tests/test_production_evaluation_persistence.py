from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
    ProductionEvaluationResult as EvaluationModel,
)
from app.schemas.evaluation import ProductionEvaluationResult
from app.services.production_evaluation_persistence_service import (
    get_production_evaluation_results,
    save_production_evaluation_results,
)


@pytest.fixture()
def db():
    """Create an isolated database for evaluation persistence tests.

    Crea una base aislada para probar persistencia evaluativa.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def create_production(db, *, prompt_id="a1-u1-l1-c3-p1"):
    submission = SubmissionModel(
        user_id="b131-user",
        level_id="A1",
        unit_id="a1-u1",
        lesson_id="a1-u1-l1",
        conversation_id="a1-u1-l1-c3",
    )
    db.add(submission)
    db.flush()

    production = ProductionModel(
        submission_id=submission.id,
        prompt_id=prompt_id,
        turn_id="a1-u1-l1-c3-t2",
        modality="text",
        response_text="My name is Ana.",
        audio_reference=None,
    )
    db.add(production)
    db.commit()
    db.refresh(production)
    return production


def build_result(
    production_id: int,
    *,
    evaluator_version: str = "1.0",
    evaluated_at: datetime | None = None,
):
    return ProductionEvaluationResult(
        production_id=production_id,
        criterion_id="a1-u1-l1-c3-p1-semantic",
        status="passed",
        score=None,
        evaluator_id="deterministic-semantic",
        evaluator_version=evaluator_version,
        evaluated_at=evaluated_at or datetime.now(UTC),
    )


def test_evaluation_result_has_separate_persistence_model():
    evaluation = EvaluationModel.__table__
    production = ProductionModel.__table__

    assert evaluation.name == "production_evaluation_results"
    assert set(evaluation.columns.keys()) == {
        "id",
        "production_id",
        "criterion_id",
        "status",
        "score",
        "evaluator_id",
        "evaluator_version",
        "evaluated_at",
    }

    foreign_key = next(
        iter(evaluation.c.production_id.foreign_keys)
    )
    assert foreign_key.target_fullname == "learner_productions.id"
    assert foreign_key.ondelete == "CASCADE"

    assert {
        "criterion_id",
        "status",
        "score",
        "evaluator_id",
        "evaluator_version",
        "evaluated_at",
    }.isdisjoint(production.columns.keys())


def test_save_evaluation_result_returns_persistent_identity(db):
    production = create_production(db)
    result = build_result(production.id)

    records = save_production_evaluation_results(
        [result],
        db,
    )

    assert len(records) == 1
    assert records[0].evaluation_result_id > 0
    assert records[0].production_id == production.id
    assert records[0].criterion_id == result.criterion_id
    assert records[0].status == "passed"


def test_multiple_evaluations_preserve_history(db):
    production = create_production(db)
    first_time = datetime.now(UTC)
    second_time = first_time + timedelta(minutes=5)

    save_production_evaluation_results(
        [
            build_result(
                production.id,
                evaluator_version="1.0",
                evaluated_at=first_time,
            ),
            build_result(
                production.id,
                evaluator_version="1.1",
                evaluated_at=second_time,
            ),
        ],
        db,
    )

    records = get_production_evaluation_results(
        production.id,
        db,
    )

    assert len(records) == 2
    assert [item.evaluator_version for item in records] == [
        "1.0",
        "1.1",
    ]
    assert records[0].evaluation_result_id != (
        records[1].evaluation_result_id
    )


def test_read_returns_only_requested_production(db):
    first = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p1",
    )
    second = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
    )

    save_production_evaluation_results(
        [
            build_result(first.id),
            build_result(second.id),
        ],
        db,
    )

    records = get_production_evaluation_results(
        first.id,
        db,
    )

    assert len(records) == 1
    assert records[0].production_id == first.id


def test_save_rejects_empty_batch(db):
    with pytest.raises(
        ValueError,
        match="At least one production evaluation result",
    ):
        save_production_evaluation_results([], db)


def test_save_rejects_unknown_production(db):
    with pytest.raises(
        ValueError,
        match="unknown productions: 999999",
    ):
        save_production_evaluation_results(
            [build_result(999999)],
            db,
        )
