"""Acquire local active candidate source evidence without integrity verification.

Adquiere evidencia local de source activa sin verificar todavía su integridad.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Sequence

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    ActiveCandidateSourceSnapshot,
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    MANIFEST_SCHEMA_VERSION,
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


@dataclass(frozen=True)
class ActiveCandidateSourceBinding:
    """Associate one declared unit with one explicit local candidate path.

    Asocia una unidad declarada con un path local explícito de candidate.
    """

    unit_id: str
    candidate_path: Path


@dataclass(frozen=True)
class AcquiredActiveCandidateSourceEntry:
    """Keep one acquired, still-unverified candidate source entry.

    Conserva una entry de source candidate adquirida y aún no verificada.
    """

    membership: ActiveCandidateMembership
    candidate_path: Path
    candidate_bytes: bytes
    candidate: PedagogicalUnitCandidate


@dataclass(frozen=True)
class ActiveCandidateSourceAcquisition:
    """Represent structurally immutable acquired, unverified source evidence.

    Representa evidencia de source adquirida y no verificada, inmutable
    estructuralmente.
    """

    snapshot: ActiveCandidateSourceSnapshot
    entries: tuple[AcquiredActiveCandidateSourceEntry, ...]


def acquire_active_candidate_source(
    manifest_path: Path,
    *,
    candidate_bindings: Sequence[ActiveCandidateSourceBinding],
) -> ActiveCandidateSourceAcquisition:
    """Acquire one complete local source without identity or digest verification.

    Adquiere una source local completa sin verificar todavía identity ni digest.
    """

    _validate_source_file_path(manifest_path, "manifest_path")
    manifest_bytes = _read_file_once(manifest_path)
    snapshot = _parse_manifest(manifest_bytes)
    _require_byte_conformant_manifest(snapshot, manifest_bytes)

    bindings = tuple(candidate_bindings)
    bindings_by_unit_id = _index_bindings(bindings)
    memberships = snapshot.collection.memberships
    declared_unit_ids = {membership.identity.unit_id for membership in memberships}

    for binding in bindings:
        if binding.unit_id not in declared_unit_ids:
            raise ValueError(
                "unexpected active candidate source binding unit_id: "
                + binding.unit_id
            )

    entries: list[AcquiredActiveCandidateSourceEntry] = []
    for membership in memberships:
        unit_id = membership.identity.unit_id
        binding = bindings_by_unit_id.get(unit_id)
        if binding is None:
            raise ValueError(
                "missing active candidate source binding unit_id: " + unit_id
            )

        _validate_source_file_path(binding.candidate_path, "candidate_path")
        candidate_bytes = _read_file_once(binding.candidate_path)
        candidate_document = _parse_json_document(
            candidate_bytes,
            "candidate",
        )
        candidate = PedagogicalUnitCandidate.model_validate(candidate_document)
        entries.append(
            AcquiredActiveCandidateSourceEntry(
                membership=membership,
                candidate_path=binding.candidate_path,
                candidate_bytes=candidate_bytes,
                candidate=candidate,
            )
        )

    return ActiveCandidateSourceAcquisition(
        snapshot=snapshot,
        entries=tuple(entries),
    )


def _validate_source_file_path(path: Path, name: str) -> None:
    if not isinstance(path, Path):
        raise ValueError(f"{name} must be a Path")
    if not path.is_absolute():
        raise ValueError(f"{name} must be absolute")
    if path.is_symlink():
        raise ValueError(f"{name} must not be a symlink")
    if not path.exists():
        raise ValueError(f"{name} must exist")
    if not path.is_file():
        raise ValueError(f"{name} must be a regular file")


def _read_file_once(path: Path) -> bytes:
    with path.open("rb") as source_file:
        return source_file.read()


def _parse_manifest(manifest_bytes: bytes) -> ActiveCandidateSourceSnapshot:
    document = _parse_json_document(manifest_bytes, "manifest")
    if type(document) is not dict:
        raise ValueError("manifest must be an object")
    _require_exact_keys(
        document,
        {
            "manifest_schema_version",
            "snapshot_revision",
            "memberships",
        },
        "manifest",
    )

    manifest_schema_version = document["manifest_schema_version"]
    if manifest_schema_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported active candidate source manifest schema")

    snapshot_revision = document["snapshot_revision"]
    if type(snapshot_revision) is not str:
        raise ValueError("manifest snapshot_revision must be a string")

    membership_documents = document["memberships"]
    if type(membership_documents) is not list:
        raise ValueError("manifest memberships must be an array")

    memberships = tuple(
        _parse_membership(item)
        for item in membership_documents
    )
    collection = build_active_candidate_membership_collection(memberships)
    return build_active_candidate_source_snapshot(
        collection,
        snapshot_revision=snapshot_revision,
    )


def _parse_membership(document: object) -> ActiveCandidateMembership:
    if type(document) is not dict:
        raise ValueError("manifest membership must be an object")
    _require_exact_keys(document, {"identity", "admission_id"}, "membership")

    identity_document = document["identity"]
    if type(identity_document) is not dict:
        raise ValueError("manifest membership identity must be an object")
    _require_exact_keys(
        identity_document,
        {
            "unit_id",
            "candidate_revision",
            "payload_schema_version",
            "content_digest",
        },
        "membership identity",
    )

    values = {
        key: identity_document[key]
        for key in (
            "unit_id",
            "candidate_revision",
            "payload_schema_version",
            "content_digest",
        )
    }
    if any(type(value) is not str for value in values.values()):
        raise ValueError("manifest membership identity values must be strings")

    admission_id = document["admission_id"]
    if type(admission_id) is not str:
        raise ValueError("manifest admission_id must be a string")

    return ActiveCandidateMembership(
        identity=CandidatePayloadIdentity(**values),
        admission_id=admission_id,
    )


def _parse_json_document(raw_bytes: bytes, name: str) -> object:
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{name} must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError(f"{name} must not contain a UTF-8 BOM")

    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (TypeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"{name} must be valid JSON") from error


def _reject_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def _reject_nonstandard_json_constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _require_exact_keys(
    document: dict[str, object],
    expected_keys: set[str],
    name: str,
) -> None:
    if set(document) != expected_keys:
        raise ValueError(f"{name} must contain exactly its contractual fields")


def _require_byte_conformant_manifest(
    snapshot: ActiveCandidateSourceSnapshot,
    manifest_bytes: bytes,
) -> None:
    expected_bytes = serialize_active_candidate_source_snapshot_manifest(snapshot)
    if manifest_bytes != expected_bytes:
        raise ValueError(
            "manifest physical format is not byte-conformant with v1"
        )


def _index_bindings(
    bindings: tuple[ActiveCandidateSourceBinding, ...],
) -> dict[str, ActiveCandidateSourceBinding]:
    bindings_by_unit_id: dict[str, ActiveCandidateSourceBinding] = {}
    for binding in bindings:
        if not isinstance(binding, ActiveCandidateSourceBinding):
            raise ValueError(
                "candidate_bindings must contain ActiveCandidateSourceBinding"
            )
        if type(binding.unit_id) is not str:
            raise ValueError("candidate binding unit_id must be a string")
        if binding.unit_id in bindings_by_unit_id:
            raise ValueError(
                "duplicate active candidate source binding unit_id: "
                + binding.unit_id
            )
        bindings_by_unit_id[binding.unit_id] = binding
    return bindings_by_unit_id
