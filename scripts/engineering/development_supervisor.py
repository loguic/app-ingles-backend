"""Compose canonical continuity facts without creating a new authority."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering import conversation_checkpoint
from scripts.engineering.operational_state import validate_operational_state


OUTPUT_FORMATS = ("compact", "json")
BACKEND_DIRTY_PREFIX = "Dirty backend reconocido:"
FRONTEND_DIRTY_PREFIX = "Dirty frontend reconocido:"


@dataclass(frozen=True)
class RepositoryState:
    head: str
    branch: str | None
    upstream: str | None
    ahead: int | None
    behind: int | None
    dirty_paths: tuple[str, ...]


@dataclass(frozen=True)
class SupervisorState:
    supervisor_status: str
    active_block: str
    next_objective: str
    backend: RepositoryState | None
    frontend: RepositoryState | None
    expected_backend_dirty_paths: tuple[str, ...]
    expected_frontend_dirty_paths: tuple[str, ...]
    unexpected_backend_dirty_paths: tuple[str, ...]
    unexpected_frontend_dirty_paths: tuple[str, ...]
    continuity_safe: bool
    actor: str
    codex_required: bool
    routing: str | None
    reconciliation_required: bool
    restrictions: str
    error: str | None = None


def _change_paths(changes: tuple[conversation_checkpoint.GitChange, ...]) -> tuple[str, ...]:
    paths = {change.path for change in changes}
    paths.update(change.original_path for change in changes if change.original_path)
    return tuple(sorted(paths))


def _repository_state(root: Path) -> RepositoryState:
    snapshot = conversation_checkpoint.inspect_git(root)
    return RepositoryState(
        head=snapshot.head,
        branch=snapshot.branch,
        upstream=snapshot.upstream,
        ahead=snapshot.ahead,
        behind=snapshot.behind,
        dirty_paths=_change_paths(snapshot.changes),
    )


def _sections(state_path: Path) -> dict[str, list[str]]:
    # The checkpoint owns parsing and path-recognition semantics.
    validate_operational_state(state_path)
    return conversation_checkpoint._read_sections(state_path)


def _semantic_section(sections: dict[str, list[str]], name: str) -> str:
    return "\n".join(sections[name]).strip()


def _documented_dirty_paths(
    sections: dict[str, list[str]],
    *,
    prefix: str,
    repository: str,
) -> tuple[str, ...]:
    """Read one explicit repository-scoped dirty allowlist from active state."""
    declarations = [
        line.removeprefix(prefix).strip()
        for line in sections["Bloque activo"]
        if line.startswith(prefix)
    ]
    if len(declarations) > 1:
        raise ValueError(
            f"Operational state has multiple {repository} dirty declarations"
        )
    if not declarations:
        return ()
    declared_paths, _, _ = declarations[0].partition(". ")
    paths = re.findall(r"`([^`\n]+)`", declared_paths)
    if not paths:
        raise ValueError(
            f"Operational state {repository} dirty declaration has no paths"
        )
    return tuple(sorted(set(paths)))


def _actor_for(next_objective: str, reconciliation_required: bool) -> tuple[str, bool, str | None]:
    if reconciliation_required:
        return "CODEX", True, "Terra / medium — reconcile canonical state before continuation"
    if "autorización humana" in next_objective.casefold():
        return "HUMAN", False, None
    if "Human Visual Review" in next_objective and "implementar `Development Supervisor" not in next_objective:
        return "HUMAN", False, None
    return "CODEX", True, "Terra / medium — bounded implementation/review under canonical state"


def build_supervisor(
    *,
    root: Path = ROOT,
    frontend_root: Path | None,
    state_path: Path | None = None,
) -> SupervisorState:
    """Build a derived, read-only continuity view; fail closed on unavailable facts."""
    canonical_path = state_path or root / "docs" / "estado-operativo.md"
    backend: RepositoryState | None = None
    frontend: RepositoryState | None = None
    sections: dict[str, list[str]] | None = None
    error: str | None = None
    checkpoint_ok = False
    try:
        # This is the backend checkpoint authority; its JSON retains full semantics.
        checkpoint = json.loads(conversation_checkpoint.build_checkpoint(
            "resume", root=root, state_path=canonical_path, output_format="json"
        ))
        checkpoint_ok = checkpoint["checkpoint_status"] == "PASS"
        sections = _sections(canonical_path)
    except (ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        error = str(exc)
        try:
            sections = _sections(canonical_path)
        except (ValueError, OSError, KeyError) as state_error:
            error = f"{error}; canonical state unavailable: {state_error}"

    try:
        backend = _repository_state(root)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        error = error or f"backend Git unavailable: {exc}"

    if frontend_root is None:
        error = error or "frontend repository path is required (--frontend-root)"
    elif not frontend_root.is_dir():
        error = error or f"frontend repository is missing: {frontend_root}"
    else:
        try:
            frontend = _repository_state(frontend_root)
        except (ValueError, OSError, subprocess.CalledProcessError) as exc:
            error = error or f"frontend Git unavailable: {exc}"

    if sections is None:
        active_block = ""
        next_objective = ""
        restrictions = ""
        expected_backend = ()
        expected_frontend = ()
    else:
        active_block = _semantic_section(sections, "Bloque activo")
        next_objective = re.sub(
            r"^NEXT\s*=\s*",
            "",
            _semantic_section(sections, "Próximo objetivo"),
            count=1,
        )
        restrictions = _semantic_section(sections, "Fronteras obligatorias")
        try:
            expected_backend = _documented_dirty_paths(
                sections,
                prefix=BACKEND_DIRTY_PREFIX,
                repository="backend",
            )
            expected_frontend = _documented_dirty_paths(
                sections,
                prefix=FRONTEND_DIRTY_PREFIX,
                repository="frontend",
            )
        except ValueError as exc:
            error = error or str(exc)
            expected_backend = ()
            expected_frontend = ()

    actual_backend = set(backend.dirty_paths if backend else ())
    actual_frontend = set(frontend.dirty_paths if frontend else ())
    unexpected_backend = tuple(sorted(actual_backend - set(expected_backend)))
    unexpected_frontend = tuple(sorted(actual_frontend - set(expected_frontend)))
    reconciliation = bool(unexpected_backend or unexpected_frontend)
    checkpoint_path_reconciliation = bool(
        error and "Operational state omits local paths" in error
    )
    if error and not checkpoint_path_reconciliation:
        status = "BLOCKED"
    elif not checkpoint_ok or reconciliation:
        status = "RECONCILIATION_REQUIRED"
    else:
        status = "PASS"
    actor, codex_required, routing = _actor_for(next_objective, status != "PASS")
    return SupervisorState(
        supervisor_status=status,
        active_block=active_block,
        next_objective=next_objective,
        backend=backend,
        frontend=frontend,
        expected_backend_dirty_paths=expected_backend,
        expected_frontend_dirty_paths=expected_frontend,
        unexpected_backend_dirty_paths=unexpected_backend,
        unexpected_frontend_dirty_paths=unexpected_frontend,
        continuity_safe=status == "PASS",
        actor=actor,
        codex_required=codex_required,
        routing=routing,
        reconciliation_required=status != "PASS",
        restrictions=restrictions,
        error=error,
    )


def _repository_fields(prefix: str, state: RepositoryState | None) -> list[str]:
    if state is None:
        return [f"{prefix}_REPOSITORY=UNAVAILABLE"]
    return [
        f"{prefix}_HEAD={state.head}", f"{prefix}_BRANCH={state.branch or 'DETACHED'}",
        f"{prefix}_UPSTREAM={state.upstream or 'UNAVAILABLE'}", f"{prefix}_AHEAD={state.ahead}",
        f"{prefix}_BEHIND={state.behind}", f"{prefix}_DIRTY={','.join(state.dirty_paths) or 'NONE'}",
    ]


def render_status(state: SupervisorState) -> str:
    lines = [f"SUPERVISOR_STATUS={state.supervisor_status}", f"ACTIVE_BLOCK={state.active_block}", f"NEXT={state.next_objective}"]
    lines += _repository_fields("BACKEND", state.backend) + _repository_fields("FRONTEND", state.frontend)
    lines += [
        f"EXPECTED_BACKEND_DIRTY={','.join(state.expected_backend_dirty_paths) or 'NONE'}",
        f"EXPECTED_FRONTEND_DIRTY={','.join(state.expected_frontend_dirty_paths) or 'NONE'}",
        f"UNEXPECTED_BACKEND_DIRTY={','.join(state.unexpected_backend_dirty_paths) or 'NONE'}",
        f"UNEXPECTED_FRONTEND_DIRTY={','.join(state.unexpected_frontend_dirty_paths) or 'NONE'}",
        f"CONTINUITY_SAFE={'YES' if state.continuity_safe else 'NO'}",
        f"CODEX_REQUIRED={'YES' if state.codex_required else 'NO'}",
        f"SUGGESTED_ROUTING={state.routing or 'NONE'}",
    ]
    if state.error:
        lines.append(f"ERROR={state.error}")
    return "\n".join(lines) + "\n"


def render_next(state: SupervisorState) -> str:
    return "\n".join((
        f"OBJECTIVE={state.next_objective}", f"ACTOR={state.actor}",
        f"CODEX_REQUIRED={'YES' if state.codex_required else 'NO'}",
        f"ROUTING={state.routing or 'NONE'}",
        f"RECOVERY_RECONCILIATION_REQUIRED={'YES' if state.reconciliation_required else 'NO'}",
    )) + "\n"


def render_handoff(state: SupervisorState) -> str:
    lines = [f"SUPERVISOR_STATUS={state.supervisor_status}", f"ACTIVE_BLOCK={state.active_block}"]
    lines += _repository_fields("BACKEND", state.backend) + _repository_fields("FRONTEND", state.frontend)
    lines += [
        f"BACKEND_DIRTY={','.join(state.backend.dirty_paths) if state.backend else 'UNAVAILABLE'}",
        f"FRONTEND_DIRTY={','.join(state.frontend.dirty_paths) if state.frontend else 'UNAVAILABLE'}",
        f"NEXT={state.next_objective}", f"READINESS={'SAFE' if state.continuity_safe else 'RECONCILIATION_REQUIRED'}",
        f"RESTRICTIONS={state.restrictions}", f"RECOMMENDED_ACTOR={state.actor}",
        f"ROUTING={state.routing or 'NONE'}",
    ]
    if state.error:
        lines.append(f"ERROR={state.error}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a read-only development continuity view.", allow_abbrev=False)
    parser.add_argument("command", choices=("status", "next", "handoff"))
    parser.add_argument("--frontend-root", type=Path, required=True)
    parser.add_argument("--format", choices=OUTPUT_FORMATS, default="compact")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state = build_supervisor(frontend_root=args.frontend_root)
    if args.format == "json":
        print(json.dumps(asdict(state), ensure_ascii=True, sort_keys=True))
    elif args.command == "status":
        print(render_status(state), end="")
    elif args.command == "next":
        print(render_next(state), end="")
    else:
        print(render_handoff(state), end="")
    return 0 if state.supervisor_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
