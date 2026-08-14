from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services import pedagogical_accumulated_curriculum_preparation as subject
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    CapabilityClaimPrecedenceDerivation,
    CapabilityClaimPrecedenceError,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    CapabilityPreparationSnapshot,
    CapabilityPreparationSnapshotPointError,
    LocalCurriculumPoint,
)
from app.services.pedagogical_curriculum_candidate_correspondence import (
    OrderedCurriculumCandidateEntry,
)
from app.services.pedagogical_curriculum_context_scope import CurriculumContextScope
from app.services.pedagogical_curriculum_unit_position import CurriculumUnitPosition
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


def _candidate(unit_id: str) -> PedagogicalUnitCandidate:
    candidate = PedagogicalUnitCandidate.model_validate(build_candidate_payload())
    candidate.specification.unit_id = unit_id
    candidate.candidate_unit.id = unit_id
    return candidate


def _entry(unit_id: str, unit_index: int) -> OrderedCurriculumCandidateEntry:
    return OrderedCurriculumCandidateEntry(
        position=CurriculumUnitPosition("A1", 0, unit_id, unit_index),
        candidate=_candidate(unit_id),
    )


def _context(*entries: OrderedCurriculumCandidateEntry):
    positions = tuple(entry.position for entry in entries)
    scope = CurriculumContextScope(positions[0], positions[-1], positions)
    return OrderedCurriculumCandidateContext(scope=scope, entries=tuple(entries))


def _claim(
    skill_id: str,
    state: str = "EXPOSURE_AVAILABLE",
    *,
    lesson_index: int = 0,
    stage_index: int = 0,
    suffix: str = "one",
) -> CapabilityClaimAvailability:
    return CapabilityClaimAvailability(
        lesson_id=f"lesson-{lesson_index}",
        lesson_index=lesson_index,
        point=IntraLessonAvailabilityPoint(
            sort_index=stage_index + 1,
            stage_id=f"stage-{stage_index}",
            stage_index=stage_index,
        ),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=(f"artifact-{suffix}",),
    )


def _point() -> LocalCurriculumPoint:
    return LocalCurriculumPoint("lesson-0", "stage-0", 0, 0)


def _install_derivations(
    monkeypatch,
    *,
    precedence_by_candidate=None,
    target_snapshot=None,
    point_error=None,
):
    precedence_by_candidate = precedence_by_candidate or {}
    precedence_calls = []
    snapshot_calls = []

    def derive_precedence(candidate):
        precedence_calls.append(candidate)
        return precedence_by_candidate.get(
            id(candidate), CapabilityClaimPrecedenceDerivation((), ())
        )

    def derive_snapshot(candidate, *, lesson_id, stage_id):
        snapshot_calls.append((candidate, lesson_id, stage_id))
        if point_error is not None:
            raise point_error
        return target_snapshot or CapabilityPreparationSnapshot(_point(), ())

    monkeypatch.setattr(
        subject, "derive_capability_claim_state_precedence", derive_precedence
    )
    monkeypatch.setattr(
        subject, "derive_capability_preparation_snapshot", derive_snapshot
    )
    return precedence_calls, snapshot_calls


def _derive(context, *, unit_id=None):
    return subject.derive_accumulated_curriculum_preparation(
        context,
        unit_id=unit_id or context.entries[-1].position.unit_id,
        lesson_id="lesson-0",
        stage_id="stage-0",
    )


def test_models_are_typed_and_immutable():
    entry = _entry("unit", 0)
    claim = _claim("skill")
    accumulated_claim = subject.AccumulatedCapabilityClaim(entry, claim)
    skill = subject.AccumulatedSkillPreparation(
        "skill", "EXPOSURE_AVAILABLE", (accumulated_claim,)
    )
    point = subject.CurriculumPreparationPoint(entry, _point())
    snapshot = subject.AccumulatedCurriculumPreparationSnapshot(point, (skill,))
    derivation = subject.AccumulatedCurriculumPreparationDerivation(
        snapshot, (), ()
    )

    with pytest.raises(FrozenInstanceError):
        point.entry = entry
    with pytest.raises(FrozenInstanceError):
        accumulated_claim.claim = claim
    with pytest.raises(FrozenInstanceError):
        skill.available_claims = ()
    with pytest.raises(FrozenInstanceError):
        derivation.snapshot = None


