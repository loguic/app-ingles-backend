from dataclasses import FrozenInstanceError
import inspect
from types import SimpleNamespace

import pytest

from app.schemas.pedagogical_unit import ValidationFinding
from app.services.pedagogical_authoritative_prerequisite_report_findings import (
    AuthoritativePrerequisiteReportFindingDerivation,
    derive_authoritative_prerequisite_report_findings,
)
from app.services.pedagogical_authoritative_prerequisite_validation_status import (
    AuthoritativePrerequisiteValidationStatusDerivation,
)


def _position(level="A1", unit="a1-u1"):
    return SimpleNamespace(level_code=level, unit_id=unit)


def _context():
    return SimpleNamespace(scope=SimpleNamespace(target_position=_position()))


def _assessment(*, skill="skill_one", state="PRACTICE_AVAILABLE"):
    prerequisite = SimpleNamespace(
        required_skill_id=skill,
        required_state=state,
    )
    before_point = SimpleNamespace(lesson_id="lesson-1", stage_id="stage-1")
    consumption = SimpleNamespace(
        prerequisite=prerequisite,
        before_point=before_point,
    )
    return SimpleNamespace(
        entry=SimpleNamespace(position=_position()),
        consumption=consumption,
        related_precedence_errors=(),
    )


def _status_derivation(
    *,
    status="passed",
    context=object(),
    scope_errors=(),
    context_errors=(),
    proof_result=object(),
    proof_errors=(),
    proof_present=True,
    conclusion_present=True,
    consumption_errors=(),
    preparation_errors=(),
    existing_findings=(),
    uncertainties=(),
):
    context_derivation = SimpleNamespace(
        context=context,
        scope_errors=scope_errors,
        context_errors=context_errors,
        scope_position_errors=(object(),),
        correspondence_position_errors=(object(),),
        correspondence_errors=(object(),),
    )
    proof_derivation = (
        SimpleNamespace(result=proof_result, errors=proof_errors)
        if proof_present
        else None
    )
    assessment_derivation = SimpleNamespace(
        consumption_errors=consumption_errors,
        preparation_resolution_errors=preparation_errors,
    )
    conclusion_derivation = (
        SimpleNamespace(
            assessment_derivation=assessment_derivation,
            uncertainties=uncertainties,
        )
        if conclusion_present
        else None
    )
    orchestration = SimpleNamespace(
        context_derivation=context_derivation,
        proof_derivation=proof_derivation,
        conclusion_derivation=conclusion_derivation,
        findings=existing_findings,
    )
    return AuthoritativePrerequisiteValidationStatusDerivation(
        orchestration=orchestration,
        status=status,
    )


def _derive(**kwargs):
    status_derivation = _status_derivation(**kwargs)
    result = derive_authoritative_prerequisite_report_findings(status_derivation)
    assert result.status_derivation is status_derivation
    return status_derivation, result


def test_model_is_frozen_and_api_accepts_only_status_derivation():
    assert AuthoritativePrerequisiteReportFindingDerivation.__dataclass_params__.frozen
    assert tuple(
        inspect.signature(
            derive_authoritative_prerequisite_report_findings
        ).parameters
    ) == ("status_derivation",)
    source, result = _derive(context=_context())
    with pytest.raises(FrozenInstanceError):
        result.status_derivation = source


def test_supported_passed_pipeline_has_no_report_findings():
    _, result = _derive(context=_context())
    assert result.findings == ()


def test_existing_findings_preserve_identity_order_and_multiplicity():
    first = ValidationFinding(
        validator_id="authoritative_prerequisite_preparation",
        severity="error",
        message="First curricular contradiction.",
        reference_ids=["a1-u1"],
    )
    second = ValidationFinding(
        validator_id="authoritative_prerequisite_preparation",
        severity="error",
        message="Second curricular contradiction.",
        reference_ids=["a1-u1"],
    )
    _, result = _derive(
        status="failed",
        context=_context(),
        existing_findings=(first, second, first),
    )
    assert result.findings == (first, second, first)
    assert result.findings[0] is first
    assert result.findings[1] is second
    assert result.findings[2] is first


