from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.content import ContentTreeResponse
from app.services import pedagogical_curriculum_context_scope as subject
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionDerivation,
    CurriculumUnitPositionError,
)


def _hierarchy(*levels) -> ContentTreeResponse:
    return ContentTreeResponse.model_validate(
        {
            "levels": [
                {
                    "code": level_code,
                    "units": [
                        {"id": unit_id, "title": unit_id, "lessons": []}
                        for unit_id in unit_ids
                    ],
                }
                for level_code, unit_ids in levels
            ]
        }
    )


def _derive(hierarchy, level="A1", unit="target"):
    return subject.derive_curriculum_context_scope(
        hierarchy,
        target_level_code=level,
        target_unit_id=unit,
    )


def test_models_are_typed_and_immutable():
    position = CurriculumUnitPosition("A1", 0, "target", 0)
    error = subject.CurriculumContextScopeError(
        "A1", "target", "target_missing", ()
    )
    scope = subject.CurriculumContextScope(position, position, (position,))
    derivation = subject.CurriculumContextScopeDerivation(scope, (), ())

    with pytest.raises(FrozenInstanceError):
        scope.target_position = position
    with pytest.raises(FrozenInstanceError):
        error.cause = "target_level_mismatch"
    with pytest.raises(FrozenInstanceError):
        derivation.scope = None


def test_first_position_target_produces_single_position_scope():
    result = _derive(_hierarchy(("A1", ["target", "later"])))

    assert result.scope is not None
    assert [position.unit_id for position in result.scope.required_positions] == [
        "target"
    ]
    assert result.scope.start_position is result.scope.required_positions[0]
    assert result.scope.target_position is result.scope.required_positions[-1]
    assert result.scope_errors == ()


def test_intermediate_target_includes_real_prefix_and_target_once():
    result = _derive(_hierarchy(("A1", ["first", "target", "later"])))

    assert result.scope is not None
    assert [position.unit_id for position in result.scope.required_positions] == [
        "first",
        "target",
    ]
    assert sum(
        position is result.scope.target_position
        for position in result.scope.required_positions
    ) == 1


def test_later_level_target_includes_prior_canonical_levels():
    result = _derive(
        _hierarchy(
            ("B1", ["target", "b-later"]),
            ("A2", ["a2-unit"]),
            ("A1", ["a1-unit"]),
        ),
        level="B1",
    )

    assert result.scope is not None
    assert [position.unit_id for position in result.scope.required_positions] == [
        "a1-unit",
        "a2-unit",
        "target",
    ]
    assert [position.level_index for position in result.scope.required_positions] == [
        0,
        1,
        2,
    ]


def test_inverse_unit_ids_do_not_order_scope():
    result = _derive(_hierarchy(("A1", ["z-unit", "a-unit"])), unit="a-unit")

    assert result.scope is not None
    assert [position.unit_id for position in result.scope.required_positions] == [
        "z-unit",
        "a-unit",
    ]


def test_positions_are_original_objects_from_slice_14(monkeypatch):
    first = CurriculumUnitPosition("A1", 0, "first", 0)
    target = CurriculumUnitPosition("A1", 0, "target", 1)
    upstream = CurriculumUnitPositionDerivation((first, target), ())
    monkeypatch.setattr(
        subject, "derive_curriculum_unit_positions", lambda hierarchy: upstream
    )

    result = _derive(_hierarchy())

    assert result.scope is not None
    assert result.scope.required_positions == (first, target)
    assert result.scope.required_positions[0] is first
    assert result.scope.target_position is target
    assert result.scope.start_position is first


def test_only_slice_14_derivation_is_used_for_positions(monkeypatch):
    target = CurriculumUnitPosition("B1", 2, "target", 7)
    calls = []

    def derive(hierarchy):
        calls.append(hierarchy)
        return CurriculumUnitPositionDerivation((target,), ())

    hierarchy = _hierarchy(("A1", ["unrelated-real-unit"]))
    monkeypatch.setattr(subject, "derive_curriculum_unit_positions", derive)

    result = _derive(hierarchy, level="B1")

    assert calls == [hierarchy]
    assert result.scope is not None
    assert result.scope.required_positions == (target,)
    source = inspect.getsource(subject)
    assert "cefr_level_index" not in source
    assert "enumerate(" not in source


def test_missing_target_produces_only_target_missing():
    result = _derive(_hierarchy(("A1", ["other"])))

    assert result.scope is None
    assert [error.cause for error in result.scope_errors] == ["target_missing"]
    assert result.scope_errors[0].related_position_errors == ()


