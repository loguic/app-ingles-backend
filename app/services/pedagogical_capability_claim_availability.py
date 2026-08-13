from dataclasses import dataclass
from app.schemas.content import Lesson
from app.schemas.pedagogical_unit import (
    CurriculumPreparationState,
    LessonCapabilityClaim,
    PedagogicalUnitCandidate,
    ValidationFinding,
)
from app.services.pedagogical_capability_artifact_reference_validation import (
    CapabilityArtifactReference,
    build_lesson_capability_artifact_index,
)
from app.services.pedagogical_capability_artifact_state_validation import (
    validate_capability_artifact_state_compatibility,
)


VALIDATOR_ID = "capability_claim_availability_integrity"


@dataclass(frozen=True, order=True)
class IntraLessonAvailabilityPoint:
    """Represent one canonical point without persisting an ordinal.

    Representa un punto canónico sin persistir un ordinal.
    """

    sort_index: int
    stage_id: str
    stage_index: int


@dataclass(frozen=True)
class CapabilityClaimAvailability:
    """Describe the derived availability of one valid capability claim.

    Describe la disponibilidad derivada de un claim válido.
    """

    lesson_id: str
    lesson_index: int
    point: IntraLessonAvailabilityPoint
    skill_id: str
    preparation_state: CurriculumPreparationState
    artifact_ids: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityClaimAvailabilityError:
    """Report that one otherwise valid claim cannot be positioned.

    Indica que un claim válido no puede posicionarse.
    """

    lesson_id: str
    skill_id: str
    preparation_state: CurriculumPreparationState
    artifact_ids: tuple[str, ...]
    cause: str


@dataclass(frozen=True)
class CapabilityClaimAvailabilityDerivation:
    """Collect every derived position and positioning error.

    Reúne todas las posiciones derivadas y errores de posicionamiento.
    """

    availabilities: tuple[CapabilityClaimAvailability, ...]
    derivation_errors: tuple[CapabilityClaimAvailabilityError, ...]


class _ClaimAvailabilityError(ValueError):
    pass


def _stage_points(lesson: Lesson) -> dict[str, IntraLessonAvailabilityPoint]:
    if lesson.experience is None:
        return {}
    return {
        stage.id: IntraLessonAvailabilityPoint(
            sort_index=index + 1,
            stage_id=stage.id,
            stage_index=index,
        )
        for index, stage in enumerate(lesson.experience.stages)
    }


def _activity_stage_ids(lesson: Lesson, activity_id: str) -> list[str]:
    if lesson.experience is None:
        return []
    return [
        stage.id
        for stage in lesson.experience.stages
        if activity_id in stage.activity_ids
    ]


def _conversation_owner_id(lesson: Lesson, artifact_id: str) -> str | None:
    for conversation in lesson.conversations:
        if conversation.id == artifact_id:
            return conversation.id
        for turn in conversation.turns:
            nested_ids = [turn.id, *(choice.id for choice in turn.choices)]
            if turn.production_prompt is not None:
                nested_ids.extend(
                    [
                        turn.production_prompt.id,
                        *(
                            variant.id
                            for variant in turn.production_prompt.transfer_variants
                        ),
                    ]
                )
            if artifact_id in nested_ids:
                return conversation.id
    return None


def _criterion_evidence_id(lesson: Lesson, artifact_id: str, candidate: PedagogicalUnitCandidate) -> str | None:
    plan = next(
        (item for item in candidate.evaluation_plans if item.lesson_id == lesson.id),
        None,
    )
    if plan is None:
        return None
    for criterion in plan.criteria:
        if criterion.id == artifact_id:
            return criterion.evidence_definition_id
    rules = {rule.id: rule for rule in plan.semantic_rules}
    rule = rules.get(artifact_id)
    if rule is None:
        return None
    criterion = next(
        (item for item in plan.criteria if item.id == rule.criterion_id),
        None,
    )
    return None if criterion is None else criterion.evidence_definition_id


def _artifact_stage_ids(
    candidate: PedagogicalUnitCandidate,
    lesson: Lesson,
    reference: CapabilityArtifactReference,
) -> list[str]:
    artifact = reference.artifact
    if reference.artifact_type == "Mission":
        return []
    if reference.artifact_type == "LessonStage":
        return [artifact.id]
    if reference.artifact_type == "LanguageSupportItem":
        return list(artifact.stage_ids)
    if reference.artifact_type == "EvidenceDefinition":
        return [artifact.stage_id]
    if reference.artifact_type in {
        "Example",
        "Conversation",
        "ExerciseMCQ",
    }:
        return _activity_stage_ids(lesson, artifact.id)
    owner_id = _conversation_owner_id(lesson, artifact.id)
    if owner_id is not None:
        return _activity_stage_ids(lesson, owner_id)
    evidence_id = _criterion_evidence_id(lesson, artifact.id, candidate)
    if evidence_id is not None and lesson.experience is not None:
        evidence = next(
            (
                item
                for item in lesson.experience.evidence_definitions
                if item.id == evidence_id
            ),
            None,
        )
        return [] if evidence is None else [evidence.stage_id]
    return []


