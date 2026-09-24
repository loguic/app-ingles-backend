"""Persist versioned, source-bound expected resource identity collections."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import tempfile

from app.services.pedagogical_expected_resource_identity_collection import (
    ExpectedResourceIdentityCollection,
)


EXPECTED_RESOURCE_IDENTITY_COLLECTION_DOCUMENT_SCHEMA_VERSION = "1.0"
_SHA256_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class ExpectedResourceIdentityCollectionDocumentV1:
    """Bind one expected collection to one canonical active-source manifest."""

    source_snapshot_revision: str
    source_snapshot_manifest_digest: str
    identities: ExpectedResourceIdentityCollection


def build_expected_resource_identity_collection_document(
    *,
    source_snapshot_revision: str,
    source_snapshot_manifest_digest: str,
    identities: ExpectedResourceIdentityCollection,
) -> ExpectedResourceIdentityCollectionDocumentV1:
    """Build one conforming durable expected-resource document value."""

    if not isinstance(source_snapshot_revision, str) or not source_snapshot_revision.strip():
        raise ValueError("source_snapshot_revision must be a non-blank string")
    if (
        not isinstance(source_snapshot_manifest_digest, str)
        or _SHA256_DIGEST_PATTERN.fullmatch(source_snapshot_manifest_digest) is None
    ):
        raise ValueError("source_snapshot_manifest_digest must be a SHA-256 digest")
    if not isinstance(identities, ExpectedResourceIdentityCollection):
        raise ValueError("identities must be an ExpectedResourceIdentityCollection")

    for identity in identities.identities:
        if not isinstance(identity.resource_id, str):
            raise ValueError("identity resource_id must be a string")
        if _SHA256_DIGEST_PATTERN.fullmatch(identity.content_digest) is None:
            raise ValueError("identity content_digest must be a SHA-256 digest")

    return ExpectedResourceIdentityCollectionDocumentV1(
        source_snapshot_revision=source_snapshot_revision,
        source_snapshot_manifest_digest=source_snapshot_manifest_digest,
        identities=identities,
    )


def serialize_expected_resource_identity_collection_document(
    document: ExpectedResourceIdentityCollectionDocumentV1,
) -> bytes:
    """Serialize one document as deterministic UTF-8 v1 bytes."""

    if not isinstance(document, ExpectedResourceIdentityCollectionDocumentV1):
        raise ValueError(
            "document must be an ExpectedResourceIdentityCollectionDocumentV1"
        )

    _validate_document_value(document)
    payload = {
        "document_schema_version": (
            EXPECTED_RESOURCE_IDENTITY_COLLECTION_DOCUMENT_SCHEMA_VERSION
        ),
        "source_snapshot_revision": document.source_snapshot_revision,
        "source_snapshot_manifest_digest": document.source_snapshot_manifest_digest,
        "identities": [
            {
                "resource_id": identity.resource_id,
                "content_digest": identity.content_digest,
            }
            for identity in document.identities.identities
        ],
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def publish_expected_resource_identity_collection_document(
    document: ExpectedResourceIdentityCollectionDocumentV1,
    *,
    document_path: Path,
) -> None:
    """Atomically replace one expected-resource document with v1 bytes."""

    document_bytes = serialize_expected_resource_identity_collection_document(document)
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
                "expected resource identity document replacement is visible but "
                "durable directory sync failed"
            ) from error
        raise
    finally:
        if temporary_path is not None and not replaced:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _validate_document_value(
    document: ExpectedResourceIdentityCollectionDocumentV1,
) -> None:
    build_expected_resource_identity_collection_document(
        source_snapshot_revision=document.source_snapshot_revision,
        source_snapshot_manifest_digest=document.source_snapshot_manifest_digest,
        identities=document.identities,
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
