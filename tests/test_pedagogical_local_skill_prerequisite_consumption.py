from copy import deepcopy
from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import (
    LessonCapabilityPlan,
    PedagogicalUnitCandidate,
    SkillPrerequisite,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    LocalCurriculumPoint,
)
from app.services.pedagogical_local_skill_prerequisite_consumption import (
    LocalSkillPrerequisiteConsumption,
    LocalSkillPrerequisiteConsumptionDerivation,
    LocalSkillPrerequisiteConsumptionError,
    derive_local_skill_prerequisite_consumptions,
)
from tests.test_lesson_experience_schema import build_experience_payload
from tests.test_pedagogical_validation_service import build_candidate_payload


def _prerequisite(
    *,
    skill_id: str = "a1_introduce_yourself",
    state: str = "EXPOSURE_AVAILABLE",
    before_stage_id: str | None = "a1-u1-l1-s2",
    reason: str = "Preparation is required before consumption.",
) -> SkillPrerequisite:
    return SkillPrerequisite.model_validate(
        {
            "required_skill_id": skill_id,
            "required_state": state,
            "before_stage_id": before_stage_id,
            "reason": reason,
        }
    )


def _candidate(
    prerequisites: list[SkillPrerequisite] | None = None,
) -> PedagogicalUnitCandidate:
    payload = deepcopy(build_candidate_payload())
    payload["candidate_unit"]["lessons"][0]["experience"] = (
        build_experience_payload()
    )
    payload["lesson_capability_plans"] = [
        {
            "lesson_id": "a1-u1-l1",
            "prerequisites": [
                prerequisite.model_dump()
                for prerequisite in (prerequisites or [])
            ],
        }
    ]
    return PedagogicalUnitCandidate.model_validate(payload)


def test_result_structures_are_typed_and_immutable():
    prerequisite = _prerequisite()
    point = LocalCurriculumPoint(
        lesson_id="a1-u1-l1",
        stage_id="a1-u1-l1-s2",
        lesson_index=0,
        stage_index=1,
    )
    consumption = LocalSkillPrerequisiteConsumption(
        lesson_id="a1-u1-l1",
        prerequisite=prerequisite,
        before_point=point,
    )
    error = LocalSkillPrerequisiteConsumptionError(
        lesson_id="a1-u1-l1",
        required_skill_id=prerequisite.required_skill_id,
        required_state=prerequisite.required_state,
        before_stage_id=prerequisite.before_stage_id,
        cause="unknown_stage_for_lesson",
    )
    result = LocalSkillPrerequisiteConsumptionDerivation(
        consumptions=(consumption,),
        resolution_errors=(error,),
    )

    with pytest.raises(FrozenInstanceError):
        result.consumptions = ()
    with pytest.raises(FrozenInstanceError):
        consumption.lesson_id = "changed"
    with pytest.raises(FrozenInstanceError):
        error.cause = "unknown_lesson"


def test_explicit_before_stage_resolves_with_canonical_indices():
    candidate = _candidate([_prerequisite()])

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.resolution_errors == ()
    assert result.consumptions[0].before_point == LocalCurriculumPoint(
        lesson_id="a1-u1-l1",
        stage_id="a1-u1-l1-s2",
        lesson_index=0,
        stage_index=1,
    )


def test_lesson_and_stage_indices_follow_lists_not_ids():
    candidate = _candidate([_prerequisite(before_stage_id="stage-a")])
    lesson = candidate.candidate_unit.lessons.pop(0)
    candidate.candidate_unit.lessons.append(lesson)
    lesson.id = "lesson-z"
    candidate.lesson_capability_plans[0].lesson_id = "lesson-z"
    lesson.experience.stages[0].id = "stage-z"
    lesson.experience.stages[1].id = "stage-a"

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions[0].before_point.lesson_index == 1
    assert result.consumptions[0].before_point.stage_index == 1


def test_missing_before_stage_uses_first_real_stage():
    candidate = _candidate([_prerequisite(before_stage_id=None)])

    point = derive_local_skill_prerequisite_consumptions(
        candidate
    ).consumptions[0].before_point

    assert point.stage_id == candidate.candidate_unit.lessons[0].experience.stages[0].id
    assert point.stage_index == 0
    assert point.stage_id != "lesson_start"
    assert point.stage_index != -1


def test_unknown_lesson_is_a_typed_error():
    candidate = _candidate([_prerequisite()])
    candidate.lesson_capability_plans[0].lesson_id = "unknown-lesson"

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions == ()
    assert result.resolution_errors[0].cause == "unknown_lesson"
    assert result.resolution_errors[0].lesson_id == "unknown-lesson"


def test_ambiguous_lesson_is_a_typed_error():
    candidate = _candidate([_prerequisite()])
    candidate.candidate_unit.lessons[1].id = "a1-u1-l1"

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions == ()
    assert result.resolution_errors[0].cause == "ambiguous_lesson"


@pytest.mark.parametrize("before_stage_id", [None, "some-stage"])
def test_lesson_without_experience_is_a_typed_error(before_stage_id):
    candidate = _candidate([_prerequisite(before_stage_id=before_stage_id)])
    candidate.candidate_unit.lessons[0].experience = None

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions == ()
    assert result.resolution_errors[0].cause == "lesson_without_experience"


