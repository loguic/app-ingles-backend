from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate, SkillPrerequisite
from app.services import pedagogical_curriculum_skill_prerequisite_assessment as subject
from app.services.pedagogical_accumulated_curriculum_preparation import (
    AccumulatedCapabilityPrecedenceError,
    AccumulatedCurriculumPreparationDerivation,
    AccumulatedCurriculumPreparationSnapshot,
    AccumulatedCurriculumUnitResolutionError,
    AccumulatedSkillPreparation,
    CurriculumPreparationPoint,
)
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    CapabilityClaimPrecedenceError,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    LocalCurriculumPoint,
)
from app.services.pedagogical_curriculum_candidate_correspondence import (
    OrderedCurriculumCandidateEntry,
)
from app.services.pedagogical_curriculum_context_scope import CurriculumContextScope
from app.services.pedagogical_curriculum_unit_position import CurriculumUnitPosition
from app.services.pedagogical_local_skill_prerequisite_consumption import (
    LocalSkillPrerequisiteConsumption,
    LocalSkillPrerequisiteConsumptionDerivation,
    LocalSkillPrerequisiteConsumptionError,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


def _candidate(unit_id: str) -> PedagogicalUnitCandidate:
    candidate = PedagogicalUnitCandidate.model_validate(build_candidate_payload())
    candidate.specification.unit_id = unit_id
    candidate.candidate_unit.id = unit_id
    return candidate


def _entry(unit_id: str, unit_index: int, *, level="A1"):
    return OrderedCurriculumCandidateEntry(
        position=CurriculumUnitPosition(level, 0 if level == "A1" else 2, unit_id, unit_index),
        candidate=_candidate(unit_id),
    )


def _context(*entries):
    positions = tuple(entry.position for entry in entries)
    return OrderedCurriculumCandidateContext(
        scope=CurriculumContextScope(positions[0], positions[-1], positions),
        entries=tuple(entries),
    )


def _consumption(
    skill_id="required_skill",
    state="EXPOSURE_AVAILABLE",
    *,
    lesson_id="lesson-real",
    stage_id="stage-real",
    before_stage_id="stage-real",
):
    prerequisite = SkillPrerequisite(
        required_skill_id=skill_id,
        required_state=state,
        before_stage_id=before_stage_id,
        reason="Structural preparation is required.",
    )
    return LocalSkillPrerequisiteConsumption(
        lesson_id=lesson_id,
        prerequisite=prerequisite,
        before_point=LocalCurriculumPoint(lesson_id, stage_id, 4, 7),
    )


def _claim(skill_id="required_skill", state="EXPOSURE_AVAILABLE"):
    return CapabilityClaimAvailability(
        lesson_id="supporting-lesson",
        lesson_index=0,
        point=IntraLessonAvailabilityPoint(1, "supporting-stage", 0),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=("artifact",),
    )


def _skill(skill_id="required_skill", state="EXPOSURE_AVAILABLE"):
    return AccumulatedSkillPreparation(
        skill_id=skill_id,
        highest_preparation_state=state,
        available_claims=(),
    )


def _precedence_error(entry, skill_id="required_skill"):
    claim = _claim(skill_id, "INSTRUCTION_AVAILABLE")
    return AccumulatedCapabilityPrecedenceError(
        entry=entry,
        error=CapabilityClaimPrecedenceError(
            claim=claim,
            required_preparation_state="EXPOSURE_AVAILABLE",
            cause="required_state_absent",
        ),
    )


def _preparation(entry, *, skills=(), errors=(), resolution_errors=()):
    snapshot = None
    if not resolution_errors:
        snapshot = AccumulatedCurriculumPreparationSnapshot(
            before_point=CurriculumPreparationPoint(
                entry=entry,
                local_point=LocalCurriculumPoint(
                    "lesson-real", "stage-real", 4, 7
                ),
            ),
            skills=tuple(skills),
        )
    return AccumulatedCurriculumPreparationDerivation(
        snapshot=snapshot,
        precedence_errors=tuple(errors),
        resolution_errors=tuple(resolution_errors),
    )


def _install(monkeypatch, consumptions_by_candidate, preparation_by_point):
    consumption_calls = []
    preparation_calls = []

    def derive_consumptions(candidate):
        consumption_calls.append(candidate)
        return consumptions_by_candidate.get(
            id(candidate), LocalSkillPrerequisiteConsumptionDerivation((), ())
        )

    def derive_preparation(context, *, unit_id, lesson_id, stage_id):
        preparation_calls.append((context, unit_id, lesson_id, stage_id))
        return preparation_by_point[(unit_id, lesson_id, stage_id)]

    monkeypatch.setattr(
        subject, "derive_local_skill_prerequisite_consumptions", derive_consumptions
    )
    monkeypatch.setattr(
        subject, "derive_accumulated_curriculum_preparation", derive_preparation
    )
    return consumption_calls, preparation_calls


def test_models_are_typed_and_immutable():
    entry = _entry("unit", 0)
    consumption = _consumption()
    assessment = subject.CurriculumSkillPrerequisiteAssessment(
        entry, consumption, None, (), "unresolved_in_context"
    )
    error = LocalSkillPrerequisiteConsumptionError(
        "lesson", "skill", "EXPOSURE_AVAILABLE", None, "unknown_lesson"
    )
    wrapped = subject.CurriculumSkillPrerequisiteConsumptionResolutionError(
        entry, error
    )
    derivation = subject.CurriculumSkillPrerequisiteAssessmentDerivation(
        (assessment,), (wrapped,), (), ()
    )

    with pytest.raises(FrozenInstanceError):
        assessment.outcome = "satisfied_in_context"
    with pytest.raises(FrozenInstanceError):
        wrapped.entry = entry
    with pytest.raises(FrozenInstanceError):
        derivation.assessments = ()


def test_context_without_prerequisites_is_empty_and_uses_only_entries(monkeypatch):
    first = _entry("z-unit", 0)
    second = _entry("a-unit", 1)
    calls, preparation_calls = _install(monkeypatch, {}, {})

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(first, second)
    )

    assert result.assessments == ()
    assert result.consumption_errors == ()
    assert result.preparation_resolution_errors == ()
    assert result.precedence_observations == ()
    assert calls == [first.candidate, second.candidate]
    assert preparation_calls == []


