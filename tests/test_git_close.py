from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import scripts.engineering.git_close as git_close_module

from scripts.engineering.git_close import (
    COMMIT_FAILED,
    FINAL_SYNC_FAILED,
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


def close(
    repository: Path,
    files: list[str],
    message: str = "close docs",
    publish_url: str | None = None,
) -> str:
    return close_git_changes(
        branch="master",
        upstream="origin/master",
        message=message,
        files=files,
        publish_url=publish_url,
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


def test_https_publish_url_pushes_without_changing_git_configuration(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository, remote = create_repository(tmp_path)
    configuration_before = (repository / ".git" / "config").read_text(encoding="utf-8")
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")

    monkeypatch.setattr(
        git_close_module,
        "_validate_publish_url",
        lambda publish_url: remote.as_uri(),
    )

    commit_hash = close(
        repository,
        ["first.txt"],
        "publish by alternate transport",
        publish_url="https://example.test/english.git",
    )

    assert git(repository, "rev-parse", "HEAD").stdout.strip() == commit_hash
    assert git(remote, "rev-parse", "refs/heads/master").stdout.strip() == commit_hash
    assert (repository / ".git" / "config").read_text(encoding="utf-8") == configuration_before
    assert porcelain(repository) == ""
    assert relation(repository) == (0, 0)


@pytest.mark.parametrize(
    "publish_url",
    [
        "",
        " https://example.test/repo.git",
        "http://example.test/repo.git",
        "ssh://example.test/repo.git",
        "git://example.test/repo.git",
        "file:///tmp/repo.git",
        "../repo.git",
        "-https://example.test/repo.git",
        "https://user:token@example.test/repo.git",
        "https://example.test/repo.git?token=value",
        "https://example.test/repo.git#fragment",
        "https://example.test:invalid/repo.git",
        "https://example.test:65536/repo.git",
        "https://example.test:0/repo.git",
        "https://exa mple.test/repo.git",
        "https://example.test/repo\n.git",
        "https://example.test/repo\t.git",
        "https://example.test\\repo.git",
    ],
)
def test_invalid_publish_url_is_rejected_before_git_effects(
    tmp_path: Path,
    publish_url: str,
) -> None:
    repository, _ = create_repository(tmp_path)
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    before_head = git(repository, "rev-parse", "HEAD").stdout.strip()

    with pytest.raises(GitCloseError, match="publish-url") as error:
        close(repository, ["first.txt"], publish_url=publish_url)

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "rev-parse", "HEAD").stdout.strip() == before_head
    assert git(repository, "diff", "--cached", "--name-only").stdout == ""


def test_publish_url_accepts_https_with_a_valid_explicit_port() -> None:
    publish_url = "https://example.test:8443/repo.git"

    assert git_close_module._validate_publish_url(publish_url) == publish_url


def test_publish_url_lookup_failure_does_not_expose_destination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    secret_url = "https://example.test/private-repository.git"

    def fail_lookup(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            ["git", *args],
            1,
            "",
            f"fatal: unable to access '{secret_url}'",
        )

    monkeypatch.setattr(git_close_module, "_run_git", fail_lookup)

    with pytest.raises(GitCloseError) as error:
        git_close_module._remote_ref_oid(
            tmp_path,
            secret_url,
            "refs/heads/master",
            PRECHECK_FAILED,
        )

    assert error.value.phase == PRECHECK_FAILED
    assert secret_url not in error.value.detail


def test_publish_url_push_failure_does_not_expose_destination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository, remote = create_repository(tmp_path)
    transport_url = remote.as_uri()
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    before_configuration = (repository / ".git" / "config").read_text(encoding="utf-8")
    original_run_git = git_close_module._run_git

    def fail_push(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args[:1] == ("push",) and args[1] == transport_url:
            return subprocess.CompletedProcess(
                ["git", *args],
                1,
                "",
                f"fatal: unable to access '{transport_url}'",
            )
        return original_run_git(root, *args)

    monkeypatch.setattr(git_close_module, "_validate_publish_url", lambda value: transport_url)
    monkeypatch.setattr(git_close_module, "_run_git", fail_push)

    with pytest.raises(GitCloseError) as error:
        close(
            repository,
            ["first.txt"],
            publish_url="https://example.test/private-repository.git",
        )

    assert error.value.phase == PUSH_FAILED
    assert transport_url not in error.value.detail
    assert (repository / ".git" / "config").read_text(encoding="utf-8") == before_configuration
    assert relation(repository) == (1, 0)


def test_publish_url_fetch_failure_does_not_expose_destination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository, remote = create_repository(tmp_path)
    transport_url = remote.as_uri()
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    before_configuration = (repository / ".git" / "config").read_text(encoding="utf-8")
    original_run_git = git_close_module._run_git
    push_destinations: list[str] = []

    def fail_fetch(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        if args[:1] == ("push",):
            push_destinations.append(args[1])
        if args[:1] == ("fetch",) and args[2] == transport_url:
            return subprocess.CompletedProcess(
                ["git", *args],
                1,
                "",
                f"fatal: unable to access '{transport_url}'",
            )
        return original_run_git(root, *args)

    monkeypatch.setattr(git_close_module, "_validate_publish_url", lambda value: transport_url)
    monkeypatch.setattr(git_close_module, "_run_git", fail_fetch)

    with pytest.raises(GitCloseError) as error:
        close(
            repository,
            ["first.txt"],
            publish_url="https://example.test/private-repository.git",
        )

    assert error.value.phase == FINAL_SYNC_FAILED
    assert transport_url not in error.value.detail
    assert "the commit may already be published remotely" in error.value.detail
    assert push_destinations == [transport_url]
    assert "origin" not in push_destinations
    assert git(remote, "rev-parse", "refs/heads/master").stdout.strip() == git(
        repository,
        "rev-parse",
        "HEAD",
    ).stdout.strip()
    assert (repository / ".git" / "config").read_text(encoding="utf-8") == before_configuration
    assert relation(repository) == (1, 0)


def test_cli_forwards_publish_url_to_close_git_changes(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def capture_close_git_changes(**kwargs: object) -> str:
        captured.update(kwargs)
        return "abc123"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "git_close.py",
            "--branch",
            "master",
            "--upstream",
            "origin/master",
            "--message",
            "close docs",
            "--file",
            "docs/estado-operativo.md",
            "--file",
            "docs/bitacora.md",
            "--publish-url",
            "https://example.test/repo.git",
        ],
    )
    monkeypatch.setattr(git_close_module, "close_git_changes", capture_close_git_changes)

    assert git_close_module.main() == 0
    assert captured == {
        "branch": "master",
        "upstream": "origin/master",
        "message": "close docs",
        "files": ["docs/estado-operativo.md", "docs/bitacora.md"],
        "publish_url": "https://example.test/repo.git",
    }


def test_publish_url_must_match_upstream_before_staging(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository, remote = create_repository(tmp_path)
    alternate_remote = tmp_path / "alternate.git"
    git(tmp_path, "init", "--bare", "--initial-branch=master", str(alternate_remote))
    rival = tmp_path / "rival"
    git(tmp_path, "clone", str(remote), str(rival))
    git(rival, "config", "user.name", "Alternate Publisher")
    git(rival, "config", "user.email", "alternate@example.test")
    git(rival, "remote", "add", "alternate", str(alternate_remote))
    (rival / "alternate.txt").write_text("alternate\n", encoding="utf-8")
    git(rival, "add", "--", "alternate.txt")
    git(rival, "commit", "-m", "alternate state")
    git(rival, "push", "alternate", "master")
    (repository / "first.txt").write_text("changed\n", encoding="utf-8")
    before_head = git(repository, "rev-parse", "HEAD").stdout.strip()

    monkeypatch.setattr(
        git_close_module,
        "_validate_publish_url",
        lambda publish_url: alternate_remote.as_uri(),
    )

    with pytest.raises(GitCloseError, match="does not match") as error:
        close(
            repository,
            ["first.txt"],
            publish_url="https://example.test/alternate.git",
        )

    assert error.value.phase == PRECHECK_FAILED
    assert git(repository, "rev-parse", "HEAD").stdout.strip() == before_head
    assert git(repository, "diff", "--cached", "--name-only").stdout == ""


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
