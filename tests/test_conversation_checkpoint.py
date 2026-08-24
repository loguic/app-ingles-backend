from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.engineering import conversation_checkpoint


def run_git(root: Path, *args: str) -> str:
    """Run Git inside one isolated test repository.

    Ejecuta Git dentro de un repositorio aislado de prueba.
    """
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def state_document(
    updated_at: str,
    recognized_paths: tuple[str, ...] = (
        "tracked.txt",
        "new file.txt",
        "renamed file.txt",
        "staged.txt",
        "untracked.txt",
    ),
) -> str:
    """Build the smallest valid canonical operational state.

    Construye el estado operativo canónico válido más pequeño.
    """
    sections = (
        "Dirección vigente",
        "Último bloque cerrado",
        "Bloque activo",
        "Automatización disponible",
        "Método operativo vigente",
        "Fronteras obligatorias",
        "Próximo objetivo",
        "Archivos clave",
    )
    lines = [
        "# Estado operativo — LOGUIC English",
        "",
        f"Actualizado: {updated_at}",
        "",
    ]
    for section in sections:
        lines.extend([f"## {section}", "", f"Contenido {section}."])
        if section == "Archivos clave":
            lines.extend(f"- `{path}`;" for path in recognized_paths)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def create_repository(tmp_path: Path) -> tuple[Path, Path]:
    """Create an isolated repository with canonical state and one commit.

    Crea un repositorio aislado con estado canónico y un commit.
    """
    root = tmp_path / "repository"
    state_path = root / "docs" / "estado-operativo.md"
    state_path.parent.mkdir(parents=True)
    state_path.write_text(
        state_document(
            datetime.now().astimezone().isoformat(timespec="seconds")
        ),
        encoding="utf-8",
    )
    (root / "tracked.txt").write_text("original\n", encoding="utf-8")
    run_git(root.parent, "init", "-q", str(root))
    run_git(root, "config", "user.name", "Checkpoint Test")
    run_git(root, "config", "user.email", "checkpoint@example.invalid")
    run_git(root, "add", ".")
    run_git(root, "commit", "-q", "-m", "initial checkpoint")
    return root, state_path


def build(root: Path, state_path: Path, command: str = "prepare") -> str:
    """Build one checkpoint against the isolated repository.

    Construye un checkpoint sobre el repositorio aislado.
    """
    return conversation_checkpoint.build_checkpoint(
        command,
        root=root,
        state_path=state_path,
    )


def test_prepare_clean_repository_without_upstream(tmp_path: Path) -> None:
    """Describe a clean repository and absent upstream without inference.

    Describe un repositorio limpio y sin upstream sin inferencias.
    """
    root, state_path = create_repository(tmp_path)

    output = build(root, state_path)

    assert "- Working tree: clean" in output
    assert "- Upstream: none" in output
    assert "- Local relation: unavailable without upstream" in output
    assert "the only source of truth" in output
    assert "were not rerun" in output


def test_reports_staged_change(tmp_path: Path) -> None:
    """Report a staged path without showing its content.

    Informa una ruta staged sin mostrar su contenido.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("secret staged content\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")

    output = build(root, state_path)

    assert '`M ` `"tracked.txt"`' in output
    assert "secret staged content" not in output


def test_reports_unstaged_change(tmp_path: Path) -> None:
    """Report an unstaged path using its porcelain status.

    Informa una ruta unstaged mediante su estado porcelain.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

    output = build(root, state_path)

    assert '` M` `"tracked.txt"`' in output


def test_reports_untracked_path(tmp_path: Path) -> None:
    """Report an untracked path without reading its content.

    Informa una ruta untracked sin leer su contenido.
    """
    root, state_path = create_repository(tmp_path)
    (root / "new file.txt").write_text("private\n", encoding="utf-8")

    output = build(root, state_path)

    assert '`??` `"new file.txt"`' in output
    assert "private" not in output


def test_reports_combined_states_and_rename(tmp_path: Path) -> None:
    """Report staged, unstaged, untracked and renamed paths together.

    Informa conjuntamente rutas staged, unstaged, untracked y renombradas.
    """
    root, state_path = create_repository(tmp_path)
    (root / "staged.txt").write_text("base\n", encoding="utf-8")
    run_git(root, "add", "staged.txt")
    run_git(root, "commit", "-q", "-m", "add staged fixture")

    run_git(root, "mv", "staged.txt", "renamed file.txt")
    (root / "tracked.txt").write_text("unstaged\n", encoding="utf-8")
    (root / "untracked.txt").write_text("new\n", encoding="utf-8")

    output = build(root, state_path)

    assert '`R ` `"renamed file.txt" (from "staged.txt")`' in output
    assert '` M` `"tracked.txt"`' in output
    assert '`??` `"untracked.txt"`' in output


def test_allows_documented_dirty_path(tmp_path: Path) -> None:
    """Allow a tracked change named exactly by canonical state.

    Permite un cambio tracked nombrado exactamente por el estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")

    assert "Working tree: 1 Git status record" in build(root, state_path)


def test_allows_documented_untracked_path(tmp_path: Path) -> None:
    """Allow an untracked path named exactly by canonical state.

    Permite una ruta untracked nombrada exactamente por el estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    (root / "untracked.txt").write_text("new\n", encoding="utf-8")

    assert '`??` `"untracked.txt"`' in build(root, state_path)