def test_legacy_candidate_without_prerequisites_produces_no_output(monkeypatch):
    entry = _entry("unit", 0)
    assert entry.candidate.lesson_capability_plans == []
    _install(monkeypatch, {}, {})

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(entry)
    )

    assert result.assessments == ()


def test_consumption_point_is_forwarded_to_slice_18_without_reinterpretation(
    monkeypatch,
):
    entry = _entry("unit", 0)
    consumption = _consumption(before_stage_id=None)
    preparation = _preparation(entry)
    _, calls = _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): preparation},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(entry)
    )

    assert result.assessments[0].consumption is consumption
    assert consumption.prerequisite.before_stage_id is None
    assert calls[0][1:] == ("unit", "lesson-real", "stage-real")


@pytest.mark.parametrize(
    ("actual", "required", "expected"),
    [
        ("PRACTICE_AVAILABLE", "PRACTICE_AVAILABLE", "satisfied_in_context"),
        ("EVIDENCE_GATE_AVAILABLE", "PRACTICE_AVAILABLE", "satisfied_in_context"),
        ("EXPOSURE_AVAILABLE", "INSTRUCTION_AVAILABLE", "unresolved_in_context"),
    ],
)
def test_state_comparison_produces_only_contextual_outcomes(
    monkeypatch, actual, required, expected
):
    entry = _entry("unit", 0)
    consumption = _consumption(state=required)
    skill = _skill(state=actual)
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): _preparation(entry, skills=(skill,))},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(entry)
    )

    assessment = result.assessments[0]
    assert assessment.outcome == expected
    assert assessment.accumulated_skill_preparation is skill


def test_state_comparison_uses_only_public_slice_9_function(monkeypatch):
    entry = _entry("unit", 0)
    consumption = _consumption(state="EVIDENCE_GATE_AVAILABLE")
    skill = _skill(state="EXPOSURE_AVAILABLE")
    calls = []

    def state_index(state):
        calls.append(state)
        return {"EXPOSURE_AVAILABLE": 9, "EVIDENCE_GATE_AVAILABLE": 1}[state]

    monkeypatch.setattr(subject, "curriculum_preparation_state_index", state_index)
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): _preparation(entry, skills=(skill,))},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert result.assessments[0].outcome == "satisfied_in_context"
    assert calls == ["EXPOSURE_AVAILABLE", "EVIDENCE_GATE_AVAILABLE"]


