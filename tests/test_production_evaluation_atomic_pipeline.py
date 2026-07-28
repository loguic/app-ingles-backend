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
from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.phonetic_evidence import PhoneticEvaluationEvidence
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_runtime_adapter import (
    build_runtime_evaluation_config_from_candidate,
)
from app.services.production_evaluation_pipeline_service import (
    evaluate_production_atomically,
)
from app.services.production_audio_phonetic_analyzer import (
    ProductionAudioPhoneticAnalyzer,
)
from app.services.production_audio_storage_service import (
    store_production_audio,
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
        build_runtime_evaluation_config_from_candidate(
            load_candidate(),
            "a1-u1-l1",
        ),
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


def test_pipeline_rolls_back_evaluation_if_feedback_fails(
    db,
    monkeypatch,
):
    production = create_production(db)
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )

    def fail_feedback_generation(*args, **kwargs):
        raise ValueError("Forced feedback failure")

    monkeypatch.setattr(
        "app.services.production_evaluation_pipeline_service."
        "generate_pedagogical_feedback",
        fail_feedback_generation,
    )

    with pytest.raises(
        ValueError,
        match="Forced feedback failure",
    ):
        evaluate_production_atomically(
            config,
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
        build_runtime_evaluation_config_from_candidate(
            load_candidate(),
            "a1-u1-l1",
        ),
        production,
        db,
        recognized_text="I am from Ecuador.",
    )

    assert outcome.evaluation_results[0].status == "passed"
    assert outcome.feedbacks[0].evaluation_status == "passed"
    assert db.query(EvaluationModel).count() == 1
    assert db.query(FeedbackModel).count() == 1

class FakePhoneticAnalyzer:
    # Return traceable acoustic evidence without real model execution.
    # Devuelve evidencia acústica trazable sin ejecutar un modelo real.
    def analyze(self, production, criterion, *, reference_text):
        assert reference_text == "I am from Ecuador."
        return PhoneticEvaluationEvidence(
            production_id=production.production_id,
            criterion_id=criterion.id,
            audio_reference=production.audio_reference,
            score=0.91,
            analyzer_id="fake-phonetic",
            analyzer_version="1.0",
            analyzed_at=datetime(2026, 7, 28, tzinfo=UTC),
        )


def build_semantic_and_phonetic_config():
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )

    phonetic_criterion = ProductionEvaluationCriterion(
        id="pronunciation-origin",
        evidence_definition_id="a1-pronunciation-origin",
        conversation_id="a1-u1-l1-c3",
        prompt_id="a1-u1-l1-c3-p2",
        dimension="phonetic",
        description="Pronounce the origin response clearly.",
        measurement_mode="score",
        success_threshold=0.80,
        applicable_modalities=["voice"],
    )

    evaluation_plan = config.evaluation_plan.model_copy(
        update={
            "criteria": [
                *config.evaluation_plan.criteria,
                phonetic_criterion,
            ]
        }
    )

    return config.model_copy(
        update={"evaluation_plan": evaluation_plan}
    )


def test_pipeline_combines_semantic_and_phonetic_results(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="voice",
        response_text=None,
        audio_reference=(
            "production-audio://"
            "11111111-1111-1111-1111-111111111111"
        ),
    )

    outcome = evaluate_production_atomically(
        build_semantic_and_phonetic_config(),
        production,
        db,
        recognized_text="I am from Ecuador.",
        phonetic_analyzer=FakePhoneticAnalyzer(),
        phonetic_reference_text="I am from Ecuador.",
    )

    evaluations = {
        result.criterion_id: result
        for result in outcome.evaluation_results
    }

    assert len(evaluations) == 2
    assert evaluations["pronunciation-origin"].score == 0.91
    assert evaluations["pronunciation-origin"].status == "passed"
    assert evaluations["pronunciation-origin"].evaluator_id == (
        "fake-phonetic"
    )
    assert len(outcome.feedbacks) == 1
    assert db.query(EvaluationModel).count() == 2
    assert db.query(FeedbackModel).count() == 1


def test_pipeline_rolls_back_when_phonetic_analyzer_is_missing(db):
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="voice",
        response_text=None,
        audio_reference=(
            "production-audio://"
            "11111111-1111-1111-1111-111111111111"
        ),
    )

    with pytest.raises(
        ValueError,
        match="Phonetic evaluation requires analyzer",
    ):
        evaluate_production_atomically(
            build_semantic_and_phonetic_config(),
            production,
            db,
            recognized_text="I am from Ecuador.",
            phonetic_reference_text="I am from Ecuador.",
        )

    assert db.query(EvaluationModel).count() == 0
    assert db.query(FeedbackModel).count() == 0
    assert db.query(ProductionModel).count() == 1

class FakeStoredAudioScorer:
    def __init__(self):
        self.calls = []

    def score(self, audio_path, *, reference_text):
        from app.schemas.phonetic_evidence import (
            AcousticPhoneticMeasurement,
        )

        self.calls.append((audio_path, reference_text))
        return AcousticPhoneticMeasurement(
            score=0.94,
            analyzer_id="fake-stored-audio",
            analyzer_version="1.0",
            analyzed_at=datetime(2026, 7, 28, tzinfo=UTC),
        )


def test_pipeline_resolves_private_audio_for_phonetic_evaluation(
    db,
    tmp_path,
):
    upload = store_production_audio(
        b"RIFF" + bytes(4) + b"WAVE" + bytes(16),
        storage_dir=tmp_path,
    )
    production = create_production(
        db,
        prompt_id="a1-u1-l1-c3-p2",
        turn_id="a1-u1-l1-c3-t4",
        modality="voice",
        response_text=None,
        audio_reference=upload.audio_reference,
    )
    scorer = FakeStoredAudioScorer()
    analyzer = ProductionAudioPhoneticAnalyzer(
        scorer,
        storage_dir=tmp_path,
    )

    outcome = evaluate_production_atomically(
        build_semantic_and_phonetic_config(),
        production,
        db,
        recognized_text="I am from Ecuador.",
        phonetic_analyzer=analyzer,
        phonetic_reference_text="I am from Ecuador.",
    )

    phonetic = next(
        result
        for result in outcome.evaluation_results
        if result.criterion_id == "pronunciation-origin"
    )

    assert phonetic.score == 0.94
    assert phonetic.evaluator_id == "fake-stored-audio"
    assert len(scorer.calls) == 1
    assert scorer.calls[0][0].is_file()
    assert scorer.calls[0][0].parent == tmp_path.resolve()
    assert scorer.calls[0][1] == "I am from Ecuador."
    assert db.query(EvaluationModel).count() == 2
    assert db.query(FeedbackModel).count() == 1


def test_pipeline_still_requires_feedback_for_semantic_result(db):
    production = create_production(db)
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )
    config = config.model_copy(
        update={
            "feedback_plan": config.feedback_plan.model_copy(
                update={"rules": []}
            )
        }
    )

    with pytest.raises(
        ValueError,
        match="Semantic evaluation requires feedback rule",
    ):
        evaluate_production_atomically(
            config,
            production,
            db,
        )

    assert db.query(EvaluationModel).count() == 0
    assert db.query(FeedbackModel).count() == 0
