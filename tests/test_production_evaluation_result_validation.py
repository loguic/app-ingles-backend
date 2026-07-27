from datetime import UTC, datetime

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResult,
)
from app.services.production_evaluation_validation_service import (
    validate_production_evaluation_result,
)


def build_production() -> LearnerProductionRecord:
    """Build one captured text production. / Construye una producción de texto capturada."""
    return LearnerProductionRecord.model_validate(
        {
            "production_id": 7,
            "prompt_id": "a1-u1-l1-c3-p1",
            "turn_id": "a1-u1-l1-c3-t2",
            "modality": "text",
            "response_text": "My name is John.",
            "audio_reference": None,
        }
    )


def build_binary_criterion() -> ProductionEvaluationCriterion:
    """Build one binary semantic criterion. / Construye un criterio semántico binario."""
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


def build_result(
    *,
    status: str = "passed",
    score: float | None = None,
) -> ProductionEvaluationResult:
    """Build one traceable evaluation result. / Construye un resultado evaluativo trazable."""
    return ProductionEvaluationResult.model_validate(
        {
            "production_id": 7,
            "criterion_id": "a1-u1-l1-c3-p1-semantic",
            "status": status,
            "score": score,
            "evaluator_id": "test-evaluator",
            "evaluator_version": "1.0",
            "evaluated_at": datetime.now(UTC),
        }
    )


def test_binary_result_matches_production_and_criterion():
    validate_production_evaluation_result(
        build_production(),
        build_binary_criterion(),
        build_result(),
    )


def test_result_rejects_wrong_production_id():
    result = build_result().model_copy(
        update={"production_id": 8}
    )

    with pytest.raises(ValueError, match="production_id must match"):
        validate_production_evaluation_result(
            build_production(),
            build_binary_criterion(),
            result,
        )


def test_result_rejects_wrong_criterion_id():
    result = build_result().model_copy(
        update={"criterion_id": "other-criterion"}
    )

    with pytest.raises(ValueError, match="criterion_id must match"):
        validate_production_evaluation_result(
            build_production(),
            build_binary_criterion(),
            result,
        )


def test_result_rejects_wrong_prompt():
    production = build_production().model_copy(
        update={"prompt_id": "a1-u1-l1-c3-p2"}
    )

    with pytest.raises(ValueError, match="prompt must match"):
        validate_production_evaluation_result(
            production,
            build_binary_criterion(),
            build_result(),
        )


def test_result_rejects_incompatible_modality():
    criterion = build_binary_criterion().model_copy(
        update={"applicable_modalities": ["voice"]}
    )

    with pytest.raises(ValueError, match="modality is not applicable"):
        validate_production_evaluation_result(
            build_production(),
            criterion,
            build_result(),
        )


def test_binary_result_rejects_score():
    with pytest.raises(ValueError, match="cannot define score"):
        validate_production_evaluation_result(
            build_production(),
            build_binary_criterion(),
            build_result(score=0.9),
        )


def test_score_result_requires_score():
    criterion = build_binary_criterion().model_copy(
        update={
            "measurement_mode": "score",
            "success_threshold": 0.8,
        }
    )

    with pytest.raises(ValueError, match="requires score"):
        validate_production_evaluation_result(
            build_production(),
            criterion,
            build_result(),
        )


def test_score_result_status_matches_threshold():
    criterion = build_binary_criterion().model_copy(
        update={
            "measurement_mode": "score",
            "success_threshold": 0.8,
        }
    )

    with pytest.raises(ValueError, match="status must match score threshold"):
        validate_production_evaluation_result(
            build_production(),
            criterion,
            build_result(status="passed", score=0.4),
        )
