import inspect

import pytest

import app.services.pedagogical_authoritative_prerequisite_validation_flow as flow_module
from app.services.pedagogical_authoritative_prerequisite_validation_flow import (
    derive_authoritative_prerequisite_validation_flow,
)
from app.services.pedagogical_authoritative_prerequisite_validation_report import (
    AuthoritativePrerequisiteValidationReport,
)


def _install_flow_doubles(monkeypatch, *, failure_at=None):
    calls = []
    orchestration = object()
    status_derivation = object()
    finding_derivation = object()
    report = object.__new__(AuthoritativePrerequisiteValidationReport)

    def derive_orchestration(
        authority,
        candidates,
        *,
        target_level_code,
        target_unit_id,
    ):
        calls.append(
            (
                "25",
                authority,
                candidates,
                target_level_code,
                target_unit_id,
            )
        )
        if failure_at == "25":
            raise RuntimeError("slice 25 failure")
        return orchestration

    def derive_status(received_orchestration):
        calls.append(("26", received_orchestration))
        if failure_at == "26":
            raise RuntimeError("slice 26 failure")
        return status_derivation

    def derive_findings(received_status):
        calls.append(("27", received_status))
        if failure_at == "27":
            raise RuntimeError("slice 27 failure")
        return finding_derivation

    def derive_report(received_findings):
        calls.append(("28", received_findings))
        if failure_at == "28":
            raise RuntimeError("slice 28 failure")
        return report

    monkeypatch.setattr(
        flow_module,
        "derive_authoritative_prerequisite_validation",
        derive_orchestration,
    )
    monkeypatch.setattr(
        flow_module,
        "derive_authoritative_prerequisite_validation_status",
        derive_status,
    )
    monkeypatch.setattr(
        flow_module,
        "derive_authoritative_prerequisite_report_findings",
        derive_findings,
    )
    monkeypatch.setattr(
        flow_module,
        "derive_authoritative_prerequisite_validation_report",
        derive_report,
    )
    return {
        "calls": calls,
        "orchestration": orchestration,
        "status_derivation": status_derivation,
        "finding_derivation": finding_derivation,
        "report": report,
    }


def test_public_signature_and_return_annotation_are_exact():
    signature = inspect.signature(
        derive_authoritative_prerequisite_validation_flow
    )
    assert tuple(signature.parameters) == (
        "authority",
        "candidates",
        "target_level_code",
        "target_unit_id",
    )
    assert signature.parameters["target_level_code"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["target_unit_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.return_annotation is AuthoritativePrerequisiteValidationReport


def test_flow_calls_25_through_28_once_in_order_and_preserves_identity(
    monkeypatch,
):
    doubles = _install_flow_doubles(monkeypatch)
    authority = object()
    candidates = [object(), object(), object()]
    before_candidates = tuple(candidates)

    result = derive_authoritative_prerequisite_validation_flow(
        authority,
        candidates,
        target_level_code="a1-Unchanged",
        target_unit_id="unit-Unchanged",
    )

    assert result is doubles["report"]
    assert [call[0] for call in doubles["calls"]] == ["25", "26", "27", "28"]
    assert len(doubles["calls"]) == 4
    first_call = doubles["calls"][0]
    assert first_call[1] is authority
    assert first_call[2] is candidates
    assert first_call[3:] == ("a1-Unchanged", "unit-Unchanged")
    assert doubles["calls"][1][1] is doubles["orchestration"]
    assert doubles["calls"][2][1] is doubles["status_derivation"]
    assert doubles["calls"][3][1] is doubles["finding_derivation"]
    assert tuple(candidates) == before_candidates


def test_candidates_are_not_sorted_deduplicated_or_prevalidated(monkeypatch):
    doubles = _install_flow_doubles(monkeypatch)
    duplicate = object()
    candidates = [object(), duplicate, duplicate]

    derive_authoritative_prerequisite_validation_flow(
        object(),
        candidates,
        target_level_code="B2",
        target_unit_id="missing-target",
    )

    received_candidates = doubles["calls"][0][2]
    assert received_candidates is candidates
    assert received_candidates == candidates
    assert received_candidates[1] is received_candidates[2]


@pytest.mark.parametrize(
    ("failure_at", "expected_stages"),
    [
        ("25", ["25"]),
        ("26", ["25", "26"]),
        ("27", ["25", "26", "27"]),
        ("28", ["25", "26", "27", "28"]),
    ],
)
def test_lower_layer_exceptions_propagate_without_wrapping(
    monkeypatch,
    failure_at,
    expected_stages,
):
    doubles = _install_flow_doubles(monkeypatch, failure_at=failure_at)

    with pytest.raises(RuntimeError, match=f"slice {failure_at} failure"):
        derive_authoritative_prerequisite_validation_flow(
            object(),
            [],
            target_level_code="A1",
            target_unit_id="a1-u1",
        )

    assert [call[0] for call in doubles["calls"]] == expected_stages


def test_flow_has_no_provider_io_reconstruction_or_local_validation():
    forbidden = {
        "ValidationFinding",
        "ValidationReport",
        "load_authoritative_curriculum_hierarchy",
        "build_content_tree",
        "validate_pedagogical_candidate",
        "derive_ordered_curriculum_candidate_context",
        "derive_curriculum_skill_prerequisite_assessments",
        "derive_complete_from_authoritative_origin",
        "derive_authoritative_prerequisite_conclusions",
        "validate_authoritative_prerequisite_conclusions",
    }
    assert forbidden.isdisjoint(
        derive_authoritative_prerequisite_validation_flow.__globals__
    )
