import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = Path("content/resources/a1-u1")
CANDIDATE_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json"
RESOURCE_BINDING_PATHS = (
    (
        "audio.a1-u1-l1.i-need-water.en-us.v1",
        RESOURCE_ROOT / "audio/i-need-water.en-us.wav",
    ),
    (
        "audio.a1-u1-l1.i-need-water.en-gb.v1",
        RESOURCE_ROOT / "audio/i-need-water.en-gb.wav",
    ),
    (
        "audio.a1-u1-l1.i-need-help.en-gb.v1",
        RESOURCE_ROOT / "audio/i-need-help.en-gb.wav",
    ),
    (
        "audio.a1-u1-l1.i-need-food.en-gb.v1",
        RESOURCE_ROOT / "audio/i-need-food.en-gb.wav",
    ),
    ("audio.a1-u1-l1.water.en-us.v1", RESOURCE_ROOT / "audio/water.en-us.wav"),
    ("audio.a1-u1-l1.water.en-gb.v1", RESOURCE_ROOT / "audio/water.en-gb.wav"),
    ("audio.a1-u1-l1.help.en-us.v1", RESOURCE_ROOT / "audio/help.en-us.wav"),
    ("audio.a1-u1-l1.help.en-gb.v1", RESOURCE_ROOT / "audio/help.en-gb.wav"),
    ("audio.a1-u1-l1.food.en-us.v1", RESOURCE_ROOT / "audio/food.en-us.wav"),
    ("audio.a1-u1-l1.food.en-gb.v1", RESOURCE_ROOT / "audio/food.en-gb.wav"),
    ("audio.a1-u1-l1.okay.en-us.v1", RESOURCE_ROOT / "audio/okay.en-us.wav"),
    ("audio.a1-u1-l1.okay.en-gb.v1", RESOURCE_ROOT / "audio/okay.en-gb.wav"),
    ("visual.a1-u1-l1.scene.water.v1", RESOURCE_ROOT / "visual/scene-water.png"),
    ("visual.a1-u1-l1.scene.food.v1", RESOURCE_ROOT / "visual/scene-food.png"),
    ("visual.a1-u1-l1.scene.help.v1", RESOURCE_ROOT / "visual/scene-help.mp4"),
    (
        "visual.a1-u1-l1.comprehension-option.need.v1",
        RESOURCE_ROOT / "visual/option-need.png",
    ),
    (
        "visual.a1-u1-l1.comprehension-option.greeting.v1",
        RESOURCE_ROOT / "visual/option-greeting.png",
    ),
    (
        "visual.a1-u1-l1.comprehension-option.farewell.v1",
        RESOURCE_ROOT / "visual/option-farewell.png",
    ),
)


def _resolve_resource_path(relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("resource path must stay under repository root")
    resource_path = ROOT / relative_path
    if not resource_path.is_relative_to(ROOT):
        raise ValueError("resource path must stay under repository root")
    return resource_path


def test_a1_resource_binding_map_matches_the_candidate_inventory() -> None:
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    resource_ids = tuple(resource_id for resource_id, _path in RESOURCE_BINDING_PATHS)
    relative_paths = tuple(path for _resource_id, path in RESOURCE_BINDING_PATHS)

    assert resource_ids == tuple(candidate["required_resource_ids"])
    assert len(resource_ids) == 18
    assert len(set(relative_paths)) == 18
    assert sum(path.suffix == ".wav" for path in relative_paths) == 12
    assert sum(path.suffix == ".png" for path in relative_paths) == 5
    assert sum(path.suffix == ".mp4" for path in relative_paths) == 1

    for relative_path in relative_paths:
        resource_path = _resolve_resource_path(relative_path)
        assert resource_path.is_relative_to(ROOT)
        assert resource_path.exists() is False


def test_a1_resource_binding_map_rejects_path_traversal() -> None:
    with pytest.raises(ValueError, match="stay under repository root"):
        _resolve_resource_path(Path("content/resources/a1-u1/../outside.wav"))