def test_scope_failure_is_one_context_finding_without_nested_duplicates():
    scope_error = SimpleNamespace(
        cause="hierarchy_position_unresolved",
        target_level_code="B1",
        target_unit_id="b1-u2",
        related_position_errors=(object(), object()),
    )
    context_error = SimpleNamespace(
        cause="correspondence_unresolved",
        position=_position("B1", "b1-u2"),
        related_correspondence_errors=(object(),),
    )
    _, result = _derive(
        status="failed",
        context=None,
        scope_errors=(scope_error,),
        context_errors=(context_error,),
        proof_present=False,
        conclusion_present=False,
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.validator_id == "authoritative_prerequisite_context_integrity"
    assert finding.severity == "error"
    assert finding.reference_ids == ["B1", "b1-u2"]
    assert "hierarchy_position_unresolved" in finding.message


def test_context_failure_without_scope_errors_uses_context_wrappers_only():
    first = SimpleNamespace(
        cause="correspondence_unresolved",
        position=_position("A2", "a2-u1"),
        related_correspondence_errors=(object(), object()),
    )
    second = SimpleNamespace(
        cause="correspondence_derivation_inconsistent",
        position=None,
        related_correspondence_errors=(),
    )
    _, result = _derive(
        status="failed",
        context=None,
        context_errors=(first, second),
        proof_present=False,
        conclusion_present=False,
    )
    assert [finding.reference_ids for finding in result.findings] == [
        ["A2", "a2-u1"],
        [],
    ]
    assert len(result.findings) == 2


def test_valid_context_does_not_translate_external_scope_errors():
    external_scope_error = SimpleNamespace(
        cause="target_missing",
        target_level_code="C2",
        target_unit_id="external",
    )
    _, result = _derive(
        context=_context(),
        scope_errors=(external_scope_error,),
        context_errors=(object(),),
    )
    assert result.findings == ()


@pytest.mark.parametrize(
    "cause",
    [
        "authoritative_hierarchy_position_unresolved",
        "context_origin_mismatch",
        "context_target_outside_authority",
        "authoritative_prefix_mismatch",
    ],
)
def test_each_proof_failure_is_one_origin_integrity_finding(cause):
    error = SimpleNamespace(cause=cause)
    _, result = _derive(
        status="failed",
        context=_context(),
        proof_result=None,
        proof_errors=(error,),
        conclusion_present=False,
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.validator_id == "authoritative_prerequisite_origin_integrity"
    assert finding.severity == "error"
    assert finding.reference_ids == ["A1", "a1-u1"]
    assert cause in finding.message


def test_consumption_error_uses_real_optional_point_references():
    error = SimpleNamespace(
        lesson_id="lesson-1",
        before_stage_id=None,
        required_skill_id="skill_one",
        required_state="PRACTICE_AVAILABLE",
        cause="lesson_without_experience",
    )
    wrapper = SimpleNamespace(
        entry=SimpleNamespace(position=_position()),
        error=error,
    )
    _, result = _derive(
        status="failed",
        context=_context(),
        consumption_errors=(wrapper,),
    )
    finding = result.findings[0]
    assert finding.validator_id == "authoritative_prerequisite_resolution"
    assert finding.severity == "error"
    assert finding.reference_ids == [
        "a1-u1",
        "lesson-1",
        "skill_one",
        "PRACTICE_AVAILABLE",
    ]
    assert "lesson_without_experience" in finding.message


def test_preparation_error_uses_resolved_consumption_references():
    assessment = _assessment()
    wrapper = SimpleNamespace(
        entry=assessment.entry,
        consumption=assessment.consumption,
        error=SimpleNamespace(cause="unknown_stage_for_lesson"),
    )
    _, result = _derive(
        status="failed",
        context=_context(),
        preparation_errors=(wrapper,),
    )
    finding = result.findings[0]
    assert finding.validator_id == "authoritative_prerequisite_resolution"
    assert finding.reference_ids == [
        "a1-u1",
        "lesson-1",
        "stage-1",
        "skill_one",
        "PRACTICE_AVAILABLE",
    ]
    assert "unknown_stage_for_lesson" in finding.message


def test_one_uncertainty_with_multiple_related_errors_is_one_warning():
    assessment = _assessment()
    assessment.related_precedence_errors = (object(), object())
    uncertainty = SimpleNamespace(assessment=assessment)
    source, result = _derive(
        status="pending",
        context=_context(),
        uncertainties=(uncertainty,),
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.validator_id == "authoritative_prerequisite_uncertainty"
    assert finding.severity == "warning"
    assert finding.reference_ids == [
        "a1-u1",
        "lesson-1",
        "stage-1",
        "skill_one",
        "PRACTICE_AVAILABLE",
    ]
    assert source.orchestration.conclusion_derivation.uncertainties == (
        uncertainty,
    )


def test_family_order_and_existing_finding_identity_are_preserved():
    context_error = SimpleNamespace(
        cause="missing_candidate",
        position=_position(),
        related_correspondence_errors=(),
    )
    proof_error = SimpleNamespace(cause="context_origin_mismatch")
    consumption = SimpleNamespace(
        entry=SimpleNamespace(position=_position()),
        error=SimpleNamespace(
            lesson_id="lesson-1",
            before_stage_id="stage-1",
            required_skill_id="skill_one",
            required_state="PRACTICE_AVAILABLE",
            cause="unknown_stage_for_lesson",
        ),
    )
    assessment = _assessment()
    preparation = SimpleNamespace(
        entry=assessment.entry,
        consumption=assessment.consumption,
        error=SimpleNamespace(cause="unknown_stage_for_lesson"),
    )
    existing = ValidationFinding(
        validator_id="authoritative_prerequisite_preparation",
        severity="error",
        message="Existing curricular conclusion.",
    )
    uncertainty = SimpleNamespace(assessment=assessment)
    _, result = _derive(
        status="failed",
        context=None,
        context_errors=(context_error,),
        proof_result=None,
        proof_errors=(proof_error,),
        consumption_errors=(consumption,),
        preparation_errors=(preparation,),
        existing_findings=(existing,),
        uncertainties=(uncertainty,),
    )
    assert [finding.validator_id for finding in result.findings] == [
        "authoritative_prerequisite_context_integrity",
        "authoritative_prerequisite_origin_integrity",
        "authoritative_prerequisite_resolution",
        "authoritative_prerequisite_resolution",
        "authoritative_prerequisite_preparation",
        "authoritative_prerequisite_uncertainty",
    ]
    assert result.findings[4] is existing


def test_messages_and_reference_ids_remain_curricular_and_serializable():
    uncertainty = SimpleNamespace(assessment=_assessment())
    _, result = _derive(
        status="pending",
        context=_context(),
        uncertainties=(uncertainty,),
    )
    message = result.findings[0].message.lower()
    assert all(
        forbidden not in message
        for forbidden in (
            "learner",
            "student",
            "mastery",
            "globally unsatisfied",
        )
    )
    assert all(
        isinstance(reference, str)
        for finding in result.findings
        for reference in finding.reference_ids
    )


def test_manually_incomplete_pipeline_does_not_invent_internal_finding():
    _, missing_proof = _derive(
        status="failed",
        context=_context(),
        proof_present=False,
        conclusion_present=False,
    )
    _, missing_conclusion = _derive(
        status="failed",
        context=_context(),
        conclusion_present=False,
    )
    assert missing_proof.findings == ()
    assert missing_conclusion.findings == ()


def test_derivation_is_pure_and_has_no_recalculation_report_or_integration():
    existing = ValidationFinding(
        validator_id="source_validator",
        severity="information",
        message="Source representation.",
    )
    source = _status_derivation(
        context=_context(),
        existing_findings=(existing,),
    )
    before_orchestration = source.orchestration
    before_findings = source.orchestration.findings
    first = derive_authoritative_prerequisite_report_findings(source)
    second = derive_authoritative_prerequisite_report_findings(source)
    assert first.findings == second.findings == (existing,)
    assert source.orchestration is before_orchestration
    assert source.orchestration.findings is before_findings
    assert first.findings[0] is existing
    forbidden = {
        "ValidationReport",
        "derive_authoritative_prerequisite_validation_status",
        "derive_authoritative_prerequisite_validation",
        "derive_ordered_curriculum_candidate_context",
        "derive_complete_from_authoritative_origin",
        "derive_authoritative_prerequisite_conclusions",
        "validate_authoritative_prerequisite_conclusions",
        "derive_curriculum_skill_prerequisite_assessments",
        "load_authoritative_curriculum_hierarchy",
        "validate_pedagogical_candidate",
    }
    assert forbidden.isdisjoint(
        derive_authoritative_prerequisite_report_findings.__globals__
    )
