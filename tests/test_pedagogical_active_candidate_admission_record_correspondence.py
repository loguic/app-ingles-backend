"""Tests for active candidate admission record correspondence verification."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.services.pedagogical_active_candidate_admission_record_acquisition import (
    AcquiredActiveCandidateAdmissionRecordEntry,
    ActiveCandidateSourceAdmissionRecordAcquisition,
)
from app.services.pedagogical_active_candidate_admission_record_correspondence import (
    ActiveCandidateSourceAdmissionRecordCorrespondenceVerification,
    verify_active_candidate_admission_record_correspondence,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
    CandidatePayloadIntegrityVerification,
)
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    serialize_candidate_admission_record_document,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


def _identity(index: int) -> CandidatePayloadIdentity:
    return CandidatePayloadIdentity(
        unit_id=f"a1-u{index}",
        candidate_revision=f"candidate-r{index}",
        payload_schema_version="1.0",
        content_digest="sha256:" + f"{index:064x}",
    )


def _record(
    index: int,
    *,
    admission_id: str | None = None,
    identity: CandidatePayloadIdentity | None = None,
    decision: str = "admitted",
) -> AdmissionRecord:
    return AdmissionRecord(
        admission_id=admission_id or f"admission-{index}",
        identity=identity or _identity(index),
        decision=decision,  # type: ignore[arg-type]
        reviewer_id="reviewer-1",
        decided_at=datetime(2026, 8, 23, 12, 30, index, tzinfo=timezone.utc),
    )


def _acquisition(
    indexes: tuple[int, ...] = (1,),
    *,
    records: tuple[AdmissionRecord, ...] | None = None,
) -> ActiveCandidateSourceAdmissionRecordAcquisition:
    memberships = tuple(
        ActiveCandidateMembership(
            identity=_identity(index),
            admission_id=f"admission-{index}",
        )
        for index in indexes
    )
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection(memberships),
        snapshot_revision="source-r1",
    )
    candidate_integrity_verification = (
        ActiveCandidateSourceCandidateIntegrityVerification(
            snapshot=snapshot,
            entries=tuple(
                CandidatePayloadIntegrityVerification(
                    membership=membership,
                    candidate_path=Path(f"/candidate/{index}.json"),
                    candidate_bytes=f"candidate-{index}".encode(),
                    derived_identity=membership.identity,
                )
                for index, membership in zip(indexes, memberships, strict=True)
            ),
        )
    )
    acquired_records = records or tuple(_record(index) for index in indexes)
    return ActiveCandidateSourceAdmissionRecordAcquisition(
        candidate_integrity_verification=candidate_integrity_verification,
        entries=tuple(
            AcquiredActiveCandidateAdmissionRecordEntry(
                membership=membership,
                document_path=Path(f"/admission/{index}.json"),
                admission_record_bytes=(
                    serialize_candidate_admission_record_document(record)
                ),
                admission_record=record,
            )
            for index, membership, record in zip(
                indexes,
                memberships,
                acquired_records,
                strict=True,
            )
        ),
    )


def test_verifies_single_and_multiple_entries_preserving_b41_aggregate() -> None:
    acquisition = _acquisition((2, 1))

    result = verify_active_candidate_admission_record_correspondence(acquisition)

    assert result.admission_record_acquisition is acquisition
    assert [entry.membership.admission_id for entry in result.admission_record_acquisition.entries] == [
        "admission-2",
        "admission-1",
    ]


def test_result_shape_is_frozen() -> None:
    result = verify_active_candidate_admission_record_correspondence(_acquisition())

    assert [field.name for field in fields(
        ActiveCandidateSourceAdmissionRecordCorrespondenceVerification
    )] == ["admission_record_acquisition"]
    with pytest.raises(FrozenInstanceError):
        result.admission_record_acquisition = _acquisition()  # type: ignore[misc]


def test_rejects_admission_id_mismatch() -> None:
    acquisition = _acquisition(
        records=(_record(1, admission_id="other-admission"),),
    )

    with pytest.raises(ValueError, match="admission_id correspondence failure"):
        verify_active_candidate_admission_record_correspondence(acquisition)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("unit_id", "a1-u-other"),
        ("candidate_revision", "candidate-r-other"),
        ("payload_schema_version", "2.0"),
        ("content_digest", "sha256:" + "f" * 64),
    ],
)
def test_rejects_each_identity_dimension_mismatch(
    field_name: str,
    value: str,
) -> None:
    changed_identity = replace(_identity(1), **{field_name: value})
    acquisition = _acquisition(records=(_record(1, identity=changed_identity),))

    with pytest.raises(ValueError, match="identity correspondence failure"):
        verify_active_candidate_admission_record_correspondence(acquisition)


def test_rejected_record_with_matching_identity_and_id_passes() -> None:
    acquisition = _acquisition(records=(_record(1, decision="rejected"),))

    result = verify_active_candidate_admission_record_correspondence(acquisition)

    assert result.admission_record_acquisition is acquisition
    assert result.admission_record_acquisition.entries[0].admission_record.decision == "rejected"


def test_is_all_or_nothing_and_empty_acquisition_is_valid() -> None:
    acquisition = _acquisition(
        (1, 2),
        records=(
            _record(1),
            _record(2, identity=replace(_identity(2), unit_id="a1-u-other")),
        ),
    )

    with pytest.raises(ValueError, match="identity correspondence failure"):
        verify_active_candidate_admission_record_correspondence(acquisition)

    empty = _acquisition(())
    result = verify_active_candidate_admission_record_correspondence(empty)

    assert result.admission_record_acquisition is empty
    assert result.admission_record_acquisition.entries == ()
