from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


class EqualToAdmitted:
    def __eq__(self, other: object) -> bool:
        return other == "admitted"


@pytest.fixture
def identity() -> CandidatePayloadIdentity:
    return CandidatePayloadIdentity(
        unit_id="A1-U1",
        candidate_revision="revision-01",
        payload_schema_version="1.0",
        content_digest="sha256:" + "a" * 64,
    )


@pytest.fixture
def decided_at() -> datetime:
    return datetime(2026, 8, 16, 12, 30, 45, 123456, tzinfo=timezone.utc)


def record(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    **overrides: object,
) -> AdmissionRecord:
    values: dict[str, object] = {
        "admission_id": "admission-01",
        "identity": identity,
        "decision": "admitted",
        "reviewer_id": "reviewer-01",
        "decided_at": decided_at,
    }
    values.update(overrides)
    return AdmissionRecord(**values)  # type: ignore[arg-type]


def test_record_has_exact_fields_and_preserves_identity(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
) -> None:
    admission = record(identity, decided_at)

    assert [field.name for field in fields(AdmissionRecord)] == [
        "admission_id",
        "identity",
        "decision",
        "reviewer_id",
        "decided_at",
    ]
    assert admission.identity is identity


def test_record_is_frozen(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
) -> None:
    admission = record(identity, decided_at)

    with pytest.raises(FrozenInstanceError):
        admission.admission_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("decision", ["admitted", "rejected"])
def test_final_decisions_are_valid(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    decision: str,
) -> None:
    assert record(identity, decided_at, decision=decision).decision == decision


@pytest.mark.parametrize("decision", ["pending", "approved", "published", "", "other"])
def test_invalid_decisions_are_rejected(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    decision: str,
) -> None:
    with pytest.raises(ValueError, match="decision"):
        record(identity, decided_at, decision=decision)


@pytest.mark.parametrize("decision", [1, EqualToAdmitted()])
def test_non_string_decisions_are_rejected(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    decision: object,
) -> None:
    with pytest.raises(ValueError, match="decision"):
        record(identity, decided_at, decision=decision)


@pytest.mark.parametrize("admission_id", ["", "   ", 1])
def test_invalid_admission_ids_are_rejected(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    admission_id: object,
) -> None:
    with pytest.raises(ValueError, match="admission_id"):
        record(identity, decided_at, admission_id=admission_id)


def test_admission_id_is_preserved_literally(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
) -> None:
    assert record(identity, decided_at, admission_id=" admission-01 ").admission_id == " admission-01 "


@pytest.mark.parametrize("reviewer_id", ["", "   ", 1])
def test_invalid_reviewer_ids_are_rejected(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
    reviewer_id: object,
) -> None:
    with pytest.raises(ValueError, match="reviewer_id"):
        record(identity, decided_at, reviewer_id=reviewer_id)


def test_reviewer_id_is_preserved_literally(
    identity: CandidatePayloadIdentity,
    decided_at: datetime,
) -> None:
    assert record(identity, decided_at, reviewer_id=" reviewer-01 ").reviewer_id == " reviewer-01 "


def test_non_identity_is_rejected(decided_at: datetime) -> None:
    with pytest.raises(ValueError, match="identity"):
        record(None, decided_at)  # type: ignore[arg-type]


def test_utc_equivalent_timezone_and_microseconds_are_preserved(
    identity: CandidatePayloadIdentity,
) -> None:
    utc_equivalent = timezone(timedelta(0), name="UTC-equivalent")
    value = datetime(2026, 8, 16, 12, 30, 45, 123456, tzinfo=utc_equivalent)

    admission = record(identity, value)

    assert admission.decided_at is value
    assert admission.decided_at.microsecond == 123456


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 8, 16, 12, 30, 45),
        datetime(2026, 8, 16, 12, 30, 45, tzinfo=timezone(timedelta(hours=1))),
        "2026-08-16T12:30:45Z",
    ],
)
def test_invalid_decided_at_values_are_rejected(
    identity: CandidatePayloadIdentity,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="decided_at"):
        record(identity, value)  # type: ignore[arg-type]
