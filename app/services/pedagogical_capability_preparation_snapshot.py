from dataclasses import dataclass
from typing import Literal

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    derive_capability_claim_state_precedence,
)


SnapshotPointErrorCause = Literal[
    "unknown_lesson",
    "ambiguous_lesson",
    "lesson_without_experience",
    "unknown_stage_for_lesson",
]


@dataclass(frozen=True)
class LocalCurriculumPoint:
    """Represent one real stage position inside the candidate unit.

    Representa la posición de una etapa real dentro de la unidad candidata.
    """

    lesson_id: str
    stage_id: str
    lesson_index: int
    stage_index: int


@dataclass(frozen=True)
class CapabilityPreparationSnapshot:
    """Contain valid individual claims strictly before one local point.

    Contiene claims válidos individuales estrictamente anteriores a un punto local.
    """

    before_point: LocalCurriculumPoint
    available_claims: tuple[CapabilityClaimAvailability, ...]


class CapabilityPreparationSnapshotPointError(ValueError):
    """Report that a requested local curriculum point cannot be resolved.

    Indica que un punto curricular local solicitado no puede resolverse.
    """

    def __init__(
        self,
        *,
        cause: SnapshotPointErrorCause,
        lesson_id: str,
        stage_id: str,
    ) -> None:
        self.cause = cause
        self.lesson_id = lesson_id
        self.stage_id = stage_id
        super().__init__(
            f"Cannot resolve local curriculum point {lesson_id}/{stage_id}: {cause}"
        )


def _resolve_local_curriculum_point(
    candidate: PedagogicalUnitCandidate,
    *,
    lesson_id: str,
    stage_id: str,
) -> LocalCurriculumPoint:
    lessons = candidate.candidate_unit.lessons
    lesson_matches = [
        (lesson_index, lesson)
        for lesson_index, lesson in enumerate(lessons)
        if lesson.id == lesson_id
    ]
    if not lesson_matches:
        raise CapabilityPreparationSnapshotPointError(
            cause="unknown_lesson",
            lesson_id=lesson_id,
            stage_id=stage_id,
        )
    if len(lesson_matches) > 1:
        raise CapabilityPreparationSnapshotPointError(
            cause="ambiguous_lesson",
            lesson_id=lesson_id,
            stage_id=stage_id,
        )
    lesson_index, lesson = lesson_matches[0]
    if lesson.experience is None:
        raise CapabilityPreparationSnapshotPointError(
            cause="lesson_without_experience",
            lesson_id=lesson_id,
            stage_id=stage_id,
        )
    stage_index = next(
        (
            index
            for index, stage in enumerate(lesson.experience.stages)
            if stage.id == stage_id
        ),
        None,
    )
    if stage_index is None:
        raise CapabilityPreparationSnapshotPointError(
            cause="unknown_stage_for_lesson",
            lesson_id=lesson_id,
            stage_id=stage_id,
        )
    return LocalCurriculumPoint(
        lesson_id=lesson_id,
        stage_id=stage_id,
        lesson_index=lesson_index,
        stage_index=stage_index,
    )


def _claim_output_key(
    claim: CapabilityClaimAvailability,
) -> tuple[object, ...]:
    return (
        claim.lesson_index,
        claim.point.stage_index,
        claim.skill_id,
        claim.preparation_state,
        claim.lesson_id,
        claim.point.stage_id,
        claim.artifact_ids,
    )


def derive_capability_preparation_snapshot(
    candidate: PedagogicalUnitCandidate,
    *,
    lesson_id: str,
    stage_id: str,
) -> CapabilityPreparationSnapshot:
    """Derive valid claims strictly before one canonical local point.

    Deriva claims válidos estrictamente anteriores a un punto local canónico.
    """
    before_point = _resolve_local_curriculum_point(
        candidate,
        lesson_id=lesson_id,
        stage_id=stage_id,
    )
    precedence = derive_capability_claim_state_precedence(candidate)
    point = before_point.lesson_index, before_point.stage_index
    available_claims = tuple(
        sorted(
            (
                claim
                for claim in precedence.valid_claims
                if (claim.lesson_index, claim.point.stage_index) < point
            ),
            key=_claim_output_key,
        )
    )
    return CapabilityPreparationSnapshot(
        before_point=before_point,
        available_claims=available_claims,
    )
