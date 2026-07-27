from sqlalchemy.orm import Session

from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.pedagogical_feedback import ProductionFeedbackRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_feedback_persistence_service import (
    save_production_feedback,
)
from app.services.pedagogical_feedback_service import (
    generate_candidate_pedagogical_feedback,
)


def generate_and_save_candidate_pedagogical_feedback(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
    result: ProductionEvaluationResultRecord,
    db: Session,
) -> ProductionFeedbackRecord:
    """Generate and persist feedback for one evaluation result.

    Genera y persiste feedback para un resultado evaluativo.
    """
    feedback = generate_candidate_pedagogical_feedback(
        candidate,
        lesson_id,
        result,
    )

    return save_production_feedback(
        feedback,
        db,
    )
