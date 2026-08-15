"""Derive exact curriculum coverage from an authoritative origin.

Deriva cobertura curricular exacta desde un origen autoritativo.
"""

from dataclasses import dataclass
from typing import Literal

from app.services.pedagogical_authoritative_curriculum_hierarchy import (
    AuthoritativeCurriculumHierarchy,
)
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPositionDerivation,
    derive_curriculum_unit_positions,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)


CompleteFromAuthoritativeOriginErrorCause = Literal[
    "authoritative_hierarchy_position_unresolved",
    "context_origin_mismatch",
    "context_target_outside_authority",
    "authoritative_prefix_mismatch",
]


@dataclass(frozen=True)
class CompleteFromAuthoritativeOrigin:
    """Prove exact context coverage from the authoritative curriculum origin.

    Demuestra cobertura exacta del contexto desde el origen curricular autoritativo.
    """

    authority: AuthoritativeCurriculumHierarchy
    context: OrderedCurriculumCandidateContext


@dataclass(frozen=True)
class CompleteFromAuthoritativeOriginError:
    """Describe why authoritative-origin coverage cannot be established.

    Describe por qué no puede demostrarse cobertura desde el origen autoritativo.
    """

    cause: CompleteFromAuthoritativeOriginErrorCause


@dataclass(frozen=True)
class CompleteFromAuthoritativeOriginDerivation:
    """Collect authoritative positions and an exact proof or one error.

    Reúne posiciones autoritativas y una prueba exacta o un error.
    """

    result: CompleteFromAuthoritativeOrigin | None
    authority_position_derivation: CurriculumUnitPositionDerivation
    errors: tuple[CompleteFromAuthoritativeOriginError, ...]


def _failed_derivation(
    position_derivation: CurriculumUnitPositionDerivation,
    cause: CompleteFromAuthoritativeOriginErrorCause,
) -> CompleteFromAuthoritativeOriginDerivation:
    return CompleteFromAuthoritativeOriginDerivation(
        result=None,
        authority_position_derivation=position_derivation,
        errors=(CompleteFromAuthoritativeOriginError(cause=cause),),
    )


def derive_complete_from_authoritative_origin(
    authority: AuthoritativeCurriculumHierarchy,
    context: OrderedCurriculumCandidateContext,
) -> CompleteFromAuthoritativeOriginDerivation:
    """Derive exact context coverage of one authoritative curriculum prefix.

    Deriva cobertura exacta del contexto sobre un prefijo curricular autoritativo.
    """
    position_derivation = derive_curriculum_unit_positions(authority.hierarchy)
    authority_positions = position_derivation.positions
    if position_derivation.resolution_errors or not authority_positions:
        return _failed_derivation(
            position_derivation,
            "authoritative_hierarchy_position_unresolved",
        )

    if context.scope.start_position != authority_positions[0]:
        return _failed_derivation(
            position_derivation,
            "context_origin_mismatch",
        )

    try:
        target_index = authority_positions.index(
            context.scope.target_position
        )
    except ValueError:
        return _failed_derivation(
            position_derivation,
            "context_target_outside_authority",
        )

    authoritative_prefix = authority_positions[: target_index + 1]
    if context.scope.required_positions != authoritative_prefix:
        return _failed_derivation(
            position_derivation,
            "authoritative_prefix_mismatch",
        )

    return CompleteFromAuthoritativeOriginDerivation(
        result=CompleteFromAuthoritativeOrigin(
            authority=authority,
            context=context,
        ),
        authority_position_derivation=position_derivation,
        errors=(),
    )
