from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.engineering import a1_resource_asset_close as asset_close


ROOT = Path(__file__).resolve().parents[1]
WATER = ROOT / "content/resources/a1-u1/visual/scene-water.png"
FOOD = ROOT / "content/resources/a1-u1/visual/scene-food.png"
NEED = ROOT / "content/resources/a1-u1/visual/option-need.png"
GREETING = ROOT / "content/resources/a1-u1/visual/option-greeting.png"


@pytest.fixture
def prepared_root(tmp_path: Path) -> Path:
    root = tmp_path / "repository"
    (root / "content/resources/a1-u1/visual").mkdir(parents=True)
    (root / "content/candidates/a1-u1").mkdir(parents=True)
    (root / "docs").mkdir()
    shutil.copy2(ROOT / asset_close.README_RELATIVE_PATH, root / asset_close.README_RELATIVE_PATH)
    shutil.copy2(ROOT / asset_close.CANDIDATE_RELATIVE_PATH, root / asset_close.CANDIDATE_RELATIVE_PATH)
    shutil.copy2(ROOT / asset_close.STATE_RELATIVE_PATH, root / asset_close.STATE_RELATIVE_PATH)
    for source in (WATER, FOOD, NEED, GREETING):
        shutil.copy2(source, root / source.relative_to(ROOT))
    return root


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _downloads(tmp_path: Path, filename: str, content: bytes) -> Path:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    (downloads / filename).write_bytes(content)
    return downloads


