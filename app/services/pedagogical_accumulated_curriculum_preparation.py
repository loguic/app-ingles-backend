from collections import defaultdict
from dataclasses import dataclass
from typing import Literal, TypeAlias

from app.schemas.pedagogical_unit import CurriculumPreparationState
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    CapabilityClaimPrecedenceError,
    curriculum_preparation_state_index,
    derive_capability_claim_state_precedence,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    CapabilityPreparationSnapshotPointError,
    LocalCurriculumPoint,
    derive_capability_preparation_snapshot,
)
from app.services.pedagogical_curriculum_candidate_correspondence import (
    OrderedCurriculumCandidateEntry,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)


AccumulatedCurriculumUnitResolutionErrorCause = Literal[
    "unknown_unit_in_context",
    "ambiguous_unit_in_context",
]


@dataclass(frozen=True)
class CurriculumPreparationPoint:
    """Identify one real local point inside an ordered curriculum entry.

    Identifica un punto local real dentro de una entry curricular ordenada.
    """

    entry: OrderedCurriculumCandidateEntry
    local_point: LocalCurriculumPoint


@dataclass(frozen=True)
class AccumulatedCapabilityClaim:
    """Attach one original valid claim to its curriculum entry.

    Vincula un claim válido original con su entry curricular.
    """

    entry: OrderedCurriculumCandidateEntry
    claim: CapabilityClaimAvailability


@dataclass(frozen=True)
class AccumulatedSkillPreparation:
    """Contain all accumulated valid claims for one Skill.

    Contiene todos los claims válidos acumulados para una Skill.
    """

    skill_id: str
    highest_preparation_state: CurriculumPreparationState
    available_claims: tuple[AccumulatedCapabilityClaim, ...]


@dataclass(frozen=True)
class AccumulatedCapabilityPrecedenceError:
    """Attach one original local precedence error to its curriculum entry.

    Vincula un error local original de precedencia con su entry curricular.
    """

    entry: OrderedCurriculumCandidateEntry
    error: CapabilityClaimPrecedenceError


@dataclass(frozen=True)
class AccumulatedCurriculumPreparationSnapshot:
    """Represent structural preparation accumulated before one real point.

    Representa preparación estructural acumulada antes de un punto real.
    """

    before_point: CurriculumPreparationPoint
    skills: tuple[AccumulatedSkillPreparation, ...]


@dataclass(frozen=True)
class AccumulatedCurriculumUnitResolutionError:
    """Describe failure to identify one unit entry in the supplied context.

    Describe un fallo al identificar una entry de unidad en el contexto.
    """

    unit_id: str
    cause: AccumulatedCurriculumUnitResolutionErrorCause


@dataclass(frozen=True)
class AccumulatedCurriculumPointResolutionError:
    """Attach a slice 8 point error to the resolved curriculum entry.

    Vincula un error de punto de slice 8 con la entry curricular resuelta.
    """

    entry: OrderedCurriculumCandidateEntry
    error: CapabilityPreparationSnapshotPointError


AccumulatedCurriculumPreparationResolutionError: TypeAlias = (
    AccumulatedCurriculumUnitResolutionError
    | AccumulatedCurriculumPointResolutionError
)


@dataclass(frozen=True)
class AccumulatedCurriculumPreparationDerivation:
    """Collect one accumulated snapshot and independent derivation errors.

    Reúne un snapshot acumulado y errores derivativos independientes.
    """

    snapshot: AccumulatedCurriculumPreparationSnapshot | None
    precedence_errors: tuple[AccumulatedCapabilityPrecedenceError, ...]
    resolution_errors: tuple[
        AccumulatedCurriculumPreparationResolutionError, ...
    ]


def derive_accumulated_curriculum_preparation(
    context: OrderedCurriculumCandidateContext,
    *,
    unit_id: str,
    lesson_id: str,
    stage_id: str,
) -> AccumulatedCurriculumPreparationDerivation:
    """Purely accumulate valid structural preparation before one real stage.

    Acumula de forma pura preparación estructural válida antes de un stage real.
    """
    target_matches = [
        (entry_index, entry)
        for entry_index, entry in enumerate(context.entries)
        if entry.position.unit_id == unit_id
    ]
    if len(target_matches) != 1:
        return AccumulatedCurriculumPreparationDerivation(
            snapshot=None,
            precedence_errors=(),
            resolution_errors=(
                AccumulatedCurriculumUnitResolutionError(
                    unit_id=unit_id,
                    cause=(
                        "unknown_unit_in_context"
                        if not target_matches
                        else "ambiguous_unit_in_context"
                    ),
                ),
            ),
        )

    target_index, target_entry = target_matches[0]
    try:
        target_snapshot = derive_capability_preparation_snapshot(
            target_entry.candidate,
            lesson_id=lesson_id,
            stage_id=stage_id,
        )
    except CapabilityPreparationSnapshotPointError as error:
        return AccumulatedCurriculumPreparationDerivation(
            snapshot=None,
            precedence_errors=(),
            resolution_errors=(
                AccumulatedCurriculumPointResolutionError(
                    entry=target_entry,
                    error=error,
                ),
            ),
        )

    accumulated_claims: list[AccumulatedCapabilityClaim] = []
    precedence_errors: list[AccumulatedCapabilityPrecedenceError] = []
    for entry in context.entries[:target_index]:
        precedence = derive_capability_claim_state_precedence(entry.candidate)
        accumulated_claims.extend(
            AccumulatedCapabilityClaim(entry=entry, claim=claim)
            for claim in precedence.valid_claims
        )
        precedence_errors.extend(
            AccumulatedCapabilityPrecedenceError(entry=entry, error=error)
            for error in precedence.precedence_errors
        )

    target_precedence = derive_capability_claim_state_precedence(
        target_entry.candidate
    )
    accumulated_claims.extend(
        AccumulatedCapabilityClaim(entry=target_entry, claim=claim)
        for claim in target_snapshot.available_claims
    )
    precedence_errors.extend(
        AccumulatedCapabilityPrecedenceError(
            entry=target_entry,
            error=error,
        )
        for error in target_precedence.precedence_errors
    )

    claims_by_skill: dict[str, list[AccumulatedCapabilityClaim]] = defaultdict(list)
    for accumulated_claim in accumulated_claims:
        claims_by_skill[accumulated_claim.claim.skill_id].append(
            accumulated_claim
        )

    skills = tuple(
        AccumulatedSkillPreparation(
            skill_id=skill_id,
            highest_preparation_state=max(
                skill_claims,
                key=lambda accumulated_claim: curriculum_preparation_state_index(
                    accumulated_claim.claim.preparation_state
                ),
            ).claim.preparation_state,
            available_claims=tuple(skill_claims),
        )
        for skill_id, skill_claims in claims_by_skill.items()
    )
    return AccumulatedCurriculumPreparationDerivation(
        snapshot=AccumulatedCurriculumPreparationSnapshot(
            before_point=CurriculumPreparationPoint(
                entry=target_entry,
                local_point=target_snapshot.before_point,
            ),
            skills=skills,
        ),
        precedence_errors=tuple(precedence_errors),
        resolution_errors=(),
    )
