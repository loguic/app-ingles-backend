from pathlib import Path

import pytest

from scripts.engineering.a1_resource_asset_close import (
    RESOURCE_ROOT,
    load_binding_map,
    validate_binding_inventory,
)

ROOT = Path(__file__).resolve().parents[1]


def _resolve_resource_path(relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("resource path must stay under repository root")
    resource_path = ROOT / relative_path
    if not resource_path.is_relative_to(ROOT):
        raise ValueError("resource path must stay under repository root")
    return resource_path


def test_a1_resource_binding_map_matches_the_candidate_inventory() -> None:
    bindings = load_binding_map(ROOT)
    validate_binding_inventory(ROOT, bindings)
    resource_ids = tuple(binding.resource_id for binding in bindings)
    relative_paths = tuple(RESOURCE_ROOT / binding.relative_path for binding in bindings)

    assert len(resource_ids) == 18
    assert len(set(relative_paths)) == 18
    assert sum(path.suffix == ".wav" for path in relative_paths) == 12
    assert sum(path.suffix == ".png" for path in relative_paths) == 5
    assert sum(path.suffix == ".mp4" for path in relative_paths) == 1

    for relative_path in relative_paths:
        resource_path = _resolve_resource_path(relative_path)
        assert resource_path.is_relative_to(ROOT)
        if resource_path.exists():
            assert resource_path.is_file()
            assert not resource_path.is_symlink()


def test_a1_resource_binding_map_rejects_path_traversal() -> None:
    with pytest.raises(ValueError, match="stay under repository root"):
        _resolve_resource_path(Path("content/resources/a1-u1/../outside.wav"))
