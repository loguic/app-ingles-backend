from dataclasses import dataclass
from typing import Literal

from app.schemas.content import ContentTreeResponse
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionError,
    derive_curriculum_unit_positions,
)


CurriculumContextScopeErrorCause = Literal[
    "target_missing",
    "target_level_mismatch",
    "target_position_unresolved",
    "hierarchy_position_unresolved",
]


@dataclass(frozen=True)
class CurriculumContextScope:
    """Represent the canonical prefix required through one target unit.

    Representa el prefijo canónico requerido hasta una unidad objetivo.
    """

    start_position: CurriculumUnitPosition
    target_position: CurriculumUnitPosition
    required_positions: tuple[CurriculumUnitPosition, ...]


@dataclass(frozen=True)
class CurriculumContextScopeError:
    """Describe why an exact hierarchy-relative scope cannot be resolved.

    Describe por qué no puede resolverse un alcance exacto relativo a la jerarquía.
    """

    target_level_code: str
    target_unit_id: str
    cause: CurriculumContextScopeErrorCause
    related_position_errors: tuple[CurriculumUnitPositionError, ...]


@dataclass(frozen=True)
class CurriculumContextScopeDerivation:
    """Collect a resolved scope or its structural resolution errors.

    Reúne un alcance resuelto o sus errores estructurales de resolución.
    """

    scope: CurriculumContextScope | None
    position_errors: tuple[CurriculumUnitPositionError, ...]
    scope_errors: tuple[CurriculumContextScopeError, ...]


def _target_related_position_errors(
    *,
    hierarchy: ContentTreeResponse,
    target_level_code: str,
    target_unit_id: str,
    position_errors: tuple[CurriculumUnitPositionError, ...],
) -> tuple[CurriculumUnitPositionError, ...]:
    target_is_present_in_level = any(
        level.code == target_level_code
        and any(unit.id == target_unit_id for unit in level.units)
        for level in hierarchy.levels
    )
    return tuple(
        error
        for error in position_errors
        if error.unit_id == target_unit_id
        or (
            error.unit_id is None
            and error.level_code == target_level_code
            and target_is_present_in_level
        )
    )


def derive_curriculum_context_scope(
    hierarchy: ContentTreeResponse,
    *,
    target_level_code: str,
    target_unit_id: str,
) -> CurriculumContextScopeDerivation:
    """Purely derive the canonical hierarchy prefix through a target unit.

    Deriva de forma pura el prefijo canónico de la jerarquía hasta una unidad objetivo.
    """
    position_derivation = derive_curriculum_unit_positions(hierarchy)
    position_errors = position_derivation.resolution_errors
    target_position = next(
        (
            position
            for position in position_derivation.positions
            if position.unit_id == target_unit_id
        ),
        None,
    )

    if target_position is None:
        related_errors = _target_related_position_errors(
            hierarchy=hierarchy,
            target_level_code=target_level_code,
            target_unit_id=target_unit_id,
            position_errors=position_errors,
        )
        return CurriculumContextScopeDerivation(
            scope=None,
            position_errors=position_errors,
            scope_errors=(
                CurriculumContextScopeError(
                    target_level_code=target_level_code,
                    target_unit_id=target_unit_id,
                    cause=(
                        "target_position_unresolved"
                        if related_errors
                        else "target_missing"
                    ),
                    related_position_errors=related_errors,
                ),
            ),
        )

    if target_level_code != target_position.level_code:
        return CurriculumContextScopeDerivation(
            scope=None,
            position_errors=position_errors,
            scope_errors=(
                CurriculumContextScopeError(
                    target_level_code=target_level_code,
                    target_unit_id=target_unit_id,
                    cause="target_level_mismatch",
                    related_position_errors=(),
                ),
            ),
        )

    if position_errors:
        return CurriculumContextScopeDerivation(
            scope=None,
            position_errors=position_errors,
            scope_errors=(
                CurriculumContextScopeError(
                    target_level_code=target_level_code,
                    target_unit_id=target_unit_id,
                    cause="hierarchy_position_unresolved",
                    related_position_errors=position_errors,
                ),
            ),
        )

    target_key = (target_position.level_index, target_position.unit_index)
    required_positions = tuple(
        position
        for position in position_derivation.positions
        if (position.level_index, position.unit_index) <= target_key
    )
    scope = CurriculumContextScope(
        start_position=required_positions[0],
        target_position=target_position,
        required_positions=required_positions,
    )
    return CurriculumContextScopeDerivation(
        scope=scope,
        position_errors=position_errors,
        scope_errors=(),
    )
