from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.content import ContentTreeResponse
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services import pedagogical_ordered_curriculum_candidate_context as subject
from app.services.pedagogical_curriculum_candidate_correspondence import (
    CurriculumCandidateCorrespondenceDerivation,
    CurriculumCandidateCorrespondenceError,
    OrderedCurriculumCandidateEntry,
)
from app.services.pedagogical_curriculum_context_scope import (
    CurriculumContextScope,
    CurriculumContextScopeDerivation,
    CurriculumContextScopeError,
)
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionError,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


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


def _candidate(unit_id="a1-u1", level="A1") -> PedagogicalUnitCandidate:
    candidate = PedagogicalUnitCandidate.model_validate(build_candidate_payload())
    candidate.specification.unit_id = unit_id
    candidate.specification.level = level
    candidate.candidate_unit.id = unit_id
    return candidate


def _derive(hierarchy, candidates, *, level="A1", unit="a1-u1"):
    return subject.derive_ordered_curriculum_candidate_context(
        hierarchy,
        candidates,
        target_level_code=level,
        target_unit_id=unit,
    )


def test_models_are_typed_and_immutable():
    position = CurriculumUnitPosition("A1", 0, "a1-u1", 0)
    candidate = _candidate()
    entry = OrderedCurriculumCandidateEntry(position, candidate)
    scope = CurriculumContextScope(position, position, (position,))
    context = subject.OrderedCurriculumCandidateContext(scope, (entry,))
    error = subject.CurriculumCandidateContextError(
        "missing_candidate", position, ()
    )
    derivation = subject.CurriculumCandidateContextDerivation(
        context, (), (), (), (), ()
    )

    with pytest.raises(FrozenInstanceError):
        context.entries = ()
    with pytest.raises(FrozenInstanceError):
        error.cause = "correspondence_unresolved"
    with pytest.raises(FrozenInstanceError):
        derivation.context = None


def test_invalid_scope_preserves_only_scope_semantics(monkeypatch):
    position_error = CurriculumUnitPositionError("A0", None, "unknown_level")
    scope_error = CurriculumContextScopeError(
        "A1", "missing", "target_missing", ()
    )
    scope_derivation = CurriculumContextScopeDerivation(
        None, (position_error,), (scope_error,)
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_context_scope",
        lambda *args, **kwargs: scope_derivation,
    )

    def unexpected(*args, **kwargs):
        raise AssertionError("correspondences must not be derived")

    monkeypatch.setattr(
        subject, "derive_curriculum_candidate_correspondences", unexpected
    )
    result = _derive(_hierarchy(), [])

    assert result.context is None
    assert result.scope_errors is scope_derivation.scope_errors
    assert result.scope_position_errors is scope_derivation.position_errors
    assert result.correspondence_position_errors == ()
    assert result.correspondence_errors == ()
    assert result.context_errors == ()


@pytest.mark.parametrize(
    ("hierarchy", "level", "unit"),
    [(_hierarchy(), "A1", "missing"), (_hierarchy(("A1", ["other"])), "A1", "missing")],
)
def test_empty_hierarchy_or_invalid_target_has_no_completeness_errors(
    hierarchy, level, unit
):
    result = _derive(hierarchy, [], level=level, unit=unit)

    assert result.context is None
    assert result.scope_errors[0].cause == "target_missing"
    assert result.context_errors == ()


def test_single_position_context_is_complete_within_hierarchy():
    candidate = _candidate()
    result = _derive(_hierarchy(("A1", ["a1-u1"])), [candidate])

    assert result.context is not None
    assert result.context.scope.required_positions == (
        result.context.scope.target_position,
    )
    assert result.context.entries[0].candidate is candidate
    assert result.context_errors == ()


def test_multiple_units_and_levels_follow_scope_order_not_candidate_input():
    first = _candidate("z-unit", "A1")
    middle = _candidate("m-unit", "A2")
    target = _candidate("a-unit", "B1")
    hierarchy = _hierarchy(
        ("B1", ["a-unit"]),
        ("A2", ["m-unit"]),
        ("A1", ["z-unit"]),
    )

    result = _derive(
        hierarchy,
        [target, middle, first],
        level="B1",
        unit="a-unit",
    )

    assert result.context is not None
    assert "a-unit" < "m-unit" < "z-unit"
    assert [entry.position.unit_id for entry in result.context.entries] == [
        "z-unit",
        "m-unit",
        "a-unit",
    ]
    assert [entry.candidate for entry in result.context.entries] == [
        first,
        middle,
        target,
    ]


