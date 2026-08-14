from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.content import ContentTreeResponse
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services import pedagogical_curriculum_candidate_correspondence as subject
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionDerivation,
    CurriculumUnitPositionError,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


POSITION = CurriculumUnitPosition(
    level_code="A1",
    level_index=0,
    unit_id="a1-u1",
    unit_index=0,
)


def _candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(build_candidate_payload())


def _hierarchy() -> ContentTreeResponse:
    return ContentTreeResponse(levels=[])


def _derive(monkeypatch, candidates, *, positions=(POSITION,), errors=()):
    position_derivation = CurriculumUnitPositionDerivation(
        positions=tuple(positions),
        resolution_errors=tuple(errors),
    )
    calls = []

    def derive_positions(hierarchy):
        calls.append(hierarchy)
        return position_derivation

    monkeypatch.setattr(subject, "derive_curriculum_unit_positions", derive_positions)
    hierarchy = _hierarchy()
    result = subject.derive_curriculum_candidate_correspondences(
        hierarchy,
        candidates,
    )
    assert calls == [hierarchy]
    return result, position_derivation, hierarchy


def test_models_are_typed_and_immutable(monkeypatch):
    candidate = _candidate()
    result, _, _ = _derive(monkeypatch, [candidate])
    error = subject.CurriculumCandidateCorrespondenceError(
        candidate=candidate,
        candidate_index=0,
        cause="unknown_candidate_unit",
        related_position_errors=(),
    )

    assert isinstance(result, subject.CurriculumCandidateCorrespondenceDerivation)
    assert isinstance(result.entries[0], subject.OrderedCurriculumCandidateEntry)
    with pytest.raises(FrozenInstanceError):
        result.entries = ()
    with pytest.raises(FrozenInstanceError):
        result.entries[0].position = POSITION
    with pytest.raises(FrozenInstanceError):
        error.cause = "candidate_level_mismatch"


def test_valid_candidate_preserves_candidate_and_position_identity(monkeypatch):
    candidate = _candidate()

    result, _, _ = _derive(monkeypatch, [candidate])

    assert result.correspondence_errors == ()
    assert result.entries[0].candidate is candidate
    assert result.entries[0].position is POSITION


def test_candidate_unit_id_mismatch_is_rejected_without_selecting_an_id(
    monkeypatch,
):
    candidate = _candidate()
    candidate.candidate_unit.id = "different-unit"

    result, _, _ = _derive(monkeypatch, [candidate])

    assert result.entries == ()
    assert result.correspondence_errors[0].cause == "candidate_unit_id_mismatch"


def test_candidate_level_must_match_position_level(monkeypatch):
    candidate = _candidate()
    candidate.specification.level = "A2"

    result, _, _ = _derive(monkeypatch, [candidate])

    assert result.entries == ()
    assert result.correspondence_errors[0].cause == "candidate_level_mismatch"


def test_unknown_candidate_unit_has_no_invented_position(monkeypatch):
    candidate = _candidate()
    candidate.specification.unit_id = "unknown-unit"
    candidate.candidate_unit.id = "unknown-unit"

    result, _, _ = _derive(monkeypatch, [candidate])

    error = result.correspondence_errors[0]
    assert result.entries == ()
    assert error.cause == "unknown_candidate_unit"
    assert error.related_position_errors == ()


@pytest.mark.parametrize("position_cause", ["duplicate_unit", "ambiguous_unit"])
def test_unit_position_error_makes_candidate_position_unresolved(
    monkeypatch, position_cause
):
    candidate = _candidate()
    position_error = CurriculumUnitPositionError(
        level_code="A1" if position_cause == "duplicate_unit" else None,
        unit_id="a1-u1",
        cause=position_cause,
    )

    result, _, _ = _derive(
        monkeypatch,
        [candidate],
        positions=(),
        errors=(position_error,),
    )

    error = result.correspondence_errors[0]
    assert error.cause == "candidate_position_unresolved"
    assert error.related_position_errors == (position_error,)
    assert error.related_position_errors[0] is position_error


@pytest.mark.parametrize("position_cause", ["duplicate_level", "unknown_level"])
def test_level_position_error_is_related_by_declared_level(
    monkeypatch, position_cause
):
    candidate = _candidate()
    position_error = CurriculumUnitPositionError(
        level_code="A1",
        unit_id=None,
        cause=position_cause,
    )

    result, _, _ = _derive(
        monkeypatch,
        [candidate],
        positions=(),
        errors=(position_error,),
    )

    error = result.correspondence_errors[0]
    assert error.cause == "candidate_position_unresolved"
    assert error.related_position_errors[0] is position_error


def test_unrelated_position_error_does_not_replace_unknown_candidate_unit(
    monkeypatch,
):
    candidate = _candidate()
    candidate.specification.unit_id = "unknown-unit"
    candidate.candidate_unit.id = "unknown-unit"
    unrelated = CurriculumUnitPositionError(
        level_code="A2",
        unit_id="other-unit",
        cause="duplicate_unit",
    )

    result, _, _ = _derive(
        monkeypatch,
        [candidate],
        positions=(),
        errors=(unrelated,),
    )

    assert result.correspondence_errors[0].cause == "unknown_candidate_unit"
    assert result.correspondence_errors[0].related_position_errors == ()


def test_position_errors_tuple_is_preserved_exactly(monkeypatch):
    position_error = CurriculumUnitPositionError(
        level_code="A0",
        unit_id=None,
        cause="unknown_level",
    )

    result, position_derivation, _ = _derive(
        monkeypatch,
        [],
        positions=(),
        errors=(position_error,),
    )

    assert result.position_errors is position_derivation.resolution_errors
    assert result.position_errors[0] is position_error


