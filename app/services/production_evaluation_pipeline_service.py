from sqlalchemy.orm import Session

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.production_evaluation_outcome import (
    ProductionEvaluationOutcome,
)
from app.schemas.production_evaluation_runtime import (
    ProductionEvaluationRuntimeConfig,
)
from app.services.pedagogical_feedback_persistence_service import (
    save_production_feedback,
)
from app.services.pedagogical_feedback_service import (
    generate_pedagogical_feedback,
)
from app.services.production_evaluation_persistence_service import (
    save_production_evaluation_results,
)
from app.services.semantic_evaluation_service import (
    evaluate_semantic_production_from_plan,
)


def evaluate_production_atomically(
    config: ProductionEvaluationRuntimeConfig,
    production: LearnerProductionRecord,
    db: Session,
    *,
    recognized_text: str | None = None,
) -> ProductionEvaluationOutcome:
    """Evaluate, persist, generate feedback and commit atomically.

    Evalúa, persiste, genera feedback y confirma todo atómicamente.
    """
    try:
        evaluation_results = (
            evaluate_semantic_production_from_plan(
                production,
                config.evaluation_plan,
                recognized_text=recognized_text,
            )
        )

        persisted_results = save_production_evaluation_results(
            evaluation_results,
            db,
            commit_transaction=False,
        )

        feedbacks = []
        for result in persisted_results:
            criterion = next(
                item
                for item in config.evaluation_plan.criteria
                if item.id == result.criterion_id
            )
            rule = next(
                item
                for item in config.feedback_plan.rules
                if item.criterion_id == criterion.id
            )
            feedback = generate_pedagogical_feedback(
                result,
                criterion,
                rule,
            )
            feedbacks.append(
                save_production_feedback(
                    feedback,
                    db,
                    commit_transaction=False,
                )
            )

        outcome = ProductionEvaluationOutcome(
            production_id=production.production_id,
            evaluation_results=persisted_results,
            feedbacks=feedbacks,
        )

        db.commit()
        return outcome
    except Exception:
        db.rollback()
        raise