def test_unknown_unit_produces_no_snapshot_or_local_calls(monkeypatch):
    context = _context(_entry("known", 0))
    precedence_calls, snapshot_calls = _install_derivations(monkeypatch)

    result = _derive(context, unit_id="unknown")

    assert result.snapshot is None
    assert result.precedence_errors == ()
    assert result.resolution_errors[0].cause == "unknown_unit_in_context"
    assert precedence_calls == []
    assert snapshot_calls == []


def test_ambiguous_unit_is_rejected_defensively(monkeypatch):
    first = _entry("duplicate", 0)
    second = _entry("duplicate", 1)
    context = _context(first, second)
    precedence_calls, snapshot_calls = _install_derivations(monkeypatch)

    result = _derive(context, unit_id="duplicate")

    assert result.snapshot is None
    assert result.resolution_errors[0].cause == "ambiguous_unit_in_context"
    assert precedence_calls == []
    assert snapshot_calls == []


@pytest.mark.parametrize(
    "cause",
    [
        "unknown_lesson",
        "ambiguous_lesson",
        "lesson_without_experience",
        "unknown_stage_for_lesson",
    ],
)
def test_slice_8_point_errors_are_preserved_without_partial_snapshot(
    monkeypatch, cause
):
    entry = _entry("unit", 0)
    context = _context(entry)
    point_error = CapabilityPreparationSnapshotPointError(
        cause=cause,
        lesson_id="lesson-0",
        stage_id="stage-0",
    )
    precedence_calls, _ = _install_derivations(
        monkeypatch, point_error=point_error
    )

    result = _derive(context)

    assert result.snapshot is None
    assert result.precedence_errors == ()
    assert result.resolution_errors[0].entry is entry
    assert result.resolution_errors[0].error is point_error
    assert precedence_calls == []


def test_before_point_preserves_target_entry_and_local_point_identity(monkeypatch):
    entry = _entry("unit", 0)
    local_point = _point()
    _install_derivations(
        monkeypatch,
        target_snapshot=CapabilityPreparationSnapshot(local_point, ()),
    )

    result = _derive(_context(entry))

    assert result.snapshot.before_point.entry is entry
    assert result.snapshot.before_point.local_point is local_point


def test_first_stage_of_first_unit_has_no_invented_preparation(monkeypatch):
    entry = _entry("unit", 0)
    precedence_calls, _ = _install_derivations(monkeypatch)

    result = _derive(_context(entry))

    assert result.snapshot.skills == ()
    assert precedence_calls == [entry.candidate]


def test_prior_units_contribute_all_valid_claims_and_target_uses_snapshot(
    monkeypatch,
):
    earlier = _entry("z-unit", 0)
    target = _entry("a-unit", 1)
    later = _entry("later", 2)
    earlier_claim = _claim("shared", suffix="earlier")
    target_included = _claim("shared", stage_index=0, suffix="target")
    target_not_available = _claim("shared", stage_index=1, suffix="later")
    precedence_by_candidate = {
        id(earlier.candidate): CapabilityClaimPrecedenceDerivation(
            (earlier_claim,), ()
        ),
        id(target.candidate): CapabilityClaimPrecedenceDerivation(
            (target_included, target_not_available), ()
        ),
        id(later.candidate): CapabilityClaimPrecedenceDerivation(
            (_claim("forbidden"),), ()
        ),
    }
    calls, _ = _install_derivations(
        monkeypatch,
        precedence_by_candidate=precedence_by_candidate,
        target_snapshot=CapabilityPreparationSnapshot(
            _point(), (target_included,)
        ),
    )

    result = _derive(_context(earlier, target, later), unit_id="a-unit")

    accumulated = result.snapshot.skills[0].available_claims
    assert [item.claim for item in accumulated] == [earlier_claim, target_included]
    assert accumulated[0].entry is earlier
    assert accumulated[0].claim is earlier_claim
    assert accumulated[1].entry is target
    assert accumulated[1].claim is target_included
    assert target_not_available not in [item.claim for item in accumulated]
    assert calls == [earlier.candidate, target.candidate]
    assert "a-unit" < "z-unit"


