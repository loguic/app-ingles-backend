import json
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
from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_pipeline_service import (
    evaluate_production_atomically,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


@pytest.fixture()
def db():
    """Create an isolated database for atomic pipeline tests.

    Crea una base aislada para probar el pipeline atómico.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def create_production(
    db,
    *,
    prompt_id="a1-u1-l1-c3-p1",
    turn_id="a1-u1-l1-c3-t2",
    modality="text",
    response_text="My name is Ana.",
    audio_reference=None,
) -> LearnerProductionRecord:
    submission = SubmissionModel(
        user_id="b134-user",
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
        turn_id=turn_id,
        modality=modality,
        response_text=response_text,
        audio_reference=audio_reference,
    )
    db.add(production)
    db.commit()
    db.refresh(production)

    return LearnerProductionRecord(
        production_id=production.id,
        prompt_id=production.prompt_id,
        turn_id=production.turn_id,
        modality=production.modality,
        response_text=production.response_text,
        audio_reference=production.audio_reference,
    )


def test_pipeline_persists_evaluation_and_feedback_atomically(db):
    production = create_production(db)

    outcome = evaluate_production_atomically(
        load_candidate(),
        "a1-u1-l1",
        production,
        db,
    )

    assert outcome.production_id == production.production_id
    assert len(outcome.evaluation_results) == 1
    assert len(outcome.feedbacks) == 1

    evaluation = outcome.evaluation_results[0]
    feedback = outcome.feedbacks[0]

    assert evaluation.status == "passed"
    assert evaluation.production_id == production.production_id
    assert feedback.evaluation_result_id == (
        evaluation.evaluation_result_id
    )
    assert feedback.production_id == production.production_id
    assert feedback.criterion_id == evaluation.criterion_id

    assert db.query(EvaluationModel).count() == 1
    assert db.query(FeedbackModel).count() == 1


def test_pipeline_rolls_back_evaluation_if_feedback_fails(db):
    production = create_production(db)
    candidate = load_candidate().model_copy(
        update={"feedback_plans": []}
    )

    with pytest.raises(
        ValueError,
        match="No feedback plan for lesson",
    ):
        evaluate_production_atomically(
            candidate,
            "a1-u1-l1",
            production,
            db,
        )

    assert db.query(EvaluationModel).count() == 0
    assert db.query(FeedbackModel).count() == 0
    assert db.query(ProductionModel).count() == 1


def test_voice_pipeline_uses_recognized_text(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="voice",
        response_text=None,
        audio_reference="local://origin.wav",
    )

    outcome = evaluate_production_atomically(
        load_candidate(),
        "a1-u1-l1",
        production,
        db,
        recognized_text="I am from Ecuador.",
    )

    assert outcome.evaluation_results[0].status == "passed"
    assert outcome.feedbacks[0].evaluation_status == "passed"
    assert db.query(EvaluationModel).count() == 1
    assert db.query(FeedbackModel).count() == 1
