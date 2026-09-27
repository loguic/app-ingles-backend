"""HTTP coverage for the content router runtime-tree selection adapter."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import content as content_endpoint
from app.main import app
from app.schemas.content import ContentTreeResponse, Lesson, Level, Unit
from app.services import pedagogical_runtime_activation_documents as documents


ROUTES = (
    ("/api/v1/content/tree", "tree"),
    ("/api/v1/content/levels/R1", "level"),
    ("/api/v1/content/levels/R1/units", "units"),
    ("/api/v1/content/units/runtime-unit", "unit"),
    ("/api/v1/content/units/runtime-unit/lessons", "lessons"),
    ("/api/v1/content/lessons/runtime-lesson", "lesson"),
)


def _tree(code: str, unit_id: str, lesson_id: str) -> ContentTreeResponse:
    return ContentTreeResponse(
        levels=[
            Level(
                code=code,
                units=[
                    Unit(
                        id=unit_id,
                        title="Runtime unit",
                        lessons=[Lesson(id=lesson_id, title="Runtime lesson")],
                    )
                ],
            )
        ]
    )


def _document_path(root: Path, family: str, revision: str) -> Path:
    digest = hashlib.sha256(revision.encode("utf-8")).hexdigest()
    return root / "content" / family / f"sha256-{digest}.json"


def _write_runtime_chain(
    tmp_path: Path,
    tree: ContentTreeResponse,
) -> Path:
    root = tmp_path / "repository"
    (root / "content/runtime-activations").mkdir(parents=True)
    (root / "content/runtime-projections").mkdir()
    projection = documents.build_runtime_content_projection_document(
        source_snapshot_revision="runtime-source",
        source_snapshot_manifest_digest="sha256:" + "a" * 64,
        content_tree=tree,
    )
    record = documents.build_runtime_activation_record_document(
        activation_revision="runtime-activation",
        projection_document=projection,
        previous_activation_revision=None,
    )
    pointer = documents.build_active_runtime_pointer_document(activation_record=record)
    _document_path(root, "runtime-projections", projection.source_snapshot_revision).write_bytes(
        documents.serialize_runtime_content_projection_document(projection)
    )
    _document_path(root, "runtime-activations", record.activation_revision).write_bytes(
        documents.serialize_runtime_activation_record_document(record)
    )
    (root / "content/runtime-active.json").write_bytes(
        documents.serialize_active_runtime_pointer_document(pointer)
    )
    return root


def _configure_router_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(
        content_endpoint,
        "CONTENT_TREE_PATH",
        root / "content/content_tree.json",
    )


@pytest.mark.parametrize(("route", "kind"), ROUTES)
def test_routes_use_the_legacy_tree_once_when_pointer_is_absent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    route: str,
    kind: str,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _configure_router_root(monkeypatch, root)
    legacy_tree = _tree("A1", "legacy-unit", "legacy-lesson")
    roots: list[Path] = []
    build_calls = 0

    def select(repository_root: Path) -> None:
        roots.append(repository_root)
        return None

    def build() -> ContentTreeResponse:
        nonlocal build_calls
        build_calls += 1
        return legacy_tree

    monkeypatch.setattr(content_endpoint, "select_active_runtime_content_tree", select)
    monkeypatch.setattr(content_endpoint, "build_content_tree", build)

    response = TestClient(app).get(route.replace("R1", "A1").replace("runtime-unit", "legacy-unit").replace("runtime-lesson", "legacy-lesson"))

    assert response.status_code == 200
    assert roots == [root]
    assert build_calls == 1
    assert "legacy" in str(response.json())


@pytest.mark.parametrize(("route", "kind"), ROUTES)
def test_routes_use_only_the_verified_runtime_tree_once_per_request(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    route: str,
    kind: str,
) -> None:
    runtime_tree = _tree("R1", "runtime-unit", "runtime-lesson")
    root = _write_runtime_chain(tmp_path, runtime_tree)
    _configure_router_root(monkeypatch, root)
    calls = 0
    original_select = content_endpoint.select_active_runtime_content_tree

    def select_once(repository_root: Path) -> ContentTreeResponse | None:
        nonlocal calls
        calls += 1
        return original_select(repository_root)

    monkeypatch.setattr(content_endpoint, "select_active_runtime_content_tree", select_once)
    monkeypatch.setattr(
        content_endpoint,
        "build_content_tree",
        lambda: pytest.fail("runtime selection must not use the legacy tree"),
    )

    response = TestClient(app).get(route)

    assert response.status_code == 200
    assert calls == 1
    assert "runtime" in str(response.json()).lower()
    assert "legacy" not in str(response.json()).lower()


@pytest.mark.parametrize(("route", "_kind"), ROUTES)
def test_routes_propagate_an_invalid_pointer_without_legacy_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    route: str,
    _kind: str,
) -> None:
    root = _write_runtime_chain(tmp_path, _tree("R1", "runtime-unit", "runtime-lesson"))
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
    _configure_router_root(monkeypatch, root)
    monkeypatch.setattr(
        content_endpoint,
        "build_content_tree",
        lambda: pytest.fail("invalid pointer must not fall back to legacy"),
    )

    with pytest.raises(ValueError, match="activation record digest mismatch"):
        TestClient(app).get(route)


@pytest.mark.parametrize(
    "route",
    (
        "/api/v1/content/levels/missing",
        "/api/v1/content/levels/missing/units",
        "/api/v1/content/units/missing",
        "/api/v1/content/units/missing/lessons",
        "/api/v1/content/lessons/missing",
    ),
)
def test_routes_preserve_not_found_behavior(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    route: str,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _configure_router_root(monkeypatch, root)
    monkeypatch.setattr(content_endpoint, "select_active_runtime_content_tree", lambda _: None)
    monkeypatch.setattr(content_endpoint, "build_content_tree", lambda: _tree("A1", "unit", "lesson"))

    assert TestClient(app).get(route).status_code == 404
