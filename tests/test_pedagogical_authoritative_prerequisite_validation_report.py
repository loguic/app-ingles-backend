from dataclasses import FrozenInstanceError
import inspect
from types import SimpleNamespace

import pytest

from app.schemas.pedagogical_unit import ValidationFinding
from app.services.pedagogical_authoritative_prerequisite_report_findings import (
    AuthoritativePrerequisiteReportFindingDerivation,
)
from app.services.pedagogical_authoritative_prerequisite_validation_report import (
    AuthoritativePrerequisiteValidationReport,
    derive_authoritative_prerequisite_validation_report,
)
from app.services.pedagogical_authoritative_prerequisite_validation_status import (
    AuthoritativePrerequisiteValidationStatusDerivation,
)


def _finding(
    severity,
    *,
    validator_id="source_validator",
    message="Source representation.",
    reference_ids=None,
):
    return ValidationFinding(
        validator_id=validator_id,
        severity=severity,
        message=message,
        reference_ids=[] if reference_ids is None else reference_ids,
    )


def _finding_derivation(status, findings=()):
    status_derivation = AuthoritativePrerequisiteValidationStatusDerivation(
        orchestration=SimpleNamespace(source="orchestration"),
        status=status,
    )
    return AuthoritativePrerequisiteReportFindingDerivation(
        status_derivation=status_derivation,
        findings=findings,
    )


def test_model_is_frozen_and_api_accepts_only_finding_derivation():
    assert AuthoritativePrerequisiteValidationReport.__dataclass_params__.frozen
    assert tuple(
        inspect.signature(
            derive_authoritative_prerequisite_validation_report
        ).parameters
    ) == ("finding_derivation",)

    source = _finding_derivation("passed")
    result = derive_authoritative_prerequisite_validation_report(source)

    assert result.finding_derivation is source
    with pytest.raises(FrozenInstanceError):
        result.finding_derivation = source


def test_status_is_copied_exactly_from_slice_26_source():
    warning = _finding("warning")
    source = _finding_derivation("pending", (warning,))

    result = derive_authoritative_prerequisite_validation_report(source)

    assert result.report.status == source.status_derivation.status == "pending"


def test_findings_preserve_structure_order_and_multiplicity():
    first = _finding(
        "error",
        validator_id="first_validator",
        message="First structural failure.",
        reference_ids=["a1-u1", "lesson-1"],
    )
    second = _finding(
        "warning",
        validator_id="second_validator",
        message="Second structural uncertainty.",
        reference_ids=["skill_one"],
    )
    source_findings = (first, second, first)
    source = _finding_derivation("failed", source_findings)

    result = derive_authoritative_prerequisite_validation_report(source)

    assert result.report.findings == [first, second, first]
    assert [finding.model_dump() for finding in result.report.findings] == [
        finding.model_dump() for finding in source_findings
    ]
    assert source.findings is source_findings


def test_failed_with_error_is_valid():
    error = _finding("error")
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("failed", (error,))
    )
    assert result.report.status == "failed"
    assert result.report.findings == [error]


def test_failed_with_error_and_warning_preserves_both():
    error = _finding("error", message="Demonstrated structural failure.")
    warning = _finding("warning", message="Related structural uncertainty.")
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("failed", (warning, error))
    )
    assert result.report.status == "failed"
    assert result.report.findings == [warning, error]


def test_pending_with_warning_is_valid():
    warning = _finding("warning")
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("pending", (warning,))
    )
    assert result.report.status == "pending"
    assert result.report.findings == [warning]


def test_passed_with_empty_findings_is_valid():
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("passed")
    )
    assert result.report.status == "passed"
    assert result.report.findings == []


def test_passed_with_information_is_valid_and_not_reclassified():
    information = _finding("information")
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("passed", (information,))
    )
    assert result.report.status == "passed"
    assert result.report.findings == [information]


@pytest.mark.parametrize(
    ("status", "findings", "message"),
    [
        (
            "failed",
            (),
            "failed status requires at least one error finding",
        ),
        (
            "pending",
            (),
            "pending status requires at least one warning and no error findings",
        ),
        (
            "pending",
            (_finding("error"),),
            "pending status requires at least one warning and no error findings",
        ),
        (
            "passed",
            (_finding("warning"),),
            "passed status cannot contain error or warning findings",
        ),
        (
            "passed",
            (_finding("error"),),
            "passed status cannot contain error or warning findings",
        ),
    ],
)
def test_manually_inconsistent_derivations_raise_value_error(
    status,
    findings,
    message,
):
    source = _finding_derivation(status, findings)
    before_status = source.status_derivation.status
    before_findings = source.findings

    with pytest.raises(ValueError, match=message):
        derive_authoritative_prerequisite_validation_report(source)

    assert source.status_derivation.status == before_status
    assert source.findings is before_findings


def test_validation_report_is_serializable_without_an_extra_dto():
    error = _finding(
        "error",
        reference_ids=["a1-u1", "lesson-1", "skill_one"],
    )
    result = derive_authoritative_prerequisite_validation_report(
        _finding_derivation("failed", (error,))
    )

    dumped = result.report.model_dump()
    dumped_json = result.report.model_dump_json()
    assert dumped == {
        "status": "failed",
        "findings": [error.model_dump()],
    }
    assert '"status":"failed"' in dumped_json
    assert '"validator_id":"source_validator"' in dumped_json


def test_derivation_is_pure_and_has_no_recalculation_or_integration():
    information = _finding("information")
    source = _finding_derivation("passed", (information,))
    before_status_derivation = source.status_derivation
    before_findings = source.findings

    first = derive_authoritative_prerequisite_validation_report(source)
    second = derive_authoritative_prerequisite_validation_report(source)

    assert first.report == second.report
    assert source.status_derivation is before_status_derivation
    assert source.findings is before_findings
    forbidden = {
        "ValidationFinding",
        "derive_authoritative_prerequisite_report_findings",
        "derive_authoritative_prerequisite_validation_status",
        "derive_authoritative_prerequisite_validation",
        "derive_ordered_curriculum_candidate_context",
        "derive_complete_from_authoritative_origin",
        "derive_authoritative_prerequisite_conclusions",
        "validate_authoritative_prerequisite_conclusions",
        "load_authoritative_curriculum_hierarchy",
        "validate_pedagogical_candidate",
    }
    assert forbidden.isdisjoint(
        derive_authoritative_prerequisite_validation_report.__globals__
    )