def test_separate_derivations_use_structural_equality_not_python_identity():
    result = _derive(
        _hierarchy(("A1", ["a1-u1", "second"])),
        [_candidate(), _candidate("second")],
        unit="second",
    )

    assert result.context is not None
    for required_position, entry in zip(
        result.context.scope.required_positions,
        result.context.entries,
        strict=True,
    ):
        assert entry.position == required_position
        assert entry.position is not required_position


def test_context_preserves_original_scope_and_correspondence_entries(monkeypatch):
    scope_position = CurriculumUnitPosition("A1", 0, "a1-u1", 0)
    entry_position = CurriculumUnitPosition("A1", 0, "a1-u1", 0)
    scope = CurriculumContextScope(scope_position, scope_position, (scope_position,))
    scope_derivation = CurriculumContextScopeDerivation(scope, (), ())
    entry = OrderedCurriculumCandidateEntry(entry_position, _candidate())
    correspondence_derivation = CurriculumCandidateCorrespondenceDerivation(
        (entry,), (), ()
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_context_scope",
        lambda *args, **kwargs: scope_derivation,
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_candidate_correspondences",
        lambda *args, **kwargs: correspondence_derivation,
    )

    result = _derive(_hierarchy(), [])

    assert result.context is not None
    assert result.context.scope is scope
    assert result.context.entries[0] is entry


def test_one_missing_candidate_produces_one_position_error():
    result = _derive(
        _hierarchy(("A1", ["a1-u1", "missing"])),
        [_candidate()],
        unit="missing",
    )

    assert result.context is None
    assert [(error.cause, error.position.unit_id) for error in result.context_errors] == [
        ("missing_candidate", "missing")
    ]
    assert result.context_errors[0].related_correspondence_errors == ()


def test_empty_candidates_produce_one_missing_error_per_required_position():
    result = _derive(
        _hierarchy(("A1", ["first", "target"])),
        [],
        unit="target",
    )

    assert result.context is None
    assert [(error.cause, error.position.unit_id) for error in result.context_errors] == [
        ("missing_candidate", "first"),
        ("missing_candidate", "target"),
    ]


def test_relevant_correspondence_error_replaces_missing_candidate():
    invalid = _candidate()
    invalid.specification.level = "A2"

    result = _derive(_hierarchy(("A1", ["a1-u1"])), [invalid])

    assert result.context is None
    assert [error.cause for error in result.context_errors] == [
        "correspondence_unresolved"
    ]
    assert result.context_errors[0].related_correspondence_errors[0] is (
        result.correspondence_errors[0]
    )


def test_multiple_relevant_errors_form_one_context_error_and_block_valid_entry():
    valid = _candidate()
    first_invalid = _candidate()
    first_invalid.specification.level = "A2"
    second_invalid = _candidate()
    second_invalid.specification.level = "B1"

    result = _derive(
        _hierarchy(("A1", ["a1-u1"])),
        [valid, first_invalid, second_invalid],
    )

    assert result.context is None
    assert len(result.context_errors) == 1
    error = result.context_errors[0]
    assert error.cause == "correspondence_unresolved"
    assert error.related_correspondence_errors == result.correspondence_errors
    assert all(
        related is source
        for related, source in zip(
            error.related_correspondence_errors,
            result.correspondence_errors,
            strict=True,
        )
    )


def test_duplicate_candidates_in_scope_are_correspondence_unresolved():
    result = _derive(
        _hierarchy(("A1", ["a1-u1"])),
        [_candidate(), _candidate()],
    )

    assert result.context is None
    assert len(result.context_errors) == 1
    assert result.context_errors[0].cause == "correspondence_unresolved"
    assert len(result.context_errors[0].related_correspondence_errors) == 2


def test_entry_after_target_is_excluded_without_blocking_context():
    first = _candidate()
    later = _candidate("later")

    result = _derive(
        _hierarchy(("A1", ["a1-u1", "later"])),
        [later, first],
    )

    assert result.context is not None
    assert [entry.candidate for entry in result.context.entries] == [first]


