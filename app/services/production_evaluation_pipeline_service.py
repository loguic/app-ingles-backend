from sqlalchemy.orm import Session

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.schemas.production_evaluation_outcome import (
    ProductionEvaluationOutcome,
)
from app.services.pedagogical_feedback_persistence_service import (
    save_production_feedback,
)
from app.services.pedagogical_feedback_service import (
    generate_candidate_pedagogical_feedback,
)
from app.services.production_evaluation_persistence_service import (
    save_production_evaluation_results,
)
from app.services.semantic_evaluation_service import (
    evaluate_candidate_semantic_production,
)


def evaluate_production_atomically(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
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
            evaluate_candidate_semantic_production(
                candidate,
                lesson_id,
                production,
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
            feedback = generate_candidate_pedagogical_feedback(
                candidate,
                lesson_id,
                result,
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
