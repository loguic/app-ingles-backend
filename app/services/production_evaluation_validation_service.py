from app.schemas.content import Lesson
from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResult,
)
from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


def validate_production_evaluation_criteria(
    lesson: Lesson,
    criteria: list[ProductionEvaluationCriterion],
) -> None:
    """Validate evaluation criteria against one lesson.

    Valida los criterios de evaluación contra una lección.
    """
    criterion_ids = [criterion.id for criterion in criteria]
    if len(criterion_ids) != len(set(criterion_ids)):
        raise ValueError("Production evaluation criterion IDs must be unique")

    if lesson.experience is None:
        raise ValueError(
            "Production evaluation criteria require LessonExperience"
        )

    evidence_by_id = {
        evidence.id: evidence
        for evidence in lesson.experience.evidence_definitions
    }
    conversations_by_id = {
        conversation.id: conversation
        for conversation in lesson.conversations
    }

    for criterion in criteria:
        evidence = evidence_by_id.get(
            criterion.evidence_definition_id
        )
        if evidence is None:
            raise ValueError(
                "Evaluation criterion "
                + criterion.id
                + " references unknown evidence: "
                + criterion.evidence_definition_id
            )

        if evidence.activity_id != criterion.conversation_id:
            raise ValueError(
                "Evaluation criterion "
                + criterion.id
                + " conversation must match evidence activity"
            )

        conversation = conversations_by_id.get(
            criterion.conversation_id
        )
        if conversation is None:
            raise ValueError(
                "Evaluation criterion "
                + criterion.id
                + " references unknown conversation: "
                + criterion.conversation_id
            )

        prompts_by_id = {
            turn.production_prompt.id: turn.production_prompt
            for turn in conversation.turns
            if turn.production_prompt is not None
        }
        prompt = prompts_by_id.get(criterion.prompt_id)

        if prompt is None:
            raise ValueError(
                "Evaluation criterion "
                + criterion.id
                + " references unknown production prompt: "
                + criterion.prompt_id
            )

        unsupported_modalities = sorted(
            set(criterion.applicable_modalities)
            - set(prompt.accepted_modalities)
        )
        if unsupported_modalities:
            raise ValueError(
                "Evaluation criterion "
                + criterion.id
                + " uses modalities not accepted by prompt "
                + criterion.prompt_id
                + ": "
                + ", ".join(unsupported_modalities)
            )

def validate_production_evaluation_result(
    production: LearnerProductionRecord,
    criterion: ProductionEvaluationCriterion,
    result: ProductionEvaluationResult,
) -> None:
    """Validate one evaluation result against its production and criterion.

    Valida un resultado de evaluación contra su producción y criterio.
    """
    if result.production_id != production.production_id:
        raise ValueError(
            "Evaluation result production_id must match learner production"
        )

    if result.criterion_id != criterion.id:
        raise ValueError(
            "Evaluation result criterion_id must match criterion"
        )

    if production.prompt_id != criterion.prompt_id:
        raise ValueError(
            "Learner production prompt must match evaluation criterion"
        )

    if production.modality not in criterion.applicable_modalities:
        raise ValueError(
            "Learner production modality is not applicable to criterion"
        )

    if criterion.measurement_mode == "binary":
        if result.score is not None:
            raise ValueError(
                "Binary evaluation result cannot define score"
            )
        return

    if result.score is None:
        raise ValueError(
            "Score evaluation result requires score"
        )

    threshold = criterion.success_threshold
    if threshold is None:
        raise ValueError(
            "Score evaluation criterion requires success_threshold"
        )

    expected_status = (
        "passed"
        if result.score >= threshold
        else "failed"
    )
    if result.status != expected_status:
        raise ValueError(
            "Evaluation result status must match score threshold"
        )


def validate_candidate_production_evaluation_plans(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate all production evaluation plans in one candidate.

    Valida todos los planes de evaluación de producción de una candidata.
    """
    lessons_by_id = {
        lesson.id: lesson
        for lesson in candidate.candidate_unit.lessons
    }
    findings: list[ValidationFinding] = []

    for plan in candidate.evaluation_plans:
        lesson = lessons_by_id[plan.lesson_id]

        try:
            validate_production_evaluation_criteria(
                lesson,
                plan.criteria,
            )
        except ValueError as error:
            findings.append(
                ValidationFinding(
                    validator_id="production_evaluation_integrity",
                    severity="error",
                    message=str(error),
                    reference_ids=[
                        plan.lesson_id,
                        *[
                            criterion.id
                            for criterion in plan.criteria
                        ],
                    ],
                )
            )

    return findings

