from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import (
    LessonCapabilityPlan,
    PedagogicalUnitCandidate,
)
from app.services import pedagogical_local_capability_preparation_view as subject
from app.services import pedagogical_validation_service
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    CapabilityPreparationSnapshot,
    CapabilityPreparationSnapshotPointError,
    LocalCurriculumPoint,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


POINT = LocalCurriculumPoint(
    lesson_id="lesson-z",
    stage_id="stage-z",
    lesson_index=1,
    stage_index=2,
)


def _candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(build_candidate_payload())


def _claim(
    state: str,
    *,
    skill_id: str = "skill_a",
    marker: str,
    lesson_index: int = 0,
    stage_index: int = 0,
) -> CapabilityClaimAvailability:
    return CapabilityClaimAvailability(
        lesson_id=f"lesson-{lesson_index}",
        lesson_index=lesson_index,
        point=IntraLessonAvailabilityPoint(
            sort_index=stage_index + 1,
            stage_id=f"stage-{lesson_index}-{stage_index}",
            stage_index=stage_index,
        ),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=(marker,),
    )


def _view(monkeypatch, claims, *, candidate=None, point=POINT):
    snapshot = CapabilityPreparationSnapshot(
        before_point=point,
        available_claims=tuple(claims),
    )
    monkeypatch.setattr(
        subject,
        "derive_capability_preparation_snapshot",
        lambda candidate, *, lesson_id, stage_id: snapshot,
    )
    return subject.derive_local_capability_preparation_view(
        candidate or _candidate(),
        lesson_id=point.lesson_id,
        stage_id=point.stage_id,
    )


def test_models_are_typed_and_immutable(monkeypatch):
    result = _view(
        monkeypatch,
        [_claim("EXPOSURE_AVAILABLE", marker="exposure")],
    )

    assert isinstance(result, subject.LocalCapabilityPreparationView)
    assert isinstance(result.skills[0], subject.LocalSkillPreparation)
    assert isinstance(result.skills, tuple)
    assert isinstance(result.skills[0].available_claims, tuple)
    with pytest.raises(FrozenInstanceError):
        result.skills = ()
    with pytest.raises(FrozenInstanceError):
        result.skills[0].highest_preparation_state = "PRACTICE_AVAILABLE"


def test_empty_snapshot_produces_empty_skills(monkeypatch):
    assert _view(monkeypatch, []).skills == ()


@pytest.mark.parametrize(
    "highest_state",
    [
        "EXPOSURE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "PRACTICE_AVAILABLE",
        "EVIDENCE_GATE_AVAILABLE",
    ],
)
def test_highest_state_uses_canonical_order(monkeypatch, highest_state):
    order = [
        "EXPOSURE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
        "PRACTICE_AVAILABLE",
        "EVIDENCE_GATE_AVAILABLE",
    ]
    claims = [
        _claim(state, marker=state)
        for state in order[: order.index(highest_state) + 1]
    ]

    result = _view(monkeypatch, claims)

    assert result.skills[0].highest_preparation_state == highest_state
    assert result.skills[0].available_claims == tuple(claims)


def test_multiple_claims_states_and_positions_are_preserved(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", marker="first", stage_index=0),
        _claim("EXPOSURE_AVAILABLE", marker="second", stage_index=1),
        _claim("INSTRUCTION_AVAILABLE", marker="third", lesson_index=1),
    ]

    skill = _view(monkeypatch, claims).skills[0]

    assert skill.available_claims == tuple(claims)
    assert skill.highest_preparation_state == "INSTRUCTION_AVAILABLE"


def test_skills_are_grouped_independently_and_sorted_by_identity(monkeypatch):
    claims = [
        _claim("INSTRUCTION_AVAILABLE", skill_id="skill_z", marker="z"),
        _claim("PRACTICE_AVAILABLE", skill_id="skill_a", marker="a"),
    ]

    result = _view(monkeypatch, claims)

    assert [skill.skill_id for skill in result.skills] == ["skill_a", "skill_z"]
    assert result.skills[0].available_claims == (claims[1],)
    assert result.skills[1].available_claims == (claims[0],)


def test_skill_without_snapshot_claims_is_absent(monkeypatch):
    candidate = _candidate()
    declared_skill = candidate.specification.skills[0].id

    result = _view(monkeypatch, [], candidate=candidate)

    assert all(skill.skill_id != declared_skill for skill in result.skills)


