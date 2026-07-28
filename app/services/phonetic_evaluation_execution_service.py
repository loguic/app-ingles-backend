from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    LessonProductionEvaluationPlan,
    ProductionEvaluationResult,
)
from app.services.phonetic_analyzer import PhoneticAnalyzer
from app.services.phonetic_evaluation_service import (
    evaluate_phonetic_production_from_evidence,
)


def evaluate_phonetic_production_from_plan(
    production: LearnerProductionRecord,
    plan: LessonProductionEvaluationPlan,
    analyzer: PhoneticAnalyzer,
    *,
    reference_text: str,
 ) -> list[ProductionEvaluationResult]:
    # Evaluate only applicable phonetic criteria through a neutral analyzer.
    # Evalúa solo criterios fonéticos aplicables mediante un analizador neutral.
    criteria = [
        criterion
        for criterion in plan.criteria
        if criterion.prompt_id == production.prompt_id
        and criterion.dimension == "phonetic"
        and production.modality in criterion.applicable_modalities
    ]

    if not criteria:
        return []

    if not reference_text.strip():
        raise ValueError("Phonetic analysis requires non-blank reference text")

    results: list[ProductionEvaluationResult] = []

    for criterion in criteria:
        evidence = analyzer.analyze(
            production,
            criterion,
            reference_text=reference_text,
        )
        results.append(
            evaluate_phonetic_production_from_evidence(
                production,
                criterion,
                evidence,
            )
        )

    return results
