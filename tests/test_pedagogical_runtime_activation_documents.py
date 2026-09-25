"""Tests for runtime projection, activation record, and pointer documents v1."""

from dataclasses import FrozenInstanceError, fields
import hashlib
import json
from pathlib import Path
import os

import pytest

import app.services.pedagogical_runtime_activation_documents as documents
from app.schemas.content import ContentTreeResponse, Level, Unit


def _digest(character: str = "a") -> str:
    return "sha256:" + character * 64


def _tree() -> ContentTreeResponse:
    return ContentTreeResponse(
        levels=[
            Level(
                code="A1",
                units=[Unit(id="a1-u1", title="New unit", lessons=[])],
            )
        ]
    )


def _projection() -> documents.RuntimeContentProjectionDocumentV1:
    return documents.build_runtime_content_projection_document(
        source_snapshot_revision="active-candidate-source-002",
        source_snapshot_manifest_digest=_digest("b"),
        content_tree=_tree(),
    )


def _record() -> documents.RuntimeActivationRecordDocumentV1:
    return documents.build_runtime_activation_record_document(
        activation_revision="runtime-activation-001",
        projection_document=_projection(),
        previous_activation_revision=None,
    )


def _pointer() -> documents.ActiveRuntimePointerDocumentV1:
    return documents.build_active_runtime_pointer_document(activation_record=_record())


def test_documents_are_frozen_and_have_exact_minimal_shapes() -> None:
    projection = _projection()
    record = _record()
    pointer = _pointer()

    assert [field.name for field in fields(projection)] == [
        "source_snapshot_revision",
        "source_snapshot_manifest_digest",
        "runtime_projection_digest",
        "content_tree",
    ]
    assert [field.name for field in fields(record)] == [
        "activation_revision",
        "source_snapshot_revision",
        "source_snapshot_manifest_digest",
        "runtime_projection_revision",
        "runtime_projection_digest",
        "previous_activation_revision",
    ]
    assert [field.name for field in fields(pointer)] == [
        "activation_revision",
        "activation_record_digest",
    ]
    with pytest.raises(FrozenInstanceError):
        pointer.activation_revision = "other"  # type: ignore[misc]


def test_canonical_serialization_and_cross_links_round_trip(tmp_path: Path) -> None:
    projection = _projection()
    record = _record()
    pointer = _pointer()
    projection_bytes = documents.serialize_runtime_content_projection_document(projection)
    record_bytes = documents.serialize_runtime_activation_record_document(record)
    pointer_bytes = documents.serialize_active_runtime_pointer_document(pointer)

    assert projection_bytes == (
        b'{"document_schema_version":"1.0",'
        b'"source_snapshot_revision":"active-candidate-source-002",'
        b'"source_snapshot_manifest_digest":"sha256:'
        + b"b" * 64
        + b'","runtime_projection_digest":"'
        + projection.runtime_projection_digest.encode("ascii")
        + b'","content_tree":{"levels":[{"code":"A1","units":['
        b'{"id":"a1-u1","title":"New unit","lessons":[]}]}]}}\n'
    )
    assert projection_bytes.endswith(b"\n")
    assert projection.runtime_projection_digest == "sha256:" + hashlib.sha256(
        documents.serialize_runtime_content_tree(_tree())
    ).hexdigest()

    projection_path = tmp_path / "projection.json"
    record_path = tmp_path / "record.json"
    pointer_path = tmp_path / "pointer.json"
    projection_path.write_bytes(projection_bytes)
    record_path.write_bytes(record_bytes)
    pointer_path.write_bytes(pointer_bytes)

    acquired_projection = documents.acquire_runtime_content_projection_document(
        projection_path
    )
    acquired_record = documents.acquire_runtime_activation_record_document(
        record_path,
        projection_document=acquired_projection,
    )
    acquired_pointer = documents.acquire_active_runtime_pointer_document(
        pointer_path,
        activation_record=acquired_record,
    )
    assert documents.serialize_runtime_content_projection_document(acquired_projection) == projection_bytes
    assert documents.serialize_runtime_activation_record_document(acquired_record) == record_bytes
    assert documents.serialize_active_runtime_pointer_document(acquired_pointer) == pointer_bytes


