from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.content import ContentTreeResponse
from app.services import pedagogical_curriculum_unit_position as subject


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


def test_models_are_typed_and_immutable():
    position = subject.CurriculumUnitPosition(
        level_code="A1",
        level_index=0,
        unit_id="unit",
        unit_index=0,
    )
    error = subject.CurriculumUnitPositionError(
        level_code="A1",
        unit_id="unit",
        cause="duplicate_unit",
    )
    result = subject.CurriculumUnitPositionDerivation(
        positions=(position,),
        resolution_errors=(error,),
    )

    with pytest.raises(FrozenInstanceError):
        position.unit_index = 1
    with pytest.raises(FrozenInstanceError):
        error.cause = "ambiguous_unit"
    with pytest.raises(FrozenInstanceError):
        result.positions = ()


def test_empty_hierarchy_produces_empty_derivation():
    result = subject.derive_curriculum_unit_positions(_hierarchy())

    assert result.positions == ()
    assert result.resolution_errors == ()


def test_valid_level_without_units_produces_no_entries():
    result = subject.derive_curriculum_unit_positions(_hierarchy(("A1", [])))

    assert result.positions == ()
    assert result.resolution_errors == ()


def test_one_unit_uses_canonical_level_and_real_unit_indices():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("B1", ["unit-z"]))
    )

    assert result.positions == (
        subject.CurriculumUnitPosition(
            level_code="B1",
            level_index=2,
            unit_id="unit-z",
            unit_index=0,
        ),
    )


def test_units_keep_level_units_order_even_when_ids_are_reversed():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("A1", ["unit-z", "unit-a"]))
    )

    assert [(item.unit_id, item.unit_index) for item in result.positions] == [
        ("unit-z", 0),
        ("unit-a", 1),
    ]


def test_levels_out_of_declaration_order_are_output_in_cefr_order():
    hierarchy = _hierarchy(
        ("B1", ["b-unit"]),
        ("A1", ["z-unit"]),
        ("A2", ["a-unit"]),
    )

    result = subject.derive_curriculum_unit_positions(hierarchy)

    assert [item.level_code for item in result.positions] == ["A1", "A2", "B1"]
    assert [item.level_index for item in result.positions] == [0, 1, 2]


def test_unknown_level_produces_error_and_no_positions_for_it():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("A0", ["unknown-unit"]), ("A1", ["valid-unit"]))
    )

    assert [item.unit_id for item in result.positions] == ["valid-unit"]
    assert result.resolution_errors == (
        subject.CurriculumUnitPositionError(
            level_code="A0",
            unit_id=None,
            cause="unknown_level",
        ),
    )


def test_duplicate_level_excludes_all_its_units():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(
            ("A1", ["first"]),
            ("A2", ["valid"]),
            ("A1", ["second"]),
        )
    )

    assert [item.unit_id for item in result.positions] == ["valid"]
    assert result.resolution_errors == (
        subject.CurriculumUnitPositionError(
            level_code="A1",
            unit_id=None,
            cause="duplicate_level",
        ),
    )


def test_duplicate_unit_within_level_excludes_every_occurrence():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("A1", ["duplicate", "valid", "duplicate"]))
    )

    assert [(item.unit_id, item.unit_index) for item in result.positions] == [
        ("valid", 1)
    ]
    assert result.resolution_errors == (
        subject.CurriculumUnitPositionError(
            level_code="A1",
            unit_id="duplicate",
            cause="duplicate_unit",
        ),
    )


def test_same_unit_id_across_levels_is_ambiguous_and_fully_excluded():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(
            ("A1", ["shared", "a-valid"]),
            ("A2", ["b-valid", "shared"]),
        )
    )

    assert [item.unit_id for item in result.positions] == ["a-valid", "b-valid"]
    assert result.resolution_errors == (
        subject.CurriculumUnitPositionError(
            level_code=None,
            unit_id="shared",
            cause="ambiguous_unit",
        ),
    )


def test_local_duplicate_and_cross_level_ambiguity_are_both_reported():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(
            ("A1", ["shared", "shared", "a-valid"]),
            ("A2", ["shared", "b-valid"]),
            ("A0", ["ignored"]),
        )
    )

    assert [item.unit_id for item in result.positions] == ["a-valid", "b-valid"]
    assert [error.cause for error in result.resolution_errors] == [
        "unknown_level",
        "duplicate_unit",
        "ambiguous_unit",
    ]


def test_no_invalid_identity_appears_in_positions_and_errors():
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("A1", ["duplicate", "duplicate", "valid"]))
    )
    error_unit_ids = {
        error.unit_id
        for error in result.resolution_errors
        if error.unit_id is not None
    }
    position_unit_ids = {position.unit_id for position in result.positions}

    assert error_unit_ids.isdisjoint(position_unit_ids)


def test_positions_and_errors_are_deterministic_when_levels_are_reordered():
    first = _hierarchy(
        ("B1", ["shared", "b-valid"]),
        ("A0", ["unknown"]),
        ("A1", ["a-valid", "shared"]),
    )
    second = _hierarchy(
        ("A1", ["a-valid", "shared"]),
        ("B1", ["shared", "b-valid"]),
        ("A0", ["unknown"]),
    )

    assert subject.derive_curriculum_unit_positions(
        first
    ) == subject.derive_curriculum_unit_positions(second)


def test_hierarchy_is_not_modified():
    hierarchy = _hierarchy(("B1", ["unit-z"]), ("A1", ["unit-a"]))
    before = deepcopy(hierarchy.model_dump())

    subject.derive_curriculum_unit_positions(hierarchy)

    assert hierarchy.model_dump() == before


def test_public_cefr_index_is_the_only_level_order_source(monkeypatch):
    calls = []

    def level_index(level_code):
        calls.append(level_code)
        return {"A1": 5, "B1": 0}[level_code]

    monkeypatch.setattr(subject, "cefr_level_index", level_index)
    result = subject.derive_curriculum_unit_positions(
        _hierarchy(("A1", ["a-unit"]), ("B1", ["b-unit"]))
    )

    assert [item.level_code for item in result.positions] == ["B1", "A1"]
    assert calls == ["A1", "B1"]


def test_module_has_no_parallel_cefr_context_candidate_or_ledger_api():
    source = inspect.getsource(subject)
    prohibited_names = {
        "CEFR_LEVEL_ORDER",
        "OrderedCurriculumCandidateContext",
        "PedagogicalUnitCandidate",
        "context_incomplete",
        "missing_candidate",
        "target_missing",
        "CurriculumCapabilityPreparationLedger",
        "ValidationFinding",
        "validator_id",
    }

    assert prohibited_names.isdisjoint(vars(subject))
    assert "skill_id" not in source
    assert "validation_report" not in source
    assert "highest_preparation_state" not in source
    assert "unsatisfied" not in source
    assert "persist" not in source
