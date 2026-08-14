from dataclasses import dataclass
from typing import Literal

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_capability_claim_precedence_validation import (
    curriculum_preparation_state_index,
)
from app.services.pedagogical_local_capability_preparation_view import (
    LocalSkillPreparation,
    derive_local_capability_preparation_view,
)
from app.services.pedagogical_local_skill_prerequisite_consumption import (
    LocalSkillPrerequisiteConsumption,
    LocalSkillPrerequisiteConsumptionError,
    derive_local_skill_prerequisite_consumptions,
)


LocalSkillPrerequisiteAssessmentOutcome = Literal[
    "satisfied_in_local_context",
    "unresolved_in_local_context",
]


@dataclass(frozen=True)
class LocalSkillPrerequisiteAssessment:
    """Assess one prerequisite using only local structural preparation.

    Evalúa un prerrequisito usando solo preparación estructural local.
    """

    consumption: LocalSkillPrerequisiteConsumption
    locally_available_preparation: LocalSkillPreparation | None
    outcome: LocalSkillPrerequisiteAssessmentOutcome


@dataclass(frozen=True)
class LocalSkillPrerequisiteAssessmentDerivation:
    """Collect local assessments and unresolved consumption-point errors.

    Reúne evaluaciones locales y errores al resolver puntos de consumo.
    """

    assessments: tuple[LocalSkillPrerequisiteAssessment, ...]
    resolution_errors: tuple[LocalSkillPrerequisiteConsumptionError, ...]


def derive_local_skill_prerequisite_assessments(
    candidate: PedagogicalUnitCandidate,
) -> LocalSkillPrerequisiteAssessmentDerivation:
    """Purely assess prerequisites demonstrable from one candidate unit.

    Evalúa de forma pura los prerrequisitos demostrables en una unidad candidata.
    """
    consumption_derivation = derive_local_skill_prerequisite_consumptions(candidate)
    assessments: list[LocalSkillPrerequisiteAssessment] = []

    for consumption in consumption_derivation.consumptions:
        preparation_view = derive_local_capability_preparation_view(
            candidate,
            lesson_id=consumption.before_point.lesson_id,
            stage_id=consumption.before_point.stage_id,
        )
        local_preparation = next(
            (
                skill
                for skill in preparation_view.skills
                if skill.skill_id == consumption.prerequisite.required_skill_id
            ),
            None,
        )

        outcome: LocalSkillPrerequisiteAssessmentOutcome
        if local_preparation is None:
            outcome = "unresolved_in_local_context"
        elif curriculum_preparation_state_index(
            local_preparation.highest_preparation_state
        ) >= curriculum_preparation_state_index(
            consumption.prerequisite.required_state
        ):
            outcome = "satisfied_in_local_context"
        else:
            outcome = "unresolved_in_local_context"

        assessments.append(
            LocalSkillPrerequisiteAssessment(
                consumption=consumption,
                locally_available_preparation=local_preparation,
                outcome=outcome,
            )
        )

    return LocalSkillPrerequisiteAssessmentDerivation(
        assessments=tuple(assessments),
        resolution_errors=consumption_derivation.resolution_errors,
    )
