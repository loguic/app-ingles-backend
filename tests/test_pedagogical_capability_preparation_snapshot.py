from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import LessonCapabilityPlan, PedagogicalUnitCandidate
from app.services import pedagogical_capability_preparation_snapshot as subject
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_capability_claim_precedence_validation import (
    CapabilityClaimPrecedenceDerivation,
    CapabilityClaimPrecedenceError,
)
from app.services import pedagogical_validation_service
from tests.test_lesson_experience_schema import build_experience_payload
from tests.test_pedagogical_validation_service import build_candidate_payload


def _candidate(*, two_lessons: bool = False) -> PedagogicalUnitCandidate:
    payload = build_candidate_payload()
    first = payload["candidate_unit"]["lessons"][0]
    first["id"] = "lesson-z"
    first["experience"] = build_experience_payload()
    if two_lessons:
        second = deepcopy(first)
        second["id"] = "lesson-a"
        payload["candidate_unit"]["lessons"] = [first, second]
    else:
        payload["candidate_unit"]["lessons"] = [first]
    return PedagogicalUnitCandidate.model_validate(payload)


def _claim(
    lesson_index: int,
    stage_index: int,
    *,
    marker: str,
    skill_id: str = "skill_a",
    state: str = "EXPOSURE_AVAILABLE",
) -> CapabilityClaimAvailability:
    return CapabilityClaimAvailability(
        lesson_id=f"claim-lesson-{lesson_index}",
        lesson_index=lesson_index,
        point=IntraLessonAvailabilityPoint(
            sort_index=stage_index + 1,
            stage_id=f"claim-stage-{lesson_index}-{stage_index}",
            stage_index=stage_index,
        ),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=(marker,),
    )


def _snapshot(monkeypatch, claims, *, lesson_id="lesson-z", stage_id="a1-u1-l1-s2", candidate=None, errors=()):
    candidate = candidate or _candidate()
    derivation = CapabilityClaimPrecedenceDerivation(
        valid_claims=tuple(claims),
        precedence_errors=tuple(errors),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_claim_state_precedence",
        lambda value: derivation,
    )
    return subject.derive_capability_preparation_snapshot(
        candidate,
        lesson_id=lesson_id,
        stage_id=stage_id,
    )


def test_point_and_snapshot_are_typed_and_immutable(monkeypatch):
    result = _snapshot(monkeypatch, [])

    assert isinstance(result.before_point, subject.LocalCurriculumPoint)
    assert isinstance(result, subject.CapabilityPreparationSnapshot)
    assert isinstance(result.available_claims, tuple)
    with pytest.raises(FrozenInstanceError):
        result.before_point.stage_index = 4
    with pytest.raises(FrozenInstanceError):
        result.available_claims = ()


def test_resolves_lesson_and_stage_indexes_from_canonical_lists(monkeypatch):
    candidate = _candidate(two_lessons=True)

    result = _snapshot(
        monkeypatch,
        [],
        candidate=candidate,
        lesson_id="lesson-a",
        stage_id="a1-u1-l1-s2",
    )

    assert result.before_point == subject.LocalCurriculumPoint(
        lesson_id="lesson-a",
        stage_id="a1-u1-l1-s2",
        lesson_index=1,
        stage_index=1,
    )


def test_reverse_ids_do_not_change_list_order(monkeypatch):
    candidate = _candidate(two_lessons=True)

    first = _snapshot(monkeypatch, [], candidate=candidate, lesson_id="lesson-z", stage_id="a1-u1-l1-s1")
    second = _snapshot(monkeypatch, [], candidate=candidate, lesson_id="lesson-a", stage_id="a1-u1-l1-s1")

    assert first.before_point.lesson_index == 0
    assert second.before_point.lesson_index == 1


@pytest.mark.parametrize(
    ("lesson_id", "stage_id", "cause"),
    [
        ("missing", "stage", "unknown_lesson"),
        ("a1-u1-l2", "stage", "lesson_without_experience"),
        ("lesson-z", "missing", "unknown_stage_for_lesson"),
    ],
)
def test_invalid_point_has_typed_cause(lesson_id, stage_id, cause):
    candidate = _candidate() if lesson_id != "a1-u1-l2" else PedagogicalUnitCandidate.model_validate(build_candidate_payload())

    with pytest.raises(subject.CapabilityPreparationSnapshotPointError) as raised:
        subject.derive_capability_preparation_snapshot(
            candidate,
            lesson_id=lesson_id,
            stage_id=stage_id,
        )

    assert raised.value.cause == cause
    assert raised.value.lesson_id == lesson_id
    assert raised.value.stage_id == stage_id


