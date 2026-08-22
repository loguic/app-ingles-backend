"""Tests for physical admission record document publication."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION,
    publish_candidate_admission_record_document,
    serialize_candidate_admission_record_document,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)
import app.services.pedagogical_candidate_admission_record_document as document_module


def _record(
    *,
    admission_id: str = " admission-01 ",
    decision: str = "admitted",
    decided_at: datetime | None = None,
) -> AdmissionRecord:
    return AdmissionRecord(
        admission_id=admission_id,
        identity=CandidatePayloadIdentity(
            unit_id="a1-u1",
            candidate_revision="candidate-r1",
            payload_schema_version="1.0",
            content_digest="sha256:" + "a" * 64,
        ),
        decision=decision,  # type: ignore[arg-type]
        reviewer_id=" revisor-ñ ",
        decided_at=decided_at
        or datetime(2026, 8, 16, 12, 30, 45, 123456, tzinfo=timezone.utc),
    )


def test_serialization_has_exact_v1_shape_and_deterministic_bytes() -> None:
    record = _record(
        decided_at=datetime(
            2026,
            8,
            16,
            12,
            30,
            45,
            123456,
            tzinfo=timezone(timedelta(0), name="UTC-equivalent"),
        )
    )

    expected = (
        b'{"document_schema_version":"1.0","admission_id":" admission-01 ",'
        b'"identity":{"unit_id":"a1-u1","candidate_revision":"candidate-r1",'
        b'"payload_schema_version":"1.0","content_digest":"sha256:'
        + b"a" * 64
        + b'"},"decision":"admitted","reviewer_id":" revisor-\xc3\xb1 ",'
        b'"decided_at":"2026-08-16T12:30:45.123456Z"}\n'
    )

    assert ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION == "1.0"
    assert serialize_candidate_admission_record_document(record) == expected
    assert serialize_candidate_admission_record_document(record) == expected


def test_rejected_decision_and_zero_microseconds_are_serializable() -> None:
    record = _record(
        decision="rejected",
        decided_at=datetime(2026, 8, 16, 12, 30, 45, tzinfo=timezone.utc),
    )

    serialized = serialize_candidate_admission_record_document(record)

    assert b'"decision":"rejected"' in serialized
    assert b'"decided_at":"2026-08-16T12:30:45.000000Z"' in serialized


def test_publish_creates_and_replaces_the_complete_document(tmp_path: Path) -> None:
    document_path = tmp_path / "admission-record.json"
    first_record = _record(admission_id="admission-01")
    second_record = _record(admission_id="admission-02")

    publish_candidate_admission_record_document(
        first_record,
        document_path=document_path,
    )
    assert document_path.read_bytes() == serialize_candidate_admission_record_document(
        first_record
    )

    with document_path.open("rb") as first_descriptor:
        publish_candidate_admission_record_document(
            second_record,
            document_path=document_path,
        )
        assert first_descriptor.read() == serialize_candidate_admission_record_document(
            first_record
        )

    assert document_path.read_bytes() == serialize_candidate_admission_record_document(
        second_record
    )


def test_publish_rejects_invalid_document_paths(tmp_path: Path) -> None:
    record = _record()
    target_directory = tmp_path / "directory-target"
    target_directory.mkdir()
    target_symlink = tmp_path / "symlink-target"
    target_symlink.symlink_to(tmp_path / "missing-target")
    parent_file = tmp_path / "parent-file"
    parent_file.write_text("not a directory", encoding="utf-8")

    for path in (
        Path("relative-admission-record.json"),
        tmp_path / "missing-parent" / "admission-record.json",
        parent_file / "admission-record.json",
        target_directory,
        target_symlink,
    ):
        try:
            publish_candidate_admission_record_document(
                record,
                document_path=path,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected invalid document path: {path}")


def test_replace_failure_keeps_previous_document_and_cleans_unpublished_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    document_path = tmp_path / "admission-record.json"
    first_record = _record(admission_id="admission-01")
    publish_candidate_admission_record_document(
        first_record,
        document_path=document_path,
    )
    original_bytes = document_path.read_bytes()

    def fail_replace(source: Path, target: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(document_module.os, "replace", fail_replace)

    try:
        publish_candidate_admission_record_document(
            _record(admission_id="admission-02"),
            document_path=document_path,
        )
    except OSError as error:
        assert str(error) == "replace failed"
    else:
        raise AssertionError("expected replace failure")

    assert document_path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".admission-record.json.*.tmp")) == []


def test_file_fsync_failure_keeps_previous_document_and_cleans_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    document_path = tmp_path / "admission-record.json"
    first_record = _record(admission_id="admission-01")
    publish_candidate_admission_record_document(
        first_record,
        document_path=document_path,
    )
    original_bytes = document_path.read_bytes()

    def fail_file_fsync(descriptor: int) -> None:
        raise OSError("temporary file sync failed")

    def unexpected_replace(source: Path, target: Path) -> None:
        raise AssertionError("os.replace must not run after file fsync failure")

    monkeypatch.setattr(document_module.os, "fsync", fail_file_fsync)
    monkeypatch.setattr(document_module.os, "replace", unexpected_replace)

    try:
        publish_candidate_admission_record_document(
            _record(admission_id="admission-02"),
            document_path=document_path,
        )
    except OSError as error:
        assert str(error) == "temporary file sync failed"
    else:
        raise AssertionError("expected temporary file fsync failure")

    assert document_path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".admission-record.json.*.tmp")) == []


def test_cleanup_failure_does_not_mask_pre_replace_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    document_path = tmp_path / "admission-record.json"
    first_record = _record(admission_id="admission-01")
    publish_candidate_admission_record_document(
        first_record,
        document_path=document_path,
    )
    original_bytes = document_path.read_bytes()

    def fail_file_fsync(descriptor: int) -> None:
        raise OSError("temporary file sync failed")

    def fail_cleanup(path: Path) -> None:
        raise OSError("cleanup failed")

    monkeypatch.setattr(document_module.os, "fsync", fail_file_fsync)
    monkeypatch.setattr(document_module.Path, "unlink", fail_cleanup)

    try:
        publish_candidate_admission_record_document(
            _record(admission_id="admission-02"),
            document_path=document_path,
        )
    except OSError as error:
        assert str(error) == "temporary file sync failed"
    else:
        raise AssertionError("expected temporary file fsync failure")

    assert document_path.read_bytes() == original_bytes


def test_directory_fsync_failure_reports_visible_but_unconfirmed_durability(
    tmp_path: Path,
    monkeypatch,
) -> None:
    document_path = tmp_path / "admission-record.json"
    record = _record()

    def fail_directory_fsync(directory: Path) -> None:
        raise OSError("directory sync failed")

    monkeypatch.setattr(document_module, "_fsync_directory", fail_directory_fsync)

    try:
        publish_candidate_admission_record_document(
            record,
            document_path=document_path,
        )
    except OSError as error:
        assert "visible but durable directory sync failed" in str(error)
    else:
        raise AssertionError("expected directory fsync failure")

    assert document_path.read_bytes() == serialize_candidate_admission_record_document(
        record
    )
