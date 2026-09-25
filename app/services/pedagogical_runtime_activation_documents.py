"""Persist and acquire source-bound runtime projection activation documents."""

from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from app.schemas.content import ContentTreeResponse


RUNTIME_DOCUMENT_SCHEMA_VERSION = "1.0"
_SHA256_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class RuntimeContentProjectionDocumentV1:
    """One immutable runtime tree projection bound to one source snapshot."""

    source_snapshot_revision: str
    source_snapshot_manifest_digest: str
    runtime_projection_digest: str
    content_tree: ContentTreeResponse


@dataclass(frozen=True)
class RuntimeActivationRecordDocumentV1:
    """One immutable append-only transition to a runtime projection."""

    activation_revision: str
    source_snapshot_revision: str
    source_snapshot_manifest_digest: str
    runtime_projection_revision: str
    runtime_projection_digest: str
    previous_activation_revision: str | None


@dataclass(frozen=True)
class ActiveRuntimePointerDocumentV1:
    """The small mutable selector for one immutable activation record."""

    activation_revision: str
    activation_record_digest: str


def build_runtime_content_projection_document(
    *,
    source_snapshot_revision: str,
    source_snapshot_manifest_digest: str,
    content_tree: ContentTreeResponse,
) -> RuntimeContentProjectionDocumentV1:
    """Build a source-bound immutable runtime projection document value."""

    _require_nonblank_string(source_snapshot_revision, "source_snapshot_revision")
    _require_digest(source_snapshot_manifest_digest, "source_snapshot_manifest_digest")
    if not isinstance(content_tree, ContentTreeResponse):
        raise ValueError("content_tree must be a ContentTreeResponse")
    runtime_projection_digest = _digest(serialize_runtime_content_tree(content_tree))
    return RuntimeContentProjectionDocumentV1(
        source_snapshot_revision=source_snapshot_revision,
        source_snapshot_manifest_digest=source_snapshot_manifest_digest,
        runtime_projection_digest=runtime_projection_digest,
        content_tree=content_tree,
    )


def build_runtime_activation_record_document(
    *,
    activation_revision: str,
    projection_document: RuntimeContentProjectionDocumentV1,
    previous_activation_revision: str | None,
) -> RuntimeActivationRecordDocumentV1:
    """Build a transition record linked exactly to one projection document."""

    _require_nonblank_string(activation_revision, "activation_revision")
    if not isinstance(projection_document, RuntimeContentProjectionDocumentV1):
        raise ValueError(
            "projection_document must be a RuntimeContentProjectionDocumentV1"
        )
    _validate_projection_document(projection_document)
    if previous_activation_revision is not None:
        _require_nonblank_string(
            previous_activation_revision,
            "previous_activation_revision",
        )
        if previous_activation_revision == activation_revision:
            raise ValueError("previous_activation_revision must differ from activation_revision")
    return RuntimeActivationRecordDocumentV1(
        activation_revision=activation_revision,
        source_snapshot_revision=projection_document.source_snapshot_revision,
        source_snapshot_manifest_digest=(
            projection_document.source_snapshot_manifest_digest
        ),
        runtime_projection_revision=projection_document.source_snapshot_revision,
        runtime_projection_digest=projection_document.runtime_projection_digest,
        previous_activation_revision=previous_activation_revision,
    )


def build_active_runtime_pointer_document(
    *,
    activation_record: RuntimeActivationRecordDocumentV1,
) -> ActiveRuntimePointerDocumentV1:
    """Build the mutable pointer to one canonical activation record."""

    if not isinstance(activation_record, RuntimeActivationRecordDocumentV1):
        raise ValueError(
            "activation_record must be a RuntimeActivationRecordDocumentV1"
        )
    _validate_activation_record_document(activation_record)
    return ActiveRuntimePointerDocumentV1(
        activation_revision=activation_record.activation_revision,
        activation_record_digest=_digest(
            serialize_runtime_activation_record_document(activation_record)
        ),
    )


def serialize_runtime_content_tree(content_tree: ContentTreeResponse) -> bytes:
    """Serialize the runtime tree portion used by projection digest v1."""

    if not isinstance(content_tree, ContentTreeResponse):
        raise ValueError("content_tree must be a ContentTreeResponse")
    return _canonical_json_bytes(content_tree.model_dump(mode="json"))


