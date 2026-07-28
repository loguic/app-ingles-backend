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
from app.services.phonetic_analyzer import PhoneticAnalyzer
from app.services.phonetic_evaluation_execution_service import (
    evaluate_phonetic_production_from_plan,
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
    phonetic_analyzer: PhoneticAnalyzer | None = None,
    phonetic_reference_text: str | None = None,
) -> ProductionEvaluationOutcome:
    """Evaluate, persist, generate feedback and commit atomically.

    Evalúa, persiste, genera feedback y confirma todo atómicamente.
    """
    try:
        evaluation_results = []

        has_semantic_criterion = any(
            criterion.prompt_id == production.prompt_id
            and criterion.dimension == "semantic"
            and production.modality in criterion.applicable_modalities
            for criterion in config.evaluation_plan.criteria
        )
        if has_semantic_criterion:
            evaluation_results.extend(
                evaluate_semantic_production_from_plan(
                    production,
                    config.evaluation_plan,
                    recognized_text=recognized_text,
                )
            )

        has_phonetic_criterion = any(
            criterion.prompt_id == production.prompt_id
            and criterion.dimension == "phonetic"
            and production.modality in criterion.applicable_modalities
            for criterion in config.evaluation_plan.criteria
        )
        if has_phonetic_criterion:
            if phonetic_analyzer is None:
                raise ValueError(
                    "Phonetic evaluation requires analyzer"
                )
            if phonetic_reference_text is None:
                raise ValueError(
                    "Phonetic evaluation requires reference text"
                )

            evaluation_results.extend(
                evaluate_phonetic_production_from_plan(
                    production,
                    config.evaluation_plan,
                    phonetic_analyzer,
                    reference_text=phonetic_reference_text,
                )
            )

        if not evaluation_results:
            raise ValueError(
                "No applicable evaluation criterion for production prompt: "
                + production.prompt_id
            )

        persisted_results = save_production_evaluation_results(
            evaluation_results,
            db,
            commit_transaction=False,
        )

        feedbacks = []
        feedback_rules_by_criterion = {
            rule.criterion_id: rule
            for rule in config.feedback_plan.rules
        }

        for result in persisted_results:
            criterion = next(
                item
                for item in config.evaluation_plan.criteria
                if item.id == result.criterion_id
            )
            rule = feedback_rules_by_criterion.get(criterion.id)
            if rule is None:
                if criterion.dimension == "phonetic":
                    continue
                raise ValueError(
                    "Semantic evaluation requires feedback rule: "
                    + criterion.id
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