def _batch_manifest(tmp_path: Path, payload: object) -> Path:
    manifest = tmp_path / "a1-u1-approved-assets.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    return manifest


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _initialize_git_repository(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Asset Close Tests")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "initial")


def _close_without_git(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(asset_close, "assert_clean_worktree", lambda root: None)
    monkeypatch.setattr(asset_close, "_run_validation_commands", lambda root, allowlist: None)

    def close(**kwargs: object) -> str:
        calls.append(kwargs)
        return "published-commit"

    monkeypatch.setattr(asset_close, "close_git_changes", close, raising=False)
    return calls


def _install(
    *,
    root: Path,
    downloads: Path,
    resource_id: str,
    sha256: str,
    monkeypatch: pytest.MonkeyPatch,
    downloads_file: str | None = None,
    validate: bool = True,
) -> tuple[str, list[dict[str, object]]]:
    calls = _close_without_git(monkeypatch)
    if not validate:
        def fail_validation(_root: Path, _allowlist: tuple[str, str]) -> None:
            raise asset_close.AssetCloseError("forced post-copy failure")

        monkeypatch.setattr(asset_close, "_run_validation_commands", fail_validation)
    result = asset_close.close_approved_asset(
        resource_id=resource_id,
        expected_sha256=sha256,
        downloads_file=downloads_file,
        human_approved=True,
        root=root,
        downloads_dir=downloads,
        now=datetime(2026, 9, 10, 19, 0, tzinfo=timezone.utc),
        close_function=asset_close.close_git_changes,
    )
    return result, calls


def test_readme_map_matches_candidate_and_allows_existing_approved_assets() -> None:
    bindings = asset_close.load_binding_map(ROOT)

    asset_close.validate_binding_inventory(ROOT, bindings)

    assert asset_close.CANDIDATE_RELATIVE_PATH == Path(
        "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
    )
    assert len(bindings) == 18
    v3_resource_ids = json.loads(
        (ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json").read_text(
            encoding="utf-8"
        )
    )["required_resource_ids"]
    v4_resource_ids = json.loads(
        (ROOT / asset_close.CANDIDATE_RELATIVE_PATH).read_text(encoding="utf-8")
    )["required_resource_ids"]
    assert v3_resource_ids == v4_resource_ids
    assert len(v4_resource_ids) == 18
    assert {binding.resource_id for binding in bindings} >= {
        "visual.a1-u1-l1.scene.water.v1",
        "visual.a1-u1-l1.scene.food.v1",
        "visual.a1-u1-l1.comprehension-option.need.v1",
        "visual.a1-u1-l1.comprehension-option.greeting.v1",
    }
    assert all(
        not (ROOT / asset_close.RESOURCE_ROOT / binding.relative_path).is_symlink()
        for binding in bindings
    )
    assert all(path.is_file() for path in (WATER, FOOD, NEED, GREETING))


def test_unknown_resource_is_rejected_without_changes(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloads = _downloads(tmp_path, "unknown.png", b"approved")
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    _close_without_git(monkeypatch)

    with pytest.raises(asset_close.AssetCloseError, match="not an A1-U1 binding"):
        asset_close.close_approved_asset(
            resource_id="unknown",
            expected_sha256=_digest(b"approved"),
            downloads_file="unknown.png",
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
        )

    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state


def test_human_approval_is_required(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloads = _downloads(tmp_path, "scene-help.mp4", b"approved")
    _close_without_git(monkeypatch)

    with pytest.raises(asset_close.AssetCloseError, match="human-approved"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.scene.help.v1",
            expected_sha256=_digest(b"approved"),
            downloads_file=None,
            human_approved=False,
            root=prepared_root,
            downloads_dir=downloads,
        )


def test_script_imports_git_close_when_executed_by_path_outside_repository(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/engineering/a1_resource_asset_close.py"),
            "--help",
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ModuleNotFoundError" not in result.stderr
    assert "--human-approved" in result.stdout


def test_default_download_filename_copies_byte_identically_and_updates_4_to_5(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved help video bytes"
    downloads = _downloads(tmp_path, "scene-help.mp4", content)

    result, calls = _install(
        root=prepared_root,
        downloads=downloads,
        resource_id="visual.a1-u1-l1.scene.help.v1",
        sha256=_digest(content),
        monkeypatch=monkeypatch,
    )

    destination = prepared_root / "content/resources/a1-u1/visual/scene-help.mp4"
    state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_text(encoding="utf-8")
    assert result == "published-commit"
    assert destination.read_bytes() == content
    assert asset_close._sha256(destination) == _digest(content)
    assert "PHYSICAL ASSETS = **5/18 APPROVED**" in state
    assert "visual.a1-u1-l1.scene.help.v1" in state
    assert _digest(content) in state
    assert "los otros 13 assets siguen pendientes" in state
    assert "Todavía no existe catálogo ni manifest" in state
    assert calls == [{
        "branch": "master",
        "upstream": "origin/master",
        "message": "feat add approved A1 asset visual.a1-u1-l1.scene.help.v1 (scene-help.mp4)",
        "files": ["content/resources/a1-u1/visual/scene-help.mp4", "docs/estado-operativo.md"],
        "root": prepared_root,
    }]


def test_batch_manifest_closes_two_assets_with_one_docs_update_and_one_close(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    help_content = b"approved help video bytes"
    farewell_content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "scene-help.mp4", help_content)
    (downloads / "option-farewell.png").write_bytes(farewell_content)
    manifest = _batch_manifest(tmp_path, [
        {
            "resource_id": "visual.a1-u1-l1.scene.help.v1",
            "sha256": _digest(help_content),
            "human_approved": True,
        },
        {
            "resource_id": "visual.a1-u1-l1.comprehension-option.farewell.v1",
            "sha256": _digest(farewell_content),
            "human_approved": True,
        },
    ])
    calls = _close_without_git(monkeypatch)
    updates = 0
    original_update = asset_close.update_operational_state

    def count_update(**kwargs: object) -> bytes:
        nonlocal updates
        updates += 1
        return original_update(**kwargs)

    monkeypatch.setattr(asset_close, "update_operational_state", count_update)
    result = asset_close.close_approved_asset_batch(
        manifest_path=manifest,
        root=prepared_root,
        downloads_dir=downloads,
        now=datetime(2026, 9, 10, 19, 0, tzinfo=timezone.utc),
        close_function=asset_close.close_git_changes,
    )

    assert result == "published-commit"
    assert updates == 1
    assert (prepared_root / "content/resources/a1-u1/visual/scene-help.mp4").read_bytes() == help_content
    assert (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").read_bytes() == farewell_content
    assert asset_close._sha256(prepared_root / "content/resources/a1-u1/visual/scene-help.mp4") == _digest(help_content)
    assert asset_close._sha256(prepared_root / "content/resources/a1-u1/visual/option-farewell.png") == _digest(farewell_content)
    state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_text(encoding="utf-8")
    assert "PHYSICAL ASSETS = **6/18 APPROVED**" in state
    assert "los otros 12 assets siguen pendientes" in state
    assert calls == [{
        "branch": "master",
        "upstream": "origin/master",
        "message": "feat close approved A1 resource asset batch (2)",
        "files": [
            "content/resources/a1-u1/visual/scene-help.mp4",
            "content/resources/a1-u1/visual/option-farewell.png",
            "docs/estado-operativo.md",
        ],
        "root": prepared_root,
    }]


@pytest.mark.parametrize(
    "payload,error",
    [
        ([], "non-empty JSON list"),
        ([{"resource_id": "x", "sha256": "0" * 64, "human_approved": True, "extra": 1}], "invalid keys"),
        ([{"resource_id": "x", "sha256": "0" * 64, "human_approved": False}], "human_approved=true"),
        ([{"resource_id": "x", "sha256": "not-a-sha", "human_approved": True}], "64 lowercase"),
        ([
            {"resource_id": "x", "sha256": "0" * 64, "human_approved": True},
            {"resource_id": "x", "sha256": "1" * 64, "human_approved": True},
        ], "resource_id values must be unique"),
    ],
)
def test_batch_manifest_is_strict(tmp_path: Path, payload: object, error: str) -> None:
    manifest = _batch_manifest(tmp_path, payload)

    with pytest.raises(asset_close.AssetCloseError, match=error):
        asset_close.load_batch_manifest(manifest)


def test_batch_manifest_inside_repository_or_symlink_is_rejected(
    prepared_root: Path, tmp_path: Path
) -> None:
    inside = prepared_root / "inside.json"
    inside.write_text("[]", encoding="utf-8")
    with pytest.raises(asset_close.AssetCloseError, match="outside the repository"):
        asset_close.load_batch_manifest(inside, root=prepared_root)

    manifest = _batch_manifest(tmp_path, [])
    symlink = tmp_path / "manifest-link.json"
    os.symlink(manifest, symlink)
    with pytest.raises(asset_close.AssetCloseError, match="must not be a symlink"):
        asset_close.load_batch_manifest(symlink, root=prepared_root)


def test_batch_preflight_mismatch_creates_no_destinations_or_docs_change(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    help_content = b"approved help video bytes"
    farewell_content = b"wrong farewell bytes"
    downloads = _downloads(tmp_path, "scene-help.mp4", help_content)
    (downloads / "option-farewell.png").write_bytes(farewell_content)
    manifest = _batch_manifest(tmp_path, [
        {
            "resource_id": "visual.a1-u1-l1.scene.help.v1",
            "sha256": _digest(help_content),
            "human_approved": True,
        },
        {
            "resource_id": "visual.a1-u1-l1.comprehension-option.farewell.v1",
            "sha256": "0" * 64,
            "human_approved": True,
        },
    ])
    _close_without_git(monkeypatch)
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()

    with pytest.raises(asset_close.AssetCloseError, match="does not match"):
        asset_close.close_approved_asset_batch(
            manifest_path=manifest,
            root=prepared_root,
            downloads_dir=downloads,
            close_function=asset_close.close_git_changes,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/scene-help.mp4").exists()
    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state


def test_batch_rejects_duplicate_destinations(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloads = _downloads(tmp_path, "same.png", b"approved")
    duplicate_bindings = (
        asset_close.ResourceBinding("first", asset_close.PurePosixPath("visual/same.png")),
        asset_close.ResourceBinding("second", asset_close.PurePosixPath("visual/same.png")),
    )
    monkeypatch.setattr(asset_close, "load_binding_map", lambda root: duplicate_bindings)
    monkeypatch.setattr(asset_close, "validate_binding_inventory", lambda root, bindings: None)
    monkeypatch.setattr(asset_close, "_assert_no_unmapped_assets", lambda root, bindings: None)

    with pytest.raises(asset_close.AssetCloseError, match="destinations must be unique"):
        asset_close._prepare_assets(
            root=prepared_root,
            requests=(
                asset_close.AssetRequest("first", _digest(b"approved"), "same.png"),
                asset_close.AssetRequest("second", _digest(b"approved"), "same.png"),
            ),
            downloads_dir=downloads,
        )


def test_batch_copy_failure_rolls_back_all_new_destinations(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    help_content = b"approved help video bytes"
    farewell_content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "scene-help.mp4", help_content)
    (downloads / "option-farewell.png").write_bytes(farewell_content)
    manifest = _batch_manifest(tmp_path, [
        {"resource_id": "visual.a1-u1-l1.scene.help.v1", "sha256": _digest(help_content), "human_approved": True},
        {"resource_id": "visual.a1-u1-l1.comprehension-option.farewell.v1", "sha256": _digest(farewell_content), "human_approved": True},
    ])
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    _close_without_git(monkeypatch)
    original_copy = asset_close._copy_new_asset
    calls = 0

    def fail_second_copy(source: Path, destination: Path, sha256: str) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise asset_close.AssetCloseError("forced second-copy failure")
        original_copy(source, destination, sha256)

    monkeypatch.setattr(asset_close, "_copy_new_asset", fail_second_copy)
    with pytest.raises(asset_close.AssetCloseError, match="forced second-copy"):
        asset_close.close_approved_asset_batch(
            manifest_path=manifest,
            root=prepared_root,
            downloads_dir=downloads,
            close_function=asset_close.close_git_changes,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/scene-help.mp4").exists()
    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state
    assert (prepared_root / "content/resources/a1-u1/visual/scene-water.png").read_bytes() == WATER.read_bytes()


def test_batch_staged_precommit_failure_restores_batch_allowlist_only(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _initialize_git_repository(prepared_root)
    help_content = b"approved help video bytes"
    farewell_content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "scene-help.mp4", help_content)
    (downloads / "option-farewell.png").write_bytes(farewell_content)
    manifest = _batch_manifest(tmp_path, [
        {"resource_id": "visual.a1-u1-l1.scene.help.v1", "sha256": _digest(help_content), "human_approved": True},
        {"resource_id": "visual.a1-u1-l1.comprehension-option.farewell.v1", "sha256": _digest(farewell_content), "human_approved": True},
    ])
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    previous_water = (prepared_root / "content/resources/a1-u1/visual/scene-water.png").read_bytes()
    monkeypatch.setattr(asset_close, "_run_validation_commands", lambda root, allowlist: None)

    def stage_then_fail(*, files: list[str], root: Path, **_kwargs: object) -> str:
        _git(root, "add", "--", *files)
        raise asset_close.AssetCloseError("forced staged batch failure")

    with pytest.raises(asset_close.AssetCloseError, match="forced staged batch"):
        asset_close.close_approved_asset_batch(
            manifest_path=manifest,
            root=prepared_root,
            downloads_dir=downloads,
            close_function=stage_then_fail,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/scene-help.mp4").exists()
    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state
    assert (prepared_root / "content/resources/a1-u1/visual/scene-water.png").read_bytes() == previous_water
    assert _git(prepared_root, "status", "--porcelain").stdout == ""
    assert _git(prepared_root, "diff", "--cached", "--name-only").stdout == ""


def test_download_override_is_one_safe_basename(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "human-approved-name.png", content)

    _install(
        root=prepared_root,
        downloads=downloads,
        resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
        sha256=_digest(content),
        downloads_file="human-approved-name.png",
        monkeypatch=monkeypatch,
    )

    assert (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").read_bytes() == content


@pytest.mark.parametrize("filename", ["/tmp/file.png", "../file.png", "nested/file.png"])
def test_downloads_file_rejects_absolute_and_traversal(
    tmp_path: Path, filename: str
) -> None:
    downloads = _downloads(tmp_path, "safe.png", b"approved")

    with pytest.raises(asset_close.AssetCloseError, match="safe basename"):
        asset_close.resolve_download_source(downloads_dir=downloads, filename=filename)


def test_download_symlink_is_rejected(tmp_path: Path) -> None:
    downloads = _downloads(tmp_path, "safe.png", b"approved")
    link = downloads / "link.png"
    os.symlink(downloads / "safe.png", link)

    with pytest.raises(asset_close.AssetCloseError, match="must not be a symlink"):
        asset_close.resolve_download_source(downloads_dir=downloads, filename="link.png")


def test_invalid_or_mismatched_sha_does_not_modify_repository(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "option-farewell.png", content)
    _close_without_git(monkeypatch)
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()

    with pytest.raises(asset_close.AssetCloseError, match="64 lowercase"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            expected_sha256="bad",
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
        )
    with pytest.raises(asset_close.AssetCloseError, match="does not match"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            expected_sha256="0" * 64,
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state


def test_existing_destination_and_dirty_worktree_are_rejected(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    downloads = _downloads(tmp_path, "scene-water.png", b"different")
    monkeypatch.setattr(asset_close, "_git_status_paths", lambda root: {"dirty.txt"})
    with pytest.raises(asset_close.AssetCloseError, match="working tree must be clean"):
        asset_close.assert_clean_worktree(prepared_root)
    monkeypatch.setattr(asset_close, "assert_clean_worktree", lambda root: None)
    with pytest.raises(asset_close.AssetCloseError, match="already exists"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.scene.water.v1",
            expected_sha256=_digest(b"different"),
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
        )


def test_unmapped_asset_is_rejected_before_copy(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "option-farewell.png", content)
    (prepared_root / "content/resources/a1-u1/visual/unmapped.png").write_bytes(b"unmapped")
    _close_without_git(monkeypatch)

    with pytest.raises(asset_close.AssetCloseError, match="unmapped asset"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            expected_sha256=_digest(content),
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
        )


def test_state_renderer_reports_the_current_four_assets_without_expected_catalog(
    prepared_root: Path
) -> None:
    bindings = asset_close.load_binding_map(prepared_root)
    asset_close.update_operational_state(
        root=prepared_root,
        bindings=bindings,
        now=datetime(2026, 9, 10, 19, 0, tzinfo=timezone.utc),
    )
    state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_text(encoding="utf-8")

    assert "PHYSICAL ASSETS = **4/18 APPROVED**" in state
    assert "los otros 14 assets siguen pendientes" in state
    assert "Todavía no existe catálogo ni manifest" in state
    assert not (prepared_root / "content/expected-resource-identities.json").exists()


def test_post_copy_failure_restores_state_and_removes_only_new_destination(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "option-farewell.png", content)
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    _close_without_git(monkeypatch)

    with pytest.raises(asset_close.AssetCloseError, match="forced post-copy failure"):
        _install(
            root=prepared_root,
            downloads=downloads,
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            sha256=_digest(content),
            monkeypatch=monkeypatch,
            validate=False,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state
    assert (prepared_root / "content/resources/a1-u1/visual/scene-water.png").exists()


def test_uncommitted_git_close_failure_also_restores_state_and_destination(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "option-farewell.png", content)
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    monkeypatch.setattr(asset_close, "assert_clean_worktree", lambda root: None)
    monkeypatch.setattr(asset_close, "_run_validation_commands", lambda root, allowlist: None)

    def fail_close(**_kwargs: object) -> str:
        raise asset_close.AssetCloseError("forced uncommitted close failure")

    with pytest.raises(asset_close.AssetCloseError, match="forced uncommitted"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            expected_sha256=_digest(content),
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
            close_function=fail_close,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state


def test_staged_precommit_failure_restores_only_allowlist_index_entries(
    prepared_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _initialize_git_repository(prepared_root)
    content = b"approved farewell bytes"
    downloads = _downloads(tmp_path, "option-farewell.png", content)
    original_state = (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes()
    previous_assets = {
        path: path.read_bytes()
        for path in (
            prepared_root / "content/resources/a1-u1/visual/scene-water.png",
            prepared_root / "content/resources/a1-u1/visual/scene-food.png",
            prepared_root / "content/resources/a1-u1/visual/option-need.png",
            prepared_root / "content/resources/a1-u1/visual/option-greeting.png",
        )
    }
    monkeypatch.setattr(asset_close, "_run_validation_commands", lambda root, allowlist: None)

    def stage_then_fail(*, files: list[str], root: Path, **_kwargs: object) -> str:
        _git(root, "add", "--", *files)
        raise asset_close.AssetCloseError("forced staged pre-commit failure")

    with pytest.raises(asset_close.AssetCloseError, match="forced staged pre-commit"):
        asset_close.close_approved_asset(
            resource_id="visual.a1-u1-l1.comprehension-option.farewell.v1",
            expected_sha256=_digest(content),
            downloads_file=None,
            human_approved=True,
            root=prepared_root,
            downloads_dir=downloads,
            close_function=stage_then_fail,
        )

    assert not (prepared_root / "content/resources/a1-u1/visual/option-farewell.png").exists()
    assert (prepared_root / asset_close.STATE_RELATIVE_PATH).read_bytes() == original_state
    assert {path: path.read_bytes() for path in previous_assets} == previous_assets
    assert _git(prepared_root, "status", "--porcelain").stdout == ""
    assert _git(prepared_root, "diff", "--cached", "--name-only").stdout == ""


def test_unstage_allowlist_preserves_foreign_staged_and_unstaged_paths(
    prepared_root: Path,
) -> None:
    _initialize_git_repository(prepared_root)
    foreign_staged = prepared_root / "foreign-staged.txt"
    foreign_unstaged = prepared_root / "foreign-unstaged.txt"
    foreign_staged.write_text("staged\n", encoding="utf-8")
    foreign_unstaged.write_text("unstaged\n", encoding="utf-8")
    _git(prepared_root, "add", "--", foreign_staged.name)
    state_path = prepared_root / asset_close.STATE_RELATIVE_PATH
    state_path.write_text("changed\n", encoding="utf-8")

    asset_close._unstage_allowlist(
        prepared_root,
        ("content/resources/a1-u1/visual/option-farewell.png", "docs/estado-operativo.md"),
    )

    assert _git(prepared_root, "diff", "--cached", "--name-only").stdout == "foreign-staged.txt\n"
    assert _git(prepared_root, "status", "--porcelain").stdout == (
        " M docs/estado-operativo.md\nA  foreign-staged.txt\n?? foreign-unstaged.txt\n"
    )
