"""Tests for the read-only active pointer → record → projection chain."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.schemas.content import ContentTreeResponse
from app.services import pedagogical_runtime_activation_documents as documents


def _path(root: Path, family: str, revision: str) -> Path:
    digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    return root / "content" / family / f"sha256-{digest}.json"


def _write_chain(
    tmp_path: Path,
    *,
    pointer_revision: str = "activation-current",
    record_revision: str = "activation-current",
) -> tuple[
    Path,
    documents.ActiveRuntimePointerDocumentV1,
    documents.RuntimeActivationRecordDocumentV1,
    documents.RuntimeContentProjectionDocumentV1,
]:
    root = tmp_path / "repository"
    (root / "content/runtime-activations").mkdir(parents=True)
    (root / "content/runtime-projections").mkdir()
    projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="source-current",
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=ContentTreeResponse(levels=[]),
    )
    record = documents.build_runtime_activation_record_document(
        activation_revision=record_revision,
        projection_document=projection,
        previous_activation_revision=None,
    )
    pointer = documents.build_active_runtime_pointer_document(activation_record=record)
    if pointer_revision != record_revision:
        pointer = documents.ActiveRuntimePointerDocumentV1(
            activation_revision=pointer_revision,
            activation_record_digest=pointer.activation_record_digest,
        )
    _path(root, "runtime-projections", projection.source_snapshot_revision).write_bytes(
        documents.serialize_runtime_content_projection_document(projection)
    )
    _path(root, "runtime-activations", pointer_revision).write_bytes(
        documents.serialize_runtime_activation_record_document(record)
    )
    (root / "content/runtime-active.json").write_bytes(
        documents.serialize_active_runtime_pointer_document(pointer)
    )
    return root, pointer, record, projection


def test_acquires_one_fully_linked_chain_and_reads_pointer_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root, pointer, record, projection = _write_chain(tmp_path)
    reads: list[Path] = []
    original_read = documents._read_file_once

    def record_read(path: Path) -> bytes:
        reads.append(path)
        return original_read(path)

    monkeypatch.setattr(documents, "_read_file_once", record_read)

    chain = documents.acquire_active_runtime_document_chain(root)

    assert chain.pointer_document == pointer
    assert chain.activation_record_document == record
    assert chain.projection_document == projection
    assert reads == [
        root / "content/runtime-active.json",
        _path(root, "runtime-activations", record.activation_revision),
        _path(root, "runtime-projections", projection.source_snapshot_revision),
    ]


def test_rejects_pointer_with_incorrect_record_digest(tmp_path: Path) -> None:
    root, pointer, _, _ = _write_chain(tmp_path)
    invalid = documents.ActiveRuntimePointerDocumentV1(
        activation_revision=pointer.activation_revision,
        activation_record_digest="sha256:" + "f" * 64,
    )
    (root / "content/runtime-active.json").write_bytes(
        documents.serialize_active_runtime_pointer_document(invalid)
    )

    with pytest.raises(ValueError, match="activation record digest mismatch"):
        documents.acquire_active_runtime_document_chain(root)


def test_rejects_missing_referenced_record(tmp_path: Path) -> None:
    root, _, record, _ = _write_chain(tmp_path)
    _path(root, "runtime-activations", record.activation_revision).unlink()

    with pytest.raises(ValueError, match="runtime activation record document path must exist"):
        documents.acquire_active_runtime_document_chain(root)


def test_rejects_pointer_record_identity_conflict(tmp_path: Path) -> None:
    root, _, _, _ = _write_chain(
        tmp_path,
        pointer_revision="activation-pointer",
        record_revision="activation-record",
    )

    with pytest.raises(ValueError, match="activation revision mismatch"):
        documents.acquire_active_runtime_document_chain(root)


def test_rejects_missing_referenced_projection(tmp_path: Path) -> None:
    root, _, _, projection = _write_chain(tmp_path)
    _path(root, "runtime-projections", projection.source_snapshot_revision).unlink()

    with pytest.raises(ValueError, match="runtime projection document path must exist"):
        documents.acquire_active_runtime_document_chain(root)
