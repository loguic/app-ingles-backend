from collections import defaultdict
from dataclasses import dataclass

from app.schemas.pedagogical_unit import (
    CurriculumPreparationState,
    PedagogicalUnitCandidate,
)
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    curriculum_preparation_state_index,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    LocalCurriculumPoint,
    derive_capability_preparation_snapshot,
)


@dataclass(frozen=True)
class LocalSkillPreparation:
    """Aggregate valid local preparation claims for one Skill.

    Agrupa claims válidos de preparación local para una Skill.
    """

    skill_id: str
    highest_preparation_state: CurriculumPreparationState
    available_claims: tuple[CapabilityClaimAvailability, ...]


@dataclass(frozen=True)
class LocalCapabilityPreparationView:
    """Describe local structural preparation before one curriculum point.

    Describe preparación estructural local antes de un punto curricular.
    """

    before_point: LocalCurriculumPoint
    skills: tuple[LocalSkillPreparation, ...]


def derive_local_capability_preparation_view(
    candidate: PedagogicalUnitCandidate,
    *,
    lesson_id: str,
    stage_id: str,
) -> LocalCapabilityPreparationView:
    """Purely aggregate one local snapshot by Skill.

    Agrega de forma pura un snapshot local por Skill.
    """
    snapshot = derive_capability_preparation_snapshot(
        candidate,
        lesson_id=lesson_id,
        stage_id=stage_id,
    )
    claims_by_skill: dict[str, list[CapabilityClaimAvailability]] = defaultdict(list)
    for claim in snapshot.available_claims:
        claims_by_skill[claim.skill_id].append(claim)

    skills = tuple(
        LocalSkillPreparation(
            skill_id=skill_id,
            highest_preparation_state=max(
                claims,
                key=lambda claim: curriculum_preparation_state_index(
                    claim.preparation_state
                ),
            ).preparation_state,
            available_claims=tuple(claims),
        )
        for skill_id, claims in sorted(claims_by_skill.items())
    )
    return LocalCapabilityPreparationView(
        before_point=snapshot.before_point,
        skills=skills,
    )
