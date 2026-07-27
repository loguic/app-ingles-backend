from sqlalchemy.orm import Session

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_persistence_service import (
    save_production_evaluation_results,
)
from app.services.semantic_evaluation_service import (
    evaluate_candidate_semantic_production,
)


def evaluate_and_save_candidate_semantic_production(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
    production: LearnerProductionRecord,
    db: Session,
    *,
    recognized_text: str | None = None,
) -> list[ProductionEvaluationResultRecord]:
    """Evaluate and persist one already captured learner production.

    Evalúa y persiste una producción del estudiante ya capturada.
    """
    results = evaluate_candidate_semantic_production(
        candidate,
        lesson_id,
        production,
        recognized_text=recognized_text,
    )

    return save_production_evaluation_results(
        results,
        db,
    )
