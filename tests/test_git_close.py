from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts.engineering.git_close import (
    COMMIT_FAILED,
    PRECHECK_FAILED,
    PUSH_FAILED,
    GitCloseError,
    close_git_changes,
)


def git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def create_repository(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", "--initial-branch=master", str(remote))
    repository = tmp_path / "repository"
    git(tmp_path, "clone", str(remote), str(repository))
    git(repository, "config", "user.name", "Git Close Test")
    git(repository, "config", "user.email", "git-close@example.test")
    (repository / "first.txt").write_text("first\n", encoding="utf-8")
    (repository / "unchanged.txt").write_text("unchanged\n", encoding="utf-8")
    git(repository, "add", "--", "first.txt", "unchanged.txt")
    git(repository, "commit", "-m", "initial")
    git(repository, "push", "-u", "origin", "master")
    return repository, remote


def close(repository: Path, files: list[str], message: str = "close docs") -> str:
    return close_git_changes(
        branch="master",
        upstream="origin/master",
        message=message,
        files=files,
        root=repository,
    )


def porcelain(repository: Path) -> str:
    return git(repository, "status", "--porcelain=v1", "--untracked-files=all").stdout


def relation(repository: Path) -> tuple[int, int]:
    values = git(
        repository,
        "rev-list",
        "--left-right",
        "--count",
        "HEAD...@{upstream}",
    ).stdout.split()
    return int(values[0]), int(values[1])


def test_happy_path_commits_pushes_and_synchronizes(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    commit_hash = close(repository, ["first.txt"], "docs finalize first")

    assert git(repository, "rev-parse", "HEAD").stdout.strip() == commit_hash
    assert git(repository, "log", "-1", "--format=%s").stdout.strip() == "docs finalize first"
    assert porcelain(repository) == ""
    assert relation(repository) == (0, 0)


def test_multiple_allowed_files_are_the_exact_commit_scope(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    (repository / "second.txt").write_text("second\n", encoding="utf-8")

    close(repository, ["first.txt", "second.txt"])

    committed = {
        path
        for path in git(
            repository,
            "diff-tree",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
        ).stdout.splitlines()
        if path
    }
    assert committed == {"first.txt", "second.txt"}
    assert porcelain(repository) == ""
    assert relation(repository) == (0, 0)


def test_unexpected_local_file_aborts_before_staging(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    (repository / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    before_head = git(repository, "rev-parse", "HEAD").stdout.strip()

    with pytest.raises(GitCloseError, match="exact --file allowlist") as error:
        close(repository, ["first.txt"])

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "rev-parse", "HEAD").stdout.strip() == before_head
    assert git(repository, "diff", "--cached", "--name-only").stdout == ""


def test_previously_staged_changes_abort_before_commit(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    git(repository, "add", "--", "first.txt")

    with pytest.raises(GitCloseError, match="Previously staged") as error:
        close(repository, ["first.txt"])

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "log", "-1", "--format=%s").stdout.strip() == "initial"


@pytest.mark.parametrize("message", ["", "   "])
def test_blank_message_is_rejected_without_git_effects(
    tmp_path: Path,
    message: str,
) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    with pytest.raises(GitCloseError, match="message must not be blank") as error:
        close(repository, ["first.txt"], message)

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "diff", "--cached", "--name-only").stdout == ""


@pytest.mark.parametrize("path", ["../outside.txt", "missing.txt"])
def test_invalid_file_paths_are_rejected(tmp_path: Path, path: str) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    with pytest.raises(GitCloseError) as error:
        close(repository, [path])

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "diff", "--cached", "--name-only").stdout == ""


def test_absolute_and_unchanged_allowed_paths_are_rejected(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    with pytest.raises(GitCloseError) as absolute_error:
        close(repository, [str(repository / "first.txt")])
    with pytest.raises(GitCloseError) as unchanged_error:
        close(repository, ["first.txt", "unchanged.txt"])

    assert absolute_error.value.phase == PRECHECK_FAILED
    assert unchanged_error.value.phase == PRECHECK_FAILED


def test_symlink_path_is_rejected(tmp_path: Path) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    (repository / "link.txt").symlink_to(repository / "first.txt")

    with pytest.raises(GitCloseError, match="symlink") as error:
        close(repository, ["link.txt"])

    assert error.value.phase == PRECHECK_FAILED


@pytest.mark.parametrize(
    ("branch", "upstream"),
    [("other", "origin/master"), ("master", "origin/other")],
)
def test_invalid_branch_or_upstream_is_rejected(
    tmp_path: Path,
    branch: str,
    upstream: str,
) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    with pytest.raises(GitCloseError) as error:
        close_git_changes(
            branch=branch,
            upstream=upstream,
            message="close docs",
            files=["first.txt"],
            root=repository,
        )

    assert error.value.phase == PRECHECK_FAILED


def test_ahead_precheck_rejects_without_creating_or_pushing_a_commit(
    tmp_path: Path,
) -> None:
    repository, remote = create_repository(tmp_path)
    (repository / "ahead.txt").write_text("ahead\n", encoding="utf-8")
    git(repository, "add", "--", "ahead.txt")
    git(repository, "commit", "-m", "existing local commit")
    assert porcelain(repository) == ""
    assert relation(repository) == (1, 0)
    remote_head = git(remote, "rev-parse", "refs/heads/master").stdout.strip()
    (repository / "first.txt").write_text("current change\n", encoding="utf-8")
    before_head = git(repository, "rev-parse", "HEAD").stdout.strip()

    with pytest.raises(GitCloseError, match="must be synchronized") as error:
        close(repository, ["first.txt"])

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "rev-parse", "HEAD").stdout.strip() == before_head
    assert git(repository, "log", "-1", "--format=%s").stdout.strip() == "existing local commit"
    assert git(remote, "rev-parse", "refs/heads/master").stdout.strip() == remote_head


def test_behind_precheck_rejects_without_creating_or_pushing_a_commit(
    tmp_path: Path,
) -> None:
    repository, remote = create_repository(tmp_path)
    rival = tmp_path / "rival"
    git(tmp_path, "clone", str(remote), str(rival))
    git(rival, "config", "user.name", "Rival")
    git(rival, "config", "user.email", "rival@example.test")
    (rival / "remote.txt").write_text("remote\n", encoding="utf-8")
    git(rival, "add", "--", "remote.txt")
    git(rival, "commit", "-m", "remote change")
    git(rival, "push", "origin", "master")
    git(repository, "fetch", "origin")
    assert porcelain(repository) == ""
    assert relation(repository) == (0, 1)
    remote_head = git(remote, "rev-parse", "refs/heads/master").stdout.strip()
    (repository / "first.txt").write_text("current change\n", encoding="utf-8")
    before_head = git(repository, "rev-parse", "HEAD").stdout.strip()

    with pytest.raises(GitCloseError, match="must be synchronized") as error:
        close(repository, ["first.txt"])

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "rev-parse", "HEAD").stdout.strip() == before_head
    assert git(remote, "rev-parse", "refs/heads/master").stdout.strip() == remote_head


def test_push_failure_preserves_local_commit(tmp_path: Path) -> None:
    repository, remote = create_repository(tmp_path)
    rival = tmp_path / "rival"
    git(tmp_path, "clone", str(remote), str(rival))
    git(rival, "config", "user.name", "Rival")
    git(rival, "config", "user.email", "rival@example.test")
    (rival / "remote.txt").write_text("remote\n", encoding="utf-8")
    git(rival, "add", "--", "remote.txt")
    git(rival, "commit", "-m", "remote change")
    git(rival, "push", "origin", "master")
    (repository / "first.txt").write_text("local\n", encoding="utf-8")

    with pytest.raises(GitCloseError, match="local commit=") as error:
        close(repository, ["first.txt"], "local close")

    assert error.value.phase == PUSH_FAILED
    assert git(repository, "log", "-1", "--format=%s").stdout.strip() == "local close"
    assert porcelain(repository) == ""
    ahead, behind = relation(repository)
    assert ahead >= 1
    assert behind == 0


def test_post_commit_dirty_worktree_prevents_push(tmp_path: Path) -> None:
    repository, remote = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    hook = repository / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nprintf 'late change\\n' >> first.txt\n", encoding="utf-8")
    hook.chmod(0o755)

    with pytest.raises(GitCloseError, match="not clean") as error:
        close(repository, ["first.txt"], "hook close")

    assert error.value.phase == COMMIT_FAILED
    assert git(repository, "log", "-1", "--format=%s").stdout.strip() == "hook close"
    assert porcelain(repository) == " M first.txt\n"
    assert git(remote, "show-ref", "--verify", "refs/heads/master").returncode == 0
    assert git(repository, "rev-parse", "HEAD").stdout.strip() != git(
        repository,
        "rev-parse",
        "@{upstream}",
    ).stdout.strip()