@pytest.mark.parametrize(
    ("serializer", "document", "name"),
    [
        (
            documents.serialize_runtime_content_projection_document,
            _projection(),
            "projection",
        ),
        (
            documents.serialize_runtime_activation_record_document,
            _record(),
            "record",
        ),
        (
            documents.serialize_active_runtime_pointer_document,
            _pointer(),
            "pointer",
        ),
    ],
)
def test_parser_rejects_bom_duplicate_unknown_and_noncanonical_bytes(
    serializer: object,
    document: object,
    name: str,
    tmp_path: Path,
) -> None:
    canonical = serializer(document)  # type: ignore[operator]
    variants = (
        b"\xef\xbb\xbf" + canonical,
        canonical.replace(b'"document_schema_version"', b'"unknown":true,"document_schema_version"'),
        canonical[:-1] + b" \n",
    )
    path = tmp_path / f"{name}.json"
    for payload in variants:
        path.write_bytes(payload)
        if name == "projection":
            with pytest.raises(ValueError):
                documents.acquire_runtime_content_projection_document(path)
        elif name == "record":
            with pytest.raises(ValueError):
                documents.acquire_runtime_activation_record_document(
                    path, projection_document=_projection()
                )
        else:
            with pytest.raises(ValueError):
                documents.acquire_active_runtime_pointer_document(
                    path, activation_record=_record()
                )

    duplicate = canonical.replace(
        b'"document_schema_version":"1.0",',
        b'"document_schema_version":"1.0","document_schema_version":"1.0",',
    )
    path.write_bytes(duplicate)
    if name == "projection":
        with pytest.raises(ValueError, match="valid JSON"):
            documents.acquire_runtime_content_projection_document(path)
    elif name == "record":
        with pytest.raises(ValueError, match="valid JSON"):
            documents.acquire_runtime_activation_record_document(
                path, projection_document=_projection()
            )
    else:
        with pytest.raises(ValueError, match="valid JSON"):
            documents.acquire_active_runtime_pointer_document(
                path, activation_record=_record()
            )


def test_projection_builder_rejects_invalid_source_digest_and_tampered_tree_digest() -> None:
    with pytest.raises(ValueError, match="source_snapshot_manifest_digest"):
        documents.build_runtime_content_projection_document(
            source_snapshot_revision="source-r1",
            source_snapshot_manifest_digest="sha256:UPPER",
            content_tree=_tree(),
        )

    projection = _projection()
    tampered = documents.RuntimeContentProjectionDocumentV1(
        source_snapshot_revision=projection.source_snapshot_revision,
        source_snapshot_manifest_digest=projection.source_snapshot_manifest_digest,
        runtime_projection_digest=_digest("f"),
        content_tree=projection.content_tree,
    )
    with pytest.raises(ValueError, match="runtime_projection_digest"):
        documents.serialize_runtime_content_projection_document(tampered)


def test_immutable_projection_and_record_create_idempotently_and_reject_different(
    tmp_path: Path,
) -> None:
    projection_path = tmp_path / "projection.json"
    record_path = tmp_path / "record.json"
    projection = _projection()
    record = _record()

    documents.publish_runtime_content_projection_document(
        projection, document_path=projection_path
    )
    documents.publish_runtime_content_projection_document(
        projection, document_path=projection_path
    )
    assert projection_path.read_bytes() == documents.serialize_runtime_content_projection_document(projection)
    different_projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="active-candidate-source-002",
        source_snapshot_manifest_digest=_digest("b"),
        content_tree=ContentTreeResponse(levels=[]),
    )
    with pytest.raises(ValueError, match="immutable target already exists"):
        documents.publish_runtime_content_projection_document(
            different_projection, document_path=projection_path
        )

    documents.publish_runtime_activation_record_document(record, document_path=record_path)
    documents.publish_runtime_activation_record_document(record, document_path=record_path)
    different_record = documents.build_runtime_activation_record_document(
        activation_revision="runtime-activation-002",
        projection_document=projection,
        previous_activation_revision="runtime-activation-001",
    )
    with pytest.raises(ValueError, match="immutable target already exists"):
        documents.publish_runtime_activation_record_document(
            different_record, document_path=record_path
        )