def test_absent_skill_is_unresolved_with_none_preparation(monkeypatch):
    entry = _entry("unit", 0)
    consumption = _consumption()
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): _preparation(entry)},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assessment = result.assessments[0]
    assert assessment.outcome == "unresolved_in_context"
    assert assessment.accumulated_skill_preparation is None


def test_assessment_order_is_context_then_consumption_order(monkeypatch):
    first = _entry("z-unit", 0)
    second = _entry("a-unit", 1)
    first_consumptions = (_consumption("skill_z"), _consumption("skill_a"))
    second_consumption = _consumption("skill_m")
    preparation_by_point = {
        ("z-unit", "lesson-real", "stage-real"): _preparation(first),
        ("a-unit", "lesson-real", "stage-real"): _preparation(second),
    }
    _install(
        monkeypatch,
        {
            id(first.candidate): LocalSkillPrerequisiteConsumptionDerivation(first_consumptions, ()),
            id(second.candidate): LocalSkillPrerequisiteConsumptionDerivation((second_consumption,), ()),
        },
        preparation_by_point,
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(first, second)
    )

    assert "a-unit" < "z-unit"
    assert [assessment.entry for assessment in result.assessments] == [first, first, second]
    assert [assessment.consumption for assessment in result.assessments] == [
        *first_consumptions,
        second_consumption,
    ]


def test_local_cache_reuses_same_point_without_deduplicating_assessments(monkeypatch):
    entry = _entry("unit", 0)
    first = _consumption("skill_a")
    second = _consumption("skill_b")
    _, preparation_calls = _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((first, second), ())},
        {("unit", "lesson-real", "stage-real"): _preparation(entry)},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert len(result.assessments) == 2
    assert len(preparation_calls) == 1


def test_consumption_error_is_preserved_without_preparation_call(monkeypatch):
    entry = _entry("unit", 0)
    error = LocalSkillPrerequisiteConsumptionError(
        "lesson", "required_skill", "EXPOSURE_AVAILABLE", None, "unknown_lesson"
    )
    _, preparation_calls = _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((), (error,))},
        {},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert result.assessments == ()
    assert result.consumption_errors[0].entry is entry
    assert result.consumption_errors[0].error is error
    assert preparation_calls == []


def test_valid_consumption_and_consumption_error_do_not_fail_fast(monkeypatch):
    entry = _entry("unit", 0)
    consumption = _consumption()
    error = LocalSkillPrerequisiteConsumptionError(
        "other", "other_skill", "EXPOSURE_AVAILABLE", None, "unknown_lesson"
    )
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), (error,))},
        {("unit", "lesson-real", "stage-real"): _preparation(entry)},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert len(result.assessments) == 1
    assert result.consumption_errors[0].error is error


def test_all_preparation_resolution_errors_are_preserved_without_assessment(monkeypatch):
    entry = _entry("unit", 0)
    consumption = _consumption()
    first_error = AccumulatedCurriculumUnitResolutionError(
        "unit", "unknown_unit_in_context"
    )
    second_error = AccumulatedCurriculumUnitResolutionError(
        "unit", "ambiguous_unit_in_context"
    )
    preparation = _preparation(
        entry, resolution_errors=(first_error, second_error)
    )
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): preparation},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert result.assessments == ()
    assert [item.error for item in result.preparation_resolution_errors] == [
        first_error,
        second_error,
    ]
    assert all(item.entry is entry for item in result.preparation_resolution_errors)
    assert all(item.consumption is consumption for item in result.preparation_resolution_errors)


def test_precedence_errors_are_observed_and_only_required_skill_is_related(monkeypatch):
    entry = _entry("unit", 0)
    consumption = _consumption("required_skill", "PRACTICE_AVAILABLE")
    sufficient = _skill("required_skill", "PRACTICE_AVAILABLE")
    related = _precedence_error(entry, "required_skill")
    unrelated = _precedence_error(entry, "other_skill")
    preparation = _preparation(
        entry, skills=(sufficient,), errors=(related, unrelated)
    )
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): preparation},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assessment = result.assessments[0]
    assert assessment.outcome == "satisfied_in_context"
    assert assessment.related_precedence_errors == (related,)
    assert assessment.related_precedence_errors[0] is related
    assert result.precedence_observations[0].consumption is consumption
    assert result.precedence_observations[0].errors is preparation.precedence_errors