def serialize_runtime_content_projection_document(
    document: RuntimeContentProjectionDocumentV1,
) -> bytes:
    """Serialize a complete immutable projection document as canonical bytes."""

    _validate_projection_document(document)
    return _canonical_json_bytes(
        {
            "document_schema_version": RUNTIME_DOCUMENT_SCHEMA_VERSION,
            "source_snapshot_revision": document.source_snapshot_revision,
            "source_snapshot_manifest_digest": (
                document.source_snapshot_manifest_digest
            ),
            "runtime_projection_digest": document.runtime_projection_digest,
            "content_tree": document.content_tree.model_dump(mode="json"),
        }
    )


def serialize_runtime_activation_record_document(
    document: RuntimeActivationRecordDocumentV1,
) -> bytes:
    """Serialize a complete immutable activation record as canonical bytes."""

    _validate_activation_record_document(document)
    return _canonical_json_bytes(
        {
            "document_schema_version": RUNTIME_DOCUMENT_SCHEMA_VERSION,
            "activation_revision": document.activation_revision,
            "source_snapshot_revision": document.source_snapshot_revision,
            "source_snapshot_manifest_digest": (
                document.source_snapshot_manifest_digest
            ),
            "runtime_projection_revision": document.runtime_projection_revision,
            "runtime_projection_digest": document.runtime_projection_digest,
            "previous_activation_revision": document.previous_activation_revision,
        }
    )


def serialize_active_runtime_pointer_document(
    document: ActiveRuntimePointerDocumentV1,
) -> bytes:
    """Serialize the mutable active pointer as canonical bytes."""

    _validate_active_pointer_document(document)
    return _canonical_json_bytes(
        {
            "document_schema_version": RUNTIME_DOCUMENT_SCHEMA_VERSION,
            "activation_revision": document.activation_revision,
            "activation_record_digest": document.activation_record_digest,
        }
    )


def publish_runtime_content_projection_document(
    document: RuntimeContentProjectionDocumentV1,
    *,
    document_path: Path,
) -> None:
    """Publish one projection immutably: same bytes are idempotent only."""

    _publish_immutable(
        serialize_runtime_content_projection_document(document),
        document_path=document_path,
        name="runtime projection document",
    )


def publish_runtime_activation_record_document(
    document: RuntimeActivationRecordDocumentV1,
    *,
    document_path: Path,
) -> None:
    """Publish one activation record immutably: same bytes are idempotent only."""

    _publish_immutable(
        serialize_runtime_activation_record_document(document),
        document_path=document_path,
        name="runtime activation record document",
    )


def publish_active_runtime_pointer_document(
    document: ActiveRuntimePointerDocumentV1,
    *,
    document_path: Path,
) -> None:
    """Atomically replace the one mutable active-runtime pointer."""

    document_bytes = serialize_active_runtime_pointer_document(document)
    _validate_publish_path(document_path)
    target_identity = _inspect_publish_target(document_path)
    temporary_path: Path | None = None
    replaced = False
    try:
        temporary_path = _write_durable_temporary(document_path, document_bytes)
        if _inspect_publish_target(document_path) != target_identity:
            raise ValueError(
                "active runtime pointer target changed before publication"
            )
        os.replace(temporary_path, document_path)
        replaced = True
        _fsync_directory(document_path.parent)
    except OSError as error:
        if replaced:
            raise OSError(
                "active runtime pointer replacement is visible but durable "
                "directory sync failed"
            ) from error
        raise
    finally:
        if temporary_path is not None and not replaced:
            _cleanup_temporary(temporary_path)


def acquire_runtime_content_projection_document(
    document_path: Path,
) -> RuntimeContentProjectionDocumentV1:
    """Acquire exactly one canonical immutable projection document."""

    document_bytes = _read_document_once(document_path, "runtime projection document")
    document = _parse_runtime_content_projection_document(document_bytes)
    if serialize_runtime_content_projection_document(document) != document_bytes:
        raise ValueError("runtime projection document is not byte-conformant with v1")
    return document