def test_pointer_replaces_atomically_and_reports_post_replace_fsync_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "runtime-active.json"
    first = _pointer()
    second_record = documents.build_runtime_activation_record_document(
        activation_revision="runtime-activation-002",
        projection_document=_projection(),
        previous_activation_revision="runtime-activation-001",
    )
    second = documents.build_active_runtime_pointer_document(
        activation_record=second_record
    )
    documents.publish_active_runtime_pointer_document(first, document_path=path)
    documents.publish_active_runtime_pointer_document(second, document_path=path)
    assert path.read_bytes() == documents.serialize_active_runtime_pointer_document(second)

    monkeypatch.setattr(
        documents,
        "_fsync_directory",
        lambda directory: (_ for _ in ()).throw(OSError("fsync failed")),
    )
    with pytest.raises(OSError, match="visible but durable directory sync failed"):
        documents.publish_active_runtime_pointer_document(first, document_path=path)
    assert path.read_bytes() == documents.serialize_active_runtime_pointer_document(first)


def test_immutable_publication_reports_visible_target_when_directory_fsync_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "projection.json"
    projection = _projection()
    monkeypatch.setattr(
        documents,
        "_fsync_directory",
        lambda directory: (_ for _ in ()).throw(OSError("fsync failed")),
    )
    with pytest.raises(OSError, match="immutable publication is visible"):
        documents.publish_runtime_content_projection_document(
            projection, document_path=path
        )
    assert path.read_bytes() == documents.serialize_runtime_content_projection_document(
        projection
    )


def test_acquisition_requires_cross_links_and_reads_each_document_once(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    projection = _projection()
    record = _record()
    pointer = _pointer()
    projection_path = tmp_path / "projection.json"
    record_path = tmp_path / "record.json"
    pointer_path = tmp_path / "pointer.json"
    projection_path.write_bytes(documents.serialize_runtime_content_projection_document(projection))
    record_path.write_bytes(documents.serialize_runtime_activation_record_document(record))
    pointer_path.write_bytes(documents.serialize_active_runtime_pointer_document(pointer))
    reads: list[Path] = []
    original_read = documents._read_file_once

    def read_once(path: Path) -> bytes:
        reads.append(path)
        return original_read(path)

    monkeypatch.setattr(documents, "_read_file_once", read_once)
    acquired_projection = documents.acquire_runtime_content_projection_document(projection_path)
    acquired_record = documents.acquire_runtime_activation_record_document(
        record_path, projection_document=acquired_projection
    )
    documents.acquire_active_runtime_pointer_document(
        pointer_path, activation_record=acquired_record
    )
    assert reads == [projection_path, record_path, pointer_path]

    mismatched_record = documents.RuntimeActivationRecordDocumentV1(
        activation_revision=record.activation_revision,
        source_snapshot_revision="other-source",
        source_snapshot_manifest_digest=record.source_snapshot_manifest_digest,
        runtime_projection_revision=record.runtime_projection_revision,
        runtime_projection_digest=record.runtime_projection_digest,
        previous_activation_revision=None,
    )
    record_path.write_bytes(documents.serialize_runtime_activation_record_document(mismatched_record))
    with pytest.raises(ValueError, match="source revision mismatch"):
        documents.acquire_runtime_activation_record_document(
            record_path, projection_document=projection
        )

    bad_pointer = documents.ActiveRuntimePointerDocumentV1(
        activation_revision=pointer.activation_revision,
        activation_record_digest=_digest("f"),
    )
    pointer_path.write_bytes(documents.serialize_active_runtime_pointer_document(bad_pointer))
    with pytest.raises(ValueError, match="activation record digest mismatch"):
        documents.acquire_active_runtime_pointer_document(
            pointer_path, activation_record=record
        )


def test_acquisition_uses_one_nofollow_regular_descriptor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "projection.json"
    path.write_bytes(documents.serialize_runtime_content_projection_document(_projection()))
    original_open = documents.os.open
    original_fstat = documents.os.fstat
    original_fdopen = documents.os.fdopen
    events: list[tuple[str, int]] = []
    captured_flags: list[int] = []

    def track_open(path_value: Path, flags: int) -> int:
        captured_flags.append(flags)
        descriptor = original_open(path_value, flags)
        events.append(("open", descriptor))
        return descriptor

    def track_fstat(descriptor: int):
        events.append(("fstat", descriptor))
        return original_fstat(descriptor)

    def track_fdopen(descriptor: int, mode: str):
        events.append(("fdopen", descriptor))
        return original_fdopen(descriptor, mode)

    monkeypatch.setattr(documents.os, "open", track_open)
    monkeypatch.setattr(documents.os, "fstat", track_fstat)
    monkeypatch.setattr(documents.os, "fdopen", track_fdopen)

    assert documents.acquire_runtime_content_projection_document(path) == _projection()
    assert [event for event, _ in events] == ["open", "fstat", "fdopen"]
    assert len({descriptor for _, descriptor in events}) == 1
    assert captured_flags[0] & os.O_NOFOLLOW
    assert captured_flags[0] & os.O_NONBLOCK


def test_acquisition_rejects_final_symlink_nonregular_and_open_time_swap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    canonical = documents.serialize_runtime_content_projection_document(_projection())
    target = tmp_path / "target.json"
    target.write_bytes(canonical)
    symlink = tmp_path / "projection-link.json"
    symlink.symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        documents.acquire_runtime_content_projection_document(symlink)

    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="regular file"):
        documents.acquire_runtime_content_projection_document(directory)

    raced = tmp_path / "raced.json"
    raced.write_bytes(canonical)
    original_open = documents.os.open

    def swap_before_open(path_value: Path, flags: int) -> int:
        if path_value == raced:
            raced.unlink()
            raced.symlink_to(target)
        return original_open(path_value, flags)

    monkeypatch.setattr(documents.os, "open", swap_before_open)
    with pytest.raises(ValueError, match="symlink"):
        documents.acquire_runtime_content_projection_document(raced)


