from collections import defaultdict
from dataclasses import dataclass

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


@dataclass(frozen=True)
class CapabilityClaimPrecedenceError:
    """Describe why one positioned claim lacks valid prior preparation.

    Describe por qué un claim posicionado carece de preparación previa válida.
    """

    claim: CapabilityClaimAvailability
    required_preparation_state: CurriculumPreparationState
    cause: str

    @property
    def lesson_id(self) -> str:
        return self.claim.lesson_id

    @property
    def skill_id(self) -> str:
        return self.claim.skill_id

    @property
    def preparation_state(self) -> CurriculumPreparationState:
        return self.claim.preparation_state

    @property
    def artifact_ids(self) -> tuple[str, ...]:
        return self.claim.artifact_ids


@dataclass(frozen=True)
class CapabilityClaimPrecedenceDerivation:
    """Partition positioned claims by whether their precedence is valid.

    Particiona claims posicionados según la validez de su precedencia.
    """

    valid_claims: tuple[CapabilityClaimAvailability, ...]
    precedence_errors: tuple[CapabilityClaimPrecedenceError, ...]


def _position(claim: CapabilityClaimAvailability) -> tuple[int, int]:
    """Return the canonical local position derived by slice 5.

    Devuelve la posición local canónica derivada por la slice 5.
    """
    return claim.lesson_index, claim.point.stage_index


def _state_index(state: CurriculumPreparationState) -> int:
    """Return one state's position in the immutable canonical order.

    Devuelve la posición de un estado en el orden canónico inmutable.
    """
    return _STATE_ORDER.index(state)


def _output_key(claim: CapabilityClaimAvailability) -> tuple[object, ...]:
    """Provide deterministic output ordering without using IDs as curriculum order.

    Proporciona salida determinista sin usar IDs como orden curricular.
    """
    return (
        *_position(claim),
        _state_index(claim.preparation_state),
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


def derive_capability_claim_state_precedence(
    candidate: PedagogicalUnitCandidate,
) -> CapabilityClaimPrecedenceDerivation:
    """Purely partition slice 5 claims by strict local precedence.

    Particiona de forma pura los claims de slice 5 por precedencia local estricta.
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
    failures: dict[int, CapabilityClaimPrecedenceError] = {}
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
                failures[id(claim)] = CapabilityClaimPrecedenceError(
                    claim=claim,
                    required_preparation_state=required_state,
                    cause=cause,
                )

    return CapabilityClaimPrecedenceDerivation(
        valid_claims=tuple(
            claim for claim in claims if id(claim) in valid_claim_ids
        ),
        precedence_errors=tuple(
            failures[id(claim)] for claim in claims if id(claim) in failures
        ),
    )


def validate_capability_claim_state_precedence(
    candidate: PedagogicalUnitCandidate,
) -> list[ValidationFinding]:
    """Translate precedence derivation errors into validation findings.

    Traduce errores de derivación de precedencia a findings de validación.
    """
    derivation = derive_capability_claim_state_precedence(candidate)

    findings: list[ValidationFinding] = []
    for error in derivation.precedence_errors:
        findings.append(
            ValidationFinding(
                validator_id=VALIDATOR_ID,
                severity="error",
                message=(
                    f"Lesson {error.lesson_id} claim for Skill {error.skill_id} "
                    f"declares {error.preparation_state} but requires "
                    f"{error.required_preparation_state} at a strictly earlier "
                    f"curriculum position: {error.cause}."
                ),
                reference_ids=[
                    error.lesson_id,
                    error.skill_id,
                    error.preparation_state,
                    error.required_preparation_state,
                    *error.artifact_ids,
                ],
            )
        )
    return findings
