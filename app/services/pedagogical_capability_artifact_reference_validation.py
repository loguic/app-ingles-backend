from dataclasses import dataclass
from typing import Literal

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)


CapabilityArtifactType = Literal[
    "Mission",
    "LessonStage",
    "LanguageSupportItem",
    "Example",
    "Conversation",
    "ConversationTurn",
    "ConversationChoice",
    "LearnerProductionPrompt",
    "TransferPromptVariant",
    "ExerciseMCQ",
    "EvidenceDefinition",
    "ProductionEvaluationCriterion",
    "SemanticEvaluationRule",
]


@dataclass(frozen=True)
class CapabilityArtifactReference:
    """Describe one typed artifact owned by a candidate lesson.

    Describe un artefacto tipado perteneciente a una lección candidata.
    """

    artifact_id: str
    artifact_type: CapabilityArtifactType
    lesson_id: str
    artifact: object


CapabilityArtifactIndex = dict[str, list[CapabilityArtifactReference]]


def build_lesson_capability_artifact_index(
    candidate: PedagogicalUnitCandidate,
    lesson_id: str,
) -> CapabilityArtifactIndex:
    """Index identifiable artifacts owned by one candidate lesson.

    Indexa los artefactos identificables pertenecientes a una lección candidata.
    """
    lesson = next(
        item
        for item in candidate.candidate_unit.lessons
        if item.id == lesson_id
    )
    index: CapabilityArtifactIndex = {}

    def add(
        artifact_id: str,
        artifact_type: CapabilityArtifactType,
        artifact: object,
    ) -> None:
        reference = CapabilityArtifactReference(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            lesson_id=lesson_id,
            artifact=artifact,
        )
        index.setdefault(artifact_id, []).append(reference)

    if lesson.experience is not None:
        experience = lesson.experience
        add(experience.mission.id, "Mission", experience.mission)
        for stage in experience.stages:
            add(stage.id, "LessonStage", stage)
        for support in experience.language_support:
            add(support.id, "LanguageSupportItem", support)
        for evidence in experience.evidence_definitions:
            add(evidence.id, "EvidenceDefinition", evidence)

    for example in lesson.examples:
        add(example.id, "Example", example)
    for conversation in lesson.conversations:
        add(conversation.id, "Conversation", conversation)
        for turn in conversation.turns:
            add(turn.id, "ConversationTurn", turn)
            for choice in turn.choices:
                add(choice.id, "ConversationChoice", choice)
            if turn.production_prompt is None:
                continue
            prompt = turn.production_prompt
            add(prompt.id, "LearnerProductionPrompt", prompt)
            for variant in prompt.transfer_variants:
                add(variant.id, "TransferPromptVariant", variant)
    for exercise in lesson.exercises:
        add(exercise.id, "ExerciseMCQ", exercise)

    evaluation_plan = next(
        (
            plan
            for plan in candidate.evaluation_plans
            if plan.lesson_id == lesson_id
        ),
        None,
    )
    if evaluation_plan is not None:
        for criterion in evaluation_plan.criteria:
            add(
                criterion.id,
                "ProductionEvaluationCriterion",
                criterion,
            )
        for rule in evaluation_plan.semantic_rules:
            add(rule.id, "SemanticEvaluationRule", rule)

    return index


def validate_capability_artifact_references(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Resolve every claim artifact inside its owning lesson.

    Resuelve cada artefacto de claim dentro de su lección propietaria.
    """
    indexes = {
        lesson.id: build_lesson_capability_artifact_index(
            candidate,
            lesson.id,
        )
        for lesson in candidate.candidate_unit.lessons
    }
    findings: list[ValidationFinding] = []

    for plan in candidate.lesson_capability_plans:
        local_index = indexes[plan.lesson_id]
        for claim in plan.claims:
            for artifact_id in claim.artifact_ids:
                matches = local_index.get(artifact_id, [])
                if len(matches) == 1:
                    continue

                if len(matches) > 1:
                    artifact_types = sorted(
                        {match.artifact_type for match in matches}
                    )
                    findings.append(
                        ValidationFinding(
                            validator_id=(
                                "capability_artifact_reference_integrity"
                            ),
                            severity="error",
                            message=(
                                f"Capability artifact {artifact_id} is "
                                f"ambiguous in lesson {plan.lesson_id}: "
                                + ", ".join(artifact_types)
                                + "."
                            ),
                            reference_ids=[plan.lesson_id, artifact_id],
                        )
                    )
                    continue

                owning_lesson_ids = sorted(
                    lesson_id
                    for lesson_id, index in indexes.items()
                    if artifact_id in index
                )
                if owning_lesson_ids:
                    detail = (
                        "belongs to another lesson: "
                        + ", ".join(owning_lesson_ids)
                    )
                else:
                    detail = "is unknown"

                findings.append(
                    ValidationFinding(
                        validator_id=(
                            "capability_artifact_reference_integrity"
                        ),
                        severity="error",
                        message=(
                            f"Capability artifact {artifact_id} {detail}; "
                            f"expected lesson {plan.lesson_id}."
                        ),
                        reference_ids=[plan.lesson_id, artifact_id],
                    )
                )

    return findings
