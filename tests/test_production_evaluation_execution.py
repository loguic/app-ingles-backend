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
)
from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_execution_service import (
    evaluate_and_save_candidate_semantic_production,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


@pytest.fixture()
def db():
    """Create an isolated database for end-to-end evaluation tests.

    Crea una base aislada para pruebas evaluativas de extremo a extremo.
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


def load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def create_production(
    db,
    *,
    prompt_id: str,
    turn_id: str,
    modality: str,
    response_text: str | None,
    audio_reference: str | None = None,
) -> LearnerProductionRecord:
    submission = SubmissionModel(
        user_id="b131-execution-user",
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


def test_passed_semantic_evaluation_is_persisted(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p1",
        turn_id="a1-u1-l1-c3-t2",
        modality="text",
        response_text="My name is Ana.",
    )

    records = evaluate_and_save_candidate_semantic_production(
        load_candidate(),
        "a1-u1-l1",
        production,
        db,
    )

    assert len(records) == 1
    assert records[0].evaluation_result_id > 0
    assert records[0].production_id == production.production_id
    assert records[0].status == "passed"


def test_failed_semantic_evaluation_is_persisted(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="text",
        response_text="Good morning.",
    )

    records = evaluate_and_save_candidate_semantic_production(
        load_candidate(),
        "a1-u1-l1",
        production,
        db,
    )

    assert records[0].status == "failed"
    assert db.query(EvaluationModel).count() == 1


def test_voice_transcript_is_evaluated_and_persisted(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="voice",
        response_text=None,
        audio_reference="local://origin.wav",
    )

    records = evaluate_and_save_candidate_semantic_production(
        load_candidate(),
        "a1-u1-l1",
        production,
        db,
        recognized_text="I am from Ecuador.",
    )

    assert records[0].status == "passed"
    assert records[0].production_id == production.production_id


def test_evaluation_error_does_not_persist_result(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p1",
        turn_id="a1-u1-l1-c3-t2",
        modality="text",
        response_text="My name is Ana.",
    )

    with pytest.raises(
        ValueError,
        match="No evaluation plan for lesson",
    ):
        evaluate_and_save_candidate_semantic_production(
            load_candidate(),
            "a1-u1-l99",
            production,
            db,
        )

    assert db.query(EvaluationModel).count() == 0
