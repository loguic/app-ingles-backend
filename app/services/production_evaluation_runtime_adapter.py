from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.schemas.production_evaluation_runtime import (
    ProductionEvaluationRuntimeConfig,
)


def build_runtime_evaluation_config_from_candidate(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
) -> ProductionEvaluationRuntimeConfig:
    """Adapt isolated candidate plans to the neutral runtime contract.

    Adapta planes de candidata aislada al contrato runtime neutral.
    """
    evaluation_plan = next(
        (
            plan
            for plan in candidate.evaluation_plans
            if plan.lesson_id == lesson_id
        ),
        None,
    )
    if evaluation_plan is None:
        raise ValueError(
            "No evaluation plan for lesson: " + lesson_id
        )

    feedback_plan = next(
        (
            plan
            for plan in candidate.feedback_plans
            if plan.lesson_id == lesson_id
        ),
        None,
    )
    if feedback_plan is None:
        raise ValueError(
            "No feedback plan for lesson: " + lesson_id
        )

    return ProductionEvaluationRuntimeConfig(
        lesson_id=lesson_id,
        evaluation_plan=evaluation_plan,
        feedback_plan=feedback_plan,
    )
