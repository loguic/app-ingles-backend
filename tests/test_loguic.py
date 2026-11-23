from __future__ import annotations

import subprocess
from dataclasses import replace
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



def test_resume_accepts_explicit_idle_without_writing(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    state_path = backend / "docs" / "estado-operativo.md"
    previous = git(backend, "rev-parse", "HEAD^")
    current = git(backend, "rev-parse", "HEAD")
    document = state_path.read_text(encoding="utf-8")

    assert f"Baseline Git previa a este checkpoint: {previous}" in document
    document = document.replace(
        f"Baseline Git previa a este checkpoint: {previous}",
        f"Baseline Git previa a este checkpoint: {current}",
    ).replace(
        "BASELINE V0 is historical.\n\n### AI CONSTRUCTOR INTEGRATION V1",
        "Sin incremento técnico abierto.\n\nBASELINE V0 is historical.",
    ).replace(
        "Estado: IMPLEMENTED / LOCAL / NOT CLOSED / NOT PUBLISHED.",
        "Dirty backend reconocido: `docs/estado-operativo.md`.",
    )
    assert "### AI CONSTRUCTOR INTEGRATION V1" not in document
    state_path.write_text(document, encoding="utf-8")
    before = git(backend, "status", "--porcelain=v1", "-z")

    output, exit_code = loguic.resume(root=backend, frontend_root=frontend)

    assert exit_code == 0, output
    assert "CHECKPOINT=PASS" in output
    assert "ACTIVE_INCREMENT=NONE" in output
    assert "FRONTEND=HEAD=" in output
    assert "RECOMMENDED_ACTOR=HUMAN" in output
    assert git(backend, "status", "--porcelain=v1", "-z") == before


def test_active_increment_rejects_undeclared_idle() -> None:
    with pytest.raises(ValueError, match="no active local increment"):
        loguic._active_increment("Historical closure only.")


def test_active_increment_rejects_idle_active_conflict() -> None:
    active_block = (
        "Sin incremento técnico abierto.\n\n"
        "### CONFLICTING INCREMENT\n\n"
        "Estado: IMPLEMENTED / LOCAL.\n"
    )
    with pytest.raises(ValueError, match="both idle and an active increment"):
        loguic._active_increment(active_block)



def test_resume_blocks_reconciliation_without_supervisor_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend, frontend = fixture(tmp_path)

    original = loguic.development_supervisor.build_supervisor(
        root=backend, frontend_root=frontend
    )
    assert original.supervisor_status == "PASS"

    inconsistent = replace(
        original,
        supervisor_status="RECONCILIATION_REQUIRED",
        unexpected_backend_dirty_paths=("unexpected.txt",),
        continuity_safe=False,
        error=None,
    )

    monkeypatch.setattr(
        loguic.development_supervisor,
        "build_supervisor",
        lambda **kwargs: inconsistent,
    )

    output, exit_code = loguic.resume(
        root=backend, frontend_root=frontend
    )

    assert exit_code == 1
    assert "CHECKPOINT=BLOCKED" in output
    assert "supervisor status=RECONCILIATION_REQUIRED" in output
    assert "unexpected.txt" in output


def test_parser_uses_project_relative_frontend_default() -> None:
    args = loguic.build_parser().parse_args(["resume"])

    assert args.frontend_root == (
        loguic.ROOT.parent.parent / "app_ingles_frontend" / "app_ingles"
    )


def test_progress_parses_and_groups_the_24_qualitative_deliverables(
    tmp_path: Path,
) -> None:
    roadmap = tmp_path / "roadmap.md"
    rows = []
    states = ("IMPLEMENTADO", "PROTOTIPO", "DOCUMENTADO")
    for outcome in range(1, 9):
        for delivery in range(1, 4):
            rows.append(
                f"| {outcome}.{delivery} | Entregable {outcome}.{delivery} | "
                f"{states[delivery - 1]} técnico; evidencia pendiente |"
            )
    roadmap.write_text(
        "\n".join((
            "## Plan de innovación MVP — especificación documental provisional",
            "",
            "| ID | Entregable | Estado / validación humana |",
            "|---|---|---|",
            *rows,
            "",
            "## Matriz V0 de trazabilidad cualitativa",
        )),
        encoding="utf-8",
    )

    matrix = loguic._progress_matrix(roadmap)
    output = loguic._render_progress_matrix(matrix)

    assert len(matrix) == 24
    assert "RESULTADO 1 — PRE-A1 Y DIAGNÓSTICO" in output
    assert "TÉCNICO=IMPLEMENTADO:1 PROTOTIPO:1 DOCUMENTADO:1" in output
    assert "PRODUCTO_ACREDITADO=SIN ACREDITAR" in output
    assert "EXPERIENCIA_UTILIZABLE=PENDIENTE DE VALIDACIÓN" in output
    assert "MVP=NO MEDIBLE" in output


def test_progress_rejects_an_incomplete_or_ambiguous_matrix(tmp_path: Path) -> None:
    roadmap = tmp_path / "roadmap.md"
    roadmap.write_text(
        "\n".join((
            "## Plan de innovación MVP — especificación documental provisional",
            "",
            "| ID | Entregable | Estado / validación humana |",
            "|---|---|---|",
            "| 1.1 | Uno | IMPLEMENTADO técnico |",
            "",
            "## Matriz V0 de trazabilidad cualitativa",
        )),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exactly 24 deliverables"):
        loguic._progress_matrix(roadmap)


def test_progress_dashboard_is_readable_without_tty_colors_and_adapts_width() -> None:
    matrix = tuple(
        loguic.ProgressDeliverable(f"{outcome}.{delivery}", "PROTOTIPO")
        for outcome in range(1, 9)
        for delivery in range(1, 4)
    )

    plain = loguic._render_progress_dashboard(
        matrix,
        active_increment="INCREMENTO LOCAL",
        next_objective=(
            "Esperar autorización humana para la siguiente verificación "
            "sin perder este texto final."
        ),
        product_achievement="NO VERIFICADO · sin hito de producto acreditado canónico.",
        technical_closure="A1-V4: CLOSED / PUBLISHED / SYNCED.",
        color=False,
        width=64,
    )
    colored = loguic._render_progress_dashboard(
        matrix,
        active_increment="INCREMENTO LOCAL",
        next_objective="Esperar autorización humana para la siguiente verificación.",
        product_achievement="NO VERIFICADO · sin hito de producto acreditado canónico.",
        technical_closure=None,
        color=True,
        width=64,
    )

    assert "LOGUIC ENGLISH · MISSION CONTROL" in plain
    assert "PRODUCTO" in plain and "INGENIERÍA" in plain
    assert "EXPERIENCIA DEL ESTUDIANTE" in plain
    assert "MISIÓN ACTUAL" in plain
    assert "ÚLTIMO HITO DE PRODUCTO" in plain
    assert "ÚLTIMO CIERRE TÉCNICO" in plain
    assert "sin perder este texto final." in plain
    assert "…" not in plain
    assert "NO EVALUADO ≠ SIN ACREDITAR" in plain
    assert "\x1b[" not in plain
    assert "\x1b[" in colored
    assert all(len(line) <= 64 for line in plain.splitlines())


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
