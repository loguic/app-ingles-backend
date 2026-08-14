from dataclasses import dataclass
from typing import Literal

from app.services.pedagogical_accumulated_curriculum_preparation import (
    AccumulatedCapabilityPrecedenceError,
    AccumulatedCurriculumPreparationDerivation,
    AccumulatedCurriculumPreparationResolutionError,
    AccumulatedSkillPreparation,
    derive_accumulated_curriculum_preparation,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    curriculum_preparation_state_index,
)
from app.services.pedagogical_curriculum_candidate_correspondence import (
    OrderedCurriculumCandidateEntry,
)
from app.services.pedagogical_local_skill_prerequisite_consumption import (
    LocalSkillPrerequisiteConsumption,
    LocalSkillPrerequisiteConsumptionError,
    derive_local_skill_prerequisite_consumptions,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)


CurriculumSkillPrerequisiteAssessmentOutcome = Literal[
    "satisfied_in_context",
    "unresolved_in_context",
]


@dataclass(frozen=True)
class CurriculumSkillPrerequisiteAssessment:
    """Assess one prerequisite using structural preparation within the context.

    Evalúa un prerequisite con preparación estructural dentro del contexto.
    """

    entry: OrderedCurriculumCandidateEntry
    consumption: LocalSkillPrerequisiteConsumption
    accumulated_skill_preparation: AccumulatedSkillPreparation | None
    related_precedence_errors: tuple[
        AccumulatedCapabilityPrecedenceError, ...
    ]
    outcome: CurriculumSkillPrerequisiteAssessmentOutcome


@dataclass(frozen=True)
class CurriculumSkillPrerequisiteConsumptionResolutionError:
    """Attach one original slice 11 error to its owning curriculum entry.

    Vincula un error original de slice 11 con su entry curricular propietaria.
    """

    entry: OrderedCurriculumCandidateEntry
    error: LocalSkillPrerequisiteConsumptionError


@dataclass(frozen=True)
class CurriculumSkillPrerequisitePreparationResolutionError:
    """Attach one preparation error to the prerequisite consumption query.

    Vincula un error de preparación con la consulta del punto de consumo.
    """

    entry: OrderedCurriculumCandidateEntry
    consumption: LocalSkillPrerequisiteConsumption
    error: AccumulatedCurriculumPreparationResolutionError


@dataclass(frozen=True)
class CurriculumSkillPrerequisitePrecedenceObservation:
    """Preserve precedence errors observed for one valid consumption point.

    Conserva errores de precedencia observados para un punto de consumo válido.
    """

    consumption: LocalSkillPrerequisiteConsumption
    errors: tuple[AccumulatedCapabilityPrecedenceError, ...]


@dataclass(frozen=True)
class CurriculumSkillPrerequisiteAssessmentDerivation:
    """Collect contextual assessments and independent derivation errors.

    Reúne assessments contextuales y errores derivativos independientes.
    """

    assessments: tuple[CurriculumSkillPrerequisiteAssessment, ...]
    consumption_errors: tuple[
        CurriculumSkillPrerequisiteConsumptionResolutionError, ...
    ]
    preparation_resolution_errors: tuple[
        CurriculumSkillPrerequisitePreparationResolutionError, ...
    ]
    precedence_observations: tuple[
        CurriculumSkillPrerequisitePrecedenceObservation, ...
    ]


def derive_curriculum_skill_prerequisite_assessments(
    context: OrderedCurriculumCandidateContext,
) -> CurriculumSkillPrerequisiteAssessmentDerivation:
    """Purely assess every prerequisite within the supplied ordered context.

    Evalúa de forma pura cada prerequisite dentro del contexto ordenado.
    """
    assessments: list[CurriculumSkillPrerequisiteAssessment] = []
    consumption_errors: list[
        CurriculumSkillPrerequisiteConsumptionResolutionError
    ] = []
    preparation_resolution_errors: list[
        CurriculumSkillPrerequisitePreparationResolutionError
    ] = []
    precedence_observations: list[
        CurriculumSkillPrerequisitePrecedenceObservation
    ] = []
    preparation_by_point: dict[
        tuple[str, str, str],
        AccumulatedCurriculumPreparationDerivation,
    ] = {}

    for entry in context.entries:
        consumption_derivation = derive_local_skill_prerequisite_consumptions(
            entry.candidate
        )
        consumption_errors.extend(
            CurriculumSkillPrerequisiteConsumptionResolutionError(
                entry=entry,
                error=error,
            )
            for error in consumption_derivation.resolution_errors
        )

        for consumption in consumption_derivation.consumptions:
            point_key = (
                entry.position.unit_id,
                consumption.before_point.lesson_id,
                consumption.before_point.stage_id,
            )
            preparation_derivation = preparation_by_point.get(point_key)
            if preparation_derivation is None:
                preparation_derivation = derive_accumulated_curriculum_preparation(
                    context,
                    unit_id=entry.position.unit_id,
                    lesson_id=consumption.before_point.lesson_id,
                    stage_id=consumption.before_point.stage_id,
                )
                preparation_by_point[point_key] = preparation_derivation

            if preparation_derivation.snapshot is None:
                preparation_resolution_errors.extend(
                    CurriculumSkillPrerequisitePreparationResolutionError(
                        entry=entry,
                        consumption=consumption,
                        error=error,
                    )
                    for error in preparation_derivation.resolution_errors
                )
                continue

            if preparation_derivation.precedence_errors:
                precedence_observations.append(
                    CurriculumSkillPrerequisitePrecedenceObservation(
                        consumption=consumption,
                        errors=preparation_derivation.precedence_errors,
                    )
                )

            required_skill_id = consumption.prerequisite.required_skill_id
            accumulated_skill_preparation = next(
                (
                    skill
                    for skill in preparation_derivation.snapshot.skills
                    if skill.skill_id == required_skill_id
                ),
                None,
            )
            related_precedence_errors = tuple(
                error
                for error in preparation_derivation.precedence_errors
                if error.error.skill_id == required_skill_id
            )
            outcome: CurriculumSkillPrerequisiteAssessmentOutcome
            if accumulated_skill_preparation is None:
                outcome = "unresolved_in_context"
            else:
                actual_index = curriculum_preparation_state_index(
                    accumulated_skill_preparation.highest_preparation_state
                )
                required_index = curriculum_preparation_state_index(
                    consumption.prerequisite.required_state
                )
                outcome = (
                    "satisfied_in_context"
                    if actual_index >= required_index
                    else "unresolved_in_context"
                )
            assessments.append(
                CurriculumSkillPrerequisiteAssessment(
                    entry=entry,
                    consumption=consumption,
                    accumulated_skill_preparation=accumulated_skill_preparation,
                    related_precedence_errors=related_precedence_errors,
                    outcome=outcome,
                )
            )

    return CurriculumSkillPrerequisiteAssessmentDerivation(
        assessments=tuple(assessments),
        consumption_errors=tuple(consumption_errors),
        preparation_resolution_errors=tuple(preparation_resolution_errors),
        precedence_observations=tuple(precedence_observations),
    )
