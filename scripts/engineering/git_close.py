from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]

PRECHECK_FAILED = "PRECHECK_FAILED"
STAGING_FAILED = "STAGING_FAILED"
STAGED_SCOPE_MISMATCH = "STAGED_SCOPE_MISMATCH"
COMMIT_FAILED = "COMMIT_FAILED"
PUSH_FAILED = "PUSH_FAILED"
FINAL_SYNC_FAILED = "FINAL_SYNC_FAILED"


class GitCloseError(RuntimeError):
    """Describe one fail-fast Git-close phase failure.

    Describe un fallo fail-fast de una fase de cierre Git.
    """

    def __init__(self, phase: str, detail: str) -> None:
        super().__init__(detail)
        self.phase = phase
        self.detail = detail


@dataclass(frozen=True)
class GitChange:
    """Represent one machine-readable Git status record.

    Representa un registro Git de estado legible por máquina.
    """

    status: str
    path: str
    original_path: str | None = None


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run Git with an explicit root and no shell interpretation.

    Ejecuta Git con root explícito y sin interpretación de shell.
    """
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
        shell=False,
    )


def _output(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout + result.stderr).strip()


def _require_git(
    root: Path,
    phase: str,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    result = _run_git(root, *args)
    if result.returncode != 0:
        detail = _output(result) or "Git command failed"
        raise GitCloseError(phase, detail)
    return result


def _parse_porcelain(output: str) -> tuple[GitChange, ...]:
    records = output.split("\0")
    changes: list[GitChange] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2] != " ":
            raise ValueError("Git porcelain output is malformed")

        status = record[:2]
        path = record[3:]
        original_path = None
        if "R" in status or "C" in status:
            if index >= len(records) or not records[index]:
                raise ValueError("Git rename/copy record lacks its original path")
            original_path = records[index]
            index += 1
        changes.append(GitChange(status, path, original_path))
    return tuple(changes)


def _status(root: Path, phase: str) -> tuple[GitChange, ...]:
    result = _require_git(
        root,
        phase,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    )
    try:
        return _parse_porcelain(result.stdout)
    except ValueError as exc:
        raise GitCloseError(phase, str(exc)) from exc


def _assert_repository_root(root: Path) -> None:
    result = _require_git(root, PRECHECK_FAILED, "rev-parse", "--show-toplevel")
    try:
        git_root = Path(result.stdout.strip()).resolve(strict=True)
    except (OSError, ValueError) as exc:
        raise GitCloseError(PRECHECK_FAILED, "Git root is invalid") from exc
    if git_root != root:
        raise GitCloseError(PRECHECK_FAILED, "Git root does not match helper root")


def _assert_branch_and_upstream(
    root: Path,
    branch: str,
    upstream: str,
    phase: str,
) -> tuple[str, str]:
    current = _run_git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if current.returncode != 0:
        raise GitCloseError(phase, "HEAD is detached")
    if current.stdout.strip() != branch:
        raise GitCloseError(phase, "Current branch does not match --branch")

    actual = _run_git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if actual.returncode != 0 or actual.stdout.strip() != upstream:
        raise GitCloseError(phase, "Configured upstream does not match --upstream")

    remote = _run_git(root, "config", "--get", f"branch.{branch}.remote")
    merge_ref = _run_git(root, "config", "--get", f"branch.{branch}.merge")
    if remote.returncode != 0 or merge_ref.returncode != 0:
        raise GitCloseError(phase, "Branch remote or merge ref is not configured")
    remote_name = remote.stdout.strip()
    destination_ref = merge_ref.stdout.strip()
    if not remote_name or not destination_ref.startswith("refs/heads/"):
        raise GitCloseError(phase, "Upstream remote/ref is not safely pushable")
    expected = f"{remote_name}/{destination_ref.removeprefix('refs/heads/')}"
    if expected != upstream:
        raise GitCloseError(phase, "--upstream is ambiguous for configured remote/ref")
    return remote_name, destination_ref


def _assert_no_operation_in_progress(root: Path) -> None:
    for ref in (
        "MERGE_HEAD",
        "REBASE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_HEAD",
    ):
        result = _run_git(root, "rev-parse", "--verify", "--quiet", ref)
        if result.returncode == 0:
            raise GitCloseError(PRECHECK_FAILED, f"Git operation in progress: {ref}")

    for path_name in ("rebase-merge", "rebase-apply", "BISECT_LOG"):
        result = _require_git(root, PRECHECK_FAILED, "rev-parse", "--git-path", path_name)
        operation_path = Path(result.stdout.strip())
        if not operation_path.is_absolute():
            operation_path = root / operation_path
        if operation_path.exists():
            raise GitCloseError(
                PRECHECK_FAILED,
                f"Git operation in progress: {path_name}",
            )


def _validate_paths(root: Path, paths: list[str]) -> tuple[str, ...]:
    if not paths:
        raise GitCloseError(PRECHECK_FAILED, "At least one --file is required")
    if len(set(paths)) != len(paths):
        raise GitCloseError(PRECHECK_FAILED, "--file paths must be unique")

    validated: list[str] = []
    for raw_path in paths:
        if not raw_path:
            raise GitCloseError(PRECHECK_FAILED, "--file path must not be empty")
        candidate_path = PurePosixPath(raw_path)
        if (
            candidate_path.is_absolute()
            or raw_path == "."
            or ".." in candidate_path.parts
            or raw_path != candidate_path.as_posix()
        ):
            raise GitCloseError(PRECHECK_FAILED, "Unsafe --file path")

        candidate = root.joinpath(*candidate_path.parts)
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(root)
        except (OSError, ValueError) as exc:
            raise GitCloseError(
                PRECHECK_FAILED,
                "--file path is outside the repository",
            ) from exc

        current = root
        for part in candidate_path.parts:
            current = current / part
            if current.is_symlink():
                raise GitCloseError(PRECHECK_FAILED, "--file path must not use a symlink")
        if not candidate.is_file():
            raise GitCloseError(PRECHECK_FAILED, "--file path must be a regular file")
        validated.append(raw_path)
    return tuple(validated)


def _assert_initial_scope(
    changes: tuple[GitChange, ...],
    allowlist: tuple[str, ...],
) -> None:
    if any(change.status[0] not in {" ", "?", "!"} for change in changes):
        raise GitCloseError(PRECHECK_FAILED, "Previously staged changes are present")
    if any("R" in change.status or "C" in change.status for change in changes):
        raise GitCloseError(PRECHECK_FAILED, "Renames and copies are unsupported")
    if any("D" in change.status for change in changes):
        raise GitCloseError(PRECHECK_FAILED, "Deletes are unsupported")

    changed_paths = {change.path for change in changes}
    if changed_paths != set(allowlist):
        raise GitCloseError(
            PRECHECK_FAILED,
            "Total local changes do not match the exact --file allowlist",
        )


def _ahead_behind(root: Path, phase: str) -> tuple[int, int]:
    result = _require_git(
        root,
        phase,
        "rev-list",
        "--left-right",
        "--count",
        "HEAD...@{upstream}",
    )
    values = result.stdout.split()
    if len(values) != 2:
        raise GitCloseError(phase, "Git ahead/behind output is malformed")
    try:
        return int(values[0]), int(values[1])
    except ValueError as exc:
        raise GitCloseError(phase, "Git ahead/behind output is malformed") from exc


def _staged_paths(root: Path, phase: str) -> set[str]:
    result = _require_git(root, phase, "diff", "--cached", "--name-only", "-z")
    return {path for path in result.stdout.split("\0") if path}


def _assert_staged_scope(root: Path, allowlist: tuple[str, ...]) -> None:
    if _staged_paths(root, STAGED_SCOPE_MISMATCH) != set(allowlist):
        raise GitCloseError(
            STAGED_SCOPE_MISMATCH,
            "Staged paths do not match the exact --file allowlist",
        )
    changes = _status(root, STAGED_SCOPE_MISMATCH)
    if (
        {change.path for change in changes} != set(allowlist)
        or any(change.status[0] == " " or change.status[1] != " " for change in changes)
    ):
        raise GitCloseError(
            STAGED_SCOPE_MISMATCH,
            "Unstaged or untracked changes remain after staging",
        )


def _assert_clean(root: Path, phase: str) -> None:
    if _status(root, phase):
        raise GitCloseError(phase, "Index or working tree is not clean")


def _commit_paths(root: Path) -> set[str]:
    result = _require_git(
        root,
        COMMIT_FAILED,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "-z",
        "HEAD",
    )
    return {path for path in result.stdout.split("\0") if path}


def _state_summary(root: Path, branch: str, upstream: str) -> str:
    head = _run_git(root, "rev-parse", "--short", "HEAD")
    ahead, behind = _ahead_behind(root, PUSH_FAILED)
    return (
        f"local commit={head.stdout.strip() or 'unknown'}; "
        f"branch={branch}; upstream={upstream}; "
        f"ahead={ahead}; behind={behind}"
    )


def close_git_changes(
    *,
    branch: str,
    upstream: str,
    message: str,
    files: list[str],
    root: Path = ROOT,
) -> str:
    """Commit and publish one exact allowlist after fail-fast checks.

    Commits and publishes one exact allowlist after fail-fast checks.
    """
    if not isinstance(message, str) or not message.strip():
        raise GitCloseError(PRECHECK_FAILED, "--message must not be blank")

    root = root.resolve()
    _assert_repository_root(root)
    allowlist = _validate_paths(root, files)
    remote, destination_ref = _assert_branch_and_upstream(
        root,
        branch,
        upstream,
        PRECHECK_FAILED,
    )
    _assert_no_operation_in_progress(root)
    _assert_initial_scope(_status(root, PRECHECK_FAILED), allowlist)
    if _ahead_behind(root, PRECHECK_FAILED) != (0, 0):
        raise GitCloseError(PRECHECK_FAILED, "HEAD and upstream must be synchronized")

    stage = _run_git(root, "add", "--", *allowlist)
    if stage.returncode != 0:
        raise GitCloseError(STAGING_FAILED, _output(stage) or "git add failed")
    _assert_staged_scope(root, allowlist)

    before_head = _require_git(root, COMMIT_FAILED, "rev-parse", "HEAD").stdout.strip()
    commit = _run_git(root, "commit", "-m", message)
    if commit.returncode != 0:
        raise GitCloseError(COMMIT_FAILED, _output(commit) or "git commit failed")

    after_head = _require_git(root, COMMIT_FAILED, "rev-parse", "HEAD").stdout.strip()
    parent = _require_git(root, COMMIT_FAILED, "rev-parse", "HEAD^").stdout.strip()
    if after_head == before_head or parent != before_head:
        raise GitCloseError(COMMIT_FAILED, "Commit did not create one expected child commit")
    if _commit_paths(root) != set(allowlist):
        raise GitCloseError(
            COMMIT_FAILED,
            f"Committed paths do not match allowlist; local commit {after_head} remains unpushed",
        )
    _assert_clean(root, COMMIT_FAILED)
    _assert_branch_and_upstream(root, branch, upstream, COMMIT_FAILED)
    if _ahead_behind(root, COMMIT_FAILED) != (1, 0):
        raise GitCloseError(
            COMMIT_FAILED,
            f"Unexpected post-commit relation; local commit {after_head} remains unpushed",
        )

    push = _run_git(root, "push", remote, f"HEAD:{destination_ref}")
    if push.returncode != 0:
        try:
            summary = _state_summary(root, branch, upstream)
        except GitCloseError:
            summary = f"local commit={after_head}; branch={branch}; upstream={upstream}"
        detail = _output(push) or "git push failed"
        raise GitCloseError(PUSH_FAILED, f"{detail}\n{summary}")

    _assert_branch_and_upstream(root, branch, upstream, FINAL_SYNC_FAILED)
    _assert_clean(root, FINAL_SYNC_FAILED)
    if _ahead_behind(root, FINAL_SYNC_FAILED) != (0, 0):
        raise GitCloseError(FINAL_SYNC_FAILED, "HEAD and upstream are not synchronized")
    return after_head


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely stage, commit, push, and verify one exact file allowlist."
    )
    parser.add_argument("--branch", required=True)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--file", action="append", required=True, dest="files")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        commit_hash = close_git_changes(
            branch=args.branch,
            upstream=args.upstream,
            message=args.message,
            files=args.files,
        )
    except GitCloseError as exc:
        print(f"{exc.phase}: {exc.detail}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"{PRECHECK_FAILED}: {exc}", file=sys.stderr)
        return 1
    print(f"Git close completed: {commit_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
