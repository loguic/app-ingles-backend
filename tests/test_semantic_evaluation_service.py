from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.semantic_evaluation import SemanticEvaluationRule
from app.services.semantic_evaluation_service import (
    evaluate_semantic_production,
)


def build_text_production() -> LearnerProductionRecord:
    return LearnerProductionRecord.model_validate(
        {
            "production_id": 1,
            "prompt_id": "a1-u1-l1-c3-p1",
            "turn_id": "a1-u1-l1-c3-t2",
            "modality": "text",
            "response_text": "My name is John.",
            "audio_reference": None,
        }
    )


def build_voice_production() -> LearnerProductionRecord:
    return LearnerProductionRecord.model_validate(
        {
            "production_id": 2,
            "prompt_id": "a1-u1-l1-c3-p1",
            "turn_id": "a1-u1-l1-c3-t2",
            "modality": "voice",
            "response_text": None,
            "audio_reference": "local://recording.wav",
        }
    )


def build_criterion() -> ProductionEvaluationCriterion:
    return ProductionEvaluationCriterion.model_validate(
        {
            "id": "a1-u1-l1-c3-p1-semantic",
            "evidence_definition_id": "a1-u1-l1-ev3",
            "conversation_id": "a1-u1-l1-c3",
            "prompt_id": "a1-u1-l1-c3-p1",
            "dimension": "semantic",
            "description": "The learner states a name.",
            "measurement_mode": "binary",
            "applicable_modalities": ["text", "voice"],
        }
    )


def build_rule() -> SemanticEvaluationRule:
    return SemanticEvaluationRule.model_validate(
        {
            "id": "a1-u1-l1-c3-p1-semantic-rule",
            "criterion_id": "a1-u1-l1-c3-p1-semantic",
            "patterns": [
                r"\bmy name is\s+[a-z][a-z-]*\b",
                r"\bi am\s+[a-z][a-z-]*\b",
                r"\bi\x27m\s+[a-z][a-z-]*\b",
            ],
        }
    )


def test_rule_rejects_duplicate_patterns():
    payload = build_rule().model_dump()
    payload["patterns"] = [r"\bhello\b", r"\bhello\b"]

    with pytest.raises(
        ValidationError,
        match="Semantic rule patterns must be unique",
    ):
        SemanticEvaluationRule.model_validate(payload)


def test_rule_rejects_invalid_regex():
    payload = build_rule().model_dump()
    payload["patterns"] = ["("]

    with pytest.raises(
        ValidationError,
        match="Semantic rule contains invalid regex",
    ):
        SemanticEvaluationRule.model_validate(payload)


def test_text_production_passes_matching_rule():
    result = evaluate_semantic_production(
        build_text_production(),
        build_criterion(),
        build_rule(),
        evaluated_at=datetime.now(UTC),
    )

    assert result.status == "passed"
    assert result.score is None


def test_text_production_fails_non_matching_rule():
    production = build_text_production().model_copy(
        update={"response_text": "Good morning."}
    )

    result = evaluate_semantic_production(
        production,
        build_criterion(),
        build_rule(),
    )

    assert result.status == "failed"


def test_voice_production_uses_recognized_text():
    result = evaluate_semantic_production(
        build_voice_production(),
        build_criterion(),
        build_rule(),
        recognized_text="Hello, I am John.",
    )

    assert result.status == "passed"
    assert result.production_id == 2


def test_semantic_evaluator_rejects_phonetic_criterion():
    criterion = build_criterion().model_copy(
        update={
            "dimension": "phonetic",
            "applicable_modalities": ["voice"],
        }
    )

    with pytest.raises(
        ValueError,
        match="requires semantic criterion",
    ):
        evaluate_semantic_production(
            build_voice_production(),
            criterion,
            build_rule(),
            recognized_text="I am John.",
        )


def test_semantic_evaluator_rejects_score_measurement():
    criterion = build_criterion().model_copy(
        update={
            "measurement_mode": "score",
            "success_threshold": 0.8,
        }
    )

    with pytest.raises(
        ValueError,
        match="requires binary measurement",
    ):
        evaluate_semantic_production(
            build_text_production(),
            criterion,
            build_rule(),
        )


def test_semantic_rule_must_match_criterion():
    rule = build_rule().model_copy(
        update={"criterion_id": "other-criterion"}
    )

    with pytest.raises(
        ValueError,
        match="criterion_id must match criterion",
    ):
        evaluate_semantic_production(
            build_text_production(),
            build_criterion(),
            rule,
        )


def test_voice_production_requires_recognized_text():
    with pytest.raises(
        ValueError,
        match="requires non-blank evaluation text",
    ):
        evaluate_semantic_production(
            build_voice_production(),
            build_criterion(),
            build_rule(),
            recognized_text="   ",
        )