def test_pointer_publication_rejects_target_swap_without_partial_publication(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / "runtime-active.json"
    documents.publish_active_runtime_pointer_document(
        _pointer(), document_path=pointer_path
    )
    victim = tmp_path / "victim.json"
    victim.write_bytes(b"must remain unchanged")
    original_write_temporary = documents._write_durable_temporary
    replace_calls: list[tuple[Path, Path]] = []

    def write_then_swap(path: Path, payload: bytes) -> Path:
        temporary = original_write_temporary(path, payload)
        pointer_path.unlink()
        pointer_path.symlink_to(victim)
        return temporary

    def track_replace(source: Path, target: Path) -> None:
        replace_calls.append((source, target))

    monkeypatch.setattr(documents, "_write_durable_temporary", write_then_swap)
    monkeypatch.setattr(documents.os, "replace", track_replace)

    with pytest.raises(ValueError, match="symlink"):
        documents.publish_active_runtime_pointer_document(
            _pointer(), document_path=pointer_path
        )
    assert replace_calls == []
    assert victim.read_bytes() == b"must remain unchanged"
    assert list(tmp_path.glob(".runtime-active.json.*.tmp")) == []


def test_pointer_publication_rejects_nonregular_target_without_temporary(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / "runtime-active.json"
    pointer_path.mkdir()

    with pytest.raises(ValueError, match="regular file"):
        documents.publish_active_runtime_pointer_document(
            _pointer(), document_path=pointer_path
        )
    assert list(tmp_path.glob(".runtime-active.json.*.tmp")) == []


def test_paths_fail_closed_and_no_runtime_authority_or_activation_dependencies(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="absolute"):
        documents.publish_runtime_content_projection_document(
            _projection(), document_path=Path("relative.json")
        )
    target = tmp_path / "target.json"
    target.write_bytes(b"target")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(ValueError, match="symlink"):
        documents.publish_active_runtime_pointer_document(_pointer(), document_path=link)
    with pytest.raises(ValueError, match="must exist"):
        documents.acquire_runtime_content_projection_document(tmp_path / "missing.json")
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match="regular file"):
        documents.acquire_runtime_content_projection_document(directory)

    source = Path(documents.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "content_service",
        "CONTENT_TREE_PATH",
        "verify_active_candidate_source_integrity",
        "run_active_candidate_source_integrity",
        "B181",
    ):
        assert forbidden not in source


def test_parser_rejects_missing_fields_without_silent_normalization(tmp_path: Path) -> None:
    payload = json.loads(
        documents.serialize_runtime_content_projection_document(_projection())
    )
    del payload["runtime_projection_digest"]
    path = tmp_path / "projection.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly"):
        documents.acquire_runtime_content_projection_document(path)
