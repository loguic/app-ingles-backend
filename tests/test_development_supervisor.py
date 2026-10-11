from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

from scripts.engineering import development_supervisor
from scripts.engineering.operational_state import ROOT_GIT_BASELINE


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def state_document(
    *,
    paths: tuple[str, ...],
    backend_paths: tuple[str, ...] = (),
    frontend_paths: tuple[str, ...] = (),
    unrelated_active_code: tuple[str, ...] = (),
    next_objective: str,
    baseline: str = ROOT_GIT_BASELINE,
) -> str:
    sections = (
        "Dirección vigente", "Último bloque cerrado", "Bloque activo", "Automatización disponible",
        "Método operativo vigente", "Fronteras obligatorias", "Próximo objetivo", "Archivos clave",
    )
    lines = ["# Estado operativo — LOGUIC English", "", f"Actualizado: {datetime.now().astimezone().isoformat(timespec='seconds')}", f"Baseline Git previa a este checkpoint: {baseline}", ""]
    for section in sections:
        content = f"Canonical {section}."
        if section == "Bloque activo":
            content = "Active block complete semantic text."
        if section == "Próximo objetivo":
            content = next_objective
        lines.extend((f"## {section}", "", content))
        if section == "Bloque activo" and backend_paths:
            lines.append(
                "Dirty backend reconocido: "
                + ", ".join(f"`{path}`" for path in backend_paths)
                + "."
            )
        if section == "Bloque activo" and frontend_paths:
            lines.append(
                "Dirty frontend reconocido: "
                + ", ".join(f"`{path}`" for path in frontend_paths)
                + "."
            )
        if section == "Bloque activo":
            lines.extend(f"Unrelated active reference `{path}`." for path in unrelated_active_code)
        if section == "Archivos clave":
            lines.extend(f"- `{path}`" for path in paths)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def repository(
    tmp_path: Path,
    name: str,
    *,
    backend: bool = False,
    backend_paths: tuple[str, ...] = (),
    frontend_paths: tuple[str, ...] = (),
    unrelated_active_code: tuple[str, ...] = (),
) -> Path:
    root = tmp_path / name
    (root / "docs").mkdir(parents=True)
    if backend:
        (root / "docs" / "estado-operativo.md").write_text(
            state_document(
                paths=("tracked.txt",),
                backend_paths=backend_paths,
                frontend_paths=frontend_paths,
                unrelated_active_code=unrelated_active_code,
                next_objective="NEXT = tras aceptación/cierre de este incremento local `Development Supervisor v1`, Human Visual Review de `PREMIUM VOICE INTERACTION`.",
            ),
            encoding="utf-8",
        )
    else:
        (root / "frontend.txt").write_text("base\n", encoding="utf-8")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    git(root.parent, "init", "-q", str(root))
    git(root, "config", "user.name", "Supervisor Test")
    git(root, "config", "user.email", "supervisor@example.invalid")
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", "initial")
    git(root, "branch", "upstream-fixture")
    git(root, "branch", "--set-upstream-to=upstream-fixture")
    return root


def fixture(
    tmp_path: Path,
    *,
    backend_paths: tuple[str, ...] = ("tracked.txt",),
    frontend_paths: tuple[str, ...] = (),
    unrelated_active_code: tuple[str, ...] = (),
) -> tuple[Path, Path]:
    return (
        repository(
            tmp_path,
            "backend",
            backend=True,
            backend_paths=backend_paths,
            frontend_paths=frontend_paths,
            unrelated_active_code=unrelated_active_code,
        ),
        repository(tmp_path, "frontend"),
    )


