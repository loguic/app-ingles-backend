from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.schemas.content import ContentTreeResponse
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionError,
    derive_curriculum_unit_positions,
)


CurriculumCandidateCorrespondenceErrorCause = Literal[
    "candidate_unit_id_mismatch",
    "unknown_candidate_unit",
    "candidate_level_mismatch",
    "candidate_position_unresolved",
    "duplicate_candidate_for_position",
]


@dataclass(frozen=True)
class OrderedCurriculumCandidateEntry:
    """Bind one candidate to its canonical curriculum unit position.

    Vincula una candidata con su posición canónica de unidad curricular.
    """

    position: CurriculumUnitPosition
    candidate: PedagogicalUnitCandidate


@dataclass(frozen=True)
class CurriculumCandidateCorrespondenceError:
    """Describe why one candidate occurrence cannot bind to a position.

    Describe por qué una ocurrencia de candidata no puede vincularse a una posición.
    """

    candidate: PedagogicalUnitCandidate
    candidate_index: int
    cause: CurriculumCandidateCorrespondenceErrorCause
    related_position_errors: tuple[CurriculumUnitPositionError, ...]


@dataclass(frozen=True)
class CurriculumCandidateCorrespondenceDerivation:
    """Collect ordered candidate entries and structural correspondence errors.

    Reúne entradas ordenadas y errores estructurales de correspondencia.
    """

    entries: tuple[OrderedCurriculumCandidateEntry, ...]
    position_errors: tuple[CurriculumUnitPositionError, ...]
    correspondence_errors: tuple[CurriculumCandidateCorrespondenceError, ...]


def _related_position_errors(
    candidate: PedagogicalUnitCandidate,
    position_errors: tuple[CurriculumUnitPositionError, ...],
) -> tuple[CurriculumUnitPositionError, ...]:
    unit_id = candidate.specification.unit_id
    level_code = candidate.specification.level
    return tuple(
        error
        for error in position_errors
        if error.unit_id == unit_id
        or (
            error.unit_id is None
            and error.level_code == level_code
        )
    )


def derive_curriculum_candidate_correspondences(
    hierarchy: ContentTreeResponse,
    candidates: Sequence[PedagogicalUnitCandidate],
) -> CurriculumCandidateCorrespondenceDerivation:
    """Purely bind candidate occurrences to canonical unit positions.

    Vincula de forma pura ocurrencias de candidatas con posiciones canónicas.
    """
    position_derivation = derive_curriculum_unit_positions(hierarchy)
    positions_by_unit_id = {
        position.unit_id: position
        for position in position_derivation.positions
    }
    correspondence_errors: list[CurriculumCandidateCorrespondenceError] = []
    provisional_by_position: dict[
        CurriculumUnitPosition,
        list[tuple[int, PedagogicalUnitCandidate]],
    ] = defaultdict(list)

    for candidate_index, candidate in enumerate(candidates):
        specification_unit_id = candidate.specification.unit_id
        if specification_unit_id != candidate.candidate_unit.id:
            correspondence_errors.append(
                CurriculumCandidateCorrespondenceError(
                    candidate=candidate,
                    candidate_index=candidate_index,
                    cause="candidate_unit_id_mismatch",
                    related_position_errors=(),
                )
            )
            continue

        position = positions_by_unit_id.get(specification_unit_id)
        if position is None:
            related_errors = _related_position_errors(
                candidate,
                position_derivation.resolution_errors,
            )
            correspondence_errors.append(
                CurriculumCandidateCorrespondenceError(
                    candidate=candidate,
                    candidate_index=candidate_index,
                    cause=(
                        "candidate_position_unresolved"
                        if related_errors
                        else "unknown_candidate_unit"
                    ),
                    related_position_errors=related_errors,
                )
            )
            continue

        if candidate.specification.level != position.level_code:
            correspondence_errors.append(
                CurriculumCandidateCorrespondenceError(
                    candidate=candidate,
                    candidate_index=candidate_index,
                    cause="candidate_level_mismatch",
                    related_position_errors=(),
                )
            )
            continue

        provisional_by_position[position].append((candidate_index, candidate))

    entries: list[OrderedCurriculumCandidateEntry] = []
    for position, occurrences in provisional_by_position.items():
        if len(occurrences) > 1:
            correspondence_errors.extend(
                CurriculumCandidateCorrespondenceError(
                    candidate=candidate,
                    candidate_index=candidate_index,
                    cause="duplicate_candidate_for_position",
                    related_position_errors=(),
                )
                for candidate_index, candidate in occurrences
            )
            continue
        _, candidate = occurrences[0]
        entries.append(
            OrderedCurriculumCandidateEntry(
                position=position,
                candidate=candidate,
            )
        )

    return CurriculumCandidateCorrespondenceDerivation(
        entries=tuple(
            sorted(
                entries,
                key=lambda entry: (
                    entry.position.level_index,
                    entry.position.unit_index,
                ),
            )
        ),
        position_errors=position_derivation.resolution_errors,
        correspondence_errors=tuple(
            sorted(
                correspondence_errors,
                key=lambda error: error.candidate_index,
            )
        ),
    )