def test_unknown_stage_for_consumer_lesson_is_a_typed_error():
    candidate = _candidate([_prerequisite(before_stage_id="missing-stage")])

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions == ()
    assert result.resolution_errors[0].cause == "unknown_stage_for_lesson"


def test_stage_from_another_lesson_is_not_accepted():
    candidate = _candidate([_prerequisite(before_stage_id="other-stage")])
    other_lesson = candidate.candidate_unit.lessons[1]
    other_lesson.experience = deepcopy(
        candidate.candidate_unit.lessons[0].experience
    )
    other_lesson.experience.stages[0].id = "other-stage"

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert result.consumptions == ()
    assert result.resolution_errors[0].cause == "unknown_stage_for_lesson"


def test_multiple_prerequisites_are_resolved_independently_in_order():
    first = _prerequisite(state="EXPOSURE_AVAILABLE", before_stage_id=None)
    second = _prerequisite(
        state="INSTRUCTION_AVAILABLE",
        before_stage_id="a1-u1-l1-s2",
    )
    candidate = _candidate([first, second])

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert [item.prerequisite.required_state for item in result.consumptions] == [
        "EXPOSURE_AVAILABLE",
        "INSTRUCTION_AVAILABLE",
    ]
    assert result.resolution_errors == ()


def test_plan_then_prerequisite_declaration_order_is_preserved():
    candidate = _candidate([_prerequisite(before_stage_id=None)])
    second_lesson = candidate.candidate_unit.lessons[1]
    second_lesson.experience = deepcopy(
        candidate.candidate_unit.lessons[0].experience
    )
    second_lesson.experience.stages[0].id = "second-stage"
    candidate.lesson_capability_plans.append(
        LessonCapabilityPlan(
            lesson_id=second_lesson.id,
            prerequisites=[
                _prerequisite(
                    skill_id="second_skill",
                    before_stage_id="second-stage",
                )
            ],
        )
    )

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert [item.lesson_id for item in result.consumptions] == [
        "a1-u1-l1",
        "a1-u1-l2",
    ]


def test_valid_and_invalid_prerequisites_do_not_fail_fast():
    candidate = _candidate(
        [
            _prerequisite(before_stage_id="missing-stage"),
            _prerequisite(before_stage_id=None),
            _prerequisite(before_stage_id="a1-u1-l1-s2"),
        ]
    )

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert len(result.consumptions) == 2
    assert len(result.resolution_errors) == 1
    assert result.resolution_errors[0].cause == "unknown_stage_for_lesson"


def test_resolution_error_preserves_prerequisite_trace_fields():
    prerequisite = _prerequisite(
        skill_id="required_skill",
        state="PRACTICE_AVAILABLE",
        before_stage_id="missing-stage",
        reason="A traceable reason.",
    )
    candidate = _candidate([prerequisite])

    error = derive_local_skill_prerequisite_consumptions(
        candidate
    ).resolution_errors[0]

    assert error == LocalSkillPrerequisiteConsumptionError(
        lesson_id="a1-u1-l1",
        required_skill_id="required_skill",
        required_state="PRACTICE_AVAILABLE",
        before_stage_id="missing-stage",
        cause="unknown_stage_for_lesson",
    )


def test_every_prerequisite_produces_consumption_xor_error():
    candidate = _candidate(
        [
            _prerequisite(before_stage_id=None),
            _prerequisite(before_stage_id="missing-stage"),
            _prerequisite(before_stage_id="a1-u1-l1-s2"),
        ]
    )

    result = derive_local_skill_prerequisite_consumptions(candidate)

    assert len(result.consumptions) + len(result.resolution_errors) == 3
    assert all(item.before_point is not None for item in result.consumptions)
    assert all(error.cause for error in result.resolution_errors)


def test_reason_does_not_change_resolution_and_original_is_preserved():
    first = _prerequisite(reason="First pedagogical rationale.")
    second = _prerequisite(reason="Different rationale.")
    first_candidate = _candidate([first])
    second_candidate = _candidate([second])

    first_result = derive_local_skill_prerequisite_consumptions(first_candidate)
    second_result = derive_local_skill_prerequisite_consumptions(second_candidate)

    assert first_result.consumptions[0].before_point == second_result.consumptions[0].before_point
    assert first_result.consumptions[0].prerequisite is first_candidate.lesson_capability_plans[0].prerequisites[0]


def test_empty_plan_and_legacy_candidate_produce_empty_derivations():
    empty_plan_candidate = _candidate([])
    legacy_candidate = PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )

    for candidate in (empty_plan_candidate, legacy_candidate):
        result = derive_local_skill_prerequisite_consumptions(candidate)
        assert result.consumptions == ()
        assert result.resolution_errors == ()


def test_candidate_is_not_modified():
    candidate = _candidate([_prerequisite(before_stage_id=None)])
    before = candidate.model_dump()

    derive_local_skill_prerequisite_consumptions(candidate)

    assert candidate.model_dump() == before


def test_module_contains_no_satisfaction_ledger_finding_or_persistence_api():
    import app.services.pedagogical_local_skill_prerequisite_consumption as module

    source = inspect.getsource(module)
    prohibited_public_names = {
        "satisfied",
        "unsatisfied",
        "actual_state",
        "highest_preparation_state",
        "ledger",
        "ValidationFinding",
        "validator_id",
    }

    assert prohibited_public_names.isdisjoint(vars(module))
    assert "pedagogical_validation_service" not in source
    assert "curriculum_preparation_state_index" not in source