def test_normal_resumable_documented_dirty_state(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    (backend / "tracked.txt").write_text("changed\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "PASS"
    assert state.continuity_safe is True
    assert state.unexpected_backend_dirty_paths == ()


def test_unexpected_backend_dirty_path_requires_reconciliation(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    (backend / "unknown.txt").write_text("unexpected\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "RECONCILIATION_REQUIRED"
    assert state.unexpected_backend_dirty_paths == ("unknown.txt",)


def test_documented_frontend_dirty_state_is_resumable(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path, frontend_paths=("frontend.txt",))
    (frontend / "frontend.txt").write_text("changed\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "PASS"
    assert state.expected_frontend_dirty_paths == ("frontend.txt",)
    assert state.unexpected_frontend_dirty_paths == ()


def test_undocumented_frontend_dirty_path_requires_reconciliation(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path, frontend_paths=("frontend.txt",))
    (frontend / "frontend.txt").write_text("changed\n", encoding="utf-8")
    (frontend / "unknown.txt").write_text("unexpected\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "RECONCILIATION_REQUIRED"
    assert state.unexpected_frontend_dirty_paths == ("unknown.txt",)


def test_frontend_documented_path_does_not_authorize_backend_collision(tmp_path: Path) -> None:
    backend, frontend = fixture(
        tmp_path,
        backend_paths=(),
        frontend_paths=("lib/example.dart",),
    )
    collision = backend / "lib" / "example.dart"
    collision.parent.mkdir()
    collision.write_text("unexpected\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "RECONCILIATION_REQUIRED"
    assert state.unexpected_backend_dirty_paths == ("lib/example.dart",)


def test_backend_documented_path_does_not_authorize_frontend_collision(tmp_path: Path) -> None:
    backend, frontend = fixture(
        tmp_path,
        backend_paths=("shared/example.txt",),
        frontend_paths=(),
    )
    collision = frontend / "shared" / "example.txt"
    collision.parent.mkdir()
    collision.write_text("unexpected\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "RECONCILIATION_REQUIRED"
    assert state.unexpected_frontend_dirty_paths == ("shared/example.txt",)


def test_unrelated_inline_code_does_not_authorize_backend_dirty_path(tmp_path: Path) -> None:
    backend, frontend = fixture(
        tmp_path,
        backend_paths=(),
        unrelated_active_code=("unrelated.txt",),
    )
    (backend / "unrelated.txt").write_text("unexpected\n", encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "RECONCILIATION_REQUIRED"
    assert state.unexpected_backend_dirty_paths == ("unrelated.txt",)


def test_checkpoint_failure_fails_closed(tmp_path: Path, monkeypatch) -> None:
    backend, frontend = fixture(tmp_path)
    monkeypatch.setattr(development_supervisor.conversation_checkpoint, "build_checkpoint", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("checkpoint failure")))

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "BLOCKED"
    assert state.error == "checkpoint failure"


def test_clean_state_and_human_next_decision(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    assert state.supervisor_status == "PASS"
    assert state.backend and state.backend.dirty_paths == ()
    assert state.actor == "HUMAN"
    assert state.codex_required is False
    assert "ACTOR=HUMAN" in development_supervisor.render_next(state)
    assert "CODEX_REQUIRED=NO" in development_supervisor.render_next(state)


def test_explicit_human_authorization_next_routes_to_human_without_duplicate_prefix(
    tmp_path: Path,
) -> None:
    backend, frontend = fixture(
        tmp_path,
        backend_paths=("tracked.txt", "docs/estado-operativo.md"),
    )
    state_path = backend / "docs" / "estado-operativo.md"
    next_objective = "NEXT = no iniciar el siguiente incremento sin autorización humana explícita."
    state_path.write_text(
        state_document(
            paths=("tracked.txt",),
            backend_paths=("docs/estado-operativo.md",),
            next_objective=next_objective,
            baseline=git(backend, "rev-parse", "HEAD"),
        ),
        encoding="utf-8",
    )

    state = development_supervisor.build_supervisor(
        root=backend,
        frontend_root=frontend,
        state_path=state_path,
    )

    assert state.supervisor_status == "PASS", state.error
    assert state.actor == "HUMAN"
    assert state.codex_required is False
    assert state.routing is None
    assert "OBJECTIVE=no iniciar el siguiente incremento" in development_supervisor.render_next(state)
    assert "NEXT=NEXT" not in development_supervisor.render_status(state)


def test_authorized_technical_next_keeps_codex_routing(tmp_path: Path) -> None:
    backend, frontend = fixture(
        tmp_path,
        backend_paths=("tracked.txt", "docs/estado-operativo.md"),
    )
    state_path = backend / "docs" / "estado-operativo.md"
    state_path.write_text(
        state_document(
            paths=("tracked.txt",),
            backend_paths=("docs/estado-operativo.md",),
            next_objective="NEXT = implementar la corrección técnica autorizada.",
            baseline=git(backend, "rev-parse", "HEAD"),
        ),
        encoding="utf-8",
    )

    state = development_supervisor.build_supervisor(
        root=backend,
        frontend_root=frontend,
        state_path=state_path,
    )

    assert state.supervisor_status == "PASS", state.error
    assert state.actor == "CODEX"
    assert state.codex_required is True
    assert state.routing == "Terra / medium — bounded implementation/review under canonical state"


def test_active_block_and_next_are_preserved_without_truncation(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    state_path = backend / "docs" / "estado-operativo.md"
    next_objective = "Human Visual Review | Unicode ñ\nwith complete details"
    state_path.write_text(state_document(paths=("tracked.txt",), next_objective=next_objective).replace("Active block complete semantic text.", "Active | complete\nsemantic text"), encoding="utf-8")

    state = development_supervisor.build_supervisor(root=backend, frontend_root=frontend, state_path=state_path)

    assert state.active_block == "Active | complete\nsemantic text"
    assert state.next_objective == next_objective


def test_supervisor_is_read_only(tmp_path: Path) -> None:
    backend, frontend = fixture(tmp_path)
    before = ((backend / "docs" / "estado-operativo.md").read_bytes(), git(backend, "status", "--porcelain=v1", "-z"), git(frontend, "status", "--porcelain=v1", "-z"))

    development_supervisor.build_supervisor(root=backend, frontend_root=frontend)

    after = ((backend / "docs" / "estado-operativo.md").read_bytes(), git(backend, "status", "--porcelain=v1", "-z"), git(frontend, "status", "--porcelain=v1", "-z"))
    assert after == before


def test_missing_frontend_repository_blocks(tmp_path: Path) -> None:
    backend, _ = fixture(tmp_path)

    state = development_supervisor.build_supervisor(root=backend, frontend_root=tmp_path / "missing")

    assert state.supervisor_status == "BLOCKED"
    assert "frontend repository is missing" in (state.error or "")