def acquire_runtime_activation_record_document(
    document_path: Path,
    *,
    projection_document: RuntimeContentProjectionDocumentV1,
) -> RuntimeActivationRecordDocumentV1:
    """Acquire one record and require its exact cross-link to a projection."""

    if not isinstance(projection_document, RuntimeContentProjectionDocumentV1):
        raise ValueError(
            "projection_document must be a RuntimeContentProjectionDocumentV1"
        )
    _validate_projection_document(projection_document)
    document_bytes = _read_document_once(document_path, "runtime activation record document")
    document = _parse_runtime_activation_record_document(document_bytes)
    if serialize_runtime_activation_record_document(document) != document_bytes:
        raise ValueError("runtime activation record document is not byte-conformant with v1")
    if document.source_snapshot_revision != projection_document.source_snapshot_revision:
        raise ValueError("runtime activation record source revision mismatch")
    if (
        document.source_snapshot_manifest_digest
        != projection_document.source_snapshot_manifest_digest
    ):
        raise ValueError("runtime activation record source manifest digest mismatch")
    if document.runtime_projection_revision != projection_document.source_snapshot_revision:
        raise ValueError("runtime activation record projection revision mismatch")
    if document.runtime_projection_digest != projection_document.runtime_projection_digest:
        raise ValueError("runtime activation record projection digest mismatch")
    return document


def acquire_active_runtime_pointer_document(
    document_path: Path,
    *,
    activation_record: RuntimeActivationRecordDocumentV1,
) -> ActiveRuntimePointerDocumentV1:
    """Acquire one pointer and require its exact link to one record."""

    if not isinstance(activation_record, RuntimeActivationRecordDocumentV1):
        raise ValueError(
            "activation_record must be a RuntimeActivationRecordDocumentV1"
        )
    _validate_activation_record_document(activation_record)
    document_bytes = _read_document_once(document_path, "active runtime pointer document")
    document = _parse_active_runtime_pointer_document(document_bytes)
    if serialize_active_runtime_pointer_document(document) != document_bytes:
        raise ValueError("active runtime pointer document is not byte-conformant with v1")
    if document.activation_revision != activation_record.activation_revision:
        raise ValueError("active runtime pointer activation revision mismatch")
    expected_digest = _digest(serialize_runtime_activation_record_document(activation_record))
    if document.activation_record_digest != expected_digest:
        raise ValueError("active runtime pointer activation record digest mismatch")
    return document


def _parse_runtime_content_projection_document(
    document_bytes: bytes,
) -> RuntimeContentProjectionDocumentV1:
    payload = _parse_payload(document_bytes, "runtime projection document")
    _require_exact_keys(
        payload,
        {
            "document_schema_version",
            "source_snapshot_revision",
            "source_snapshot_manifest_digest",
            "runtime_projection_digest",
            "content_tree",
        },
        "runtime projection document",
    )
    _require_schema(payload, "runtime projection document")
    _require_string_field(payload, "source_snapshot_revision", "runtime projection document")
    _require_string_field(
        payload,
        "source_snapshot_manifest_digest",
        "runtime projection document",
    )
    _require_string_field(
        payload,
        "runtime_projection_digest",
        "runtime projection document",
    )
    if type(payload["content_tree"]) is not dict:
        raise ValueError("runtime projection document content_tree must be an object")
    try:
        content_tree = ContentTreeResponse.model_validate(payload["content_tree"])
    except ValueError as error:
        raise ValueError("runtime projection document content_tree is invalid") from error
    return _build_projection_from_parsed(
        source_snapshot_revision=payload["source_snapshot_revision"],
        source_snapshot_manifest_digest=payload["source_snapshot_manifest_digest"],
        runtime_projection_digest=payload["runtime_projection_digest"],
        content_tree=content_tree,
    )


def _parse_runtime_activation_record_document(
    document_bytes: bytes,
) -> RuntimeActivationRecordDocumentV1:
    payload = _parse_payload(document_bytes, "runtime activation record document")
    _require_exact_keys(
        payload,
        {
            "document_schema_version",
            "activation_revision",
            "source_snapshot_revision",
            "source_snapshot_manifest_digest",
            "runtime_projection_revision",
            "runtime_projection_digest",
            "previous_activation_revision",
        },
        "runtime activation record document",
    )
    _require_schema(payload, "runtime activation record document")
    for field in (
        "activation_revision",
        "source_snapshot_revision",
        "source_snapshot_manifest_digest",
        "runtime_projection_revision",
        "runtime_projection_digest",
    ):
        _require_string_field(payload, field, "runtime activation record document")
    previous = payload["previous_activation_revision"]
    if previous is not None and type(previous) is not str:
        raise ValueError(
            "runtime activation record document previous activation revision "
            "must be a string or null"
        )
    document = RuntimeActivationRecordDocumentV1(
        activation_revision=payload["activation_revision"],
        source_snapshot_revision=payload["source_snapshot_revision"],
        source_snapshot_manifest_digest=payload["source_snapshot_manifest_digest"],
        runtime_projection_revision=payload["runtime_projection_revision"],
        runtime_projection_digest=payload["runtime_projection_digest"],
        previous_activation_revision=previous,
    )
    _validate_activation_record_document(document)
    return document


