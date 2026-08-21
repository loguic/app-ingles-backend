"""Serialize and atomically publish active candidate source manifests.

Serializa y publica atómicamente manifests de la source activa de candidatos.
"""

import json
import os
from pathlib import Path
import tempfile

from app.services.pedagogical_active_candidate_source_snapshot import (
    ActiveCandidateSourceSnapshot,
)


MANIFEST_SCHEMA_VERSION = "1.0"


def serialize_active_candidate_source_snapshot_manifest(
    snapshot: ActiveCandidateSourceSnapshot,
) -> bytes:
    """Serialize one logical snapshot as the deterministic manifest v1 bytes.

    Serializa un snapshot lógico como bytes deterministas del manifest v1.
    """

    if not isinstance(snapshot, ActiveCandidateSourceSnapshot):
        raise ValueError("snapshot must be an ActiveCandidateSourceSnapshot")

    memberships = []
    for membership in snapshot.collection.memberships:
        identity = membership.identity
        memberships.append(
            {
                "identity": {
                    "unit_id": identity.unit_id,
                    "candidate_revision": identity.candidate_revision,
                    "payload_schema_version": identity.payload_schema_version,
                    "content_digest": identity.content_digest,
                },
                "admission_id": membership.admission_id,
            }
        )

    document = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "snapshot_revision": snapshot.snapshot_revision,
        "memberships": memberships,
    }
    return json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def publish_active_candidate_source_snapshot_manifest(
    snapshot: ActiveCandidateSourceSnapshot,
    *,
    manifest_path: Path,
) -> None:
    """Atomically replace one local active manifest with a complete document.

    Sustituye atómicamente un manifest activo local por un documento completo.
    """

    _validate_manifest_path(manifest_path)
    manifest_bytes = serialize_active_candidate_source_snapshot_manifest(snapshot)
    temporary_path: Path | None = None
    replaced = False

    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{manifest_path.name}.",
            suffix=".tmp",
            dir=manifest_path.parent,
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(manifest_bytes)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, manifest_path)
        replaced = True
        _fsync_directory(manifest_path.parent)
    except OSError as error:
        if replaced:
            raise OSError(
                "manifest replacement is visible but durable directory sync failed"
            ) from error
        raise
    finally:
        if temporary_path is not None and not replaced:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _validate_manifest_path(manifest_path: Path) -> None:
    if not isinstance(manifest_path, Path):
        raise ValueError("manifest_path must be a Path")
    if not manifest_path.is_absolute():
        raise ValueError("manifest_path must be absolute")
    if not manifest_path.parent.exists() or not manifest_path.parent.is_dir():
        raise ValueError("manifest_path parent must be an existing directory")
    if manifest_path.is_symlink():
        raise ValueError("manifest_path target must not be a symlink")
    if manifest_path.exists() and not manifest_path.is_file():
        raise ValueError(
            "manifest_path target must be nonexistent or a regular file"
        )


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
