from collections.abc import Callable

from app.schemas.content import (
    Conversation,
    ConversationChoice,
    ConversationTurn,
    EvidenceDefinition,
    ExerciseMCQ,
    LanguageSupportItem,
    LearnerProductionPrompt,
    Lesson,
    LessonStage,
    TransferPromptVariant,
)
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.pedagogical_unit import (
    LessonCapabilityClaim,
    PedagogicalUnitCandidate,
    ValidationFinding,
)
from app.schemas.semantic_evaluation import SemanticEvaluationRule
from app.services.pedagogical_capability_artifact_reference_validation import (
    CapabilityArtifactReference,
    build_lesson_capability_artifact_index,
)


VALIDATOR_ID = "capability_artifact_state_compatibility"


def _references_by_type(
    references: list[CapabilityArtifactReference],
) -> dict[str, list[CapabilityArtifactReference]]:
    grouped: dict[str, list[CapabilityArtifactReference]] = {}
    for reference in references:
        grouped.setdefault(reference.artifact_type, []).append(reference)
    return grouped


def _conversation_owners(
    lesson: Lesson,
) -> tuple[
    dict[str, Conversation],
    dict[str, tuple[Conversation, ConversationTurn]],
    dict[str, tuple[Conversation, ConversationTurn, ConversationChoice]],
    dict[str, tuple[Conversation, ConversationTurn, LearnerProductionPrompt]],
    dict[
        str,
        tuple[
            Conversation,
            ConversationTurn,
            LearnerProductionPrompt,
            TransferPromptVariant,
        ],
    ],
]:
    conversations = {
        conversation.id: conversation
        for conversation in lesson.conversations
    }
    turns: dict[str, tuple[Conversation, ConversationTurn]] = {}
    choices: dict[
        str,
        tuple[Conversation, ConversationTurn, ConversationChoice],
    ] = {}
    prompts: dict[
        str,
        tuple[Conversation, ConversationTurn, LearnerProductionPrompt],
    ] = {}
    variants: dict[
        str,
        tuple[
            Conversation,
            ConversationTurn,
            LearnerProductionPrompt,
            TransferPromptVariant,
        ],
    ] = {}

    for conversation in lesson.conversations:
        for turn in conversation.turns:
            turns[turn.id] = (conversation, turn)
            for choice in turn.choices:
                choices[choice.id] = (conversation, turn, choice)
            if turn.production_prompt is None:
                continue
            prompt = turn.production_prompt
            prompts[prompt.id] = (conversation, turn, prompt)
            for variant in prompt.transfer_variants:
                variants[variant.id] = (
                    conversation,
                    turn,
                    prompt,
                    variant,
                )

    return conversations, turns, choices, prompts, variants