def _parse_active_runtime_pointer_document(
    document_bytes: bytes,
) -> ActiveRuntimePointerDocumentV1:
    payload = _parse_payload(document_bytes, "active runtime pointer document")
    _require_exact_keys(
        payload,
        {
            "document_schema_version",
            "activation_revision",
            "activation_record_digest",
        },
        "active runtime pointer document",
    )
    _require_schema(payload, "active runtime pointer document")
    _require_string_field(payload, "activation_revision", "active runtime pointer document")
    _require_string_field(
        payload,
        "activation_record_digest",
        "active runtime pointer document",
    )
    document = ActiveRuntimePointerDocumentV1(
        activation_revision=payload["activation_revision"],
        activation_record_digest=payload["activation_record_digest"],
    )
    _validate_active_pointer_document(document)
    return document


def _build_projection_from_parsed(
    *,
    source_snapshot_revision: str,
    source_snapshot_manifest_digest: str,
    runtime_projection_digest: str,
    content_tree: ContentTreeResponse,
) -> RuntimeContentProjectionDocumentV1:
    document = RuntimeContentProjectionDocumentV1(
        source_snapshot_revision=source_snapshot_revision,
        source_snapshot_manifest_digest=source_snapshot_manifest_digest,
        runtime_projection_digest=runtime_projection_digest,
        content_tree=content_tree,
    )
    _validate_projection_document(document)
    return document


def _validate_projection_document(document: RuntimeContentProjectionDocumentV1) -> None:
    if not isinstance(document, RuntimeContentProjectionDocumentV1):
        raise ValueError("document must be a RuntimeContentProjectionDocumentV1")
    _require_nonblank_string(document.source_snapshot_revision, "source_snapshot_revision")
    _require_digest(document.source_snapshot_manifest_digest, "source_snapshot_manifest_digest")
    _require_digest(document.runtime_projection_digest, "runtime_projection_digest")
    if not isinstance(document.content_tree, ContentTreeResponse):
        raise ValueError("content_tree must be a ContentTreeResponse")
    if document.runtime_projection_digest != _digest(
        serialize_runtime_content_tree(document.content_tree)
    ):
        raise ValueError("runtime_projection_digest must match canonical content_tree bytes")


def _validate_activation_record_document(
    document: RuntimeActivationRecordDocumentV1,
) -> None:
    if not isinstance(document, RuntimeActivationRecordDocumentV1):
        raise ValueError("document must be a RuntimeActivationRecordDocumentV1")
    _require_nonblank_string(document.activation_revision, "activation_revision")
    _require_nonblank_string(document.source_snapshot_revision, "source_snapshot_revision")
    _require_digest(document.source_snapshot_manifest_digest, "source_snapshot_manifest_digest")
    _require_nonblank_string(
        document.runtime_projection_revision,
        "runtime_projection_revision",
    )
    _require_digest(document.runtime_projection_digest, "runtime_projection_digest")
    if document.previous_activation_revision is not None:
        _require_nonblank_string(
            document.previous_activation_revision,
            "previous_activation_revision",
        )
        if document.previous_activation_revision == document.activation_revision:
            raise ValueError("previous_activation_revision must differ from activation_revision")


def _validate_active_pointer_document(document: ActiveRuntimePointerDocumentV1) -> None:
    if not isinstance(document, ActiveRuntimePointerDocumentV1):
        raise ValueError("document must be an ActiveRuntimePointerDocumentV1")
    _require_nonblank_string(document.activation_revision, "activation_revision")
    _require_digest(document.activation_record_digest, "activation_record_digest")


