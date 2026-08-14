from dataclasses import dataclass
from typing import Literal

from app.schemas.pedagogical_unit import (
    CurriculumPreparationState,
    PedagogicalUnitCandidate,
    SkillPrerequisite,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    LocalCurriculumPoint,
)


PrerequisiteConsumptionErrorCause = Literal[
    "unknown_lesson",
    "ambiguous_lesson",
    "lesson_without_experience",
    "unknown_stage_for_lesson",
]


@dataclass(frozen=True)
class LocalSkillPrerequisiteConsumption:
    """Bind one prerequisite to its canonical local consumption point.

    Vincula un prerrequisito con su punto canónico local de consumo.
    """

    lesson_id: str
    prerequisite: SkillPrerequisite
    before_point: LocalCurriculumPoint


@dataclass(frozen=True)
class LocalSkillPrerequisiteConsumptionError:
    """Describe why one prerequisite consumption point cannot be resolved.

    Describe por qué no puede resolverse el punto de consumo de un prerrequisito.
    """

    lesson_id: str
    required_skill_id: str
    required_state: CurriculumPreparationState
    before_stage_id: str | None
    cause: PrerequisiteConsumptionErrorCause


@dataclass(frozen=True)
class LocalSkillPrerequisiteConsumptionDerivation:
    """Collect all local prerequisite points and resolution errors.

    Reúne todos los puntos locales de prerrequisitos y sus errores de resolución.
    """

    consumptions: tuple[LocalSkillPrerequisiteConsumption, ...]
    resolution_errors: tuple[LocalSkillPrerequisiteConsumptionError, ...]


class _ConsumptionPointResolutionError(ValueError):
    def __init__(self, cause: PrerequisiteConsumptionErrorCause) -> None:
        self.cause = cause
        super().__init__(cause)


def _resolve_consumption_point(
    candidate: PedagogicalUnitCandidate,
    *,
    lesson_id: str,
    before_stage_id: str | None,
) -> LocalCurriculumPoint:
    lesson_matches = [
        (lesson_index, lesson)
        for lesson_index, lesson in enumerate(candidate.candidate_unit.lessons)
        if lesson.id == lesson_id
    ]
    if not lesson_matches:
        raise _ConsumptionPointResolutionError("unknown_lesson")
    if len(lesson_matches) > 1:
        raise _ConsumptionPointResolutionError("ambiguous_lesson")

    lesson_index, lesson = lesson_matches[0]
    if lesson.experience is None:
        raise _ConsumptionPointResolutionError("lesson_without_experience")

    if before_stage_id is None:
        stage_index = 0
        stage = lesson.experience.stages[stage_index]
    else:
        stage_match = next(
            (
                (stage_index, stage)
                for stage_index, stage in enumerate(lesson.experience.stages)
                if stage.id == before_stage_id
            ),
            None,
        )
        if stage_match is None:
            raise _ConsumptionPointResolutionError("unknown_stage_for_lesson")
        stage_index, stage = stage_match

    return LocalCurriculumPoint(
        lesson_id=lesson.id,
        stage_id=stage.id,
        lesson_index=lesson_index,
        stage_index=stage_index,
    )


def derive_local_skill_prerequisite_consumptions(
    candidate: PedagogicalUnitCandidate,
) -> LocalSkillPrerequisiteConsumptionDerivation:
    """Purely resolve every local prerequisite consumption point.

    Resuelve de forma pura cada punto local de consumo de prerrequisitos.
    """
    consumptions: list[LocalSkillPrerequisiteConsumption] = []
    errors: list[LocalSkillPrerequisiteConsumptionError] = []
    for plan in candidate.lesson_capability_plans:
        for prerequisite in plan.prerequisites:
            try:
                point = _resolve_consumption_point(
                    candidate,
                    lesson_id=plan.lesson_id,
                    before_stage_id=prerequisite.before_stage_id,
                )
            except _ConsumptionPointResolutionError as error:
                errors.append(
                    LocalSkillPrerequisiteConsumptionError(
                        lesson_id=plan.lesson_id,
                        required_skill_id=prerequisite.required_skill_id,
                        required_state=prerequisite.required_state,
                        before_stage_id=prerequisite.before_stage_id,
                        cause=error.cause,
                    )
                )
            else:
                consumptions.append(
                    LocalSkillPrerequisiteConsumption(
                        lesson_id=plan.lesson_id,
                        prerequisite=prerequisite,
                        before_point=point,
                    )
                )
    return LocalSkillPrerequisiteConsumptionDerivation(
        consumptions=tuple(consumptions),
        resolution_errors=tuple(errors),
    )
