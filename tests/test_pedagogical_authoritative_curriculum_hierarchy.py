from dataclasses import FrozenInstanceError, fields
import inspect

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.content import ContentTreeResponse, Level, Unit
from app.services import content_service
from app.services.pedagogical_authoritative_curriculum_hierarchy import (
    AuthoritativeCurriculumHierarchy,
)


def _tree() -> ContentTreeResponse:
    return ContentTreeResponse(
        levels=[Level(code="B1", units=[Unit(id="unit-z", title="Unit")])]
    )


def test_authoritative_hierarchy_is_frozen_and_contains_only_hierarchy():
    tree = _tree()
    authority = content_service.load_authoritative_curriculum_hierarchy()

    assert tuple(field.name for field in fields(authority)) == ("hierarchy",)
    with pytest.raises(FrozenInstanceError):
        authority.hierarchy = tree


def test_ordinary_content_tree_is_not_authoritative():
    tree = _tree()

    assert isinstance(tree, ContentTreeResponse)
    assert not isinstance(tree, AuthoritativeCurriculumHierarchy)


def test_direct_authority_construction_is_rejected():
    with pytest.raises(TypeError, match="authoritative curriculum provider"):
        AuthoritativeCurriculumHierarchy(_tree())


def test_authoritative_loader_has_no_caller_inputs():
    assert tuple(
        inspect.signature(
            content_service.load_authoritative_curriculum_hierarchy
        ).parameters
    ) == ()


def test_authoritative_loader_calls_builder_once_and_preserves_identity(
    monkeypatch,
):
    tree = _tree()
    calls = 0

    def build_tree() -> ContentTreeResponse:
        nonlocal calls
        calls += 1
        return tree

    monkeypatch.setattr(content_service, "build_content_tree", build_tree)

    authority = content_service.load_authoritative_curriculum_hierarchy()

    assert calls == 1
    assert isinstance(authority, AuthoritativeCurriculumHierarchy)
    assert authority.hierarchy is tree


def test_authoritative_loader_propagates_builder_error(monkeypatch):
    error = RuntimeError("provider failed")

    def fail_to_build() -> ContentTreeResponse:
        raise error

    monkeypatch.setattr(content_service, "build_content_tree", fail_to_build)

    with pytest.raises(RuntimeError) as captured:
        content_service.load_authoritative_curriculum_hierarchy()

    assert captured.value is error


def test_build_content_tree_still_returns_ordinary_content_tree():
    tree = content_service.build_content_tree()

    assert isinstance(tree, ContentTreeResponse)
    assert not isinstance(tree, AuthoritativeCurriculumHierarchy)


def test_partial_helpers_do_not_emit_authoritative_hierarchy(monkeypatch):
    tree = _tree()
    monkeypatch.setattr(content_service, "build_content_tree", lambda: tree)

    level = content_service.get_level_by_code("B1")
    unit = content_service.get_unit_by_id("unit-z")

    assert isinstance(level, Level)
    assert isinstance(unit, Unit)
    assert not isinstance(level, AuthoritativeCurriculumHierarchy)
    assert not isinstance(unit, AuthoritativeCurriculumHierarchy)


def test_content_tree_endpoint_exposes_transport_schema_not_authority():
    response = TestClient(app).get("/api/v1/content/tree")

    assert response.status_code == 200
    assert set(response.json()) == {"levels"}
    assert "hierarchy" not in response.json()


def test_authority_declares_no_parallel_metadata_or_order():
    forbidden = {
        "is_authoritative",
        "is_complete",
        "origin_unit_id",
        "origin_position",
        "indices",
        "version",
        "track",
        "locale",
        "checksum",
        "manifest",
    }

    assert forbidden.isdisjoint(
        field.name for field in fields(AuthoritativeCurriculumHierarchy)
    )