@pytest.mark.parametrize("untracked", [False, True])
def test_rejects_undocumented_dirty_or_untracked_path(
    tmp_path: Path,
    untracked: bool,
) -> None:
    """Reject tracked and untracked paths absent from canonical state.

    Rechaza rutas tracked y untracked ausentes del estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    path = root / ("unknown.txt" if untracked else "tracked.txt")
    if not untracked:
        state_path.write_text(
            state_document(
                datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                (),
            ),
            encoding="utf-8",
        )
        run_git(root, "add", "docs/estado-operativo.md")
        run_git(root, "commit", "-q", "-m", "remove recognized paths")
    path.write_text("changed\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Operational state omits local paths"):
        build(root, state_path)


def test_rejects_all_undocumented_paths_in_one_error(tmp_path: Path) -> None:
    """Report every omitted path deterministically in one failure.

    Informa determinísticamente todas las rutas omitidas en un único fallo.
    """
    root, state_path = create_repository(tmp_path)
    (root / "tracked.txt").write_text("changed\n", encoding="utf-8")
    (root / "unknown.txt").write_text("new\n", encoding="utf-8")

    with pytest.raises(ValueError) as captured:
        build(root, state_path)

    assert '"unknown.txt"' in str(captured.value)
    assert '"tracked.txt"' not in str(captured.value)


def test_rename_requires_documented_source_and_destination(tmp_path: Path) -> None:
    """Require exact recognition of both paths in a rename.

    Exige reconocimiento exacto de ambas rutas de un rename.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "mv", "tracked.txt", "renamed file.txt")

    assert '`R ` `"renamed file.txt" (from "tracked.txt")`' in build(
        root,
        state_path,
    )


def test_rename_rejects_undocumented_destination(tmp_path: Path) -> None:
    """Reject a rename when its destination is absent from canonical state.

    Rechaza un rename cuyo destino está ausente del estado canónico.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "mv", "tracked.txt", "unknown-name.txt")

    with pytest.raises(ValueError, match='"unknown-name.txt"'):
        build(root, state_path)


@pytest.mark.parametrize(
    "path",
    [
        "name`with-backtick.txt",
        "name\nwith-newline.txt",
        "name\x01with-control.txt",
        "name\u0085with-next-line.txt",
        "name\u2028with-line-separator.txt",
        "name\u2029with-paragraph-separator.txt",
    ],
)
def test_git_paths_use_reversible_json_representation(path: str) -> None:
    """Escape Markdown-sensitive and control characters in Git paths.

    Escapa caracteres de rutas Git sensibles a Markdown o de control.
    """
    rendered = conversation_checkpoint._format_git_path(path)

    assert conversation_checkpoint.json.loads(rendered) == path
    assert "\n" not in rendered
    assert "\x01" not in rendered
    assert "\u0085" not in rendered
    assert "\u2028" not in rendered
    assert "\u2029" not in rendered
    if "`" in path:
        assert "`" not in rendered
        assert "\\u0060" in rendered


def test_rename_paths_share_safe_json_representation() -> None:
    """Render both rename paths without literal line or control breaks.

    Renderiza ambas rutas de rename sin saltos ni controles literales.
    """
    change = conversation_checkpoint.GitChange(
        status="R ",
        path="new`name\n.txt",
        original_path="old\x02name.txt",
    )

    rendered = conversation_checkpoint._format_change(change)

    assert "\n" not in rendered
    assert "\x02" not in rendered
    assert '"new\\u0060name\\n.txt"' in rendered
    assert '"old\\u0002name.txt"' in rendered


def test_reports_local_ahead_and_behind_against_upstream(tmp_path: Path) -> None:
    """Calculate ahead and behind only from local references.

    Calcula ahead y behind únicamente desde referencias locales.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "branch", "upstream-fixture")
    run_git(root, "branch", "--set-upstream-to=upstream-fixture")

    output = build(root, state_path)

    assert "- Upstream: `upstream-fixture`" in output
    assert "- Local relation: ahead 0, behind 0" in output


def test_reports_detached_head(tmp_path: Path) -> None:
    """Represent detached HEAD without inventing a branch.

    Representa detached HEAD sin inventar una rama.
    """
    root, state_path = create_repository(tmp_path)
    run_git(root, "checkout", "-q", "--detach", "HEAD")

    output = build(root, state_path, command="resume")

    assert "- Command: `resume`." in output
    assert "- Branch: detached HEAD" in output


def test_fail_closed_for_invalid_operational_state(tmp_path: Path) -> None:
    """Reject invalid canonical state before inspecting Git.

    Rechaza estado canónico inválido antes de inspeccionar Git.
    """
    root, state_path = create_repository(tmp_path)
    state_path.write_text("invalid\n", encoding="utf-8")

    with pytest.raises(ValueError, match="title is invalid"):
        build(root, state_path)


def test_fail_closed_for_state_older_than_latest_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Reject a canonical state demonstrably older than Git.

    Rechaza un estado canónico demostrablemente anterior a Git.
    """
    root, state_path = create_repository(tmp_path)
    report_at = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
    (root / "tracked.txt").write_text("newer\n", encoding="utf-8")
    run_git(root, "add", "tracked.txt")
    run_git(root, "commit", "-q", "-m", "newer than state")
    state_path.write_text(
        state_document(report_at.isoformat()),
        encoding="utf-8",
    )
    validate_state = conversation_checkpoint.validate_operational_state
    monkeypatch.setattr(
        conversation_checkpoint,
        "validate_operational_state",
        lambda path: validate_state(
            path,
            now=report_at,
        ),
    )

    with pytest.raises(ValueError, match="older than the Git baseline"):
        build(root, state_path)