def test_related_error_with_absent_or_lower_skill_stays_unresolved(monkeypatch):
    entry = _entry("unit", 0)
    absent_consumption = _consumption("absent", "INSTRUCTION_AVAILABLE")
    lower_consumption = _consumption("lower", "PRACTICE_AVAILABLE")
    absent_error = _precedence_error(entry, "absent")
    lower_error = _precedence_error(entry, "lower")
    preparation = _preparation(
        entry,
        skills=(_skill("lower", "EXPOSURE_AVAILABLE"),),
        errors=(absent_error, lower_error),
    )
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((absent_consumption, lower_consumption), ())},
        {("unit", "lesson-real", "stage-real"): preparation},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert [item.outcome for item in result.assessments] == [
        "unresolved_in_context",
        "unresolved_in_context",
    ]
    assert result.assessments[0].related_precedence_errors == (absent_error,)
    assert result.assessments[1].related_precedence_errors == (lower_error,)


def test_early_unresolved_and_later_satisfied_are_independent(monkeypatch):
    early_entry = _entry("early", 0)
    later_entry = _entry("later", 1)
    early = _consumption()
    later = _consumption()
    _install(
        monkeypatch,
        {
            id(early_entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((early,), ()),
            id(later_entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((later,), ()),
        },
        {
            ("early", "lesson-real", "stage-real"): _preparation(early_entry),
            ("later", "lesson-real", "stage-real"): _preparation(
                later_entry, skills=(_skill(),)
            ),
        },
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(
        _context(early_entry, later_entry)
    )

    assert [item.outcome for item in result.assessments] == [
        "unresolved_in_context",
        "satisfied_in_context",
    ]


def test_context_beginning_at_b1_keeps_only_contextual_outcome(monkeypatch):
    entry = _entry("b1-unit", 0, level="B1")
    consumption = _consumption()
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("b1-unit", "lesson-real", "stage-real"): _preparation(entry)},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(_context(entry))

    assert result.assessments[0].outcome == "unresolved_in_context"
    assert not hasattr(result.assessments[0], "globally_complete")


def test_inputs_and_source_objects_are_not_modified(monkeypatch):
    entry = _entry("unit", 0)
    context = _context(entry)
    consumption = _consumption()
    skill = _skill()
    context_before = deepcopy(context)
    candidate_before = deepcopy(entry.candidate.model_dump())
    consumption_before = deepcopy(consumption)
    preparation = _preparation(entry, skills=(skill,))
    _install(
        monkeypatch,
        {id(entry.candidate): LocalSkillPrerequisiteConsumptionDerivation((consumption,), ())},
        {("unit", "lesson-real", "stage-real"): preparation},
    )

    result = subject.derive_curriculum_skill_prerequisite_assessments(context)

    assert context == context_before
    assert entry.candidate.model_dump() == candidate_before
    assert consumption == consumption_before
    assert result.assessments[0].entry is entry
    assert result.assessments[0].consumption is consumption
    assert result.assessments[0].consumption.prerequisite is consumption.prerequisite
    assert result.assessments[0].accumulated_skill_preparation is skill


def test_no_raw_prerequisites_global_outcomes_repair_ledger_or_findings():
    source = inspect.getsource(subject)

    assert "lesson_capability_plans" not in source
    assert "before_stage_id" not in source
    assert "stage_index" not in source
    assert "globally_satisfied" not in source
    assert "globally_unsatisfied" not in source
    assert "missing_required_skill" not in source
    assert "insufficient_preparation" not in source
    assert "Ledger" not in source
    assert "ValidationFinding" not in source
    assert "validate_pedagogical_candidate" not in source
    assert "Progress" not in source
    assert "attempt" not in source
    assert "persist" not in source.lower()
    assert set(subject.CurriculumSkillPrerequisiteAssessmentOutcome.__args__) == {
        "satisfied_in_context",
        "unresolved_in_context",
    }
