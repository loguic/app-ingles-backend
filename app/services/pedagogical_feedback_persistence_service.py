from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    ProductionEvaluationResult as EvaluationModel,
    ProductionFeedback as FeedbackModel,
)
from app.schemas.pedagogical_feedback import (
    ProductionFeedback,
    ProductionFeedbackRecord,
)


def _build_feedback_record(
    feedback: FeedbackModel,
    evaluation: EvaluationModel,
) -> ProductionFeedbackRecord:
    """Reconstruct persisted feedback with evaluation traceability.

    Reconstruye feedback persistido con trazabilidad evaluativa.
    """
    return ProductionFeedbackRecord(
        feedback_id=feedback.id,
        evaluation_result_id=evaluation.id,
        production_id=evaluation.production_id,
        criterion_id=evaluation.criterion_id,
        evaluation_status=evaluation.status,
        criterion_description=feedback.criterion_description,
        message=feedback.message,
        guidance=feedback.guidance,
        generator_id=feedback.generator_id,
        generator_version=feedback.generator_version,
        generated_at=feedback.generated_at,
    )


def save_production_feedback(
    feedback: ProductionFeedback,
    db: Session,
    *,
    commit_transaction: bool = True,
) -> ProductionFeedbackRecord:
    """Persist one traceable feedback item without overwriting history.

    Persiste un feedback trazable sin sobrescribir el historial.
    """
    evaluation = (
        db.query(EvaluationModel)
        .filter(
            EvaluationModel.id
            == feedback.evaluation_result_id
        )
        .one_or_none()
    )
    if evaluation is None:
        raise ValueError(
            "Feedback references unknown evaluation result: "
            + str(feedback.evaluation_result_id)
        )

    if evaluation.production_id != feedback.production_id:
        raise ValueError(
            "Feedback production_id must match evaluation result"
        )
    if evaluation.criterion_id != feedback.criterion_id:
        raise ValueError(
            "Feedback criterion_id must match evaluation result"
        )
    if evaluation.status != feedback.evaluation_status:
        raise ValueError(
            "Feedback status must match evaluation result"
        )

    model = FeedbackModel(
        evaluation_result_id=evaluation.id,
        criterion_description=feedback.criterion_description,
        message=feedback.message,
        guidance=feedback.guidance,
        generator_id=feedback.generator_id,
        generator_version=feedback.generator_version,
    )

    try:
        db.add(model)
        db.flush()
        db.refresh(model)
        record = _build_feedback_record(
            model,
            evaluation,
        )
        if commit_transaction:
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return record


def get_production_feedback_by_evaluation_result(
    evaluation_result_id: int,
    db: Session,
) -> list[ProductionFeedbackRecord]:
    """Return feedback history for one persisted evaluation.

    Devuelve el historial de feedback de una evaluación persistida.
    """
    evaluation = (
        db.query(EvaluationModel)
        .filter(EvaluationModel.id == evaluation_result_id)
        .one_or_none()
    )
    if evaluation is None:
        return []

    rows = (
        db.query(FeedbackModel)
        .filter(
            FeedbackModel.evaluation_result_id
            == evaluation_result_id
        )
        .order_by(
            FeedbackModel.generated_at.asc(),
            FeedbackModel.id.asc(),
        )
        .all()
    )

    return [
        _build_feedback_record(row, evaluation)
        for row in rows
    ]
