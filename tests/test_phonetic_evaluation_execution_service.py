from datetime import UTC, datetime

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    LessonProductionEvaluationPlan,
    ProductionEvaluationCriterion,
)
from app.schemas.phonetic_evidence import PhoneticEvaluationEvidence
from app.services.phonetic_evaluation_execution_service import (
    evaluate_phonetic_production_from_plan,
)


def make_voice_production():
    return LearnerProductionRecord(
        production_id=7,
        prompt_id="a1-test-p1",
        turn_id="a1-test-t1",
        modality="voice",
        response_text=None,
        audio_reference="production-audio://11111111-1111-1111-1111-111111111111",
    )


def make_phonetic_plan():
    return LessonProductionEvaluationPlan(
        lesson_id="a1-test",
        criteria=[
            ProductionEvaluationCriterion(
                id="pronunciation-target",
                evidence_definition_id="evidence-pronunciation",
                conversation_id="a1-test-c1",
                prompt_id="a1-test-p1",
                dimension="phonetic",
                description="Pronounce the target phrase clearly.",
                measurement_mode="score",
                success_threshold=0.80,
                applicable_modalities=["voice"],
            )
        ],
    )


class FakePhoneticAnalyzer:
    def __init__(self, score=0.91):
        self.score = score
        self.calls = []

    def analyze(self, production, criterion, *, reference_text):
        self.calls.append((production, criterion, reference_text))
        return PhoneticEvaluationEvidence(
            production_id=production.production_id,
            criterion_id=criterion.id,
            audio_reference=production.audio_reference,
            score=self.score,
            analyzer_id="fake-phonetic",
            analyzer_version="1.0",
            analyzed_at=datetime(2026, 7, 28, tzinfo=UTC),
        )


def test_executes_phonetic_analyzer_and_returns_result():
    production = make_voice_production()
    analyzer = FakePhoneticAnalyzer()

    results = evaluate_phonetic_production_from_plan(
        production,
        make_phonetic_plan(),
        analyzer,
        reference_text="Hello, I am John.",
    )

    assert len(results) == 1
    assert results[0].status == "passed"
    assert results[0].score == 0.91
    assert results[0].evaluator_id == "fake-phonetic"
    assert analyzer.calls[0][2] == "Hello, I am John."


def test_requires_non_blank_reference_text():
    with pytest.raises(
        ValueError,
        match="Phonetic analysis requires non-blank reference text",
    ):
        evaluate_phonetic_production_from_plan(
            make_voice_production(),
            make_phonetic_plan(),
            FakePhoneticAnalyzer(),
            reference_text="   ",
        )


def test_returns_empty_when_plan_has_no_applicable_phonetic_criterion():
    plan = LessonProductionEvaluationPlan(
        lesson_id="a1-test",
        criteria=[
            ProductionEvaluationCriterion(
                id="semantic-target",
                evidence_definition_id="evidence-semantic",
                conversation_id="a1-test-c1",
                prompt_id="a1-test-p1",
                dimension="semantic",
                description="Provide the requested information.",
                measurement_mode="binary",
                applicable_modalities=["voice"],
            )
        ],
    )

    results = evaluate_phonetic_production_from_plan(
        make_voice_production(),
        plan,
        FakePhoneticAnalyzer(),
        reference_text="Hello, I am John.",
    )

    assert results == []
