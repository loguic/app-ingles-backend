"""Install and close one human-approved physical A1-U1 resource asset.

This helper records an operational acknowledgement of a prior human approval.
It does not review media semantically, create expected identities, or verify B51/B52.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering.git_close import close_git_changes

README_RELATIVE_PATH = Path("content/resources/a1-u1/README.md")
RESOURCE_ROOT = Path("content/resources/a1-u1")
CANDIDATE_RELATIVE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json"
)
STATE_RELATIVE_PATH = Path("docs/estado-operativo.md")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
ASSET_STATE_PATTERN = re.compile(
    r"PHYSICAL ASSETS = \*\*\d+/18 APPROVED\*\*: .*? No hay B52,",
    re.DOTALL,
)
NEXT_OBJECTIVE_PATTERN = re.compile(
    r"Producir únicamente los \d+ assets A1-U1 restantes"
)


@dataclass(frozen=True)
class ResourceBinding:
    resource_id: str
    relative_path: PurePosixPath


@dataclass(frozen=True)
class AssetRequest:
    resource_id: str
    expected_sha256: str
    downloads_file: str | None = None


@dataclass(frozen=True)
class PreparedAsset:
    request: AssetRequest
    binding: ResourceBinding
    source: Path
    destination: Path


class AssetCloseError(RuntimeError):
    """Describe one fail-closed asset-installation error."""


def _repository_path(root: Path, relative_path: Path) -> Path:
    candidate = root / relative_path
    try:
        candidate.resolve(strict=False).relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise AssetCloseError("repository path escapes repository root") from exc
    return candidate


def _parse_binding_row(line: str) -> ResourceBinding | None:
    if not line.startswith("|"):
        return None
    cells = [cell.strip() for cell in line.split("|")[1:-1]]
    if len(cells) != 2 or cells[0].startswith("-"):
        return None
    resource_id = cells[0].removeprefix("`").removesuffix("`")
    raw_path = cells[1].removeprefix("`").removesuffix("`")
    path = PurePosixPath(raw_path)
    if (
        not resource_id
        or not raw_path
        or path.is_absolute()
        or ".." in path.parts
        or path.as_posix() != raw_path
    ):
        raise AssetCloseError("README resource binding row is invalid")
    return ResourceBinding(resource_id=resource_id, relative_path=path)


def load_binding_map(root: Path = ROOT) -> tuple[ResourceBinding, ...]:
    """Parse the sole A1-U1 physical-binding map from its canonical README."""
    readme = _repository_path(root, README_RELATIVE_PATH)
    try:
        lines = readme.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AssetCloseError("canonical A1-U1 binding README is unavailable") from exc

    try:
        start = lines.index("| resource_id | relative path |") + 2
    except ValueError as exc:
        raise AssetCloseError("canonical A1-U1 binding table is unavailable") from exc

    bindings: list[ResourceBinding] = []
    for line in lines[start:]:
        row = _parse_binding_row(line)
        if row is None:
            break
        bindings.append(row)

    if not bindings or len({item.resource_id for item in bindings}) != len(bindings):
        raise AssetCloseError("canonical A1-U1 binding IDs are invalid")
    if len({item.relative_path for item in bindings}) != len(bindings):
        raise AssetCloseError("canonical A1-U1 binding paths are invalid")
    return tuple(bindings)


def validate_binding_inventory(
    root: Path,
    bindings: tuple[ResourceBinding, ...],
) -> None:
    """Require the README map to cover the exact candidate inventory."""
    candidate_path = _repository_path(root, CANDIDATE_RELATIVE_PATH)
    try:
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        required_resource_ids = tuple(candidate["required_resource_ids"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise AssetCloseError("A1-U1 candidate resource inventory is invalid") from exc

    if len(bindings) != 18 or tuple(item.resource_id for item in bindings) != required_resource_ids:
        raise AssetCloseError("README bindings do not match A1-U1 required_resource_ids")
    resource_root = _repository_path(root, RESOURCE_ROOT)
    for binding in bindings:
        destination = resource_root.joinpath(*binding.relative_path.parts)
        try:
            destination.resolve(strict=False).relative_to(resource_root.resolve(strict=False))
        except ValueError as exc:
            raise AssetCloseError("resource binding escapes A1-U1 resource root") from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_sha256(value: str) -> str:
    if SHA256_PATTERN.fullmatch(value) is None:
        raise AssetCloseError("--sha256 must be 64 lowercase hexadecimal characters")
    return value


def _validate_basename(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or len(path.parts) != 1
        or path.name in {".", ".."}
        or path.as_posix() != value
    ):
        raise AssetCloseError("--downloads-file must be one safe basename")
    return value


def resolve_download_source(
    *,
    downloads_dir: Path,
    filename: str,
) -> Path:
    """Resolve one non-symlink regular source file inside Downloads."""
    filename = _validate_basename(filename)
    try:
        downloads_root = downloads_dir.resolve(strict=True)
    except OSError as exc:
        raise AssetCloseError("Downloads directory is unavailable") from exc
    source = downloads_dir / filename
    if source.is_symlink():
        raise AssetCloseError("download source must not be a symlink")
    try:
        resolved = source.resolve(strict=True)
        resolved.relative_to(downloads_root)
        mode = resolved.stat().st_mode
    except (OSError, ValueError) as exc:
        raise AssetCloseError("download source is outside Downloads or unavailable") from exc
    if not stat.S_ISREG(mode):
        raise AssetCloseError("download source must be a regular file")
    return resolved


def load_batch_manifest(manifest_path: Path, *, root: Path = ROOT) -> tuple[AssetRequest, ...]:
    """Read one strict, external manifest of prior human approvals."""
    root = root.resolve(strict=True)
    if manifest_path.is_symlink():
        raise AssetCloseError("batch manifest must not be a symlink")
    try:
        resolved = manifest_path.resolve(strict=True)
        resolved.relative_to(root)
    except ValueError:
        pass
    except OSError as exc:
        raise AssetCloseError("batch manifest is unavailable") from exc
    else:
        raise AssetCloseError("batch manifest must stay outside the repository")
    try:
        if not stat.S_ISREG(resolved.stat().st_mode):
            raise AssetCloseError("batch manifest must be a regular file")
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        raise AssetCloseError("batch manifest is invalid JSON") from exc
    if not isinstance(payload, list) or not payload:
        raise AssetCloseError("batch manifest must be a non-empty JSON list")

    requests: list[AssetRequest] = []
    expected_keys = {"resource_id", "sha256", "human_approved"}
    allowed_keys = expected_keys | {"downloads_file"}
    for entry in payload:
        if not isinstance(entry, dict) or set(entry) - allowed_keys or set(entry) < expected_keys:
            raise AssetCloseError("batch manifest entry has invalid keys")
        resource_id = entry["resource_id"]
        sha256 = entry["sha256"]
        downloads_file = entry.get("downloads_file")
        if not isinstance(resource_id, str) or not resource_id:
            raise AssetCloseError("batch manifest resource_id is invalid")
        if not isinstance(sha256, str):
            raise AssetCloseError("batch manifest SHA-256 is invalid")
        if entry["human_approved"] is not True:
            raise AssetCloseError("batch manifest requires human_approved=true")
        if downloads_file is not None and not isinstance(downloads_file, str):
            raise AssetCloseError("batch manifest downloads_file is invalid")
        requests.append(
            AssetRequest(
                resource_id=resource_id,
                expected_sha256=_validate_sha256(sha256),
                downloads_file=(
                    _validate_basename(downloads_file)
                    if downloads_file is not None
                    else None
                ),
            )
        )
    if len({request.resource_id for request in requests}) != len(requests):
        raise AssetCloseError("batch manifest resource_id values must be unique")
    return tuple(requests)


def _assert_no_unmapped_assets(root: Path, bindings: tuple[ResourceBinding, ...]) -> None:
    resource_root = _repository_path(root, RESOURCE_ROOT)
    allowed = {
        (resource_root / binding.relative_path).resolve(strict=False)
        for binding in bindings
    }
    readme = _repository_path(root, README_RELATIVE_PATH).resolve(strict=False)
    if not resource_root.exists():
        raise AssetCloseError("A1-U1 resource root is unavailable")
    for path in resource_root.rglob("*"):
        if path.is_dir():
            continue
        if path.resolve(strict=False) == readme:
            continue
        if path.is_symlink() or path.resolve(strict=False) not in allowed:
            raise AssetCloseError("A1-U1 resource root contains an unmapped asset")


def _installed_assets(root: Path, bindings: tuple[ResourceBinding, ...]) -> tuple[ResourceBinding, ...]:
    resource_root = _repository_path(root, RESOURCE_ROOT)
    installed: list[ResourceBinding] = []
    for binding in bindings:
        path = resource_root / binding.relative_path
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise AssetCloseError("mapped asset must be a regular non-symlink file")
            installed.append(binding)
    return tuple(installed)


def _render_asset_state(root: Path, bindings: tuple[ResourceBinding, ...]) -> str:
    installed = _installed_assets(root, bindings)
    entries = "; ".join(
        f"`{binding.resource_id}` está producido y aprobado en "
        f"`{(RESOURCE_ROOT / binding.relative_path).as_posix()}`, con SHA-256 "
        f"`{_sha256(_repository_path(root, RESOURCE_ROOT) / binding.relative_path)}`"
        for binding in installed
    )
    pending = len(bindings) - len(installed)
    return (
        f"PHYSICAL ASSETS = **{len(installed)}/18 APPROVED**: {entries}; "
        f"los otros {pending} assets siguen pendientes. Todavía no existe catálogo "
        "ni manifest de expected `ResourcePhysicalIdentity`; no se inventarán "
        "identities adicionales y estas se derivarán solo de bytes finales "
        "semánticamente/humanamente aprobados. A1 v3 queda **MEMBER DURABLE / "
        "NOT ACTIVE**; B52 = **NOT VERIFIED**, `LOADER = BLOCKED` y B181 sigue "
        "PAUSED. No hay B52,"
    )


def update_operational_state(
    *,
    root: Path,
    bindings: tuple[ResourceBinding, ...],
    now: datetime | None = None,
) -> bytes:
    """Regenerate the bounded A1 asset state from installed mapped bytes."""
    state_path = _repository_path(root, STATE_RELATIVE_PATH)
    original = state_path.read_bytes()
    text = original.decode("utf-8")
    replacement = _render_asset_state(root, bindings)
    text, replacements = ASSET_STATE_PATTERN.subn(replacement, text)
    if replacements != 1:
        raise AssetCloseError("operational asset state marker is invalid")
    pending = len(bindings) - len(_installed_assets(root, bindings))
    text, objective_replacements = NEXT_OBJECTIVE_PATTERN.subn(
        f"Producir únicamente los {pending} assets A1-U1 restantes",
        text,
    )
    if objective_replacements != 1:
        raise AssetCloseError("operational next-objective marker is invalid")
    timestamp = (now or datetime.now().astimezone()).isoformat(timespec="seconds")
    text, timestamp_replacements = re.subn(
        r"(?m)^Actualizado: .*?$", f"Actualizado: {timestamp}", text
    )
    if timestamp_replacements != 1:
        raise AssetCloseError("operational timestamp marker is invalid")
    if not text.endswith("\n"):
        text += "\n"
    state_path.write_text(text, encoding="utf-8")
    return original


def _git_status_paths(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if result.returncode != 0:
        raise AssetCloseError("Git status is unavailable")
    return {record[3:] for record in result.stdout.split("\0") if record}


def _git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _unstage_allowlist(root: Path, allowlist: tuple[str, ...]) -> None:
    """Restore only this helper's initial-clean index entries from HEAD."""
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z", "--", *allowlist],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if staged.returncode != 0:
        raise AssetCloseError("could not inspect helper allowlist in Git index")
    staged_allowlist = tuple(path for path in staged.stdout.split("\0") if path)
    if not staged_allowlist:
        return
    result = subprocess.run(
        ["git", "restore", "--staged", "--", *staged_allowlist],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if result.returncode != 0:
        raise AssetCloseError("could not restore helper allowlist from Git index")


def assert_clean_worktree(root: Path) -> None:
    if _git_status_paths(root):
        raise AssetCloseError("working tree must be clean before asset installation")


def _run_validation_commands(root: Path, allowlist: tuple[str, ...]) -> None:
    for command in (
        ["git", "diff", "--check"],
        [sys.executable, "scripts/engineering/operational_state.py", "validate"],
        [sys.executable, "scripts/engineering/conversation_checkpoint.py", "prepare"],
    ):
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode != 0:
            raise AssetCloseError("post-copy validation failed")
    if _git_status_paths(root) != set(allowlist):
        raise AssetCloseError("post-copy scope does not match asset allowlist")
    state_path = _repository_path(root, STATE_RELATIVE_PATH)
    if not state_path.read_bytes().endswith(b"\n"):
        raise AssetCloseError("operational state EOF is invalid")


def _copy_new_asset(source: Path, destination: Path, expected_sha256: str) -> None:
    if destination.exists() or destination.is_symlink():
        raise AssetCloseError("mapped destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        created = True
        with source.open("rb") as input_file, os.fdopen(descriptor, "wb") as output_file:
            descriptor = None
            shutil.copyfileobj(input_file, output_file, length=1024 * 1024)
            output_file.flush()
            os.fsync(output_file.fileno())
        if _sha256(destination) != expected_sha256:
            raise AssetCloseError("copied destination SHA-256 does not match")
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created and destination.exists() and not destination.is_symlink():
            destination.unlink()
        raise


def _commit_message(resource_id: str, destination: Path) -> str:
    return f"feat add approved A1 asset {resource_id} ({destination.name})"


def _batch_commit_message(requests: tuple[AssetRequest, ...]) -> str:
    return f"feat close approved A1 resource asset batch ({len(requests)})"


def _prepare_assets(
    *,
    root: Path,
    requests: tuple[AssetRequest, ...],
    downloads_dir: Path,
) -> tuple[PreparedAsset, ...]:
    if not requests:
        raise AssetCloseError("at least one approved asset request is required")
    if len({request.resource_id for request in requests}) != len(requests):
        raise AssetCloseError("asset request resource_id values must be unique")
    bindings = load_binding_map(root)
    validate_binding_inventory(root, bindings)
    _assert_no_unmapped_assets(root, bindings)
    binding_by_id = {binding.resource_id: binding for binding in bindings}
    prepared: list[PreparedAsset] = []
    destinations: set[Path] = set()
    resource_root = _repository_path(root, RESOURCE_ROOT)
    for request in requests:
        expected_sha256 = _validate_sha256(request.expected_sha256)
        binding = binding_by_id.get(request.resource_id)
        if binding is None:
            raise AssetCloseError("resource_id is not an A1-U1 binding")
        destination = resource_root / binding.relative_path
        try:
            destination.resolve(strict=False).relative_to(resource_root.resolve(strict=False))
        except ValueError as exc:
            raise AssetCloseError("mapped destination escapes A1-U1 resource root") from exc
        if destination in destinations:
            raise AssetCloseError("batch manifest destinations must be unique")
        destinations.add(destination)
        if destination.exists() or destination.is_symlink():
            raise AssetCloseError("mapped destination already exists")
        source = resolve_download_source(
            downloads_dir=downloads_dir,
            filename=request.downloads_file or destination.name,
        )
        if _sha256(source) != expected_sha256:
            raise AssetCloseError("download source SHA-256 does not match --sha256")
        prepared.append(
            PreparedAsset(
                request=request,
                binding=binding,
                source=source,
                destination=destination,
            )
        )
    return tuple(prepared)


def close_approved_assets(
    *,
    requests: tuple[AssetRequest, ...],
    commit_message: str,
    root: Path = ROOT,
    downloads_dir: Path | None = None,
    now: datetime | None = None,
    close_function: Callable[..., str] | None = None,
) -> str:
    """Install, validate, document, commit, and publish one approved asset collection."""
    root = root.resolve(strict=True)
    assert_clean_worktree(root)
    prepared = _prepare_assets(
        root=root,
        requests=requests,
        downloads_dir=downloads_dir or Path.home() / "Downloads",
    )
    bindings = load_binding_map(root)

    original_state: bytes | None = None
    copied_destinations: list[Path] = []
    close_started = False
    head_before_close: str | None = None
    allowlist = tuple(
        item.destination.relative_to(root).as_posix() for item in prepared
    ) + (STATE_RELATIVE_PATH.as_posix(),)
    try:
        for item in prepared:
            _copy_new_asset(item.source, item.destination, item.request.expected_sha256)
            copied_destinations.append(item.destination)
        for item in prepared:
            if _sha256(item.destination) != item.request.expected_sha256:
                raise AssetCloseError("copied destination SHA-256 does not match")
        original_state = update_operational_state(root=root, bindings=bindings, now=now)
        _run_validation_commands(root, allowlist)
        if close_function is None:
            close_function = close_git_changes
        head_before_close = _git_head(root)
        close_started = True
        commit = close_function(
            branch="master",
            upstream="origin/master",
            message=commit_message,
            files=list(allowlist),
            root=root,
        )
        return commit
    except Exception:
        if not close_started or _git_head(root) == head_before_close:
            unstage_error: AssetCloseError | None = None
            if close_started and head_before_close is not None:
                try:
                    _unstage_allowlist(root, allowlist)
                except AssetCloseError as exc:
                    unstage_error = exc
            if original_state is not None:
                _repository_path(root, STATE_RELATIVE_PATH).write_bytes(original_state)
            for destination in reversed(copied_destinations):
                if destination.exists() and not destination.is_symlink():
                    destination.unlink()
            if unstage_error is not None:
                raise unstage_error
        raise


def close_approved_asset(
    *,
    resource_id: str,
    expected_sha256: str,
    downloads_file: str | None,
    human_approved: bool,
    root: Path = ROOT,
    downloads_dir: Path | None = None,
    now: datetime | None = None,
    close_function: Callable[..., str] | None = None,
) -> str:
    """Preserve the single-asset interface as a one-element collection."""
    if not human_approved:
        raise AssetCloseError("--human-approved is required before installation")
    request = AssetRequest(
        resource_id=resource_id,
        expected_sha256=_validate_sha256(expected_sha256),
        downloads_file=(
            _validate_basename(downloads_file)
            if downloads_file is not None
            else None
        ),
    )
    destination = _repository_path(root.resolve(strict=True), RESOURCE_ROOT)
    binding = next(
        (item for item in load_binding_map(root) if item.resource_id == resource_id),
        None,
    )
    if binding is None:
        raise AssetCloseError("resource_id is not an A1-U1 binding")
    return close_approved_assets(
        requests=(request,),
        commit_message=_commit_message(resource_id, destination / binding.relative_path),
        root=root,
        downloads_dir=downloads_dir,
        now=now,
        close_function=close_function,
    )


def close_approved_asset_batch(
    *,
    manifest_path: Path,
    root: Path = ROOT,
    downloads_dir: Path | None = None,
    now: datetime | None = None,
    close_function: Callable[..., str] | None = None,
) -> str:
    """Close one external manifest of previously human-approved assets."""
    requests = load_batch_manifest(manifest_path, root=root)
    return close_approved_assets(
        requests=requests,
        commit_message=_batch_commit_message(requests),
        root=root,
        downloads_dir=downloads_dir,
        now=now,
        close_function=close_function,
    )


def _parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install and close one prior human-approved A1-U1 asset; this command "
            "does not perform semantic media review."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--resource-id")
    mode.add_argument("--batch-manifest", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--downloads-file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = _parse_arguments(argv)
    try:
        if arguments.batch_manifest is not None:
            if arguments.sha256 is not None or arguments.human_approved or arguments.downloads_file is not None:
                raise AssetCloseError("--batch-manifest cannot use individual asset arguments")
            commit = close_approved_asset_batch(manifest_path=arguments.batch_manifest)
        else:
            if arguments.sha256 is None or not arguments.human_approved:
                raise AssetCloseError("individual mode requires --sha256 and --human-approved")
            commit = close_approved_asset(
                resource_id=arguments.resource_id,
                expected_sha256=arguments.sha256,
                downloads_file=arguments.downloads_file,
                human_approved=arguments.human_approved,
            )
    except AssetCloseError as exc:
        print(f"ASSET_CLOSE_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"A1 resource asset close completed: {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
