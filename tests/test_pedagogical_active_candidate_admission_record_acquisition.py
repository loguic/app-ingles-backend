"""Tests for local active candidate admission record acquisition."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

import app.services.pedagogical_active_candidate_admission_record_acquisition as acquisition_module
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    serialize_candidate_admission_record_document,
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
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


def _identity(index: int, *, payload_schema_version: str = "1.0") -> CandidatePayloadIdentity:
    return CandidatePayloadIdentity(
        unit_id=f"a1-u{index}",
        candidate_revision=f"candidate-r{index}",
        payload_schema_version=payload_schema_version,
        content_digest="sha256:" + f"{index:064x}",
    )


def _record(
    index: int,
    *,
    admission_id: str | None = None,
    identity: CandidatePayloadIdentity | None = None,
    decision: str = "admitted",
    reviewer_id: str = "reviewer-ñ",
    decided_at: datetime | None = None,
) -> AdmissionRecord:
    return AdmissionRecord(
        admission_id=admission_id or f"admission-{index}",
        identity=identity or _identity(index),
        decision=decision,  # type: ignore[arg-type]
        reviewer_id=reviewer_id,
        decided_at=decided_at
        or datetime(2026, 8, 23, 12, 30, index, index, tzinfo=timezone.utc),
    )


def _verification(
    indexes: tuple[int, ...] = (1,),
) -> ActiveCandidateSourceCandidateIntegrityVerification:
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
    entries = tuple(
        CandidatePayloadIntegrityVerification(
            membership=membership,
            candidate_path=Path(f"/candidate/{index}.json"),
            candidate_bytes=f"candidate-{index}".encode(),
            derived_identity=membership.identity,
        )
        for index, membership in zip(indexes, memberships, strict=True)
    )
    return ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=snapshot,
        entries=entries,
    )


def _write_record(tmp_path: Path, record: AdmissionRecord, name: str) -> Path:
    path = tmp_path / name
    path.write_bytes(serialize_candidate_admission_record_document(record))
    return path


def _bindings(
    verification: ActiveCandidateSourceCandidateIntegrityVerification,
    paths: tuple[Path, ...],
):
    return tuple(
        acquisition_module.ActiveCandidateAdmissionRecordBinding(
            admission_id=entry.membership.admission_id,
            document_path=path,
        )
        for entry, path in zip(verification.entries, paths, strict=True)
    )


def test_acquires_unverified_records_in_b39_order_and_preserves_bytes(
    tmp_path: Path,
) -> None:
    verification = _verification((2, 1))
    first_path = _write_record(tmp_path, _record(2), "first.json")
    second_path = _write_record(tmp_path, _record(1), "second.json")
    bindings = _bindings(verification, (first_path, second_path))

    result = acquisition_module.acquire_active_candidate_admission_records(
        verification,
        admission_record_bindings=tuple(reversed(bindings)),
    )

    assert result.candidate_integrity_verification is verification
    assert [entry.membership for entry in result.entries] == [
        entry.membership for entry in verification.entries
    ]
    assert [entry.document_path for entry in result.entries] == [
        first_path,
        second_path,
    ]
    assert [entry.admission_record for entry in result.entries] == [
        _record(2),
        _record(1),
    ]
    assert result.entries[0].admission_record_bytes == first_path.read_bytes()


def test_result_shapes_are_frozen_and_empty_verification_is_valid() -> None:
    empty = _verification(())

    result = acquisition_module.acquire_active_candidate_admission_records(
        empty,
        admission_record_bindings=(),
    )

    assert [field.name for field in fields(
        acquisition_module.ActiveCandidateAdmissionRecordBinding
    )] == ["admission_id", "document_path"]
    assert [field.name for field in fields(
        acquisition_module.AcquiredActiveCandidateAdmissionRecordEntry
    )] == [
        "membership",
        "document_path",
        "admission_record_bytes",
        "admission_record",
    ]
    assert [field.name for field in fields(
        acquisition_module.ActiveCandidateSourceAdmissionRecordAcquisition
    )] == ["candidate_integrity_verification", "entries"]
    assert result.entries == ()
    with pytest.raises(FrozenInstanceError):
        result.entries = ()  # type: ignore[misc]


def test_rejects_missing_duplicate_unexpected_and_duplicate_path_bindings(
    tmp_path: Path,
) -> None:
    verification = _verification((1, 2))
    first_path = _write_record(tmp_path, _record(1), "first.json")
    second_path = _write_record(tmp_path, _record(2), "second.json")
    first_binding, second_binding = _bindings(
        verification,
        (first_path, second_path),
    )

    with pytest.raises(ValueError, match="missing"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(first_binding,),
        )
    with pytest.raises(ValueError, match="duplicate.*admission_id"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(first_binding, first_binding),
        )
    with pytest.raises(ValueError, match="unexpected"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(
                first_binding,
                acquisition_module.ActiveCandidateAdmissionRecordBinding(
                    admission_id="admission-extra",
                    document_path=second_path,
                ),
            ),
        )
    with pytest.raises(ValueError, match="duplicate.*document_path"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(
                first_binding,
                acquisition_module.ActiveCandidateAdmissionRecordBinding(
                    admission_id=second_binding.admission_id,
                    document_path=first_path,
                ),
            ),
        )


def test_rejects_missing_binding_before_opening_any_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verification = _verification((1, 2))
    first_path = _write_record(tmp_path, _record(1), "first.json")
    opened_paths: list[Path] = []
    original_open = Path.open

    def track_open(document_path: Path, *args: object, **kwargs: object):
        opened_paths.append(document_path)
        return original_open(document_path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", track_open)

    with pytest.raises(ValueError, match="missing"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(
                acquisition_module.ActiveCandidateAdmissionRecordBinding(
                    admission_id="admission-1",
                    document_path=first_path,
                ),
            ),
        )

    assert opened_paths == []


def test_rejects_invalid_document_paths(tmp_path: Path) -> None:
    verification = _verification()
    valid_path = _write_record(tmp_path, _record(1), "record.json")
    directory = tmp_path / "directory"
    directory.mkdir()
    symlink = tmp_path / "record-link.json"
    symlink.symlink_to(valid_path)

    for path, message in (
        (Path("relative.json"), "absolute"),
        (tmp_path / "missing.json", "exist"),
        (directory, "regular"),
        (symlink, "symlink"),
    ):
        with pytest.raises(ValueError, match=message):
            acquisition_module.acquire_active_candidate_admission_records(
                verification,
                admission_record_bindings=(
                    acquisition_module.ActiveCandidateAdmissionRecordBinding(
                        admission_id="admission-1",
                        document_path=path,
                    ),
                ),
            )


@pytest.mark.parametrize(
    ("raw_bytes", "message"),
    [
        (b"\xff", "valid UTF-8"),
        (b"\xef\xbb\xbf{}", "BOM"),
        (b"{", "valid JSON"),
        (b'{"x":NaN}', "valid JSON"),
        (
            b'{"document_schema_version":"1.0","document_schema_version":"1.0"}',
            "valid JSON",
        ),
    ],
)
def test_rejects_invalid_encoding_and_json(
    tmp_path: Path,
    raw_bytes: bytes,
    message: str,
) -> None:
    verification = _verification()
    path = tmp_path / "record.json"
    path.write_bytes(raw_bytes)

    with pytest.raises(ValueError, match=message):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=(
                acquisition_module.ActiveCandidateAdmissionRecordBinding(
                    admission_id="admission-1",
                    document_path=path,
                ),
            ),
        )


def test_rejects_invalid_document_schema_shape_types_and_timestamp(
    tmp_path: Path,
) -> None:
    verification = _verification()
    record = _record(1)
    document = json.loads(serialize_candidate_admission_record_document(record))
    path = tmp_path / "record.json"
    invalid_documents = (
        {**document, "document_schema_version": "2.0"},
        {**document, "unexpected": "value"},
        {key: value for key, value in document.items() if key != "reviewer_id"},
        {**document, "admission_id": 1},
        {**document, "decided_at": "2026-08-23T12:30:01+00:00"},
    )

    for invalid_document in invalid_documents:
        path.write_bytes(
            json.dumps(invalid_document, ensure_ascii=False).encode("utf-8")
            + b"\n"
        )
        with pytest.raises(ValueError):
            acquisition_module.acquire_active_candidate_admission_records(
                verification,
                admission_record_bindings=(
                    acquisition_module.ActiveCandidateAdmissionRecordBinding(
                        admission_id="admission-1",
                        document_path=path,
                    ),
                ),
            )


def test_rejects_noncanonical_document_bytes(tmp_path: Path) -> None:
    verification = _verification()
    record = _record(1, reviewer_id="reviewer-é")
    document = json.loads(serialize_candidate_admission_record_document(record))
    path = tmp_path / "record.json"
    nonconformant_documents = (
        {
            "admission_id": document["admission_id"],
            "document_schema_version": document["document_schema_version"],
            "identity": document["identity"],
            "decision": document["decision"],
            "reviewer_id": document["reviewer_id"],
            "decided_at": document["decided_at"],
        },
        document,
        document,
    )
    raw_values = (
        json.dumps(
            nonconformant_documents[0],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n",
        json.dumps(document, ensure_ascii=False, indent=2).encode("utf-8")
        + b"\n",
        json.dumps(
            document,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n",
        serialize_candidate_admission_record_document(record).rstrip(b"\n"),
    )

    for raw_bytes in raw_values:
        path.write_bytes(raw_bytes)
        with pytest.raises(ValueError, match="byte-conformant"):
            acquisition_module.acquire_active_candidate_admission_records(
                verification,
                admission_record_bindings=(
                    acquisition_module.ActiveCandidateAdmissionRecordBinding(
                        admission_id="admission-1",
                        document_path=path,
                    ),
                ),
            )


def test_acquires_unverified_mismatched_and_rejected_records(tmp_path: Path) -> None:
    verification = _verification((1, 2, 3))
    paths = (
        _write_record(tmp_path, _record(1, admission_id="other-admission"), "one.json"),
        _write_record(
            tmp_path,
            _record(2, identity=replace(_identity(2), unit_id="a1-other")),
            "two.json",
        ),
        _write_record(tmp_path, _record(3, decision="rejected"), "three.json"),
    )

    result = acquisition_module.acquire_active_candidate_admission_records(
        verification,
        admission_record_bindings=_bindings(verification, paths),
    )

    assert result.entries[0].admission_record.admission_id == "other-admission"
    assert result.entries[1].admission_record.identity.unit_id == "a1-other"
    assert result.entries[2].admission_record.decision == "rejected"


def test_accepts_unsupported_declared_payload_schema_version(tmp_path: Path) -> None:
    verification = _verification()
    record_path = _write_record(
        tmp_path,
        _record(1, identity=_identity(1, payload_schema_version="99.0")),
        "record.json",
    )

    result = acquisition_module.acquire_active_candidate_admission_records(
        verification,
        admission_record_bindings=(
            acquisition_module.ActiveCandidateAdmissionRecordBinding(
                admission_id="admission-1",
                document_path=record_path,
            ),
        ),
    )

    assert result.entries[0].admission_record.identity.payload_schema_version == "99.0"


def test_reads_each_document_once_and_preserves_evidence_after_path_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verification = _verification()
    record = _record(1)
    path = _write_record(tmp_path, record, "record.json")
    original_open = Path.open
    opened_paths: list[Path] = []

    def track_open(document_path: Path, *args: object, **kwargs: object):
        if document_path == path:
            opened_paths.append(document_path)
        return original_open(document_path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", track_open)
    result = acquisition_module.acquire_active_candidate_admission_records(
        verification,
        admission_record_bindings=(
            acquisition_module.ActiveCandidateAdmissionRecordBinding(
                admission_id="admission-1",
                document_path=path,
            ),
        ),
    )
    path.unlink()

    assert opened_paths == [path]
    assert result.entries[0].admission_record_bytes == (
        serialize_candidate_admission_record_document(record)
    )
    assert result.entries[0].admission_record == record


def test_is_all_or_nothing_when_one_document_fails(tmp_path: Path) -> None:
    verification = _verification((1, 2))
    valid_path = _write_record(tmp_path, _record(1), "valid.json")
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_bytes(b"{")

    with pytest.raises(ValueError, match="valid JSON"):
        acquisition_module.acquire_active_candidate_admission_records(
            verification,
            admission_record_bindings=_bindings(
                verification,
                (valid_path, invalid_path),
            ),
        )
