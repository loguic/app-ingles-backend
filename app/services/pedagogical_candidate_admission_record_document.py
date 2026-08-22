"""Serialize and atomically publish physical admission record documents.

Serializa y publica atómicamente documentos físicos de admission record.
"""

from datetime import timezone
import json
import os
from pathlib import Path
import tempfile

from app.services.pedagogical_candidate_admission import AdmissionRecord


ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION = "1.0"


def serialize_candidate_admission_record_document(
    record: AdmissionRecord,
) -> bytes:
    """Serialize one admission record as deterministic document v1 bytes.

    Serializa un admission record como bytes deterministas de documento v1.
    """

    if not isinstance(record, AdmissionRecord):
        raise ValueError("record must be an AdmissionRecord")

    identity = record.identity
    document = {
        "document_schema_version": ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION,
        "admission_id": record.admission_id,
        "identity": {
            "unit_id": identity.unit_id,
            "candidate_revision": identity.candidate_revision,
            "payload_schema_version": identity.payload_schema_version,
            "content_digest": identity.content_digest,
        },
        "decision": record.decision,
        "reviewer_id": record.reviewer_id,
        "decided_at": _serialize_decided_at(record),
    }
    return json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def publish_candidate_admission_record_document(
    record: AdmissionRecord,
    *,
    document_path: Path,
) -> None:
    """Atomically replace one local admission record document.

    Sustituye atómicamente un documento local de admission record.
    """

    document_bytes = serialize_candidate_admission_record_document(record)
    _validate_document_path(document_path)
    temporary_path: Path | None = None
    replaced = False

    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{document_path.name}.",
            suffix=".tmp",
            dir=document_path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(document_bytes)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, document_path)
        replaced = True
        _fsync_directory(document_path.parent)
    except OSError as error:
        if replaced:
            raise OSError(
                "admission record replacement is visible but durable directory "
                "sync failed"
            ) from error
        raise
    finally:
        if temporary_path is not None and not replaced:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _serialize_decided_at(record: AdmissionRecord) -> str:
    decided_at_utc = record.decided_at.astimezone(timezone.utc)
    return decided_at_utc.isoformat(timespec="microseconds").replace(
        "+00:00",
        "Z",
    )


def _validate_document_path(document_path: Path) -> None:
    if not isinstance(document_path, Path):
        raise ValueError("document_path must be a Path")
    if not document_path.is_absolute():
        raise ValueError("document_path must be absolute")
    if not document_path.parent.exists() or not document_path.parent.is_dir():
        raise ValueError("document_path parent must be an existing directory")
    if document_path.is_symlink():
        raise ValueError("document_path target must not be a symlink")
    if document_path.exists() and not document_path.is_file():
        raise ValueError(
            "document_path target must be nonexistent or a regular file"
        )


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
