from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
    ValidationReport,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_verification import (
    AdmissionGateVerification,
)
import app.services.pedagogical_candidate_admission_verification as verification
from app.services.pedagogical_candidate_payload_identity import (
    PAYLOAD_SCHEMA_VERSION,
    CandidatePayloadIdentity,
)


def candidate_payload() -> dict:
    return {
        "specification": {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Introductions",
            "learner_outcome": "Introduce yourself.",
            "skills": [{
                "id": "a1_introduce_yourself",
                "description": "Introduce yourself.",
                "required_stages": ["introduce"],
            }],
            "required_evidence": ["One introduction."],
            "lesson_scope": ["Introductions."],
            "language_scope": ["My name is..."],
            "pronunciation_scope": ["Sentence stress."],
            "content_constraints": ["Use A1 language."],
            "technical_constraints": ["Use existing contracts."],
            "acceptance_criteria": ["Produce one introduction."],
        },
        "candidate_unit": {
            "id": "a1-u1",
            "title": "Introductions",
            "lessons": [{"id": "a1-u1-l1", "title": "Names"}],
        },
        "evaluation_plans": [{
            "lesson_id": "a1-u1-l1",
            "criteria": [{
                "id": "a1-u1-l1-semantic",
                "evidence_definition_id": "a1-u1-l1-ev1",
                "conversation_id": "a1-u1-l1-c1",
                "prompt_id": "a1-u1-l1-p1",
                "dimension": "semantic",
                "description": "States a name.",
                "measurement_mode": "score",
                "success_threshold": 0.0,
                "applicable_modalities": ["text"],
            }],
        }],
        "feedback_plans": [{
            "lesson_id": "a1-u1-l1",
            "rules": [{
                "id": "a1-u1-l1-semantic-feedback",
                "criterion_id": "a1-u1-l1-semantic",
                "passed_message": "Clear introduction.",
                "passed_guidance": "Continue.",
                "failed_message": "Introduction incomplete.",
                "failed_guidance": "State your name.",
            }],
        }],
        "lesson_capability_plans": [{
            "lesson_id": "a1-u1-l1", "claims": [], "prerequisites": []
        }],
        "skill_coverage": [{
            "skill_id": "a1_introduce_yourself",
            "introduced_in_lesson_id": "a1-u1-l1",
            "modalities": ["speaking"],
            "status": "complete",
        }],
        "required_resource_ids": [],
        "validation_report": {"status": "passed", "findings": []},
        "pending_human_decisions": [],
        "proposed_change_summary": ["Candidate ready for review."],
    }


def candidate(**updates: object) -> PedagogicalUnitCandidate:
    payload = candidate_payload()
    payload.update(updates)
    return PedagogicalUnitCandidate.model_validate(payload)


def report(status: str) -> ValidationReport:
    if status == "passed":
        return ValidationReport(status="passed", findings=[])
    severity = "error" if status == "failed" else "warning"
    return ValidationReport(
        status=status,  # type: ignore[arg-type]
        findings=[
            ValidationFinding(
                validator_id="review_status",
                severity=severity,
                message="Controlled validation result.",
            )
        ],
    )


def identity(
    *,
    unit_id: str = "a1-u1",
    revision: str = "revision-01",
    schema_version: str = PAYLOAD_SCHEMA_VERSION,
    digest: str = "sha256:" + "a" * 64,
) -> CandidatePayloadIdentity:
    return CandidatePayloadIdentity(
        unit_id=unit_id,
        candidate_revision=revision,
        payload_schema_version=schema_version,
        content_digest=digest,
    )


def admission(
    value: CandidatePayloadIdentity,
    *,
    decision: str = "admitted",
) -> AdmissionRecord:
    return AdmissionRecord(
        admission_id="admission-01",
        identity=value,
        decision=decision,  # type: ignore[arg-type]
        reviewer_id="reviewer-01",
        decided_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )


def patch_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    *,
    derived: CandidatePayloadIdentity,
    local_report: ValidationReport,
) -> tuple[list[str], list[PedagogicalUnitCandidate]]:
    revisions: list[str] = []
    candidates: list[PedagogicalUnitCandidate] = []

    def derive(
        value: PedagogicalUnitCandidate, *, candidate_revision: str
    ) -> CandidatePayloadIdentity:
        candidates.append(value)
        revisions.append(candidate_revision)
        return derived

    def validate(value: PedagogicalUnitCandidate) -> ValidationReport:
        candidates.append(value)
        return local_report

    monkeypatch.setattr(verification, "derive_candidate_payload_identity", derive)
    monkeypatch.setattr(verification, "validate_pedagogical_candidate", validate)
    return revisions, candidates


def test_result_shape_is_frozen_and_verified_is_derived() -> None:
    value = identity()
    result = AdmissionGateVerification(
        derived_identity=value,
        admission_record=admission(value),
        local_validation_report=report("passed"),
        identity_matches=True,
        local_validation_passed=True,
        pending_human_decisions_clear=True,
        human_decision_admitted=True,
    )

    assert [field.name for field in fields(result)] == [
        "derived_identity", "admission_record", "local_validation_report",
        "identity_matches", "local_validation_passed",
        "pending_human_decisions_clear", "human_decision_admitted",
    ]
    assert result.verified is True
    with pytest.raises(FrozenInstanceError):
        result.identity_matches = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "gate",
    [
        "identity_matches",
        "local_validation_passed",
        "pending_human_decisions_clear",
        "human_decision_admitted",
    ],
)
def test_verified_is_exact_and_of_all_gates(gate: str) -> None:
    values = {
        "identity_matches": True,
        "local_validation_passed": True,
        "pending_human_decisions_clear": True,
        "human_decision_admitted": True,
    }
    values[gate] = False
    value = identity()

    result = AdmissionGateVerification(
        derived_identity=value,
        admission_record=admission(value),
        local_validation_report=report("passed"),
        **values,
    )

    assert result.verified is False


