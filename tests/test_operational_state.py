import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.engineering import operational_state
from scripts.engineering.operational_state import (
    OperationalStateReport,
    ROOT_GIT_BASELINE,
    git_baseline_oid,
    git_baseline_timestamp,
    latest_git_commit_timestamp,
    render_operational_summary,
    validate_against_git,
    validate_operational_state,
)


def build_state(
    updated_at: str = "2026-08-05T12:00:00+00:00",
    git_baseline: str = "1" * 40,
) -> str:
    lines = [
        "# Estado operativo — LOGUIC English",
        "",
        f"Actualizado: {updated_at}",
        f"Baseline Git previa a este checkpoint: {git_baseline}",
        "",
    ]
    for section in (
        "Dirección vigente",
        "Último bloque cerrado",
        "Bloque activo",
        "Automatización disponible",
        "Método operativo vigente",
        "Fronteras obligatorias",
        "Próximo objetivo",
        "Archivos clave",
    ):
        lines.extend(
            [
                f"## {section}",
                "",
                f"Contenido de {section}.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def test_validate_compact_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(), encoding="utf-8")

    report = validate_operational_state(
        path,
        now=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
    )

    assert report.updated_at == datetime(
        2026,
        8,
        5,
        12,
        0,
        tzinfo=timezone.utc,
    )
    assert report.git_baseline == "1" * 40
    assert report.line_count < 140


def test_reject_missing_prior_git_baseline(tmp_path: Path) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(
        build_state().replace(
            f"Baseline Git previa a este checkpoint: {'1' * 40}\n",
            "",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exactly one prior Git baseline"):
        validate_operational_state(path)


def test_reject_duplicate_prior_git_baseline(tmp_path: Path) -> None:
    path = tmp_path / "estado-operativo.md"
    line = f"Baseline Git previa a este checkpoint: {'1' * 40}"
    path.write_text(build_state().replace(line, f"{line}\n{line}"), encoding="utf-8")

    with pytest.raises(ValueError, match="exactly one prior Git baseline"):
        validate_operational_state(path)


@pytest.mark.parametrize(
    "baseline",
    ["abc123", "A" * 40, "1" * 39, "1" * 41, f"{'1' * 40} "],
)
def test_reject_malformed_prior_git_baseline(
    tmp_path: Path,
    baseline: str,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(git_baseline=baseline), encoding="utf-8")

    with pytest.raises(ValueError, match="full lowercase OID"):
        validate_operational_state(path)


@pytest.mark.parametrize(
    "field",
    [
        "- HEAD publicado: `abc123`.",
        "- Branch: `master`.",
        "- Upstream: `origin/master`.",
        "- Ahead/behind: 0/0.",
        "- Working tree: clean.",
    ],
)
def test_reject_reserved_live_git_fields(
    tmp_path: Path,
    field: str,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state() + field + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must not declare live Git fields"):
        validate_operational_state(path)


def test_reject_stale_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(
        build_state("2026-07-01T12:00:00+00:00"),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Operational state is stale",
    ):
        validate_operational_state(
            path,
            now=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        )


def test_reject_missing_required_section(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    content = build_state().replace(
        "## Próximo objetivo",
        "## Objetivo eliminado",
    )
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Próximo objetivo",
    ):
        validate_operational_state(
            path,
            now=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        )


def test_reject_oversized_operational_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    content = build_state() + ("línea histórica\n" * 150)
    path.write_text(content, encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="exceeds 140 lines",
    ):
        validate_operational_state(
            path,
            now=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        )


def test_render_short_operational_summary(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(), encoding="utf-8")

    summary = render_operational_summary(path)

    assert "## Último bloque cerrado" in summary
    assert "## Bloque activo" in summary
    assert "## Próximo objetivo" in summary
    assert "## Dirección vigente" not in summary


@pytest.mark.parametrize(
    "updated_at",
    [
        "2026-08-05",
        "20260805T120000+0000",
        "2026-08-05T12:00:00",
        "2026-08-05T12:00:00Z",
        "2026-08-05T12:00:00.000000+00:00",
        "2026-08-05T12:00+00:00",
        "2026-08-05T12:00:00+0000",
        "2026-08-05T12:00:00+00:00 ",
    ],
)
def test_reject_noncanonical_update_timestamp(
    tmp_path: Path,
    updated_at: str,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(build_state(updated_at), encoding="utf-8")

    with pytest.raises(ValueError, match="update timestamp must use"):
        validate_operational_state(path)


def test_reject_future_update_timestamp_by_instant(
    tmp_path: Path,
) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(
        build_state("2026-08-05T14:00:01+02:00"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="timestamp is in the future"):
        validate_operational_state(
            path,
            now=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        )


def test_reject_duplicate_update_timestamps(tmp_path: Path) -> None:
    path = tmp_path / "estado-operativo.md"
    path.write_text(
        build_state().replace(
            "Actualizado: 2026-08-05T12:00:00+00:00",
            "Actualizado: 2026-08-05T12:00:00+00:00\n"
            "Actualizado: 2026-08-05T12:00:00+00:00",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exactly one update timestamp"):
        validate_operational_state(path)


def run_git(
    root: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


def initialize_repository(root: Path) -> None:
    run_git(root.parent, "init", "-q", str(root))
    run_git(root, "config", "user.name", "Operational State Test")
    run_git(root, "config", "user.email", "state@example.invalid")


def commit_at(root: Path, message: str, timestamp: str) -> None:
    environment = os.environ | {
        "GIT_AUTHOR_DATE": timestamp,
        "GIT_COMMITTER_DATE": timestamp,
    }
    run_git(root, "commit", "-q", "-m", message, env=environment)


def test_git_baseline_uses_parent_for_checkpoint_commit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    (root / "tracked.txt").write_text("initial\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")
    commit_at(root, "initial", "2026-08-24T10:00:00+00:00")
    prior_head = run_git(root, "rev-parse", "HEAD")

    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    updated_at = datetime(2026, 8, 24, 10, 0, 10, tzinfo=timezone.utc)
    state_path.write_text(
        build_state(updated_at.isoformat(), prior_head),
        encoding="utf-8",
    )
    run_git(root, "add", "docs/estado-operativo.md")
    commit_at(root, "checkpoint", "2026-08-24T10:00:20+00:00")

    baseline_timestamp = latest_git_commit_timestamp(root, "HEAD^")
    head_timestamp = latest_git_commit_timestamp(root)
    assert baseline_timestamp < updated_at < head_timestamp
    assert git_baseline_oid(root, state_path) == prior_head
    assert git_baseline_timestamp(root, state_path) == baseline_timestamp

    validate_against_git(
        OperationalStateReport(
            path=state_path,
            updated_at=updated_at,
            git_baseline=prior_head,
            line_count=1,
            sections=(),
        ),
        root,
    )


def test_git_baseline_omits_root_checkpoint_commit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    updated_at = datetime.now().astimezone().replace(microsecond=0)
    state_path.write_text(
        build_state(updated_at.isoformat(), ROOT_GIT_BASELINE),
        encoding="utf-8",
    )
    run_git(root, "add", "docs/estado-operativo.md")
    run_git(root, "commit", "-q", "-m", "root checkpoint")

    assert git_baseline_oid(root, state_path) == ROOT_GIT_BASELINE
    assert git_baseline_timestamp(root, state_path) is None
    validate_against_git(
        OperationalStateReport(
            path=state_path,
            updated_at=updated_at,
            git_baseline=ROOT_GIT_BASELINE,
            line_count=1,
            sections=(),
        ),
        root,
    )


def test_head_parent_error_is_not_treated_as_root(tmp_path: Path) -> None:
    with pytest.raises(subprocess.CalledProcessError):
        operational_state._head_has_parent(tmp_path)


def test_git_baseline_rejects_timestamp_older_than_head(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    (root / "tracked.txt").write_text("initial\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")
    run_git(root, "commit", "-q", "-m", "initial")
    head = run_git(root, "rev-parse", "HEAD")
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    state_path.write_text(build_state(git_baseline=head), encoding="utf-8")

    report = OperationalStateReport(
        path=state_path,
        updated_at=datetime.now().astimezone() - timedelta(days=1),
        git_baseline=head,
        line_count=1,
        sections=(),
    )

    with pytest.raises(ValueError, match="older than the Git baseline"):
        validate_against_git(report, root)


def test_git_baseline_uses_head_while_state_is_modified(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    state_path.write_text(
        build_state(updated_at, ROOT_GIT_BASELINE),
        encoding="utf-8",
    )
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "root checkpoint")
    head = run_git(root, "rev-parse", "HEAD")

    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    state_path.write_text(build_state(updated_at, head), encoding="utf-8")
    report = validate_operational_state(state_path)

    assert git_baseline_oid(root, state_path) == head
    validate_against_git(report, root)


def test_reject_incompatible_prior_git_baseline(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    state_path.write_text(
        build_state(updated_at, ROOT_GIT_BASELINE),
        encoding="utf-8",
    )
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "root checkpoint")
    state_path.write_text(build_state(updated_at, "2" * 40), encoding="utf-8")

    with pytest.raises(ValueError, match="baseline is incompatible"):
        validate_against_git(validate_operational_state(state_path), root)


def test_reject_clean_checkpoint_not_incorporated_by_head(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    initialize_repository(root)
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir()
    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    state_path.write_text(
        build_state(updated_at, ROOT_GIT_BASELINE),
        encoding="utf-8",
    )
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "root checkpoint")
    (root / "later.txt").write_text("later\n", encoding="utf-8")
    run_git(root, "add", "later.txt")
    run_git(root, "commit", "-q", "-m", "later without checkpoint")

    with pytest.raises(ValueError, match="does not incorporate checkpoint"):
        validate_against_git(validate_operational_state(state_path), root)