def test_duplicate_lesson_identity_is_rejected_independently_of_order():
    candidate = _candidate(two_lessons=True)
    candidate.candidate_unit.lessons[1].id = "lesson-z"

    for lessons in (
        list(candidate.candidate_unit.lessons),
        list(reversed(candidate.candidate_unit.lessons)),
    ):
        candidate.candidate_unit.lessons = lessons
        with pytest.raises(
            subject.CapabilityPreparationSnapshotPointError
        ) as raised:
            subject.derive_capability_preparation_snapshot(
                candidate,
                lesson_id="lesson-z",
                stage_id="a1-u1-l1-s1",
            )

        assert raised.value.cause == "ambiguous_lesson"
        assert raised.value.lesson_id == "lesson-z"


def test_before_first_stage_of_first_lesson_is_empty(monkeypatch):
    result = _snapshot(monkeypatch, [_claim(0, 0, marker="same")], stage_id="a1-u1-l1-s1")
    assert result.available_claims == ()


def test_strictly_earlier_claim_is_included(monkeypatch):
    claim = _claim(0, 0, marker="earlier")
    assert _snapshot(monkeypatch, [claim]).available_claims == (claim,)


def test_same_and_later_positions_are_excluded(monkeypatch):
    claims = [
        _claim(0, 1, marker="same"),
        _claim(1, 0, marker="later"),
    ]
    assert _snapshot(monkeypatch, claims).available_claims == ()


def test_claims_from_previous_lesson_are_included(monkeypatch):
    candidate = _candidate(two_lessons=True)
    claim = _claim(0, 1, marker="previous-lesson")

    result = _snapshot(
        monkeypatch,
        [claim],
        candidate=candidate,
        lesson_id="lesson-a",
        stage_id="a1-u1-l1-s1",
    )

    assert result.available_claims == (claim,)


def test_multiple_claims_states_positions_and_skills_are_preserved(monkeypatch):
    claims = [
        _claim(0, 0, marker="a", skill_id="skill_a"),
        _claim(0, 0, marker="b", skill_id="skill_b"),
        _claim(0, 0, marker="c", state="INSTRUCTION_AVAILABLE"),
    ]

    result = _snapshot(monkeypatch, list(reversed(claims)))

    assert len(result.available_claims) == 3
    assert {id(claim) for claim in result.available_claims} == {
        id(claim) for claim in claims
    }


def test_precedence_errors_are_never_available(monkeypatch):
    invalid = _claim(0, 0, marker="invalid", state="PRACTICE_AVAILABLE")
    error = CapabilityClaimPrecedenceError(
        claim=invalid,
        required_preparation_state="INSTRUCTION_AVAILABLE",
        cause="required_state_absent",
    )

    result = _snapshot(monkeypatch, [], errors=[error])

    assert result.available_claims == ()


def test_slice_5_exclusions_cannot_reappear(monkeypatch):
    result = _snapshot(monkeypatch, [])
    assert result.available_claims == ()


def test_declaration_order_produces_identical_snapshot(monkeypatch):
    claims = [
        _claim(0, 0, marker="z"),
        _claim(0, 0, marker="a"),
    ]

    first = _snapshot(monkeypatch, claims)
    second = _snapshot(monkeypatch, list(reversed(claims)))

    assert first == second


def test_legacy_candidate_and_empty_plan_return_empty_snapshot(monkeypatch):
    legacy = _candidate()
    legacy.lesson_capability_plans = []

    assert _snapshot(monkeypatch, [], candidate=legacy).available_claims == ()


def test_plan_without_claims_returns_empty_snapshot(monkeypatch):
    candidate = _candidate()
    candidate.lesson_capability_plans = [
        LessonCapabilityPlan(lesson_id="lesson-z")
    ]

    assert _snapshot(monkeypatch, [], candidate=candidate).available_claims == ()


def test_derivation_does_not_modify_candidate(monkeypatch):
    candidate = _candidate()
    before = candidate.model_dump(mode="json")

    _snapshot(monkeypatch, [], candidate=candidate)

    assert candidate.model_dump(mode="json") == before


def test_snapshot_preserves_original_availability_objects(monkeypatch):
    claim = _claim(0, 0, marker="original")
    result = _snapshot(monkeypatch, [claim])
    assert result.available_claims[0] is claim


def test_snapshot_has_no_ledger_aggregation(monkeypatch):
    result = _snapshot(monkeypatch, [_claim(0, 0, marker="claim")])
    assert not hasattr(result, "highest_preparation_state")
    assert not hasattr(result, "supporting_lesson_ids")
    assert not hasattr(result, "supporting_artifact_ids")


def test_snapshot_is_not_integrated_as_a_candidate_validator():
    source = inspect.getsource(pedagogical_validation_service)
    assert "derive_capability_preparation_snapshot" not in source
    assert "CapabilityPreparationSnapshot" not in source