def _has_presented_content(
    lesson: Lesson,
    stage: LessonStage,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> bool:
    if any(
        support.artifact.id in {
            reference.artifact.id
            for reference in grouped.get("LanguageSupportItem", [])
        }
        and stage.id in support.artifact.stage_ids
        for support in grouped.get("LanguageSupportItem", [])
    ):
        return True
    if grouped.get("Example"):
        return True

    conversations, turns, _, _, _ = _conversation_owners(lesson)
    if any(
        reference.artifact.id in stage.activity_ids
        for reference in grouped.get("Conversation", [])
    ):
        return True
    if any(
        turns[reference.artifact.id][0].id in stage.activity_ids
        for reference in grouped.get("ConversationTurn", [])
    ):
        return True

    reinforcement = lesson.experience.pronunciation_reinforcement
    if reinforcement is not None and reinforcement.stage_id == stage.id:
        return True

    # Mission needs another contextual artifact; it never satisfies this alone.
    # Mission necesita otro artefacto contextual; nunca basta por sí sola.
    return False


def _validate_exposure(
    lesson: Lesson,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> str | None:
    allowed = {
        "Mission",
        "LessonStage",
        "LanguageSupportItem",
        "Example",
        "Conversation",
        "ConversationTurn",
    }
    forbidden = sorted(set(grouped) - allowed)
    if forbidden:
        return "artifact types cannot support exposure: " + ", ".join(forbidden)

    stages = [
        reference.artifact
        for reference in grouped.get("LessonStage", [])
        if reference.artifact.type in {"encounter", "comprehension"}
    ]
    if not stages:
        return "an encounter or comprehension LessonStage is required"
    if not any(_has_presented_content(lesson, stage, grouped) for stage in stages):
        return "the compatible stage has no referenced contextual content"
    return None


def _has_instructional_content(
    lesson: Lesson,
    stage: LessonStage,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> bool:
    if any(
        stage.id in reference.artifact.stage_ids
        for reference in grouped.get("LanguageSupportItem", [])
    ):
        return True
    if any(
        reference.artifact.id in stage.activity_ids
        for reference in grouped.get("Example", [])
    ):
        return True

    _, turns, _, _, _ = _conversation_owners(lesson)
    if any(
        reference.artifact.id in stage.activity_ids
        for reference in grouped.get("Conversation", [])
    ):
        return True
    if any(
        turns[reference.artifact.id][0].id in stage.activity_ids
        for reference in grouped.get("ConversationTurn", [])
    ):
        return True

    reinforcement = lesson.experience.pronunciation_reinforcement
    return (
        reinforcement is not None
        and reinforcement.stage_id == stage.id
    )


def _validate_instruction(
    lesson: Lesson,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> str | None:
    allowed = {
        "LessonStage",
        "LanguageSupportItem",
        "Example",
        "Conversation",
        "ConversationTurn",
    }
    forbidden = sorted(set(grouped) - allowed)
    if forbidden:
        return "artifact types cannot support instruction: " + ", ".join(forbidden)

    stages = [
        reference.artifact
        for reference in grouped.get("LessonStage", [])
        if reference.artifact.type == "language_support"
        and reference.artifact.instruction.strip()
    ]
    if not stages:
        return "a non-blank language_support LessonStage is required"
    if not any(
        _has_instructional_content(lesson, stage, grouped)
        for stage in stages
    ):
        return "the instructional content is not associated with the stage"
    return None


def _practice_action_for_stage(
    lesson: Lesson,
    stage: LessonStage,
    skill_id: str,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> bool:
    for reference in grouped.get("ExerciseMCQ", []):
        exercise: ExerciseMCQ = reference.artifact
        if exercise.id in stage.activity_ids and skill_id in exercise.skill_ids:
            return True

    conversations, turns, choices, prompts, variants = _conversation_owners(lesson)
    selected_conversation_ids: set[str] = set()
    for reference in grouped.get("Conversation", []):
        conversation = conversations[reference.artifact.id]
        if any(
            turn.speaker == "learner"
            and (turn.choices or turn.production_prompt is not None)
            for turn in conversation.turns
        ):
            selected_conversation_ids.add(conversation.id)
    for reference in grouped.get("ConversationTurn", []):
        conversation, turn = turns[reference.artifact.id]
        if turn.speaker == "learner" and (
            turn.choices or turn.production_prompt is not None
        ):
            selected_conversation_ids.add(conversation.id)
    for reference in grouped.get("ConversationChoice", []):
        conversation, turn, _ = choices[reference.artifact.id]
        if turn.speaker == "learner":
            selected_conversation_ids.add(conversation.id)
    for reference in grouped.get("LearnerProductionPrompt", []):
        conversation, turn, _ = prompts[reference.artifact.id]
        if turn.speaker == "learner":
            selected_conversation_ids.add(conversation.id)
    for reference in grouped.get("TransferPromptVariant", []):
        conversation, turn, _, _ = variants[reference.artifact.id]
        if turn.speaker == "learner":
            selected_conversation_ids.add(conversation.id)

    if any(
        conversation_id in stage.activity_ids
        for conversation_id in selected_conversation_ids
    ):
        return True

    reinforcement = lesson.experience.pronunciation_reinforcement
    return (
        reinforcement is not None
        and reinforcement.stage_id == stage.id
        and reinforcement.shadowing
        and bool(stage.activity_ids)
    )


def _validate_practice(
    lesson: Lesson,
    claim: LessonCapabilityClaim,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> str | None:
    allowed = {
        "LessonStage",
        "Conversation",
        "ConversationTurn",
        "ConversationChoice",
        "LearnerProductionPrompt",
        "TransferPromptVariant",
        "ExerciseMCQ",
    }
    forbidden = sorted(set(grouped) - allowed)
    if forbidden:
        return "artifact types cannot support practice: " + ", ".join(forbidden)

    practice_types = {
        "comprehension",
        "guided_production",
        "assisted_response",
        "applied_conversation",
        "adaptive_feedback",
    }
    stages = [
        reference.artifact
        for reference in grouped.get("LessonStage", [])
        if reference.artifact.type in practice_types
    ]
    if not stages:
        return "a practice-compatible LessonStage is required"
    if not any(
        _practice_action_for_stage(lesson, stage, claim.skill_id, grouped)
        for stage in stages
    ):
        return "the stage has no compatible executable learner action"
    return None


def _referenced_conversation_for_evidence(
    lesson: Lesson,
    evidence: EvidenceDefinition,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> Conversation | None:
    conversations, turns, choices, prompts, variants = _conversation_owners(lesson)
    referenced_ids = {
        reference.artifact.id
        for artifact_type in (
            "Conversation",
            "ConversationTurn",
            "ConversationChoice",
            "LearnerProductionPrompt",
            "TransferPromptVariant",
        )
        for reference in grouped.get(artifact_type, [])
    }
    if evidence.activity_id in referenced_ids:
        return conversations.get(evidence.activity_id)
    for artifact_id in referenced_ids:
        owner = (
            turns.get(artifact_id)
            or choices.get(artifact_id)
            or prompts.get(artifact_id)
            or variants.get(artifact_id)
        )
        if owner is not None and owner[0].id == evidence.activity_id:
            return owner[0]
    return None


def _has_automatic_evaluation(
    evidence: EvidenceDefinition,
    conversation: Conversation,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> bool:
    criteria = [
        reference.artifact
        for reference in grouped.get("ProductionEvaluationCriterion", [])
    ]
    rules = [
        reference.artifact
        for reference in grouped.get("SemanticEvaluationRule", [])
    ]
    for criterion in criteria:
        if (
            criterion.evidence_definition_id != evidence.id
            or criterion.conversation_id != conversation.id
            or evidence.production_prompt_id != criterion.prompt_id
        ):
            continue
        if criterion.dimension == "phonetic":
            return True
        if any(rule.criterion_id == criterion.id for rule in rules):
            return True
    return False


def _validate_evidence_gate(
    lesson: Lesson,
    claim: LessonCapabilityClaim,
    grouped: dict[str, list[CapabilityArtifactReference]],
) -> str | None:
    allowed = {
        "LessonStage",
        "Conversation",
        "ConversationTurn",
        "ConversationChoice",
        "LearnerProductionPrompt",
        "TransferPromptVariant",
        "ExerciseMCQ",
        "EvidenceDefinition",
        "ProductionEvaluationCriterion",
        "SemanticEvaluationRule",
    }
    forbidden = sorted(set(grouped) - allowed)
    if forbidden:
        return "artifact types cannot support an evidence gate: " + ", ".join(forbidden)

    stages = {
        reference.artifact.id: reference.artifact
        for reference in grouped.get("LessonStage", [])
        if reference.artifact.type == "evidence"
    }
    if not stages:
        return "an evidence LessonStage is required"

    evidences = [
        reference.artifact
        for reference in grouped.get("EvidenceDefinition", [])
    ]
    if not evidences:
        return "a referenced EvidenceDefinition is required"

    exercises = {
        reference.artifact.id: reference.artifact
        for reference in grouped.get("ExerciseMCQ", [])
    }
    for evidence in evidences:
        stage = stages.get(evidence.stage_id)
        if (
            stage is None
            or evidence.activity_id not in stage.activity_ids
            or claim.skill_id not in evidence.skill_ids
        ):
            continue

        exercise = exercises.get(evidence.activity_id)
        if exercise is not None:
            if (
                evidence.evidence_type == "exercise_result"
                and evidence.measurement_mode in {"binary", "score"}
                and claim.skill_id in exercise.skill_ids
            ):
                return None
            continue

        conversation = _referenced_conversation_for_evidence(
            lesson,
            evidence,
            grouped,
        )
        if conversation is None:
            continue
        prompts = {
            turn.production_prompt.id: turn.production_prompt
            for turn in conversation.turns
            if turn.speaker == "learner"
            and turn.production_prompt is not None
        }
        has_production_prompt = (
            evidence.production_prompt_id is not None
            and evidence.production_prompt_id in prompts
        )
        choice_ids = {
            choice.id
            for turn in conversation.turns
            if turn.speaker == "learner"
            for choice in turn.choices
        }
        has_referenced_choice = any(
            reference.artifact.id in choice_ids
            for reference in grouped.get("ConversationChoice", [])
        )
        if not has_production_prompt and not has_referenced_choice:
            continue
        if evidence.external_review_requirements:
            return None
        if (
            has_production_prompt
            and _has_automatic_evaluation(evidence, conversation, grouped)
        ):
            return None

    return "no referenced evidence forms an executable and evaluable gate"


StateValidator = Callable[
    [Lesson, LessonCapabilityClaim, dict[str, list[CapabilityArtifactReference]]],
    str | None,
]


def validate_capability_artifact_state_compatibility(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate resolved artifact sets against their declared state.

    Valida conjuntos resueltos de artefactos frente a su estado declarado.
    """
    lessons = {
        lesson.id: lesson
        for lesson in candidate.candidate_unit.lessons
    }
    indexes = {
        lesson_id: build_lesson_capability_artifact_index(
            candidate,
            lesson_id,
        )
        for lesson_id in lessons
    }
    findings: list[ValidationFinding] = []

    for plan in candidate.lesson_capability_plans:
        lesson = lessons[plan.lesson_id]
        index = indexes[plan.lesson_id]
        for claim in plan.claims:
            matches = [index.get(artifact_id, []) for artifact_id in claim.artifact_ids]
            if any(len(items) != 1 for items in matches):
                continue
            references = [items[0] for items in matches]
            grouped = _references_by_type(references)

            if (
                lesson.experience is None
                or claim.skill_id not in lesson.experience.skill_ids
            ):
                reason = "the Skill is not linked by LessonExperience"
            elif claim.preparation_state == "EXPOSURE_AVAILABLE":
                reason = _validate_exposure(lesson, grouped)
            elif claim.preparation_state == "INSTRUCTION_AVAILABLE":
                reason = _validate_instruction(lesson, grouped)
            elif claim.preparation_state == "PRACTICE_AVAILABLE":
                reason = _validate_practice(lesson, claim, grouped)
            else:
                reason = _validate_evidence_gate(lesson, claim, grouped)

            if reason is None:
                continue
            findings.append(
                ValidationFinding(
                    validator_id=VALIDATOR_ID,
                    severity="error",
                    message=(
                        f"Lesson {plan.lesson_id} claim for Skill "
                        f"{claim.skill_id} in state "
                        f"{claim.preparation_state} is incompatible: "
                        f"{reason}. Artifacts: "
                        + ", ".join(claim.artifact_ids)
                        + "."
                    ),
                    reference_ids=[
                        plan.lesson_id,
                        claim.skill_id,
                        *claim.artifact_ids,
                    ],
                )
            )

    return findings
