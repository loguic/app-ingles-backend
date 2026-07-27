from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResult,
)
from app.schemas.phonetic_evidence import PhoneticEvaluationEvidence


def evaluate_phonetic_production_from_evidence(
    production: LearnerProductionRecord,
    criterion: ProductionEvaluationCriterion,
    evidence: PhoneticEvaluationEvidence,
) -> ProductionEvaluationResult:
    """Convert trusted acoustic evidence into a pedagogical result.

    Convierte evidencia acústica confiable en un resultado pedagógico.
    """
    if production.modality != "voice":
        raise ValueError(
            "Phonetic evaluation requires voice production"
        )

    if criterion.dimension != "phonetic":
        raise ValueError(
            "Phonetic evaluator requires phonetic criterion"
        )

    if criterion.measurement_mode != "score":
        raise ValueError(
            "Phonetic evidence evaluator requires score measurement"
        )

    if criterion.prompt_id != production.prompt_id:
        raise ValueError(
            "Evaluation criterion does not match production prompt"
        )

    if evidence.production_id != production.production_id:
        raise ValueError(
            "Phonetic evidence does not match production"
        )

    if evidence.criterion_id != criterion.id:
        raise ValueError(
            "Phonetic evidence does not match criterion"
        )

    if evidence.audio_reference != production.audio_reference:
        raise ValueError(
            "Phonetic evidence does not match production audio"
        )

    threshold = criterion.success_threshold
    if threshold is None:
        raise ValueError(
            "Phonetic score criterion requires success threshold"
        )

    return ProductionEvaluationResult(
        production_id=production.production_id,
        criterion_id=criterion.id,
        status="passed" if evidence.score >= threshold else "failed",
        score=evidence.score,
        evaluator_id=evidence.analyzer_id,
        evaluator_version=evidence.analyzer_version,
        evaluated_at=evidence.analyzed_at,
    )
