import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
    ProductionEvaluationResult as EvaluationModel,
    ProductionFeedback as FeedbackModel,
)
from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.pedagogical_feedback import ProductionFeedback
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_feedback_execution_service import (
    generate_and_save_candidate_pedagogical_feedback,
)
from app.services.pedagogical_feedback_persistence_service import (
    get_production_feedback_by_evaluation_result,
    save_production_feedback,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def create_evaluation(db, *, status="passed"):
    submission = SubmissionModel(
        user_id="b133-user",
        level_id="A1",
        unit_id="a1-u1",
        lesson_id="a1-u1-l1",
        conversation_id="a1-u1-l1-c3",
    )
    db.add(submission)
    db.flush()

    production = ProductionModel(
        submission_id=submission.id,
        prompt_id="a1-u1-l1-c3-p1",
        turn_id="a1-u1-l1-c3-t2",
        modality="text",
        response_text="My name is Ana.",
        audio_reference=None,
    )
    db.add(production)
    db.flush()

    evaluation = EvaluationModel(
        production_id=production.id,
        criterion_id="a1-u1-l1-c3-p1-semantic",
        status=status,
        score=None,
        evaluator_id="deterministic-semantic",
        evaluator_version="1.0",
        evaluated_at=datetime.now(UTC),
    )
    db.add(evaluation)
    db.commit()
    db.refresh(production)
    db.refresh(evaluation)

    record = ProductionEvaluationResultRecord(
        evaluation_result_id=evaluation.id,
        production_id=production.id,
        criterion_id=evaluation.criterion_id,
        status=evaluation.status,
        score=evaluation.score,
        evaluator_id=evaluation.evaluator_id,
        evaluator_version=evaluation.evaluator_version,
        evaluated_at=evaluation.evaluated_at,
    )
    return production, evaluation, record


def build_feedback(record, *, generator_version="1.0"):
    return ProductionFeedback(
        evaluation_result_id=record.evaluation_result_id,
        production_id=record.production_id,
        criterion_id=record.criterion_id,
        evaluation_status=record.status,
        criterion_description="The learner states a name.",
        message="You stated your name successfully.",
        guidance="Keep using a clear introduction structure naturally.",
        generator_id="deterministic-pedagogical-feedback",
        generator_version=generator_version,
    )


def test_feedback_has_separate_persistence_model():
    table = FeedbackModel.__table__

    assert table.name == "production_feedbacks"
    assert set(table.columns.keys()) == {
        "id",
        "evaluation_result_id",
        "criterion_description",
        "message",
        "guidance",
        "generator_id",
        "generator_version",
        "generated_at",
    }

    foreign_key = next(
        iter(table.c.evaluation_result_id.foreign_keys)
    )
    assert foreign_key.target_fullname == (
        "production_evaluation_results.id"
    )
    assert foreign_key.ondelete == "CASCADE"


def test_save_feedback_preserves_traceability(db):
    _, evaluation, record = create_evaluation(db)

    persisted = save_production_feedback(
        build_feedback(record),
        db,
    )

    assert persisted.feedback_id > 0
    assert persisted.evaluation_result_id == evaluation.id
    assert persisted.production_id == record.production_id
    assert persisted.criterion_id == record.criterion_id
    assert persisted.evaluation_status == "passed"


def test_feedback_history_is_append_only(db):
    _, evaluation, record = create_evaluation(db)

    save_production_feedback(
        build_feedback(record, generator_version="1.0"),
        db,
    )
    save_production_feedback(
        build_feedback(record, generator_version="1.1"),
        db,
    )

    history = get_production_feedback_by_evaluation_result(
        evaluation.id,
        db,
    )

    assert len(history) == 2
    assert [item.generator_version for item in history] == [
        "1.0",
        "1.1",
    ]
    assert history[0].feedback_id != history[1].feedback_id


def test_unknown_evaluation_is_rejected(db):
    _, _, record = create_evaluation(db)
    feedback = build_feedback(record).model_copy(
        update={"evaluation_result_id": 999999}
    )

    with pytest.raises(
        ValueError,
        match="unknown evaluation result",
    ):
        save_production_feedback(feedback, db)


def test_mismatched_production_is_rejected(db):
    _, _, record = create_evaluation(db)
    feedback = build_feedback(record).model_copy(
        update={"production_id": record.production_id + 100}
    )

    with pytest.raises(
        ValueError,
        match="production_id must match",
    ):
        save_production_feedback(feedback, db)


def test_mismatched_criterion_is_rejected(db):
    _, _, record = create_evaluation(db)
    feedback = build_feedback(record).model_copy(
        update={"criterion_id": "other-criterion"}
    )

    with pytest.raises(
        ValueError,
        match="criterion_id must match",
    ):
        save_production_feedback(feedback, db)


def test_mismatched_status_is_rejected(db):
    _, _, record = create_evaluation(db)
    feedback = build_feedback(record).model_copy(
        update={"evaluation_status": "failed"}
    )

    with pytest.raises(
        ValueError,
        match="status must match",
    ):
        save_production_feedback(feedback, db)


def test_candidate_feedback_is_generated_and_persisted(db):
    _, evaluation, record = create_evaluation(db)
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )

    persisted = generate_and_save_candidate_pedagogical_feedback(
        candidate,
        "a1-u1-l1",
        record,
        db,
    )

    assert persisted.evaluation_result_id == evaluation.id
    assert persisted.production_id == record.production_id
    assert persisted.criterion_id == record.criterion_id
    assert persisted.evaluation_status == "passed"
    assert "name successfully" in persisted.message
    assert db.query(FeedbackModel).count() == 1
