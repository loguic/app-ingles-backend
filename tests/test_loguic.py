from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from scripts.engineering import conversation_checkpoint, loguic


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def state_document(*, baseline: str, next_objective: str) -> str:
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
        f"Actualizado: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Baseline Git previa a este checkpoint: {baseline}",
        "",
    ]
    for section in sections:
        content = f"Canonical {section}."
        if section == "Bloque activo":
            content = "\n".join((
                "BASELINE V0 is historical.",
                "",
                "### AI CONSTRUCTOR INTEGRATION V1",
                "",
                "Estado: IMPLEMENTED / LOCAL / NOT CLOSED / NOT PUBLISHED.",
            ))
        if section == "Próximo objetivo":
            content = next_objective
        if section == "Fronteras obligatorias":
            content = "- No activar contenido."
        lines.extend((f"## {section}", "", content, ""))
    return "\n".join(lines).rstrip() + "\n"


def repository(tmp_path: Path, name: str, *, backend: bool = False) -> Path:
    root = tmp_path / name
    root.mkdir()
    if backend:
        (root / "docs").mkdir()
        (root / "docs" / "estado-operativo.md").write_text(
            state_document(
                baseline="0" * 40,
                next_objective="NEXT = esperar autorización humana.",
            ),
            encoding="utf-8",
        )
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    git(root.parent, "init", "-q", str(root))
    git(root, "config", "user.name", "Entrypoint Test")
    git(root, "config", "user.email", "entrypoint@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "initial")
    git(root, "branch", "upstream-fixture")
    git(root, "branch", "--set-upstream-to=upstream-fixture")
    if backend:
        state_path = root / "docs" / "estado-operativo.md"
        state_path.write_text(
            state_document(
                baseline=git(root, "rev-parse", "HEAD"),
                next_objective="NEXT = esperar autorización humana.",
            ),
            encoding="utf-8",
        )
        git(root, "add", "docs/estado-operativo.md")
        git(root, "commit", "-q", "-m", "set state baseline")
    return root


def fixture(tmp_path: Path) -> tuple[Path, Path]:
    return repository(tmp_path, "backend", backend=True), repository(tmp_path, "frontend")


def test_resume_renders_compact_canonical_facts(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)

    output = loguic.render_resume(root=backend, frontend_root=frontend)

    assert "CHECKPOINT=PASS" in output
    assert "BACKEND=HEAD=" in output
    assert "FRONTEND=HEAD=" in output
    assert "ACTIVE_INCREMENT=AI CONSTRUCTOR INTEGRATION V1" in output
    assert "RESTRICTIONS=- No activar contenido." in output
    assert "NEXT=esperar autorización humana." in output
    assert "RECOMMENDED_ACTOR=HUMAN" in output
    assert "ROUTING=NONE" in output


def test_resume_reports_documented_dirty_state_without_writing(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    state_path = backend / "docs" / "estado-operativo.md"
    baseline = git(backend, "rev-parse", "HEAD")
    state_path.write_text(
        state_path.read_text(encoding="utf-8")
        .replace(
            f"Baseline Git previa a este checkpoint: {git(backend, 'rev-parse', 'HEAD^')}",
            f"Baseline Git previa a este checkpoint: {baseline}",
        )
        .replace(
            "Estado: IMPLEMENTED / LOCAL / NOT CLOSED / NOT PUBLISHED.",
            "Estado: IMPLEMENTED / LOCAL / NOT CLOSED / NOT PUBLISHED.\nDirty backend reconocido: `tracked.txt`, `docs/estado-operativo.md`.",
        ),
        encoding="utf-8",
    )
    (backend / "tracked.txt").write_text("changed\n", encoding="utf-8")
    before = git(backend, "status", "--porcelain=v1", "-z")

    output = loguic.render_resume(root=backend, frontend_root=frontend)

    assert "CHECKPOINT=PASS" in output
    assert "BACKEND=" in output and "tracked.txt" in output
    assert git(backend, "status", "--porcelain=v1", "-z") == before


def test_resume_fails_closed_when_frontend_is_missing(tmp_path: Path) -> None:
    backend, _ = fixture(tmp_path)

    output, exit_code = loguic.resume(root=backend, frontend_root=tmp_path / "missing")

    assert exit_code == 1
    assert "CHECKPOINT=PASS" in output
    assert "FRONTEND=UNAVAILABLE" in output
    assert "ERROR=frontend repository is missing" in output


def test_resume_fails_closed_when_checkpoint_is_invalid(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    (backend / "docs" / "estado-operativo.md").write_text("invalid\n", encoding="utf-8")

    output, exit_code = loguic.resume(root=backend, frontend_root=frontend)

    assert exit_code == 1
    assert "CHECKPOINT=BLOCKED" in output
    assert "BACKEND=UNAVAILABLE" in output
    assert "FRONTEND=UNAVAILABLE" in output


def test_resume_rejects_ambiguous_active_increment(tmp_path: Path) -> None:
    active_block = "\n".join((
        "Historical state.",
        "",
        "### FIRST ACTIVE INCREMENT",
        "",
        "Estado: IMPLEMENTED / LOCAL.",
        "",
        "### SECOND ACTIVE INCREMENT",
        "",
        "Estado: IMPLEMENTED / LOCAL.",
    ))

    with pytest.raises(ValueError, match="ambiguous active increments"):
        loguic._active_increment(active_block)


def test_parser_uses_project_relative_frontend_default() -> None:
    args = loguic.build_parser().parse_args(["resume"])

    assert args.frontend_root == (
        loguic.ROOT.parent.parent / "app_ingles_frontend" / "app_ingles"
    )


def test_direct_and_module_entrypoints_start(tmp_path: Path) -> None:
    script = loguic.ROOT / "scripts" / "engineering" / "loguic.py"
    commands = (
        (sys.executable, str(script), "--help"),
        (sys.executable, "-m", "scripts.engineering.loguic", "--help"),
    )

    for command in commands:
        result = subprocess.run(
            command,
            cwd=loguic.ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "Resume LOGUIC English" in result.stdout
