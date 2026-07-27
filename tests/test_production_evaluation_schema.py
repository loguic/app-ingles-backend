from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResult,
)


def build_criterion() -> dict:
    """Build one valid semantic criterion. / Construye un criterio semántico válido."""
    return {
        "id": "a1-u1-l1-c3-p1-semantic",
        "evidence_definition_id": "a1-u1-l1-ev3",
        "conversation_id": "a1-u1-l1-c3",
        "prompt_id": "a1-u1-l1-c3-p1",
        "dimension": "semantic",
        "description": "The learner states a name.",
        "measurement_mode": "binary",
        "success_threshold": None,
        "applicable_modalities": ["text", "voice"],
    }


def test_semantic_binary_criterion_is_valid():
    criterion = ProductionEvaluationCriterion.model_validate(
        build_criterion()
    )

    assert criterion.dimension == "semantic"
    assert criterion.applicable_modalities == ["text", "voice"]


def test_score_criterion_requires_threshold():
    payload = build_criterion()
    payload["measurement_mode"] = "score"

    with pytest.raises(
        ValidationError,
        match="Score evaluation criterion requires success_threshold",
    ):
        ProductionEvaluationCriterion.model_validate(payload)


def test_binary_criterion_rejects_threshold():
    payload = build_criterion()
    payload["success_threshold"] = 0.8

    with pytest.raises(
        ValidationError,
        match="Only score evaluation criterion",
    ):
        ProductionEvaluationCriterion.model_validate(payload)


def test_criterion_rejects_duplicate_modalities():
    payload = build_criterion()
    payload["applicable_modalities"] = ["voice", "voice"]

    with pytest.raises(
        ValidationError,
        match="Evaluation criterion modalities must be unique",
    ):
        ProductionEvaluationCriterion.model_validate(payload)


def test_phonetic_criterion_requires_voice_only():
    payload = build_criterion()
    payload["dimension"] = "phonetic"
    payload["applicable_modalities"] = ["text", "voice"]

    with pytest.raises(
        ValidationError,
        match="Phonetic evaluation criterion requires voice modality",
    ):
        ProductionEvaluationCriterion.model_validate(payload)


def test_evaluation_result_is_traceable_and_normalized():
    result = ProductionEvaluationResult.model_validate(
        {
            "production_id": 7,
            "criterion_id": "a1-u1-l1-c3-p1-semantic",
            "status": "passed",
            "score": 0.91,
            "evaluator_id": "semantic-evaluator",
            "evaluator_version": "1.0",
            "evaluated_at": datetime.now(UTC),
        }
    )

    assert result.production_id == 7
    assert result.status == "passed"
    assert result.score == 0.91
