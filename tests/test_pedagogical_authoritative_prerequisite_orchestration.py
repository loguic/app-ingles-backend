from dataclasses import FrozenInstanceError
import inspect
from types import SimpleNamespace

import pytest

from app.services import (
    pedagogical_authoritative_prerequisite_orchestration as orchestration,
)
from app.services.pedagogical_authoritative_prerequisite_orchestration import (
    AuthoritativePrerequisiteValidationDerivation,
    derive_authoritative_prerequisite_validation,
)


def _authority():
    return SimpleNamespace(hierarchy=object())


def _run_pipeline(
    monkeypatch,
    *,
    context=object(),
    proof=object(),
    conclusions=(),
    uncertainties=(),
    assessment_errors=(),
    findings=(),
    candidates=None,
):
    authority = _authority()
    candidates = candidates if candidates is not None else [object(), object()]
    context_derivation = SimpleNamespace(
        context=context,
        context_errors=(),
    )
    proof_derivation = SimpleNamespace(result=proof, errors=())
    assessment_derivation = SimpleNamespace(
        consumption_errors=assessment_errors,
        preparation_resolution_errors=(),
    )
    conclusion_derivation = SimpleNamespace(
        conclusions=conclusions,
        uncertainties=uncertainties,
        assessment_derivation=assessment_derivation,
    )
    calls = []

    def derive_context(hierarchy, received_candidates, **target):
        calls.append(("context", hierarchy, received_candidates, target))
        return context_derivation

    def derive_proof(received_authority, received_context):
        calls.append(("proof", received_authority, received_context))
        return proof_derivation

    def derive_conclusions(received_proof):
        calls.append(("conclusions", received_proof))
        return conclusion_derivation

    def validate(received_derivation):
        calls.append(("findings", received_derivation))
        return list(findings)

    monkeypatch.setattr(
        orchestration,
        "derive_ordered_curriculum_candidate_context",
        derive_context,
    )
    monkeypatch.setattr(
        orchestration,
        "derive_complete_from_authoritative_origin",
        derive_proof,
    )
    monkeypatch.setattr(
        orchestration,
        "derive_authoritative_prerequisite_conclusions",
        derive_conclusions,
    )
    monkeypatch.setattr(
        orchestration,
        "validate_authoritative_prerequisite_conclusions",
        validate,
    )

    result = derive_authoritative_prerequisite_validation(
        authority,
        candidates,
        target_level_code="B1",
        target_unit_id="target-unit",
    )
    return SimpleNamespace(
        result=result,
        authority=authority,
        candidates=candidates,
        context=context,
        context_derivation=context_derivation,
        proof=proof,
        proof_derivation=proof_derivation,
        conclusion_derivation=conclusion_derivation,
        calls=calls,
    )


def test_model_is_frozen_and_api_has_only_required_inputs():
    assert AuthoritativePrerequisiteValidationDerivation.__dataclass_params__.frozen
    assert tuple(
        inspect.signature(
            derive_authoritative_prerequisite_validation
        ).parameters
    ) == (
        "authority",
        "candidates",
        "target_level_code",
        "target_unit_id",
    )
    model = AuthoritativePrerequisiteValidationDerivation(
        authority=object(),  # type: ignore[arg-type]
        context_derivation=object(),  # type: ignore[arg-type]
        proof_derivation=None,
        conclusion_derivation=None,
        findings=(),
    )
    with pytest.raises(FrozenInstanceError):
        model.findings = ()


def test_valid_pipeline_calls_slices_once_in_order_and_preserves_identity(
    monkeypatch,
):
    finding = object()
    run = _run_pipeline(monkeypatch, findings=(finding,))

    assert [call[0] for call in run.calls] == [
        "context",
        "proof",
        "conclusions",
        "findings",
    ]
    context_call = run.calls[0]
    assert context_call[1] is run.authority.hierarchy
    assert context_call[2] is run.candidates
    assert context_call[3] == {
        "target_level_code": "B1",
        "target_unit_id": "target-unit",
    }
    assert run.calls[1][1:] == (run.authority, run.context)
    assert run.calls[2][1] is run.proof
    assert run.calls[3][1] is run.conclusion_derivation
    assert run.result.authority is run.authority
    assert run.result.context_derivation is run.context_derivation
    assert run.result.proof_derivation is run.proof_derivation
    assert run.result.conclusion_derivation is run.conclusion_derivation
    assert run.result.findings == (finding,)


def test_context_failure_is_fail_closed_and_preserves_derivation(monkeypatch):
    run = _run_pipeline(monkeypatch, context=None)

    assert [call[0] for call in run.calls] == ["context"]
    assert run.result.context_derivation is run.context_derivation
    assert run.result.proof_derivation is None
    assert run.result.conclusion_derivation is None
    assert run.result.findings == ()


def test_proof_failure_is_fail_closed_and_preserves_last_stage(monkeypatch):
    run = _run_pipeline(monkeypatch, proof=None)

    assert [call[0] for call in run.calls] == ["context", "proof"]
    assert run.result.context_derivation is run.context_derivation
    assert run.result.proof_derivation is run.proof_derivation
    assert run.result.conclusion_derivation is None
    assert run.result.findings == ()


def test_valid_pipeline_without_conclusions_keeps_empty_findings(monkeypatch):
    run = _run_pipeline(monkeypatch)

    assert run.result.conclusion_derivation is run.conclusion_derivation
    assert run.result.conclusion_derivation.conclusions == ()
    assert run.result.findings == ()


def test_uncertainties_and_assessment_errors_remain_source_only(monkeypatch):
    uncertainty = object()
    assessment_error = object()
    run = _run_pipeline(
        monkeypatch,
        uncertainties=(uncertainty,),
        assessment_errors=(assessment_error,),
    )

    assert run.result.findings == ()
    assert run.result.conclusion_derivation.uncertainties == (uncertainty,)
    assert (
        run.result.conclusion_derivation.assessment_derivation
        .consumption_errors
    ) == (assessment_error,)


def test_multiple_findings_keep_slice_24_order_and_multiplicity(monkeypatch):
    first = object()
    second = object()
    run = _run_pipeline(
        monkeypatch,
        conclusions=(object(), object()),
        findings=(first, second),
    )

    assert run.result.findings == (first, second)
    assert run.result.findings[0] is first
    assert run.result.findings[1] is second


def test_candidates_are_forwarded_in_arbitrary_order_without_mutation(
    monkeypatch,
):
    candidates = [SimpleNamespace(id="z"), SimpleNamespace(id="a")]
    before = tuple(candidates)

    run = _run_pipeline(monkeypatch, candidates=candidates)

    assert run.calls[0][2] is candidates
    assert tuple(candidates) == before


def test_orchestrator_has_no_provider_report_or_integration_dependencies():
    module_globals = derive_authoritative_prerequisite_validation.__globals__
    forbidden = {
        "load_authoritative_curriculum_hierarchy",
        "build_content_tree",
        "ValidationReport",
        "validate_pedagogical_candidate",
        "derive_curriculum_context_scope",
        "derive_curriculum_candidate_correspondences",
    }
    assert forbidden.isdisjoint(module_globals)