def test_same_stage_and_later_claims_are_excluded_by_slice_8_snapshot(monkeypatch):
    entry = _entry("unit", 0)
    earlier = _claim("skill", stage_index=0, suffix="earlier")
    same_stage = _claim("skill", stage_index=1, suffix="same")
    later = _claim("skill", stage_index=2, suffix="later")
    _install_derivations(
        monkeypatch,
        precedence_by_candidate={
            id(entry.candidate): CapabilityClaimPrecedenceDerivation(
                (earlier, same_stage, later), ()
            )
        },
        target_snapshot=CapabilityPreparationSnapshot(_point(), (earlier,)),
    )

    result = _derive(_context(entry))

    assert [
        item.claim for item in result.snapshot.skills[0].available_claims
    ] == [earlier]


def test_precedence_errors_are_preserved_by_entry_without_blocking_valid_claims(
    monkeypatch,
):
    earlier = _entry("earlier", 0)
    target = _entry("target", 1)
    valid = _claim("valid-skill")
    invalid_claim = _claim("invalid-skill", "INSTRUCTION_AVAILABLE")
    earlier_error = CapabilityClaimPrecedenceError(
        invalid_claim, "EXPOSURE_AVAILABLE", "required_state_absent"
    )
    target_error = CapabilityClaimPrecedenceError(
        invalid_claim, "EXPOSURE_AVAILABLE", "required_state_absent"
    )
    _install_derivations(
        monkeypatch,
        precedence_by_candidate={
            id(earlier.candidate): CapabilityClaimPrecedenceDerivation(
                (valid,), (earlier_error,)
            ),
            id(target.candidate): CapabilityClaimPrecedenceDerivation(
                (), (target_error,)
            ),
        },
    )

    result = _derive(_context(earlier, target))

    assert result.snapshot is not None
    assert result.snapshot.skills[0].available_claims[0].claim is valid
    assert [item.entry for item in result.precedence_errors] == [earlier, target]
    assert result.precedence_errors[0].error is earlier_error
    assert result.precedence_errors[1].error is target_error
    assert invalid_claim not in [
        item.claim
        for skill in result.snapshot.skills
        for item in skill.available_claims
    ]


def test_multiple_skills_and_equivalent_claims_are_kept_without_deduplication(
    monkeypatch,
):
    entry = _entry("unit", 0)
    first = _claim("skill-a", suffix="first")
    second = _claim("skill-a", suffix="second")
    other = _claim("skill-b", suffix="other")
    _install_derivations(
        monkeypatch,
        target_snapshot=CapabilityPreparationSnapshot(
            _point(), (first, second, other)
        ),
    )

    result = _derive(_context(entry))

    assert [skill.skill_id for skill in result.snapshot.skills] == [
        "skill-a",
        "skill-b",
    ]
    assert [
        item.claim for item in result.snapshot.skills[0].available_claims
    ] == [first, second]
    assert len(result.snapshot.skills[0].available_claims) == 2


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("EXPOSURE_AVAILABLE", "EXPOSURE_AVAILABLE"),
        ("INSTRUCTION_AVAILABLE", "INSTRUCTION_AVAILABLE"),
        ("PRACTICE_AVAILABLE", "PRACTICE_AVAILABLE"),
        ("EVIDENCE_GATE_AVAILABLE", "EVIDENCE_GATE_AVAILABLE"),
    ],
)
def test_highest_uses_public_state_index_for_all_states(monkeypatch, state, expected):
    entry = _entry("unit", 0)
    claim = _claim("skill", state)
    calls = []

    def state_index(value):
        calls.append(value)
        return {
            "EXPOSURE_AVAILABLE": 0,
            "INSTRUCTION_AVAILABLE": 1,
            "PRACTICE_AVAILABLE": 2,
            "EVIDENCE_GATE_AVAILABLE": 3,
        }[value]

    monkeypatch.setattr(subject, "curriculum_preparation_state_index", state_index)
    _install_derivations(
        monkeypatch,
        target_snapshot=CapabilityPreparationSnapshot(_point(), (claim,)),
    )

    result = _derive(_context(entry))

    skill = result.snapshot.skills[0]
    assert skill.highest_preparation_state == expected
    assert skill.highest_preparation_state in {
        item.claim.preparation_state for item in skill.available_claims
    }
    assert calls == [state]


