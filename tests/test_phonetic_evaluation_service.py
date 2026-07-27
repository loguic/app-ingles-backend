from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
    ProductionEvaluationResult as EvaluationModel,
)

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.phonetic_evidence import PhoneticEvaluationEvidence
from app.services.phonetic_evaluation_service import (
    evaluate_phonetic_production_from_evidence,
)


@pytest.fixture()
def db():
    """Create an isolated database for phonetic persistence tests.

    Crea una base aislada para pruebas de persistencia fonética.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def create_persisted_voice_production(db):
    """Persist one real voice production for traceability tests.

    Persiste una producción de voz real para pruebas de trazabilidad.
    """
    submission = SubmissionModel(
        user_id="b136-user",
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
        modality="voice",
        response_text=None,
        audio_reference="local://learner-introduction.wav",
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


def build_production():
    return LearnerProductionRecord(
        production_id=7,
        prompt_id="a1-u1-l1-c3-p1",
        turn_id="a1-u1-l1-c3-t2",
        modality="voice",
        audio_reference="local://learner-introduction.wav",
    )


def build_criterion():
    return ProductionEvaluationCriterion(
        id="a1-u1-l1-c3-p1-phonetic",
        evidence_definition_id="a1-u1-l1-c3-p1-evidence",
        conversation_id="a1-u1-l1-c3",
        prompt_id="a1-u1-l1-c3-p1",
        dimension="phonetic",
        description="Pronounce the introduction clearly.",
        measurement_mode="score",
        success_threshold=0.75,
        applicable_modalities=["voice"],
    )


def build_evidence(score=0.82):
    return PhoneticEvaluationEvidence(
        production_id=7,
        criterion_id="a1-u1-l1-c3-p1-phonetic",
        audio_reference="local://learner-introduction.wav",
        score=score,
        analyzer_id="test-acoustic-analyzer",
        analyzer_version="1.0",
        analyzed_at=datetime.now(timezone.utc),
    )


def test_phonetic_evidence_above_threshold_passes():
    result = evaluate_phonetic_production_from_evidence(
        build_production(),
        build_criterion(),
        build_evidence(0.82),
    )

    assert result.status == "passed"
    assert result.score == 0.82
    assert result.evaluator_id == "test-acoustic-analyzer"
    assert result.evaluator_version == "1.0"


def test_phonetic_evidence_below_threshold_fails():
    result = evaluate_phonetic_production_from_evidence(
        build_production(),
        build_criterion(),
        build_evidence(0.60),
    )

    assert result.status == "failed"
    assert result.score == 0.60


def test_phonetic_evidence_rejects_score_out_of_range():
    with pytest.raises(ValidationError):
        build_evidence(1.01)


def test_phonetic_evaluator_rejects_semantic_criterion():
    criterion = build_criterion().model_copy(
        update={
            "dimension": "semantic",
            "applicable_modalities": ["text", "voice"],
        }
    )

    with pytest.raises(
        ValueError,
        match="requires phonetic criterion",
    ):
        evaluate_phonetic_production_from_evidence(
            build_production(),
            criterion,
            build_evidence(),
        )


def test_phonetic_evaluator_rejects_binary_measurement():
    criterion = build_criterion().model_copy(
        update={
            "measurement_mode": "binary",
            "success_threshold": None,
        }
    )

    with pytest.raises(
        ValueError,
        match="requires score measurement",
    ):
        evaluate_phonetic_production_from_evidence(
            build_production(),
            criterion,
            build_evidence(),
        )


def test_phonetic_evaluator_rejects_other_production_evidence():
    evidence = build_evidence().model_copy(
        update={"production_id": 99}
    )

    with pytest.raises(
        ValueError,
        match="does not match production",
    ):
        evaluate_phonetic_production_from_evidence(
            build_production(),
            build_criterion(),
            evidence,
        )


def test_phonetic_evaluator_rejects_other_audio_evidence():
    evidence = build_evidence().model_copy(
        update={"audio_reference": "local://other.wav"}
    )

    with pytest.raises(
        ValueError,
        match="does not match production audio",
    ):
        evaluate_phonetic_production_from_evidence(
            build_production(),
            build_criterion(),
            evidence,
        )


def test_phonetic_result_uses_existing_evaluation_persistence(db):
    from app.services.production_evaluation_persistence_service import (
        save_production_evaluation_results,
    )

    production = create_persisted_voice_production(db)
    evidence = build_evidence(0.82).model_copy(
        update={"production_id": production.production_id}
    )

    result = evaluate_phonetic_production_from_evidence(
        production,
        build_criterion(),
        evidence,
    )

    persisted = save_production_evaluation_results(
        [result],
        db,
    )

    assert len(persisted) == 1
    assert persisted[0].production_id == production.production_id
    assert persisted[0].criterion_id == result.criterion_id
    assert persisted[0].score == 0.82
    assert persisted[0].evaluator_id == "test-acoustic-analyzer"
    assert persisted[0].evaluator_version == "1.0"

    row = db.query(EvaluationModel).one()
    assert row.production_id == production.production_id
    assert row.score == 0.82