def test_unknown_candidate_outside_scope_is_preserved_without_blocking():
    valid = _candidate()
    unknown = _candidate("outside")

    result = _derive(
        _hierarchy(("A1", ["a1-u1", "later"])),
        [unknown, valid],
    )

    assert result.context is not None
    assert result.correspondence_errors[0].cause == "unknown_candidate_unit"
    assert result.correspondence_errors[0].candidate is unknown
    assert result.context_errors == ()


def test_contradictory_candidate_ids_are_not_arbitrarily_selected():
    valid = _candidate()
    contradictory = _candidate("outside")
    contradictory.candidate_unit.id = "a1-u1"

    result = _derive(
        _hierarchy(("A1", ["a1-u1"])),
        [valid, contradictory],
    )

    assert result.context is None
    assert result.context_errors[0].cause == "correspondence_unresolved"
    assert result.context_errors[0].related_correspondence_errors[0].candidate is (
        contradictory
    )


def test_structurally_different_position_errors_block_composition(monkeypatch):
    position = CurriculumUnitPosition("A1", 0, "a1-u1", 0)
    scope_position_error = CurriculumUnitPositionError(
        "A0", None, "unknown_level"
    )
    correspondence_position_error = CurriculumUnitPositionError(
        "A1", "other", "duplicate_unit"
    )
    scope = CurriculumContextScope(position, position, (position,))
    scope_derivation = CurriculumContextScopeDerivation(
        scope, (scope_position_error,), ()
    )
    correspondence_derivation = CurriculumCandidateCorrespondenceDerivation(
        (), (correspondence_position_error,), ()
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_context_scope",
        lambda *args, **kwargs: scope_derivation,
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_candidate_correspondences",
        lambda *args, **kwargs: correspondence_derivation,
    )

    result = _derive(_hierarchy(), [])

    assert result.context is None
    assert result.context_errors[0].cause == "correspondence_derivation_inconsistent"
    assert result.scope_position_errors is scope_derivation.position_errors
    assert result.correspondence_position_errors is (
        correspondence_derivation.position_errors
    )
    assert result.scope_position_errors[0] is scope_position_error
    assert result.correspondence_position_errors[0] is correspondence_position_error


def test_equal_position_error_tuples_need_not_share_python_identity(monkeypatch):
    position = CurriculumUnitPosition("A1", 0, "a1-u1", 0)
    scope_error = CurriculumUnitPositionError("A0", None, "unknown_level")
    correspondence_error = CurriculumUnitPositionError("A0", None, "unknown_level")
    scope = CurriculumContextScope(position, position, (position,))
    scope_derivation = CurriculumContextScopeDerivation(scope, (scope_error,), ())
    entry = OrderedCurriculumCandidateEntry(position, _candidate())
    correspondence_derivation = CurriculumCandidateCorrespondenceDerivation(
        (entry,), (correspondence_error,), ()
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_context_scope",
        lambda *args, **kwargs: scope_derivation,
    )
    monkeypatch.setattr(
        subject,
        "derive_curriculum_candidate_correspondences",
        lambda *args, **kwargs: correspondence_derivation,
    )

    result = _derive(_hierarchy(), [])

    assert result.context is not None
    assert result.scope_position_errors[0] is scope_error
    assert result.correspondence_position_errors[0] is correspondence_error
    assert scope_error is not correspondence_error


def test_legacy_candidate_without_plans_covers_required_position():
    candidate = _candidate()
    assert candidate.lesson_capability_plans == []

    result = _derive(_hierarchy(("A1", ["a1-u1"])), [candidate])

    assert result.context is not None
    assert result.context.entries[0].candidate is candidate


def test_hierarchy_and_candidates_are_not_modified():
    hierarchy = _hierarchy(("A1", ["a1-u1"]))
    candidate = _candidate()
    hierarchy_before = deepcopy(hierarchy.model_dump())
    candidate_before = deepcopy(candidate.model_dump())

    _derive(hierarchy, [candidate])

    assert hierarchy.model_dump() == hierarchy_before
    assert candidate.model_dump() == candidate_before


def test_context_has_no_boolean_global_preparation_ledger_or_findings():
    source = inspect.getsource(subject)

    assert "is_complete" not in source
    assert "globally_complete" not in source
    assert "highest_preparation_state" not in source
    assert "SkillPrerequisite" not in source
    assert "unsatisfied" not in source
    assert "cycle" not in source
    assert "Ledger" not in source
    assert "ValidationFinding" not in source
    assert "validation_report" not in source