def test_higher_prior_state_does_not_decrease_after_lower_target_claim(monkeypatch):
    earlier = _entry("earlier", 0)
    target = _entry("target", 1)
    higher = _claim("skill", "EVIDENCE_GATE_AVAILABLE", suffix="higher")
    lower = _claim("skill", "EXPOSURE_AVAILABLE", suffix="lower")
    _install_derivations(
        monkeypatch,
        precedence_by_candidate={
            id(earlier.candidate): CapabilityClaimPrecedenceDerivation((higher,), ()),
        },
        target_snapshot=CapabilityPreparationSnapshot(_point(), (lower,)),
    )

    result = _derive(_context(earlier, target))

    assert result.snapshot.skills[0].highest_preparation_state == (
        "EVIDENCE_GATE_AVAILABLE"
    )
    assert [
        item.claim for item in result.snapshot.skills[0].available_claims
    ] == [higher, lower]


def test_skill_without_accumulated_claims_is_absent(monkeypatch):
    entry = _entry("unit", 0)
    _install_derivations(monkeypatch)

    result = _derive(_context(entry))

    assert result.snapshot.skills == ()


def test_legacy_candidate_without_claims_adds_nothing(monkeypatch):
    entry = _entry("unit", 0)
    assert entry.candidate.lesson_capability_plans == []
    _install_derivations(monkeypatch)

    result = _derive(_context(entry))

    assert result.snapshot.skills == ()
    assert result.precedence_errors == ()


def test_context_beginning_at_b1_is_not_labeled_global(monkeypatch):
    entry = OrderedCurriculumCandidateEntry(
        CurriculumUnitPosition("B1", 2, "b1-unit", 0),
        _candidate("b1-unit"),
    )
    context = _context(entry)
    _install_derivations(monkeypatch)

    result = _derive(context, unit_id="b1-unit")

    assert result.snapshot is not None
    assert result.snapshot.before_point.entry is entry
    assert not hasattr(result.snapshot, "globally_complete")
    assert not hasattr(result.snapshot, "global_history")


def test_context_entries_candidates_and_claims_are_not_modified(monkeypatch):
    entry = _entry("unit", 0)
    context = _context(entry)
    claim = _claim("skill")
    context_before = deepcopy(context)
    candidate_before = deepcopy(entry.candidate.model_dump())
    claim_before = deepcopy(claim)
    _install_derivations(
        monkeypatch,
        target_snapshot=CapabilityPreparationSnapshot(_point(), (claim,)),
    )

    _derive(context)

    assert context == context_before
    assert entry.candidate.model_dump() == candidate_before
    assert claim == claim_before


def test_no_raw_claims_prerequisite_globality_ledger_findings_or_persistence():
    source = inspect.getsource(subject)

    assert "lesson_capability_plans" not in source
    assert "SkillPrerequisite" not in source
    assert "missing_required_skill" not in source
    assert "insufficient_preparation" not in source
    assert "unsatisfied" not in source
    assert "globally_complete" not in source
    assert "Progress" not in source
    assert "attempt" not in source
    assert "Ledger" not in source
    assert "ValidationFinding" not in source
    assert "validation_report" not in source
    assert "persist" not in source.lower()