def _publish_immutable(document_bytes: bytes, *, document_path: Path, name: str) -> None:
    _validate_publish_path(document_path)
    if document_path.exists():
        existing_bytes = _read_file_once(document_path)
        if existing_bytes == document_bytes:
            return
        raise ValueError(f"{name} immutable target already exists with different bytes")

    temporary_path: Path | None = None
    try:
        temporary_path = _write_durable_temporary(document_path, document_bytes)
        try:
            os.link(temporary_path, document_path)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise
            _validate_existing_regular_path(document_path)
            if _read_file_once(document_path) != document_bytes:
                raise ValueError(
                    f"{name} immutable target already exists with different bytes"
                ) from error
            return
        try:
            _fsync_directory(document_path.parent)
        except OSError as error:
            raise OSError(
                f"{name} immutable publication is visible but durable directory "
                "sync failed"
            ) from error
    finally:
        if temporary_path is not None:
            _cleanup_temporary(temporary_path)


def _validate_publish_path(document_path: Path) -> None:
    if not isinstance(document_path, Path):
        raise ValueError("document_path must be a Path")
    if not document_path.is_absolute():
        raise ValueError("document_path must be absolute")
    if not document_path.parent.exists() or not document_path.parent.is_dir():
        raise ValueError("document_path parent must be an existing directory")


def _validate_existing_regular_path(document_path: Path) -> None:
    if document_path.is_symlink() or not document_path.is_file():
        raise ValueError("document_path target must be a regular non-symlink file")


def _read_document_once(document_path: Path, name: str) -> bytes:
    if not isinstance(document_path, Path):
        raise ValueError("document_path must be a Path")
    if not document_path.is_absolute():
        raise ValueError("document_path must be absolute")
    try:
        return _read_file_once(document_path)
    except FileNotFoundError as error:
        raise ValueError(f"{name} path must exist") from error
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise ValueError(f"{name} path must not be a symlink") from error
        raise


def _read_file_once(document_path: Path) -> bytes:
    descriptor = _open_nofollow(document_path)
    try:
        descriptor_status = os.fstat(descriptor)
        if not stat.S_ISREG(descriptor_status.st_mode):
            raise ValueError("document_path target must be a regular file")
        with os.fdopen(descriptor, "rb") as source_file:
            descriptor = -1
            return source_file.read()
    finally:
        if descriptor != -1:
            os.close(descriptor)


def _inspect_publish_target(document_path: Path) -> tuple[int, int] | None:
    """Return one existing regular target identity without following symlinks."""

    try:
        descriptor = _open_nofollow(document_path)
    except FileNotFoundError:
        return None
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise ValueError("document_path target must not be a symlink") from error
        raise
    try:
        descriptor_status = os.fstat(descriptor)
        if not stat.S_ISREG(descriptor_status.st_mode):
            raise ValueError(
                "document_path target must be nonexistent or a regular file"
            )
        return (descriptor_status.st_dev, descriptor_status.st_ino)
    finally:
        os.close(descriptor)


def _open_nofollow(document_path: Path) -> int:
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    return os.open(document_path, flags)


def _write_durable_temporary(document_path: Path, document_bytes: bytes) -> Path:
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
    return temporary_path


def _cleanup_temporary(temporary_path: Path) -> None:
    try:
        temporary_path.unlink()
    except FileNotFoundError:
        pass


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _parse_payload(document_bytes: bytes, name: str) -> dict[str, object]:
    if not isinstance(document_bytes, bytes):
        raise ValueError(f"{name} bytes must be bytes")
    try:
        text = document_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{name} must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError(f"{name} must not contain a UTF-8 BOM")
    try:
        payload = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (TypeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"{name} must be valid JSON") from error
    if type(payload) is not dict:
        raise ValueError(f"{name} must be an object")
    return payload


def _canonical_json_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def _digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _require_nonblank_string(value: object, name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a non-blank string")


def _require_digest(value: object, name: str) -> None:
    if type(value) is not str or _SHA256_DIGEST_PATTERN.fullmatch(value) is None:
        raise ValueError(f"{name} must be a SHA-256 digest")


def _require_exact_keys(
    payload: dict[str, object], expected_keys: set[str], name: str
) -> None:
    if set(payload) != expected_keys:
        raise ValueError(f"{name} must contain exactly its contractual fields")


def _require_schema(payload: dict[str, object], name: str) -> None:
    if payload["document_schema_version"] != RUNTIME_DOCUMENT_SCHEMA_VERSION:
        raise ValueError(f"unsupported {name} schema")


def _require_string_field(payload: dict[str, object], field: str, name: str) -> None:
    if type(payload[field]) is not str:
        raise ValueError(f"{name} {field} must be a string")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate JSON key: {key}")
        payload[key] = value
    return payload


def _reject_nonstandard_json_constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")