def test_empty_hierarchy_produces_target_missing_not_empty_scope():
    result = _derive(_hierarchy())

    assert result.scope is None
    assert result.position_errors == ()
    assert result.scope_errors[0].cause == "target_missing"


def test_valid_level_without_units_produces_target_missing():
    result = _derive(_hierarchy(("A1", [])))

    assert result.scope is None
    assert result.scope_errors[0].cause == "target_missing"


def test_target_level_mismatch_does_not_correct_declared_level():
    result = _derive(_hierarchy(("A1", ["target"])), level="A2")

    assert result.scope is None
    assert result.scope_errors[0].cause == "target_level_mismatch"
    assert result.scope_errors[0].related_position_errors == ()


@pytest.mark.parametrize(
    ("hierarchy", "level", "unit", "expected_cause"),
    [
        (
            _hierarchy(("A1", ["target", "target"])),
            "A1",
            "target",
            "duplicate_unit",
        ),
        (
            _hierarchy(("A1", ["target"]), ("A2", ["target"])),
            "A1",
            "target",
            "ambiguous_unit",
        ),
        (
            _hierarchy(("A1", ["target"]), ("A1", ["other"])),
            "A1",
            "target",
            "duplicate_level",
        ),
    ],
)
def test_target_affected_by_position_error_is_unresolved(
    hierarchy, level, unit, expected_cause
):
    result = _derive(hierarchy, level=level, unit=unit)

    assert result.scope is None
    assert result.scope_errors[0].cause == "target_position_unresolved"
    assert [
        error.cause for error in result.scope_errors[0].related_position_errors
    ] == [expected_cause]
    assert result.scope_errors[0].related_position_errors[0] is result.position_errors[0]


def test_missing_target_in_duplicate_level_is_not_related_by_level_alone():
    result = _derive(
        _hierarchy(
            ("A1", ["first-real-unit"]),
            ("A1", ["second-real-unit"]),
        ),
        level="A1",
        unit="z-unit",
    )

    assert result.scope is None
    assert result.scope_errors[0].cause == "target_missing"
    assert result.scope_errors[0].cause != "target_position_unresolved"
    assert result.position_errors == (
        CurriculumUnitPositionError("A1", None, "duplicate_level"),
    )
    assert result.scope_errors[0].related_position_errors == ()


def test_valid_target_with_unclassifiable_hierarchy_error_blocks_scope():
    result = _derive(
        _hierarchy(("A1", ["target"]), ("A0", ["unknown-position"]))
    )

    assert result.scope is None
    assert result.scope_errors[0].cause == "hierarchy_position_unresolved"
    assert result.scope_errors[0].related_position_errors == result.position_errors
    assert result.scope_errors[0].related_position_errors[0] is result.position_errors[0]


def test_valid_target_with_duplicate_non_target_unit_blocks_partial_scope():
    result = _derive(
        _hierarchy(("A1", ["duplicate", "target", "duplicate"]))
    )

    assert result.scope is None
    assert result.scope_errors[0].cause == "hierarchy_position_unresolved"
    assert result.scope_errors[0].related_position_errors == result.position_errors


def test_position_errors_are_preserved_exactly(monkeypatch):
    target = CurriculumUnitPosition("A1", 0, "target", 0)
    error = CurriculumUnitPositionError("A0", None, "unknown_level")
    upstream = CurriculumUnitPositionDerivation((target,), (error,))
    monkeypatch.setattr(
        subject, "derive_curriculum_unit_positions", lambda hierarchy: upstream
    )

    result = _derive(_hierarchy())

    assert result.position_errors is upstream.resolution_errors
    assert result.position_errors[0] is error
    assert result.scope_errors[0].related_position_errors[0] is error


def test_hierarchy_is_not_modified():
    hierarchy = _hierarchy(("B1", ["target"]), ("A1", ["first"]))
    before = deepcopy(hierarchy.model_dump())

    _derive(hierarchy, level="B1")

    assert hierarchy.model_dump() == before


def test_scope_has_no_candidates_completeness_preparation_or_ledger():
    source = inspect.getsource(subject)

    assert "PedagogicalUnitCandidate" not in source
    assert "OrderedCurriculumCandidate" not in source
    assert "missing_candidate" not in source
    assert "context_incomplete" not in source
    assert "is_complete" not in source
    assert "Skill" not in source
    assert "unsatisfied" not in source
    assert "Ledger" not in source
    assert "ValidationFinding" not in source
    assert "validation_report" not in source
