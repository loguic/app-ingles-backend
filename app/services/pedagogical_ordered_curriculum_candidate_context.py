from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.schemas.content import ContentTreeResponse
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_curriculum_candidate_correspondence import (
    CurriculumCandidateCorrespondenceError,
    OrderedCurriculumCandidateEntry,
    derive_curriculum_candidate_correspondences,
)
from app.services.pedagogical_curriculum_context_scope import (
    CurriculumContextScope,
    CurriculumContextScopeError,
    derive_curriculum_context_scope,
)
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionError,
)


CurriculumCandidateContextErrorCause = Literal[
    "missing_candidate",
    "correspondence_unresolved",
    "correspondence_derivation_inconsistent",
]


@dataclass(frozen=True)
class OrderedCurriculumCandidateContext:
    """Represent candidate coverage complete within one resolved hierarchy scope.

    Representa cobertura de candidatas completa dentro de un scope de jerarquía.
    """

    scope: CurriculumContextScope
    entries: tuple[OrderedCurriculumCandidateEntry, ...]


@dataclass(frozen=True)
class CurriculumCandidateContextError:
    """Describe why required candidate coverage cannot form an exact context.

    Describe por qué la cobertura requerida no forma un contexto exacto.
    """

    cause: CurriculumCandidateContextErrorCause
    position: CurriculumUnitPosition | None
    related_correspondence_errors: tuple[
        CurriculumCandidateCorrespondenceError, ...
    ]


@dataclass(frozen=True)
class CurriculumCandidateContextDerivation:
    """Collect an exact hierarchy-relative context and all source errors.

    Reúne un contexto exacto relativo a la jerarquía y todos los errores fuente.
    """

    context: OrderedCurriculumCandidateContext | None
    scope_errors: tuple[CurriculumContextScopeError, ...]
    scope_position_errors: tuple[CurriculumUnitPositionError, ...]
    correspondence_position_errors: tuple[CurriculumUnitPositionError, ...]
    correspondence_errors: tuple[CurriculumCandidateCorrespondenceError, ...]
    context_errors: tuple[CurriculumCandidateContextError, ...]


def _correspondence_error_relates_to_position(
    error: CurriculumCandidateCorrespondenceError,
    position: CurriculumUnitPosition,
) -> bool:
    candidate = error.candidate
    specification_unit_id = candidate.specification.unit_id
    candidate_unit_id = candidate.candidate_unit.id
    if error.cause == "candidate_unit_id_mismatch":
        return position.unit_id in {
            specification_unit_id,
            candidate_unit_id,
        }
    return specification_unit_id == position.unit_id


def derive_ordered_curriculum_candidate_context(
    hierarchy: ContentTreeResponse,
    candidates: Sequence[PedagogicalUnitCandidate],
    *,
    target_level_code: str,
    target_unit_id: str,
) -> CurriculumCandidateContextDerivation:
    """Purely derive exact candidate coverage within a canonical target scope.

    Deriva de forma pura cobertura exacta de candidatas dentro del scope objetivo.
    """
    scope_derivation = derive_curriculum_context_scope(
        hierarchy,
        target_level_code=target_level_code,
        target_unit_id=target_unit_id,
    )
    if scope_derivation.scope is None:
        return CurriculumCandidateContextDerivation(
            context=None,
            scope_errors=scope_derivation.scope_errors,
            scope_position_errors=scope_derivation.position_errors,
            correspondence_position_errors=(),
            correspondence_errors=(),
            context_errors=(),
        )

    correspondence_derivation = derive_curriculum_candidate_correspondences(
        hierarchy,
        candidates,
    )
    if (
        scope_derivation.position_errors
        != correspondence_derivation.position_errors
    ):
        return CurriculumCandidateContextDerivation(
            context=None,
            scope_errors=scope_derivation.scope_errors,
            scope_position_errors=scope_derivation.position_errors,
            correspondence_position_errors=(
                correspondence_derivation.position_errors
            ),
            correspondence_errors=(
                correspondence_derivation.correspondence_errors
            ),
            context_errors=(
                CurriculumCandidateContextError(
                    cause="correspondence_derivation_inconsistent",
                    position=None,
                    related_correspondence_errors=(),
                ),
            ),
        )

    entries_by_position: dict[
        CurriculumUnitPosition,
        list[OrderedCurriculumCandidateEntry],
    ] = defaultdict(list)
    for entry in correspondence_derivation.entries:
        entries_by_position[entry.position].append(entry)

    context_entries: list[OrderedCurriculumCandidateEntry] = []
    context_errors: list[CurriculumCandidateContextError] = []
    for required_position in scope_derivation.scope.required_positions:
        related_errors = tuple(
            error
            for error in correspondence_derivation.correspondence_errors
            if _correspondence_error_relates_to_position(
                error,
                required_position,
            )
        )
        if related_errors:
            context_errors.append(
                CurriculumCandidateContextError(
                    cause="correspondence_unresolved",
                    position=required_position,
                    related_correspondence_errors=related_errors,
                )
            )
            continue

        matching_entries = entries_by_position.get(required_position, [])
        if not matching_entries:
            context_errors.append(
                CurriculumCandidateContextError(
                    cause="missing_candidate",
                    position=required_position,
                    related_correspondence_errors=(),
                )
            )
            continue
        if len(matching_entries) > 1:
            context_errors.append(
                CurriculumCandidateContextError(
                    cause="correspondence_derivation_inconsistent",
                    position=required_position,
                    related_correspondence_errors=(),
                )
            )
            continue
        context_entries.append(matching_entries[0])

    context = (
        None
        if context_errors
        else OrderedCurriculumCandidateContext(
            scope=scope_derivation.scope,
            entries=tuple(context_entries),
        )
    )
    return CurriculumCandidateContextDerivation(
        context=context,
        scope_errors=scope_derivation.scope_errors,
        scope_position_errors=scope_derivation.position_errors,
        correspondence_position_errors=(
            correspondence_derivation.position_errors
        ),
        correspondence_errors=correspondence_derivation.correspondence_errors,
        context_errors=tuple(context_errors),
    )
