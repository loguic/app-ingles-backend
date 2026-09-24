"""Acquire one source-bound expected-resource document into B45 evidence."""

import hashlib
import json
from pathlib import Path

from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_expected_resource_identity_collection import (
    ExpectedResourceIdentityCollection,
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_expected_resource_identity_collection_document import (
    EXPECTED_RESOURCE_IDENTITY_COLLECTION_DOCUMENT_SCHEMA_VERSION,
    ExpectedResourceIdentityCollectionDocumentV1,
    build_expected_resource_identity_collection_document,
    serialize_expected_resource_identity_collection_document,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def acquire_expected_resource_identity_collection(
    document_path: Path,
    *,
    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    ),
) -> ExpectedResourceIdentityCollection:
    """Read one canonical document and return B45 for the same B39 source."""

    if not isinstance(
        candidate_integrity_verification,
        ActiveCandidateSourceCandidateIntegrityVerification,
    ):
        raise ValueError(
            "candidate_integrity_verification must be an "
            "ActiveCandidateSourceCandidateIntegrityVerification"
        )
    _validate_document_path(document_path)
    document_bytes = _read_file_once(document_path)
    document = _parse_document(document_bytes)
    if serialize_expected_resource_identity_collection_document(document) != document_bytes:
        raise ValueError(
            "expected resource identity document physical format is not "
            "byte-conformant with v1"
        )

    snapshot = candidate_integrity_verification.snapshot
    if document.source_snapshot_revision != snapshot.snapshot_revision:
        raise ValueError("expected resource identity document source revision mismatch")
    expected_manifest_digest = "sha256:" + hashlib.sha256(
        serialize_active_candidate_source_snapshot_manifest(snapshot)
    ).hexdigest()
    if document.source_snapshot_manifest_digest != expected_manifest_digest:
        raise ValueError("expected resource identity document source manifest digest mismatch")

    return document.identities


def _validate_document_path(document_path: Path) -> None:
    if not isinstance(document_path, Path):
        raise ValueError("document_path must be a Path")
    if not document_path.is_absolute():
        raise ValueError("document_path must be absolute")
    if document_path.is_symlink():
        raise ValueError("document_path must not be a symlink")
    if not document_path.exists():
        raise ValueError("document_path must exist")
    if not document_path.is_file():
        raise ValueError("document_path must be a regular file")


def _read_file_once(document_path: Path) -> bytes:
    with document_path.open("rb") as source_file:
        return source_file.read()


def _parse_document(document_bytes: bytes) -> ExpectedResourceIdentityCollectionDocumentV1:
    if not isinstance(document_bytes, bytes):
        raise ValueError("expected resource identity document bytes must be bytes")
    try:
        text = document_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("expected resource identity document must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("expected resource identity document must not contain a UTF-8 BOM")
    try:
        payload = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (TypeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("expected resource identity document must be valid JSON") from error
    if type(payload) is not dict:
        raise ValueError("expected resource identity document must be an object")
    _require_exact_keys(
        payload,
        {
            "document_schema_version",
            "source_snapshot_revision",
            "source_snapshot_manifest_digest",
            "identities",
        },
        "expected resource identity document",
    )
    if payload["document_schema_version"] != (
        EXPECTED_RESOURCE_IDENTITY_COLLECTION_DOCUMENT_SCHEMA_VERSION
    ):
        raise ValueError("unsupported expected resource identity document schema")
    if type(payload["source_snapshot_revision"]) is not str:
        raise ValueError("expected resource identity document source revision must be a string")
    if type(payload["source_snapshot_manifest_digest"]) is not str:
        raise ValueError(
            "expected resource identity document source manifest digest must be a string"
        )
    if type(payload["identities"]) is not list:
        raise ValueError("expected resource identity document identities must be an array")

    identities = build_expected_resource_identity_collection(
        tuple(_parse_identity(value) for value in payload["identities"])
    )
    try:
        return build_expected_resource_identity_collection_document(
            source_snapshot_revision=payload["source_snapshot_revision"],
            source_snapshot_manifest_digest=payload[
                "source_snapshot_manifest_digest"
            ],
            identities=identities,
        )
    except ValueError as error:
        raise ValueError("expected resource identity document is invalid") from error


def _parse_identity(value: object) -> ResourcePhysicalIdentity:
    if type(value) is not dict:
        raise ValueError("expected resource identity must be an object")
    _require_exact_keys(
        value,
        {"resource_id", "content_digest"},
        "expected resource identity",
    )
    if type(value["resource_id"]) is not str:
        raise ValueError("expected resource identity resource_id must be a string")
    if type(value["content_digest"]) is not str:
        raise ValueError("expected resource identity content_digest must be a string")
    return ResourcePhysicalIdentity(
        resource_id=value["resource_id"],
        content_digest=value["content_digest"],
    )


def _require_exact_keys(
    payload: dict[str, object],
    expected_keys: set[str],
    name: str,
) -> None:
    if set(payload) != expected_keys:
        raise ValueError(f"{name} must contain exactly its contractual fields")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def _reject_nonstandard_json_constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")