def test_alternative_claims_are_not_reduced_to_one_chain(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", marker="exposure-a"),
        _claim("EXPOSURE_AVAILABLE", marker="exposure-b"),
        _claim("INSTRUCTION_AVAILABLE", marker="instruction-a"),
        _claim("INSTRUCTION_AVAILABLE", marker="instruction-b"),
    ]

    skill = _view(monkeypatch, claims).skills[0]

    assert skill.available_claims == tuple(claims)


def test_snapshot_claims_are_partitioned_exactly_once(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", skill_id="skill_a", marker="a1"),
        _claim("INSTRUCTION_AVAILABLE", skill_id="skill_a", marker="a2"),
        _claim("EXPOSURE_AVAILABLE", skill_id="skill_b", marker="b1"),
    ]

    result = _view(monkeypatch, claims)
    aggregated = [
        claim
        for skill in result.skills
        for claim in skill.available_claims
    ]

    assert len(aggregated) == len(claims)
    assert {id(claim) for claim in aggregated} == {id(claim) for claim in claims}


def test_original_claim_objects_and_order_are_preserved(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", marker="first"),
        _claim("EXPOSURE_AVAILABLE", marker="second"),
    ]

    result = _view(monkeypatch, claims)

    assert result.skills[0].available_claims[0] is claims[0]
    assert result.skills[0].available_claims[1] is claims[1]


def test_before_point_is_the_snapshot_object(monkeypatch):
    result = _view(monkeypatch, [])
    assert result.before_point is POINT


def test_public_state_index_is_the_only_maximum_source(monkeypatch):
    claims = [
        _claim("EXPOSURE_AVAILABLE", marker="first"),
        _claim("INSTRUCTION_AVAILABLE", marker="second"),
    ]
    calls = []

    def state_index(state):
        calls.append(state)
        return {"EXPOSURE_AVAILABLE": 10, "INSTRUCTION_AVAILABLE": 0}[state]

    monkeypatch.setattr(subject, "curriculum_preparation_state_index", state_index)

    result = _view(monkeypatch, claims)

    assert result.skills[0].highest_preparation_state == "EXPOSURE_AVAILABLE"
    assert calls == ["EXPOSURE_AVAILABLE", "INSTRUCTION_AVAILABLE"]


@pytest.mark.parametrize(
    "cause",
    [
        "unknown_lesson",
        "ambiguous_lesson",
        "lesson_without_experience",
        "unknown_stage_for_lesson",
    ],
)
def test_snapshot_point_errors_propagate(monkeypatch, cause):
    error = CapabilityPreparationSnapshotPointError(
        cause=cause,
        lesson_id="lesson",
        stage_id="stage",
    )

    def fail(candidate, *, lesson_id, stage_id):
        raise error

    monkeypatch.setattr(subject, "derive_capability_preparation_snapshot", fail)

    with pytest.raises(CapabilityPreparationSnapshotPointError) as raised:
        subject.derive_local_capability_preparation_view(
            _candidate(),
            lesson_id="lesson",
            stage_id="stage",
        )

    assert raised.value is error


def test_legacy_candidate_and_empty_plan_produce_empty_view(monkeypatch):
    legacy = _candidate()
    legacy.lesson_capability_plans = []
    assert _view(monkeypatch, [], candidate=legacy).skills == ()

    legacy.lesson_capability_plans = [
        LessonCapabilityPlan(lesson_id="a1-u1-l1")
    ]
    assert _view(monkeypatch, [], candidate=legacy).skills == ()


def test_candidate_is_not_modified(monkeypatch):
    candidate = _candidate()
    before = candidate.model_dump(mode="json")

    _view(monkeypatch, [], candidate=candidate)

    assert candidate.model_dump(mode="json") == before


def test_view_has_no_global_or_supporting_aggregation(monkeypatch):
    result = _view(
        monkeypatch,
        [_claim("EXPOSURE_AVAILABLE", marker="claim")],
    )

    assert not hasattr(result, "highest_preparation_state")
    assert not hasattr(result.skills[0], "supporting_lesson_ids")
    assert not hasattr(result.skills[0], "supporting_artifact_ids")
    assert not hasattr(result.skills[0], "selected_chain")


def test_view_is_not_integrated_as_a_candidate_validator():
    source = inspect.getsource(pedagogical_validation_service)
    assert "derive_local_capability_preparation_view" not in source
    assert "LocalCapabilityPreparationView" not in source
