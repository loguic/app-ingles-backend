"""Tests for the read-only active runtime selection seam."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from app.schemas.content import ContentTreeResponse, Level, Unit
from app.services import content_service
from app.services import pedagogical_runtime_activation_documents as documents
from app.services import pedagogical_runtime_selection_seam as selection_seam


def _path(root: Path, family: str, revision: str) -> Path:
    digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    return root / "content" / family / f"sha256-{digest}.json"


def _write_valid_chain(tmp_path: Path) -> tuple[Path, ContentTreeResponse]:
    root = tmp_path / "repository"
    (root / "content/runtime-activations").mkdir(parents=True)
    (root / "content/runtime-projections").mkdir()
    content_tree = ContentTreeResponse(
        levels=[Level(code="A1", units=[Unit(id="selected-unit", title="Selected")])]
    )
    projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="source-selected",
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=content_tree,
    )
    record = documents.build_runtime_activation_record_document(
        activation_revision="activation-selected",
        projection_document=projection,
        previous_activation_revision=None,
    )
    pointer = documents.build_active_runtime_pointer_document(activation_record=record)
    _path(root, "runtime-projections", projection.source_snapshot_revision).write_bytes(
        documents.serialize_runtime_content_projection_document(projection)
    )
    _path(root, "runtime-activations", record.activation_revision).write_bytes(
        documents.serialize_runtime_activation_record_document(record)
    )
    (root / "content/runtime-active.json").write_bytes(
        documents.serialize_active_runtime_pointer_document(pointer)
    )
    return root, content_tree


def test_returns_none_when_the_explicit_root_has_no_pointer(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()

    assert selection_seam.select_active_runtime_content_tree(root) is None


def test_content_service_legacy_tree_remains_the_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    legacy_path = tmp_path / "content_tree.json"
    legacy_path.write_bytes(content_service.CONTENT_TREE_PATH.read_bytes())
    monkeypatch.setattr(content_service, "CONTENT_TREE_PATH", legacy_path)

    legacy_tree = content_service.build_content_tree()

    assert legacy_tree.model_dump(mode="json") == ContentTreeResponse.model_validate_json(
        legacy_path.read_bytes()
    ).model_dump(mode="json")


def test_content_service_explicit_selection_returns_none_without_a_pointer(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()

    assert content_service.select_active_runtime_content_tree(root) is None


def test_returns_only_the_verified_projection_from_one_chain_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root, expected_tree = _write_valid_chain(tmp_path)
    calls: list[Path] = []
    original_acquire = selection_seam.acquire_active_runtime_document_chain

    def acquire_once(repository_root: Path):
        calls.append(repository_root)
        return original_acquire(repository_root)

    monkeypatch.setattr(selection_seam, "acquire_active_runtime_document_chain", acquire_once)

    selected_tree = selection_seam.select_active_runtime_content_tree(root)

    assert selected_tree == expected_tree
    assert selected_tree.levels[0].units[0].id == "selected-unit"
    assert calls == [root]


def test_content_service_explicit_selection_returns_the_verified_projection(
    tmp_path: Path,
) -> None:
    root, expected_tree = _write_valid_chain(tmp_path)

    assert content_service.select_active_runtime_content_tree(root) == expected_tree


def test_rejects_a_present_pointer_with_an_inconsistent_chain(tmp_path: Path) -> None:
    root, _ = _write_valid_chain(tmp_path)
    pointer_path = root / "content/runtime-active.json"
    pointer = documents._parse_active_runtime_pointer_document(pointer_path.read_bytes())
    invalid_pointer = documents.ActiveRuntimePointerDocumentV1(
        activation_revision=pointer.activation_revision,
        activation_record_digest="sha256:" + "f" * 64,
    )
    pointer_path.write_bytes(documents.serialize_active_runtime_pointer_document(invalid_pointer))

    with pytest.raises(ValueError, match="activation record digest mismatch"):
        selection_seam.select_active_runtime_content_tree(root)


def test_content_service_explicit_selection_propagates_an_invalid_pointer(
    tmp_path: Path,
) -> None:
    root, _ = _write_valid_chain(tmp_path)
    pointer_path = root / "content/runtime-active.json"
    pointer = documents._parse_active_runtime_pointer_document(pointer_path.read_bytes())
    pointer_path.write_bytes(
        documents.serialize_active_runtime_pointer_document(
            documents.ActiveRuntimePointerDocumentV1(
                activation_revision=pointer.activation_revision,
                activation_record_digest="sha256:" + "f" * 64,
            )
        )
    )

    with pytest.raises(ValueError, match="activation record digest mismatch"):
        content_service.select_active_runtime_content_tree(root)


def test_historical_a1_v2_resolution_remains_available_from_a_temporary_archive(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    archive = tmp_path / "a1-u1-l1-2.0.json"
    archive.write_bytes(content_service.HISTORICAL_A1_U1_L1_V2_PATH.read_bytes())
    monkeypatch.setattr(content_service, "HISTORICAL_A1_U1_L1_V2_PATH", archive)
    monkeypatch.setattr(content_service, "get_lesson_context_by_id", lambda _: None)

    level_id, unit_id, lesson = (
        content_service.get_lesson_context_by_id_and_contract_version("a1-u1-l1", "2.0")
    )

    assert (level_id, unit_id, lesson.id) == ("A1", "a1-u1", "a1-u1-l1")
    assert lesson.experience is not None
    assert lesson.experience.contract_version == "2.0"