def _derive_claim(
    candidate: PedagogicalUnitCandidate,
    lesson: Lesson,
    lesson_index: int,
    claim: LessonCapabilityClaim,
    references: list[CapabilityArtifactReference],
) -> CapabilityClaimAvailability:
    stage_points = _stage_points(lesson)
    points: list[IntraLessonAvailabilityPoint] = []
    for reference in references:
        stage_ids = _artifact_stage_ids(candidate, lesson, reference)
        if not stage_ids:
            raise _ClaimAvailabilityError(
                f"artifact {reference.artifact_id} has no canonical stage"
            )
        unknown = [stage_id for stage_id in stage_ids if stage_id not in stage_points]
        if unknown:
            raise _ClaimAvailabilityError(
                f"artifact {reference.artifact_id} references unknown stage "
                + ", ".join(unknown)
            )
        points.extend(stage_points[stage_id] for stage_id in stage_ids)

    if not points:
        raise _ClaimAvailabilityError("the complete claim has no canonical point")
    return CapabilityClaimAvailability(
        lesson_id=lesson.id,
        lesson_index=lesson_index,
        point=max(points),
        skill_id=claim.skill_id,
        preparation_state=claim.preparation_state,
        artifact_ids=tuple(claim.artifact_ids),
    )


def _eligible_claims(candidate: PedagogicalUnitCandidate):
    incompatible = {
        tuple(finding.reference_ids)
        for finding in validate_capability_artifact_state_compatibility(candidate)
    }
    lessons = list(candidate.candidate_unit.lessons)
    indexes = {
        lesson.id: build_lesson_capability_artifact_index(candidate, lesson.id)
        for lesson in lessons
    }
    lesson_indexes = {lesson.id: index for index, lesson in enumerate(lessons)}
    lessons_by_id = {lesson.id: lesson for lesson in lessons}
    for plan in candidate.lesson_capability_plans:
        lesson = lessons_by_id[plan.lesson_id]
        index = indexes[plan.lesson_id]
        for claim in plan.claims:
            matches = [index.get(artifact_id, []) for artifact_id in claim.artifact_ids]
            if any(len(items) != 1 for items in matches):
                continue
            identity = tuple([plan.lesson_id, claim.skill_id, *claim.artifact_ids])
            if identity in incompatible:
                continue
            yield lesson, lesson_indexes[lesson.id], claim, [items[0] for items in matches]


def derive_capability_claim_availabilities(
    candidate: PedagogicalUnitCandidate,
) -> CapabilityClaimAvailabilityDerivation:
    """Purely derive positions for all resolved and compatible claims.

    Deriva de forma pura posiciones para claims resueltos y compatibles.
    """
    availabilities: list[CapabilityClaimAvailability] = []
    errors: list[CapabilityClaimAvailabilityError] = []
    for lesson, lesson_index, claim, references in _eligible_claims(candidate):
        try:
            availabilities.append(
                _derive_claim(
                    candidate,
                    lesson,
                    lesson_index,
                    claim,
                    references,
                )
            )
        except _ClaimAvailabilityError as error:
            errors.append(
                CapabilityClaimAvailabilityError(
                    lesson_id=lesson.id,
                    skill_id=claim.skill_id,
                    preparation_state=claim.preparation_state,
                    artifact_ids=tuple(claim.artifact_ids),
                    cause=str(error),
                )
            )
    return CapabilityClaimAvailabilityDerivation(
        availabilities=tuple(availabilities),
        derivation_errors=tuple(errors),
    )


def validate_capability_claim_availability(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Return one deterministic positioning finding per invalid claim.

    Devuelve un finding determinista de posición por claim inválido.
    """
    derivation = derive_capability_claim_availabilities(candidate)
    return [
        ValidationFinding(
            validator_id=VALIDATOR_ID,
            severity="error",
            message=(
                f"Lesson {error.lesson_id} claim for Skill {error.skill_id} "
                f"cannot be positioned: {error.cause}."
            ),
            reference_ids=[error.lesson_id, error.skill_id, *error.artifact_ids],
        )
        for error in derivation.derivation_errors
    ]
