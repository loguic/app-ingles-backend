from collections import defaultdict

from app.schemas.pedagogical_unit import (
    CurriculumPreparationState,
    PedagogicalUnitCandidate,
    ValidationFinding,
)
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    derive_capability_claim_availabilities,
)


VALIDATOR_ID = "capability_claim_state_precedence"

_STATE_ORDER = (
    "EXPOSURE_AVAILABLE",
    "INSTRUCTION_AVAILABLE",
    "PRACTICE_AVAILABLE",
    "EVIDENCE_GATE_AVAILABLE",
)
_STATE_INDEX = {state: index for index, state in enumerate(_STATE_ORDER)}


def _position(claim: CapabilityClaimAvailability) -> tuple[int, int]:
    """Return the canonical local position derived by slice 5.

    Devuelve la posición local canónica derivada por la slice 5.
    """
    return claim.lesson_index, claim.point.stage_index


def _output_key(claim: CapabilityClaimAvailability) -> tuple[object, ...]:
    """Provide deterministic output ordering without using IDs as curriculum order.

    Proporciona salida determinista sin usar IDs como orden curricular.
    """
    return (
        *_position(claim),
        _STATE_INDEX[claim.preparation_state],
        claim.skill_id,
        claim.lesson_id,
        claim.artifact_ids,
    )


def _failure_cause(
    claim: CapabilityClaimAvailability,
    required_claims: list[CapabilityClaimAvailability],
    valid_claim_ids: set[int],
) -> str | None:
    """Classify one missing predecessor with a stable priority.

    Clasifica un predecesor ausente con una prioridad estable.
    """
    point = _position(claim)
    valid = [item for item in required_claims if id(item) in valid_claim_ids]
    if any(_position(item) < point for item in valid):
        return None

    # Priority: invalid earlier, valid same point, valid later, any other
    # invalid predecessor, and finally complete absence of the required state.
    if any(_position(item) < point for item in required_claims):
        return "required_state_not_validly_chained"
    if any(_position(item) == point for item in valid):
        return "required_state_same_position"
    if any(_position(item) > point for item in valid):
        return "required_state_only_later"
    if required_claims:
        return "required_state_not_validly_chained"
    return "required_state_absent"


def validate_capability_claim_state_precedence(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Validate strict local state precedence using only slice 5 output.

    Valida la precedencia local estricta usando solo la salida de la slice 5.
    """
    derivation = derive_capability_claim_availabilities(candidate)
    claims = sorted(derivation.availabilities, key=_output_key)
    by_skill_and_state: dict[
        tuple[str, CurriculumPreparationState],
        list[CapabilityClaimAvailability],
    ] = defaultdict(list)
    for claim in claims:
        by_skill_and_state[(claim.skill_id, claim.preparation_state)].append(claim)

    valid_claim_ids: set[int] = set()
    failures: dict[int, tuple[CapabilityClaimAvailability, CurriculumPreparationState, str]] = {}
    for state_index, state in enumerate(_STATE_ORDER):
        state_claims = [claim for claim in claims if claim.preparation_state == state]
        if state_index == 0:
            valid_claim_ids.update(id(claim) for claim in state_claims)
            continue
        required_state = _STATE_ORDER[state_index - 1]
        for claim in state_claims:
            required_claims = by_skill_and_state[(claim.skill_id, required_state)]
            cause = _failure_cause(claim, required_claims, valid_claim_ids)
            if cause is None:
                valid_claim_ids.add(id(claim))
            else:
                failures[id(claim)] = (claim, required_state, cause)

    findings: list[ValidationFinding] = []
    for claim in claims:
        failure = failures.get(id(claim))
        if failure is None:
            continue
        _, required_state, cause = failure
        findings.append(
            ValidationFinding(
                validator_id=VALIDATOR_ID,
                severity="error",
                message=(
                    f"Lesson {claim.lesson_id} claim for Skill {claim.skill_id} "
                    f"declares {claim.preparation_state} but requires "
                    f"{required_state} at a strictly earlier curriculum "
                    f"position: {cause}."
                ),
                reference_ids=[
                    claim.lesson_id,
                    claim.skill_id,
                    claim.preparation_state,
                    required_state,
                    *claim.artifact_ids,
                ],
            )
        )
    return findings
