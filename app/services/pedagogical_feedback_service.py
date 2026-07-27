from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResultRecord,
)
from app.schemas.pedagogical_feedback import (
    ProductionFeedback,
    ProductionFeedbackRule,
)
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate


def generate_pedagogical_feedback(
    result: ProductionEvaluationResultRecord,
    criterion: ProductionEvaluationCriterion,
    rule: ProductionFeedbackRule,
    *,
    generator_id: str = "deterministic-pedagogical-feedback",
    generator_version: str = "1.0",
) -> ProductionFeedback:
    """Generate feedback without altering the evaluation result.

    Genera feedback sin modificar el resultado evaluativo.
    """
    if result.criterion_id != criterion.id:
        raise ValueError(
            "Evaluation result criterion_id must match criterion"
        )

    if rule.criterion_id != criterion.id:
        raise ValueError(
            "Feedback rule criterion_id must match criterion"
        )

    if result.status == "passed":
        message = rule.passed_message
        guidance = rule.passed_guidance
    else:
        message = rule.failed_message
        guidance = rule.failed_guidance

    return ProductionFeedback(
        evaluation_result_id=result.evaluation_result_id,
        production_id=result.production_id,
        criterion_id=criterion.id,
        evaluation_status=result.status,
        criterion_description=criterion.description,
        message=message,
        guidance=guidance,
        generator_id=generator_id,
        generator_version=generator_version,
    )


def generate_candidate_pedagogical_feedback(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
    result: ProductionEvaluationResultRecord,
) -> ProductionFeedback:
    """Resolve criterion and feedback rule from one candidate.

    Resuelve criterio y regla de feedback desde una candidata.
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

    criterion = next(
        (
            item
            for item in evaluation_plan.criteria
            if item.id == result.criterion_id
        ),
        None,
    )
    if criterion is None:
        raise ValueError(
            "Evaluation result references unknown criterion: "
            + result.criterion_id
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

    rule = next(
        (
            item
            for item in feedback_plan.rules
            if item.criterion_id == criterion.id
        ),
        None,
    )
    if rule is None:
        raise ValueError(
            "No feedback rule for criterion: " + criterion.id
        )

    return generate_pedagogical_feedback(
        result,
        criterion,
        rule,
    )