def test_verifies_all_true_and_preserves_exact_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = candidate()
    expected_identity = identity()
    expected_report = report("passed")
    record = admission(expected_identity)
    revisions, calls = patch_dependencies(
        monkeypatch, derived=expected_identity, local_report=expected_report
    )

    result = verification.verify_candidate_admission(value, record)

    assert result.verified is True
    assert result.identity_matches is True
    assert result.local_validation_passed is True
    assert result.pending_human_decisions_clear is True
    assert result.human_decision_admitted is True
    assert result.derived_identity is expected_identity
    assert result.admission_record is record
    assert result.local_validation_report is expected_report
    assert revisions == ["revision-01"]
    assert calls == [value, value]


@pytest.mark.parametrize(
    "changed_field, changed_value",
    [
        ("unit_id", "a1-u2"),
        ("candidate_revision", "revision-02"),
        ("payload_schema_version", "2.0"),
        ("content_digest", "sha256:" + "b" * 64),
    ],
)
def test_identity_mismatches_use_full_structural_equality(
    monkeypatch: pytest.MonkeyPatch,
    changed_field: str,
    changed_value: str,
) -> None:
    record_identity = identity()
    derived_values = {
        "unit_id": record_identity.unit_id,
        "revision": record_identity.candidate_revision,
        "schema_version": record_identity.payload_schema_version,
        "digest": record_identity.content_digest,
    }
    target = {
        "candidate_revision": "revision",
        "payload_schema_version": "schema_version",
        "content_digest": "digest",
    }.get(changed_field, changed_field)
    derived_values[target] = changed_value
    derived = identity(**derived_values)
    patch_dependencies(monkeypatch, derived=derived, local_report=report("passed"))

    result = verification.verify_candidate_admission(
        candidate(), admission(record_identity)
    )

    assert result.identity_matches is False
    assert result.verified is False


@pytest.mark.parametrize(
    "recalculated_status, expected_gate",
    [("passed", True), ("pending", False), ("failed", False)],
)
def test_local_validation_uses_recalculated_report_not_embedded_report(
    monkeypatch: pytest.MonkeyPatch,
    recalculated_status: str,
    expected_gate: bool,
) -> None:
    embedded = report("passed" if recalculated_status != "passed" else "pending")
    value = candidate(validation_report=embedded)
    expected_identity = identity()
    recalculated = report(recalculated_status)
    patch_dependencies(
        monkeypatch, derived=expected_identity, local_report=recalculated
    )

    result = verification.verify_candidate_admission(value, admission(expected_identity))

    assert result.local_validation_report is recalculated
    assert result.local_validation_passed is expected_gate
    assert result.verified is expected_gate


def test_pending_decisions_and_rejected_decision_are_normal_full_evaluations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = candidate(pending_human_decisions=["Resolve wording."])
    expected_identity = identity()
    revisions, calls = patch_dependencies(
        monkeypatch, derived=expected_identity, local_report=report("passed")
    )

    result = verification.verify_candidate_admission(
        value, admission(expected_identity, decision="rejected")
    )

    assert result.pending_human_decisions_clear is False
    assert result.human_decision_admitted is False
    assert result.verified is False
    assert revisions == ["revision-01"]
    assert calls == [value, value]


def test_unsupported_version_skips_both_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_derive(*args: object, **kwargs: object) -> CandidatePayloadIdentity:
        raise AssertionError("identity derivation must not run")

    def fail_validate(*args: object, **kwargs: object) -> ValidationReport:
        raise AssertionError("local validation must not run")

    monkeypatch.setattr(verification, "derive_candidate_payload_identity", fail_derive)
    monkeypatch.setattr(verification, "validate_pedagogical_candidate", fail_validate)

    with pytest.raises(ValueError, match="unsupported payload schema version"):
        verification.verify_candidate_admission(
            candidate(), admission(identity(schema_version="2.0"))
        )


def test_dependency_errors_propagate(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_identity = identity()

    def fail_derive(*args: object, **kwargs: object) -> CandidatePayloadIdentity:
        raise RuntimeError("derivation failed")

    monkeypatch.setattr(verification, "derive_candidate_payload_identity", fail_derive)
    with pytest.raises(RuntimeError, match="derivation failed"):
        verification.verify_candidate_admission(candidate(), admission(expected_identity))

    monkeypatch.setattr(
        verification,
        "derive_candidate_payload_identity",
        lambda *args, **kwargs: expected_identity,
    )
    monkeypatch.setattr(
        verification,
        "validate_pedagogical_candidate",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("validator failed")),
    )
    with pytest.raises(RuntimeError, match="validator failed"):
        verification.verify_candidate_admission(candidate(), admission(expected_identity))


def test_verification_does_not_mutate_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = candidate()
    expected_identity = identity()
    record = admission(expected_identity)
    candidate_before = value.model_dump()
    report_before = value.validation_report.model_dump()
    patch_dependencies(
        monkeypatch, derived=expected_identity, local_report=report("passed")
    )

    verification.verify_candidate_admission(value, record)

    assert value.model_dump() == candidate_before
    assert value.validation_report.model_dump() == report_before
    assert record.identity is expected_identity
