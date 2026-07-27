import re
from datetime import UTC, datetime

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    LessonProductionEvaluationPlan,
    ProductionEvaluationCriterion,
    ProductionEvaluationResult,
)
from app.schemas.semantic_evaluation import SemanticEvaluationRule
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_validation_service import (
    validate_production_evaluation_result,
)


def evaluate_semantic_production(
    production: LearnerProductionRecord,
    criterion: ProductionEvaluationCriterion,
    rule: SemanticEvaluationRule,
    *,
    recognized_text: str | None = None,
    evaluator_id: str = "deterministic-semantic",
    evaluator_version: str = "1.0",
    evaluated_at: datetime | None = None,
) -> ProductionEvaluationResult:
    """Evaluate one production with an explicit deterministic rule.

    Evalúa una producción mediante una regla determinista explícita.
    """
    if criterion.dimension != "semantic":
        raise ValueError(
            "Semantic evaluator requires semantic criterion"
        )

    if criterion.measurement_mode != "binary":
        raise ValueError(
            "Initial semantic evaluator requires binary measurement"
        )

    if rule.criterion_id != criterion.id:
        raise ValueError(
            "Semantic rule criterion_id must match criterion"
        )

    if production.modality == "text":
        evaluation_text = production.response_text
    else:
        evaluation_text = recognized_text

    if evaluation_text is None or not evaluation_text.strip():
        raise ValueError(
            "Semantic evaluation requires non-blank evaluation text"
        )

    flags = 0 if rule.case_sensitive else re.IGNORECASE
    passed = any(
        re.search(pattern, evaluation_text.strip(), flags) is not None
        for pattern in rule.patterns
    )

    result = ProductionEvaluationResult(
        production_id=production.production_id,
        criterion_id=criterion.id,
        status="passed" if passed else "failed",
        score=None,
        evaluator_id=evaluator_id,
        evaluator_version=evaluator_version,
        evaluated_at=evaluated_at or datetime.now(UTC),
    )

    validate_production_evaluation_result(
        production,
        criterion,
        result,
    )

    return result


def evaluate_semantic_production_from_plan(
    production: LearnerProductionRecord,
    plan: LessonProductionEvaluationPlan,
    *,
    recognized_text: str | None = None,
    evaluator_id: str = "deterministic-semantic",
    evaluator_version: str = "1.0",
    evaluated_at: datetime | None = None,
) -> list[ProductionEvaluationResult]:
    """Evaluate one production using semantic criteria declared by its plan.

    Evalúa una producción usando los criterios semánticos declarados por su plan.
    """
    criteria = [
        criterion
        for criterion in plan.criteria
        if criterion.prompt_id == production.prompt_id
        and criterion.dimension == "semantic"
        and production.modality in criterion.applicable_modalities
    ]

    if not criteria:
        raise ValueError(
            "No applicable semantic criterion for production prompt: "
            + production.prompt_id
        )

    rules_by_criterion_id = {
        rule.criterion_id: rule
        for rule in plan.semantic_rules
    }

    results: list[ProductionEvaluationResult] = []

    for criterion in criteria:
        rule = rules_by_criterion_id.get(criterion.id)
        if rule is None:
            raise ValueError(
                "Semantic criterion has no evaluation rule: "
                + criterion.id
            )

        results.append(
            evaluate_semantic_production(
                production,
                criterion,
                rule,
                recognized_text=recognized_text,
                evaluator_id=evaluator_id,
                evaluator_version=evaluator_version,
                evaluated_at=evaluated_at,
            )
        )

    return results

def evaluate_candidate_semantic_production(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
    production: LearnerProductionRecord,
    *,
    recognized_text: str | None = None,
) -> list[ProductionEvaluationResult]:
    """Evaluate one production using its lesson plan in a candidate.

    Evalúa una producción usando el plan de su lección en una candidata.
    """
    plans = [
        plan
        for plan in candidate.evaluation_plans
        if plan.lesson_id == lesson_id
    ]

    if not plans:
        raise ValueError(
            "No evaluation plan for lesson: " + lesson_id
        )

    return evaluate_semantic_production_from_plan(
        production,
        plans[0],
        recognized_text=recognized_text,
    )

