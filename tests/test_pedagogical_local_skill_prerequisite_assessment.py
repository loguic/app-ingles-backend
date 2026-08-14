from dataclasses import FrozenInstanceError
import inspect

import pytest

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    SkillPrerequisite,
)
from app.services import pedagogical_local_skill_prerequisite_assessment as subject
from app.services.pedagogical_capability_claim_availability import (
    CapabilityClaimAvailability,
    IntraLessonAvailabilityPoint,
)
from app.services.pedagogical_capability_preparation_snapshot import (
    LocalCurriculumPoint,
)
from app.services.pedagogical_local_capability_preparation_view import (
    LocalCapabilityPreparationView,
    LocalSkillPreparation,
)
from app.services.pedagogical_local_skill_prerequisite_consumption import (
    LocalSkillPrerequisiteConsumption,
    LocalSkillPrerequisiteConsumptionDerivation,
    LocalSkillPrerequisiteConsumptionError,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


POINT = LocalCurriculumPoint(
    lesson_id="lesson-1",
    stage_id="stage-2",
    lesson_index=0,
    stage_index=1,
)


def _candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(build_candidate_payload())


def _prerequisite(
    required_state: str = "EXPOSURE_AVAILABLE",
    *,
    skill_id: str = "skill_a",
) -> SkillPrerequisite:
    return SkillPrerequisite.model_validate(
        {
            "required_skill_id": skill_id,
            "required_state": required_state,
            "before_stage_id": POINT.stage_id,
            "reason": "Local structural preparation is required.",
        }
    )


def _consumption(
    required_state: str = "EXPOSURE_AVAILABLE",
    *,
    skill_id: str = "skill_a",
    point: LocalCurriculumPoint = POINT,
) -> LocalSkillPrerequisiteConsumption:
    return LocalSkillPrerequisiteConsumption(
        lesson_id=point.lesson_id,
        prerequisite=_prerequisite(required_state, skill_id=skill_id),
        before_point=point,
    )


def _claim(
    state: str,
    *,
    marker: str,
    skill_id: str = "skill_a",
) -> CapabilityClaimAvailability:
    return CapabilityClaimAvailability(
        lesson_id="producer-lesson",
        lesson_index=0,
        point=IntraLessonAvailabilityPoint(
            sort_index=1,
            stage_id="producer-stage",
            stage_index=0,
        ),
        skill_id=skill_id,
        preparation_state=state,
        artifact_ids=(marker,),
    )


def _preparation(
    state: str,
    *,
    skill_id: str = "skill_a",
    claims: tuple[CapabilityClaimAvailability, ...] | None = None,
) -> LocalSkillPreparation:
    return LocalSkillPreparation(
        skill_id=skill_id,
        highest_preparation_state=state,
        available_claims=claims or (_claim(state, marker=state, skill_id=skill_id),),
    )


def _derive(
    monkeypatch,
    *,
    consumptions=(),
    errors=(),
    views=None,
    candidate=None,
):
    consumption_result = LocalSkillPrerequisiteConsumptionDerivation(
        consumptions=tuple(consumptions),
        resolution_errors=tuple(errors),
    )
    monkeypatch.setattr(
        subject,
        "derive_local_skill_prerequisite_consumptions",
        lambda candidate: consumption_result,
    )
    view_by_point = views or {}

    def derive_view(candidate, *, lesson_id, stage_id):
        return view_by_point.get(
            (lesson_id, stage_id),
            LocalCapabilityPreparationView(before_point=POINT, skills=()),
        )

    monkeypatch.setattr(
        subject,
        "derive_local_capability_preparation_view",
        derive_view,
    )
    result = subject.derive_local_skill_prerequisite_assessments(
        candidate or _candidate()
    )
    return result, consumption_result


def test_models_are_typed_and_immutable(monkeypatch):
    consumption = _consumption()
    preparation = _preparation("EXPOSURE_AVAILABLE")
    result, _ = _derive(
        monkeypatch,
        consumptions=(consumption,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assert isinstance(result, subject.LocalSkillPrerequisiteAssessmentDerivation)
    assert isinstance(result.assessments[0], subject.LocalSkillPrerequisiteAssessment)
    assert isinstance(result.assessments, tuple)
    assert isinstance(result.resolution_errors, tuple)
    with pytest.raises(FrozenInstanceError):
        result.assessments = ()
    with pytest.raises(FrozenInstanceError):
        result.assessments[0].outcome = "unresolved_in_local_context"


@pytest.mark.parametrize(
    ("actual", "required"),
    [
        ("EXPOSURE_AVAILABLE", "EXPOSURE_AVAILABLE"),
        ("INSTRUCTION_AVAILABLE", "INSTRUCTION_AVAILABLE"),
        ("PRACTICE_AVAILABLE", "PRACTICE_AVAILABLE"),
        ("EVIDENCE_GATE_AVAILABLE", "EVIDENCE_GATE_AVAILABLE"),
        ("EVIDENCE_GATE_AVAILABLE", "EXPOSURE_AVAILABLE"),
    ],
)
def test_equal_or_superior_local_preparation_is_satisfied(
    monkeypatch, actual, required
):
    consumption = _consumption(required)
    preparation = _preparation(actual)

    result, _ = _derive(
        monkeypatch,
        consumptions=(consumption,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assert result.assessments[0].outcome == "satisfied_in_local_context"


@pytest.mark.parametrize(
    ("actual", "required"),
    [
        ("EXPOSURE_AVAILABLE", "INSTRUCTION_AVAILABLE"),
        ("INSTRUCTION_AVAILABLE", "PRACTICE_AVAILABLE"),
        ("PRACTICE_AVAILABLE", "EVIDENCE_GATE_AVAILABLE"),
    ],
)
def test_inferior_local_preparation_is_unresolved(monkeypatch, actual, required):
    consumption = _consumption(required)
    preparation = _preparation(actual)

    result, _ = _derive(
        monkeypatch,
        consumptions=(consumption,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assessment = result.assessments[0]
    assert assessment.outcome == "unresolved_in_local_context"
    assert assessment.locally_available_preparation is preparation


def test_absent_skill_and_empty_view_are_unresolved_without_preparation(monkeypatch):
    consumption = _consumption(skill_id="missing_skill")

    result, _ = _derive(monkeypatch, consumptions=(consumption,))

    assessment = result.assessments[0]
    assert assessment.outcome == "unresolved_in_local_context"
    assert assessment.locally_available_preparation is None


def test_public_state_index_is_the_only_comparison_source(monkeypatch):
    consumption = _consumption("EVIDENCE_GATE_AVAILABLE")
    preparation = _preparation("EXPOSURE_AVAILABLE")
    calls = []

    def state_index(state):
        calls.append(state)
        return {"EXPOSURE_AVAILABLE": 10, "EVIDENCE_GATE_AVAILABLE": 0}[state]

    monkeypatch.setattr(subject, "curriculum_preparation_state_index", state_index)
    result, _ = _derive(
        monkeypatch,
        consumptions=(consumption,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assert result.assessments[0].outcome == "satisfied_in_local_context"
    assert calls == ["EXPOSURE_AVAILABLE", "EVIDENCE_GATE_AVAILABLE"]


def test_original_consumption_prerequisite_point_and_preparation_are_preserved(
    monkeypatch,
):
    consumption = _consumption()
    claims = (
        _claim("EXPOSURE_AVAILABLE", marker="alternative-a"),
        _claim("EXPOSURE_AVAILABLE", marker="alternative-b"),
    )
    preparation = _preparation("EXPOSURE_AVAILABLE", claims=claims)

    result, _ = _derive(
        monkeypatch,
        consumptions=(consumption,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assessment = result.assessments[0]
    assert assessment.consumption is consumption
    assert assessment.consumption.prerequisite is consumption.prerequisite
    assert assessment.consumption.before_point is POINT
    assert assessment.locally_available_preparation is preparation
    assert assessment.locally_available_preparation.available_claims is claims


def test_multiple_prerequisites_are_independent_and_keep_consumption_order(monkeypatch):
    exposure = _consumption("EXPOSURE_AVAILABLE")
    practice = _consumption("PRACTICE_AVAILABLE")
    preparation = _preparation("INSTRUCTION_AVAILABLE")
    view = LocalCapabilityPreparationView(before_point=POINT, skills=(preparation,))

    result, _ = _derive(
        monkeypatch,
        consumptions=(exposure, practice),
        views={(POINT.lesson_id, POINT.stage_id): view},
    )

    assert [item.consumption for item in result.assessments] == [exposure, practice]
    assert [item.outcome for item in result.assessments] == [
        "satisfied_in_local_context",
        "unresolved_in_local_context",
    ]


def test_valid_consumptions_continue_when_resolution_errors_exist(monkeypatch):
    consumption = _consumption()
    error = LocalSkillPrerequisiteConsumptionError(
        lesson_id="missing-lesson",
        required_skill_id="skill_b",
        required_state="PRACTICE_AVAILABLE",
        before_stage_id=None,
        cause="unknown_lesson",
    )
    preparation = _preparation("EXPOSURE_AVAILABLE")

    result, consumption_result = _derive(
        monkeypatch,
        consumptions=(consumption,),
        errors=(error,),
        views={
            (POINT.lesson_id, POINT.stage_id): LocalCapabilityPreparationView(
                before_point=POINT,
                skills=(preparation,),
            )
        },
    )

    assert len(result.assessments) == 1
    assert result.resolution_errors is consumption_result.resolution_errors
    assert result.resolution_errors == (error,)


@pytest.mark.parametrize(
    "cause",
    [
        "unknown_lesson",
        "ambiguous_lesson",
        "lesson_without_experience",
        "unknown_stage_for_lesson",
    ],
)
def test_resolution_error_causes_propagate_without_assessment(monkeypatch, cause):
    error = LocalSkillPrerequisiteConsumptionError(
        lesson_id="lesson",
        required_skill_id="skill",
        required_state="EXPOSURE_AVAILABLE",
        before_stage_id="stage",
        cause=cause,
    )

    result, consumption_result = _derive(monkeypatch, errors=(error,))

    assert result.assessments == ()
    assert result.resolution_errors is consumption_result.resolution_errors
    assert result.resolution_errors[0] is error


def test_each_valid_consumption_produces_exactly_one_assessment(monkeypatch):
    consumptions = (
        _consumption(skill_id="skill_a"),
        _consumption(skill_id="skill_b"),
        _consumption(skill_id="skill_c"),
    )

    result, _ = _derive(monkeypatch, consumptions=consumptions)

    assert len(result.assessments) == len(consumptions)
    assert [item.consumption for item in result.assessments] == list(consumptions)


def test_legacy_candidate_and_empty_prerequisites_produce_empty_derivation(
    monkeypatch,
):
    result, consumption_result = _derive(monkeypatch)

    assert result.assessments == ()
    assert result.resolution_errors == ()
    assert consumption_result.consumptions == ()


def test_candidate_is_not_modified(monkeypatch):
    candidate = _candidate()
    before = candidate.model_dump()

    _derive(monkeypatch, candidate=candidate)

    assert candidate.model_dump() == before


def test_module_has_no_global_conclusion_validator_ledger_or_persistence_api():
    source = inspect.getsource(subject)
    prohibited_public_names = {
        "unsatisfied",
        "unavailable",
        "globally_satisfied",
        "globally_unsatisfied",
        "invalid",
        "mastery",
        "learner_state",
        "validator_id",
        "ledger",
    }

    assert prohibited_public_names.isdisjoint(vars(subject))
    assert "pedagogical_validation_service" not in source
    assert "validation_report" not in source
    assert "CURRICULUM_PREPARATION_STATE_ORDER" not in source
