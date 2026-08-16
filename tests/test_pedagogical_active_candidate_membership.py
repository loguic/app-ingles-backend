from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timezone

import pytest

from app.schemas.pedagogical_unit import ValidationReport
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
    declare_active_candidate_membership,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_verification import (
    AdmissionGateVerification,
)
from app.services.pedagogical_candidate_payload_identity import (
    PAYLOAD_SCHEMA_VERSION,
    CandidatePayloadIdentity,
)


def identity() -> CandidatePayloadIdentity:
    return CandidatePayloadIdentity(
        unit_id="a1-u1",
        candidate_revision="revision-01",
        payload_schema_version=PAYLOAD_SCHEMA_VERSION,
        content_digest="sha256:" + "a" * 64,
    )


def admission(value: CandidatePayloadIdentity) -> AdmissionRecord:
    return AdmissionRecord(
        admission_id="admission-01",
        identity=value,
        decision="admitted",
        reviewer_id="reviewer-01",
        decided_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )


def verification(
    *,
    identity_matches: bool = True,
    local_validation_passed: bool = True,
    pending_human_decisions_clear: bool = True,
    human_decision_admitted: bool = True,
) -> AdmissionGateVerification:
    value = identity()
    return AdmissionGateVerification(
        derived_identity=value,
        admission_record=admission(value),
        local_validation_report=ValidationReport(
            status="passed",
            findings=[],
        ),
        identity_matches=identity_matches,
        local_validation_passed=local_validation_passed,
        pending_human_decisions_clear=pending_human_decisions_clear,
        human_decision_admitted=human_decision_admitted,
    )


def test_active_candidate_membership_shape_is_frozen() -> None:
    value = identity()
    membership = ActiveCandidateMembership(
        identity=value,
        admission_id="admission-01",
    )

    assert [field.name for field in fields(membership)] == [
        "identity",
        "admission_id",
    ]

    with pytest.raises(FrozenInstanceError):
        membership.admission_id = "other-admission"  # type: ignore[misc]


def test_declares_membership_from_verified_admission_and_preserves_evidence() -> None:
    admission_verification = verification()

    membership = declare_active_candidate_membership(admission_verification)

    assert admission_verification.verified is True
    assert membership.identity is admission_verification.derived_identity
    assert (
        membership.admission_id
        == admission_verification.admission_record.admission_id
    )


def test_unverified_admission_cannot_declare_active_membership() -> None:
    admission_verification = verification(identity_matches=False)

    assert admission_verification.verified is False

    with pytest.raises(ValueError):
        declare_active_candidate_membership(admission_verification)