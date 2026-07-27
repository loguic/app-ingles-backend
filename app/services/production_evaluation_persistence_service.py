from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    LearnerProduction as ProductionModel,
    ProductionEvaluationResult as EvaluationModel,
)
from app.schemas.evaluation import (
    ProductionEvaluationResult,
    ProductionEvaluationResultRecord,
)


def _build_result_record(
    result: EvaluationModel,
) -> ProductionEvaluationResultRecord:
    """Reconstruct one persisted evaluation result.

    Reconstruye un resultado evaluativo persistido.
    """
    return ProductionEvaluationResultRecord(
        evaluation_result_id=result.id,
        production_id=result.production_id,
        criterion_id=result.criterion_id,
        status=result.status,
        score=result.score,
        evaluator_id=result.evaluator_id,
        evaluator_version=result.evaluator_version,
        evaluated_at=result.evaluated_at,
    )


def save_production_evaluation_results(
    results: list[ProductionEvaluationResult],
    db: Session,
) -> list[ProductionEvaluationResultRecord]:
    """Persist one evaluation batch atomically.

    Persiste un lote de evaluaciones de forma atómica.
    """
    if not results:
        raise ValueError(
            "At least one production evaluation result is required"
        )

    production_ids = {
        result.production_id
        for result in results
    }
    existing_ids = {
        row[0]
        for row in (
            db.query(ProductionModel.id)
            .filter(ProductionModel.id.in_(production_ids))
            .all()
        )
    }
    missing_ids = sorted(production_ids - existing_ids)
    if missing_ids:
        raise ValueError(
            "Evaluation results reference unknown productions: "
            + ", ".join(str(item) for item in missing_ids)
        )

    persisted: list[EvaluationModel] = []

    try:
        for result in results:
            model = EvaluationModel(
                production_id=result.production_id,
                criterion_id=result.criterion_id,
                status=result.status,
                score=result.score,
                evaluator_id=result.evaluator_id,
                evaluator_version=result.evaluator_version,
                evaluated_at=result.evaluated_at,
            )
            db.add(model)
            persisted.append(model)

        db.flush()
        records = [
            _build_result_record(item)
            for item in persisted
        ]
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return records


def get_production_evaluation_results(
    production_id: int,
    db: Session,
) -> list[ProductionEvaluationResultRecord]:
    """Return the traceable evaluation history of one production.

    Devuelve el historial evaluativo trazable de una producción.
    """
    results = (
        db.query(EvaluationModel)
        .filter(EvaluationModel.production_id == production_id)
        .order_by(
            EvaluationModel.evaluated_at.asc(),
            EvaluationModel.id.asc(),
        )
        .all()
    )

    return [
        _build_result_record(item)
        for item in results
    ]
