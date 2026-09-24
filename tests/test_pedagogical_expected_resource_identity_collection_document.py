"""Tests for durable expected-resource identity documents v1."""

from dataclasses import FrozenInstanceError, fields
import hashlib
from pathlib import Path

import pytest

import app.services.pedagogical_expected_resource_identity_collection_document as document_module
from app.services.pedagogical_expected_resource_identity_collection import (
    build_expected_resource_identity_collection,
)
from app.services.pedagogical_resource_physical_identity import (
    ResourcePhysicalIdentity,
)


def _digest(character: str = "a") -> str:
    return "sha256:" + character * 64


def _document(
    identities: tuple[ResourcePhysicalIdentity, ...] = (
        ResourcePhysicalIdentity("resource-1", _digest()),
    ),
):
    return document_module.build_expected_resource_identity_collection_document(
        source_snapshot_revision="source-r1",
        source_snapshot_manifest_digest=_digest("b"),
        identities=build_expected_resource_identity_collection(identities),
    )


def test_document_shape_is_frozen_and_serialization_is_deterministic() -> None:
    document = _document(
        (
            ResourcePhysicalIdentity("  Resource ", _digest()),
            ResourcePhysicalIdentity("resource-2", _digest()),
        )
    )

    assert [field.name for field in fields(document)] == [
        "source_snapshot_revision",
        "source_snapshot_manifest_digest",
        "identities",
    ]
    assert document.identities.identities[0].resource_id == "  Resource "
    with pytest.raises(FrozenInstanceError):
        document.source_snapshot_revision = "other"  # type: ignore[misc]

    expected = (
        b'{"document_schema_version":"1.0",'
        b'"source_snapshot_revision":"source-r1",'
        b'"source_snapshot_manifest_digest":"sha256:' + b"b" * 64 + b'",'
        b'"identities":[{"resource_id":"  Resource ","content_digest":"sha256:'
        + b"a" * 64
        + b'"},{"resource_id":"resource-2","content_digest":"sha256:'
        + b"a" * 64
        + b'"}]}\n'
    )
    assert document_module.serialize_expected_resource_identity_collection_document(
        document
    ) == expected


@pytest.mark.parametrize(
    ("revision", "manifest_digest", "identities", "match"),
    [
        ("", _digest(), (), "source_snapshot_revision"),
        ("   ", _digest(), (), "source_snapshot_revision"),
        ("source-r1", "sha256:UPPER", (), "source_snapshot_manifest_digest"),
        (
            "source-r1",
            _digest(),
            (ResourcePhysicalIdentity("r1", "not-a-digest"),),
            "identity content_digest",
        ),
    ],
)
def test_builder_rejects_invalid_document_values(
    revision: str,
    manifest_digest: str,
    identities: tuple[ResourcePhysicalIdentity, ...],
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        document_module.build_expected_resource_identity_collection_document(
            source_snapshot_revision=revision,
            source_snapshot_manifest_digest=manifest_digest,
            identities=build_expected_resource_identity_collection(identities),
        )


def test_builder_preserves_distinct_ids_with_same_digest_and_rejects_duplicates() -> None:
    shared = _digest()
    document = _document(
        (
            ResourcePhysicalIdentity("r1", shared),
            ResourcePhysicalIdentity("r2", shared),
        )
    )
    assert [item.resource_id for item in document.identities.identities] == ["r1", "r2"]

    with pytest.raises(ValueError, match="duplicate expected resource identity"):
        build_expected_resource_identity_collection(
            (ResourcePhysicalIdentity("r1", shared), ResourcePhysicalIdentity("r1", shared))
        )


def test_builder_rejects_nonstring_resource_id_and_preserves_string_literal() -> None:
    invalid = build_expected_resource_identity_collection(
        (ResourcePhysicalIdentity(7, _digest()),)  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="identity resource_id must be a string"):
        document_module.build_expected_resource_identity_collection_document(
            source_snapshot_revision="source-r1",
            source_snapshot_manifest_digest=_digest("b"),
            identities=invalid,
        )

    document = _document((ResourcePhysicalIdentity("7", _digest()),))
    assert document.identities.identities[0].resource_id == "7"


def test_publication_creates_and_replaces_complete_document(tmp_path: Path) -> None:
    path = tmp_path / "expected.json"
    first = _document()
    second = _document((ResourcePhysicalIdentity("resource-2", _digest("c")),))

    document_module.publish_expected_resource_identity_collection_document(
        first, document_path=path
    )
    assert path.read_bytes() == document_module.serialize_expected_resource_identity_collection_document(first)

    document_module.publish_expected_resource_identity_collection_document(
        second, document_path=path
    )
    assert path.read_bytes() == document_module.serialize_expected_resource_identity_collection_document(second)


@pytest.mark.parametrize("path_value", [Path("relative.json"), object()])
def test_publication_rejects_invalid_paths(path_value: object, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="document_path"):
        document_module.publish_expected_resource_identity_collection_document(
            _document(), document_path=path_value  # type: ignore[arg-type]
        )


def test_publication_rejects_symlink_and_cleans_unpublished_temp_on_replace_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.json"
    target.write_text("target", encoding="utf-8")
    symlink = tmp_path / "expected-link.json"
    symlink.symlink_to(target)
    with pytest.raises(ValueError, match="must not be a symlink"):
        document_module.publish_expected_resource_identity_collection_document(
            _document(), document_path=symlink
        )

    path = tmp_path / "expected.json"
    path.write_text("previous", encoding="utf-8")

    def fail_replace(*args: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(document_module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        document_module.publish_expected_resource_identity_collection_document(
            _document(), document_path=path
        )
    assert path.read_text(encoding="utf-8") == "previous"
    assert list(tmp_path.glob(".expected.json.*.tmp")) == []


def test_publication_reports_visible_replace_when_directory_fsync_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "expected.json"
    monkeypatch.setattr(
        document_module,
        "_fsync_directory",
        lambda directory: (_ for _ in ()).throw(OSError("directory fsync failed")),
    )

    with pytest.raises(OSError, match="visible but durable directory sync failed"):
        document_module.publish_expected_resource_identity_collection_document(
            _document(), document_path=path
        )
    assert path.read_bytes() == document_module.serialize_expected_resource_identity_collection_document(
        _document()
    )


def test_document_manifest_digest_is_explicit_sha256_not_derived_from_resources() -> None:
    document = _document()
    serialized = document_module.serialize_expected_resource_identity_collection_document(
        document
    )
    assert hashlib.sha256(serialized).hexdigest()
    assert b"resource_path" not in serialized
    assert b"resource_bytes" not in serialized