def test_same_candidate_instance_twice_invalidates_both_occurrences(monkeypatch):
    candidate = _candidate()

    result, _, _ = _derive(monkeypatch, [candidate, candidate])

    assert result.entries == ()
    assert [error.candidate_index for error in result.correspondence_errors] == [0, 1]
    assert all(
        error.cause == "duplicate_candidate_for_position"
        for error in result.correspondence_errors
    )
    assert all(error.candidate is candidate for error in result.correspondence_errors)


def test_distinct_candidates_for_same_position_are_both_rejected(monkeypatch):
    first = _candidate()
    second = _candidate()

    result, _, _ = _derive(monkeypatch, [first, second])

    assert result.entries == ()
    assert [error.candidate for error in result.correspondence_errors] == [
        first,
        second,
    ]
    assert all(
        error.cause == "duplicate_candidate_for_position"
        for error in result.correspondence_errors
    )


def test_individually_invalid_candidate_does_not_contaminate_valid_candidate(
    monkeypatch,
):
    valid = _candidate()
    invalid = _candidate()
    invalid.specification.level = "A2"

    result, _, _ = _derive(monkeypatch, [valid, invalid])

    assert len(result.entries) == 1
    assert result.entries[0].candidate is valid
    assert result.correspondence_errors[0].candidate is invalid
    assert result.correspondence_errors[0].cause == "candidate_level_mismatch"


def test_multiple_valid_entries_are_ordered_by_existing_positions(monkeypatch):
    later = _candidate()
    later.specification.unit_id = "b1-unit-z"
    later.candidate_unit.id = "b1-unit-z"
    later.specification.level = "B1"
    earlier = _candidate()
    earlier.specification.unit_id = "a1-unit-z"
    earlier.candidate_unit.id = "a1-unit-z"
    positions = (
        CurriculumUnitPosition("B1", 2, "b1-unit-z", 0),
        CurriculumUnitPosition("A1", 0, "a1-unit-z", 4),
    )

    result, _, _ = _derive(
        monkeypatch,
        [later, earlier],
        positions=positions,
    )

    assert [entry.candidate for entry in result.entries] == [earlier, later]
    assert result.entries[0].position is positions[1]
    assert result.entries[1].position is positions[0]


def test_entry_order_ignores_inverse_unit_ids_and_candidate_input(monkeypatch):
    later = _candidate()
    later.specification.unit_id = "a-unit"
    later.candidate_unit.id = "a-unit"
    later.specification.level = "B1"
    earlier = _candidate()
    earlier.specification.unit_id = "z-unit"
    earlier.candidate_unit.id = "z-unit"
    positions = (
        CurriculumUnitPosition("B1", 2, "a-unit", 0),
        CurriculumUnitPosition("A1", 0, "z-unit", 0),
    )

    result, _, _ = _derive(
        monkeypatch,
        [later, earlier],
        positions=positions,
    )

    assert "a-unit" < "z-unit"
    assert [entry.position.unit_id for entry in result.entries] == [
        "z-unit",
        "a-unit",
    ]
    assert [entry.candidate for entry in result.entries] == [earlier, later]


def test_valid_and_invalid_candidates_coexist_without_fail_fast(monkeypatch):
    valid = _candidate()
    invalid = _candidate()
    invalid.candidate_unit.id = "mismatch"

    result, _, _ = _derive(monkeypatch, [invalid, valid])

    assert [entry.candidate for entry in result.entries] == [valid]
    assert result.correspondence_errors[0].candidate is invalid
    assert result.correspondence_errors[0].candidate_index == 0


def test_every_candidate_occurrence_produces_entry_xor_error(monkeypatch):
    valid = _candidate()
    invalid = _candidate()
    invalid.specification.unit_id = "unknown"
    invalid.candidate_unit.id = "unknown"

    result, _, _ = _derive(monkeypatch, [valid, invalid])

    assert len(result.entries) + len(result.correspondence_errors) == 2
    entry_candidates = {id(entry.candidate) for entry in result.entries}
    error_candidates = {id(error.candidate) for error in result.correspondence_errors}
    assert entry_candidates.isdisjoint(error_candidates)


def test_legacy_candidate_without_plans_can_produce_entry(monkeypatch):
    candidate = _candidate()
    assert candidate.lesson_capability_plans == []

    result, _, _ = _derive(monkeypatch, [candidate])

    assert result.entries[0].candidate is candidate


def test_empty_candidates_keep_position_errors_but_no_correspondence_entries(
    monkeypatch,
):
    position_error = CurriculumUnitPositionError(
        level_code="A0",
        unit_id=None,
        cause="unknown_level",
    )

    result, _, _ = _derive(monkeypatch, [], errors=(position_error,))

    assert result.entries == ()
    assert result.correspondence_errors == ()
    assert result.position_errors == (position_error,)


def test_hierarchy_and_candidates_are_not_modified(monkeypatch):
    candidate = _candidate()
    candidate_before = deepcopy(candidate.model_dump())

    _, _, hierarchy = _derive(monkeypatch, [candidate])

    assert candidate.model_dump() == candidate_before
    assert hierarchy.model_dump() == {"levels": []}


def test_module_does_not_recalculate_positions_or_add_context_global_state():
    source = inspect.getsource(subject)
    prohibited_names = {
        "cefr_level_index",
        "CEFR_LEVEL_ORDER",
        "OrderedCurriculumCandidateContext",
        "context_incomplete",
        "missing_candidate",
        "target_missing",
        "CurriculumCapabilityPreparationLedger",
        "ValidationFinding",
        "validator_id",
    }

    assert prohibited_names.isdisjoint(vars(subject))
    assert "validation_report" not in source
    assert "highest_preparation_state" not in source
    assert "unsatisfied" not in source
    assert "persist" not in source
