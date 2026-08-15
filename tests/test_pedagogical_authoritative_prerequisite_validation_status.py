from dataclasses import FrozenInstanceError
import inspect
from types import SimpleNamespace

import pytest

from app.schemas.pedagogical_unit import ValidationFinding
from app.services.pedagogical_authoritative_prerequisite_validation_status import (
    AuthoritativePrerequisiteValidationStatusDerivation,
    derive_authoritative_prerequisite_validation_status,
)


def _orchestration(
    *,
    context=object(),
    proof=object(),
    include_proof_derivation=True,
    include_conclusion_derivation=True,
    consumption_errors=(),
    preparation_errors=(),
    uncertainties=(),
    findings=(),
    context_errors=(),
):
    context_derivation = SimpleNamespace(
        context=context,
        context_errors=context_errors,
        correspondence_errors=context_errors,
    )
    proof_derivation = (
        SimpleNamespace(result=proof, errors=())
        if include_proof_derivation
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
        if include_conclusion_derivation
        else None
    )
    return SimpleNamespace(
        context_derivation=context_derivation,
        proof_derivation=proof_derivation,
        conclusion_derivation=conclusion_derivation,
        findings=findings,
    )


def _status(orchestration):
    result = derive_authoritative_prerequisite_validation_status(orchestration)
    assert result.orchestration is orchestration
    return result.status


def _finding(severity):
    return ValidationFinding(
        validator_id="source_validator",
        severity=severity,
        message="Source result.",
    )


def test_model_is_frozen_api_accepts_only_orchestration_and_keeps_identity():
    assert AuthoritativePrerequisiteValidationStatusDerivation.__dataclass_params__.frozen
    assert tuple(
        inspect.signature(
            derive_authoritative_prerequisite_validation_status
        ).parameters
    ) == ("orchestration",)
    orchestration = _orchestration()
    result = derive_authoritative_prerequisite_validation_status(orchestration)
    assert result.orchestration is orchestration
    with pytest.raises(FrozenInstanceError):
        result.status = "failed"


def test_fully_resolved_empty_or_satisfied_only_pipeline_passes():
    assert _status(_orchestration()) == "passed"
    satisfied_assessment = object()
    orchestration = _orchestration()
    orchestration.conclusion_derivation.assessment_derivation.assessments = (
        satisfied_assessment,
    )
    assert _status(orchestration) == "passed"


@pytest.mark.parametrize(
    "orchestration",
    [
        _orchestration(context=None),
        _orchestration(include_proof_derivation=False),
        _orchestration(proof=None),
        _orchestration(include_conclusion_derivation=False),
    ],
)
def test_incomplete_pipeline_fails_closed(orchestration):
    assert _status(orchestration) == "failed"


def test_context_errors_external_to_valid_scope_do_not_fail():
    external_error = object()
    orchestration = _orchestration(context_errors=(external_error,))

    assert orchestration.context_derivation.context is not None
    assert _status(orchestration) == "passed"
    assert orchestration.context_derivation.context_errors == (external_error,)


@pytest.mark.parametrize(
    ("consumption_errors", "preparation_errors"),
    [
        ((object(),), ()),
        ((), (object(),)),
        ((object(),), (object(),)),
    ],
)
def test_any_assessment_derivation_error_fails(
    consumption_errors,
    preparation_errors,
):
    orchestration = _orchestration(
        consumption_errors=consumption_errors,
        preparation_errors=preparation_errors,
    )

    assert _status(orchestration) == "failed"
    assert (
        orchestration.conclusion_derivation.assessment_derivation
        .consumption_errors
    ) is consumption_errors
    assert (
        orchestration.conclusion_derivation.assessment_derivation
        .preparation_resolution_errors
    ) is preparation_errors


def test_error_finding_fails_and_preserves_source():
    error = _finding("error")
    orchestration = _orchestration(findings=(error,))

    assert _status(orchestration) == "failed"
    assert orchestration.findings == (error,)


def test_uncertainty_only_is_pending_and_remains_accessible():
    uncertainty = object()
    orchestration = _orchestration(uncertainties=(uncertainty,))

    assert _status(orchestration) == "pending"
    assert orchestration.conclusion_derivation.uncertainties == (uncertainty,)


@pytest.mark.parametrize(
    "failed_source",
    [
        {"findings": (_finding("error"),)},
        {"consumption_errors": (object(),)},
        {"preparation_errors": (object(),)},
    ],
)
def test_failed_has_precedence_over_uncertainty(failed_source):
    uncertainty = object()
    orchestration = _orchestration(
        uncertainties=(uncertainty,),
        **failed_source,
    )

    assert _status(orchestration) == "failed"
    assert orchestration.conclusion_derivation.uncertainties == (uncertainty,)


@pytest.mark.parametrize("severity", ["warning", "information"])
def test_non_error_findings_do_not_apply_generic_report_policy(severity):
    orchestration = _orchestration(findings=(_finding(severity),))

    assert _status(orchestration) == "passed"


def test_classifier_is_pure_and_has_no_recalculation_or_report_dependencies():
    uncertainty = object()
    orchestration = _orchestration(uncertainties=(uncertainty,))
    before_context = orchestration.context_derivation
    before_proof = orchestration.proof_derivation
    before_conclusion = orchestration.conclusion_derivation
    before_findings = orchestration.findings

    first = derive_authoritative_prerequisite_validation_status(orchestration)
    second = derive_authoritative_prerequisite_validation_status(orchestration)

    assert first.status == second.status == "pending"
    assert orchestration.context_derivation is before_context
    assert orchestration.proof_derivation is before_proof
    assert orchestration.conclusion_derivation is before_conclusion
    assert orchestration.findings is before_findings
    forbidden = {
        "ValidationReport",
        "ValidationFinding",
        "derive_authoritative_prerequisite_validation",
        "derive_ordered_curriculum_candidate_context",
        "derive_complete_from_authoritative_origin",
        "derive_authoritative_prerequisite_conclusions",
        "validate_authoritative_prerequisite_conclusions",
        "load_authoritative_curriculum_hierarchy",
        "validate_pedagogical_candidate",
    }
    assert forbidden.isdisjoint(
        derive_authoritative_prerequisite_validation_status.__globals__
    )
