from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Literal

from app.schemas.content import ContentTreeResponse, Level
from app.services.pedagogical_curriculum_order import cefr_level_index


CurriculumUnitPositionErrorCause = Literal[
    "unknown_level",
    "duplicate_level",
    "duplicate_unit",
    "ambiguous_unit",
]


@dataclass(frozen=True)
class CurriculumUnitPosition:
    """Represent one canonical unit position in the curriculum hierarchy.

    Representa una posición canónica de unidad en la jerarquía curricular.
    """

    level_code: str
    level_index: int
    unit_id: str
    unit_index: int


@dataclass(frozen=True)
class CurriculumUnitPositionError:
    """Describe one structural unit-position resolution error.

    Describe un error estructural al resolver la posición de una unidad.
    """

    level_code: str | None
    unit_id: str | None
    cause: CurriculumUnitPositionErrorCause


@dataclass(frozen=True)
class CurriculumUnitPositionDerivation:
    """Collect unambiguous positions and structural resolution errors.

    Reúne posiciones inequívocas y errores estructurales de resolución.
    """

    positions: tuple[CurriculumUnitPosition, ...]
    resolution_errors: tuple[CurriculumUnitPositionError, ...]


def _error_output_key(
    error: CurriculumUnitPositionError,
) -> tuple[object, ...]:
    cause_index = {
        "unknown_level": 0,
        "duplicate_level": 1,
        "duplicate_unit": 2,
        "ambiguous_unit": 3,
    }[error.cause]
    try:
        level_index = (
            cefr_level_index(error.level_code)
            if error.level_code is not None
            else -1
        )
    except ValueError:
        level_index = -1
    return (
        cause_index,
        level_index,
        error.level_code or "",
        error.unit_id or "",
    )


def derive_curriculum_unit_positions(
    hierarchy: ContentTreeResponse,
) -> CurriculumUnitPositionDerivation:
    """Purely derive canonical positions for unambiguous curriculum units.

    Deriva de forma pura posiciones canónicas de unidades inequívocas.
    """
    levels_by_code = defaultdict(list)
    for level in hierarchy.levels:
        levels_by_code[level.code].append(level)

    errors: list[CurriculumUnitPositionError] = []
    valid_levels: list[tuple[int, Level]] = []
    for level_code, levels in levels_by_code.items():
        try:
            level_index = cefr_level_index(level_code)
        except ValueError:
            errors.append(
                CurriculumUnitPositionError(
                    level_code=level_code,
                    unit_id=None,
                    cause="unknown_level",
                )
            )
            if len(levels) > 1:
                errors.append(
                    CurriculumUnitPositionError(
                        level_code=level_code,
                        unit_id=None,
                        cause="duplicate_level",
                    )
                )
            continue
        if len(levels) > 1:
            errors.append(
                CurriculumUnitPositionError(
                    level_code=level_code,
                    unit_id=None,
                    cause="duplicate_level",
                )
            )
            continue
        valid_levels.append((level_index, levels[0]))

    unit_occurrences = defaultdict(list)
    locally_duplicated: set[tuple[str, str]] = set()
    for level_index, level in valid_levels:
        unit_counts = Counter(unit.id for unit in level.units)
        for unit_id, count in unit_counts.items():
            if count > 1:
                locally_duplicated.add((level.code, unit_id))
                errors.append(
                    CurriculumUnitPositionError(
                        level_code=level.code,
                        unit_id=unit_id,
                        cause="duplicate_unit",
                    )
                )
        for unit_index, unit in enumerate(level.units):
            unit_occurrences[unit.id].append(
                (level.code, level_index, unit_index)
            )

    ambiguous_unit_ids = {
        unit_id
        for unit_id, occurrences in unit_occurrences.items()
        if len({level_code for level_code, _, _ in occurrences}) > 1
    }
    errors.extend(
        CurriculumUnitPositionError(
            level_code=None,
            unit_id=unit_id,
            cause="ambiguous_unit",
        )
        for unit_id in ambiguous_unit_ids
    )

    positions = tuple(
        sorted(
            (
                CurriculumUnitPosition(
                    level_code=level_code,
                    level_index=level_index,
                    unit_id=unit_id,
                    unit_index=unit_index,
                )
                for unit_id, occurrences in unit_occurrences.items()
                for level_code, level_index, unit_index in occurrences
                if (level_code, unit_id) not in locally_duplicated
                and unit_id not in ambiguous_unit_ids
            ),
            key=lambda position: (position.level_index, position.unit_index),
        )
    )
    return CurriculumUnitPositionDerivation(
        positions=positions,
        resolution_errors=tuple(sorted(errors, key=_error_output_key)),
    )
