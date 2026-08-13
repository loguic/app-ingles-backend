from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering.operational_state import (
    validate_against_git,
    validate_operational_state,
)


CHECKPOINT_SECTIONS = (
    "Dirección vigente",
    "Último bloque cerrado",
    "Bloque activo",
    "Método operativo vigente",
    "Fronteras obligatorias",
    "Próximo objetivo",
    "Archivos clave",
)

LOCAL_PATH_SECTIONS = ("Bloque activo", "Archivos clave")


@dataclass(frozen=True)
class GitChange:
    """Describe one path reported by Git without interpreting its meaning.

    Describe una ruta informada por Git sin interpretar su significado.
    """

    status: str
    path: str
    original_path: str | None = None


@dataclass(frozen=True)
class GitSnapshot:
    """Capture the local Git facts required for conversation handoff.

    Captura los hechos Git locales necesarios para cambiar de conversación.
    """

    head: str
    subject: str
    branch: str | None
    upstream: str | None
    ahead: int | None
    behind: int | None
    changes: tuple[GitChange, ...]


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run one read-only Git query with deterministic decoding.

    Ejecuta una consulta Git de solo lectura con decodificación determinista.
    """
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )


def _optional_git(root: Path, *args: str) -> str | None:
    """Return one optional Git value without treating absence as failure.

    Devuelve un valor Git opcional sin tratar su ausencia como fallo.
    """
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="surrogateescape",
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _parse_porcelain(output: str) -> tuple[GitChange, ...]:
    """Parse NUL-delimited porcelain v1, including rename source paths.

    Analiza porcelain v1 delimitado por NUL, incluidas rutas origen de rename.
    """
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
                raise ValueError("Git rename record lacks its original path")
            original_path = records[index]
            index += 1
        changes.append(
            GitChange(
                status=status,
                path=path,
                original_path=original_path,
            )
        )
    return tuple(changes)


def inspect_git(root: Path) -> GitSnapshot:
    """Inspect local repository state without fetching or writing.

    Inspecciona el estado local del repositorio sin descargar ni escribir.
    """
    head = _run_git(root, "rev-parse", "--short", "HEAD").stdout.strip()
    subject = _run_git(root, "log", "-1", "--format=%s").stdout.strip()
    branch = _optional_git(root, "symbolic-ref", "--short", "HEAD")
    upstream = _optional_git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )

    ahead = None
    behind = None
    if upstream is not None:
        counts = _run_git(
            root,
            "rev-list",
            "--left-right",
            "--count",
            "HEAD...@{upstream}",
        ).stdout.split()
        if len(counts) != 2:
            raise ValueError("Git ahead/behind output is malformed")
        ahead, behind = (int(value) for value in counts)

    status = _run_git(
        root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
    ).stdout
    return GitSnapshot(
        head=head,
        subject=subject,
        branch=branch,
        upstream=upstream,
        ahead=ahead,
        behind=behind,
        changes=_parse_porcelain(status),
    )


def _read_sections(path: Path) -> dict[str, list[str]]:
    """Read canonical sections after validation without changing content.

    Lee secciones canónicas tras validarlas sin cambiar su contenido.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def _documented_local_paths(sections: dict[str, list[str]]) -> set[str]:
    """Extract exact inline-code paths from canonical local-state sections.

    Extrae rutas exactas en código inline de secciones canónicas locales.
    """
    paths: set[str] = set()
    for section_name in LOCAL_PATH_SECTIONS:
        for line in sections[section_name]:
            paths.update(re.findall(r"`([^`\n]+)`", line))
    return paths


def _validate_local_paths(
    sections: dict[str, list[str]],
    changes: tuple[GitChange, ...],
) -> None:
    """Fail closed when canonical state omits any locally changed path.

    Falla cerrado cuando el estado canónico omite una ruta con cambios locales.
    """
    if not changes:
        return
    changed_paths = {change.path for change in changes}
    changed_paths.update(
        change.original_path
        for change in changes
        if change.original_path is not None
    )
    undocumented = sorted(changed_paths - _documented_local_paths(sections))
    if undocumented:
        rendered = ", ".join(_format_git_path(path) for path in undocumented)
        raise ValueError("Operational state omits local paths: " + rendered)


def _format_change(change: GitChange) -> str:
    path = _format_git_path(change.path)
    if change.original_path is not None:
        path += f" (from {_format_git_path(change.original_path)})"
    return f"- `{change.status}` `{path}`"


def _format_git_path(path: str) -> str:
    """Represent one Git path as a reversible JSON string for Markdown.

    Representa una ruta Git como cadena JSON reversible para Markdown.
    """
    return json.dumps(path, ensure_ascii=True).replace("`", "\\u0060")


def _render_change_group(
    title: str,
    changes: list[GitChange],
) -> list[str]:
    lines = [f"### {title}", ""]
    if changes:
        lines.extend(_format_change(change) for change in changes)
    else:
        lines.append("- None.")
    return lines


def render_checkpoint(
    command: str,
    state_path: Path,
    snapshot: GitSnapshot,
) -> str:
    """Render a deterministic ephemeral Markdown checkpoint.

    Renderiza un checkpoint Markdown efímero y determinista.
    """
    sections = _read_sections(state_path)
    _validate_local_paths(sections, snapshot.changes)
    staged = [
        change
        for change in snapshot.changes
        if change.status[0] not in {" ", "?", "!"}
    ]
    unstaged = [
        change
        for change in snapshot.changes
        if change.status[1] not in {" ", "?", "!"}
    ]
    untracked = [
        change for change in snapshot.changes if change.status == "??"
    ]

    output = [
        "# Checkpoint de cambio de conversación",
        "",
        f"- Command: `{command}`.",
        "- Canonical source: `docs/estado-operativo.md` (the only source of truth).",
        "- This output is an ephemeral read-only view; it is not a persisted checkpoint.",
        "- Documented validations are reproduced as historical evidence and were not rerun.",
        "",
        "## Git local",
        "",
        f"- HEAD: `{snapshot.head}` — {snapshot.subject}",
        (
            f"- Branch: `{snapshot.branch}`"
            if snapshot.branch is not None
            else "- Branch: detached HEAD"
        ),
        (
            f"- Upstream: `{snapshot.upstream}`"
            if snapshot.upstream is not None
            else "- Upstream: none"
        ),
    ]
    if snapshot.upstream is not None:
        output.append(
            f"- Local relation: ahead {snapshot.ahead}, behind {snapshot.behind}"
        )
    else:
        output.append("- Local relation: unavailable without upstream")
    output.append(
        "- Working tree: clean"
        if not snapshot.changes
        else f"- Working tree: {len(snapshot.changes)} Git status record(s)"
    )

    output.extend([""] + _render_change_group("Staged", staged))
    output.extend([""] + _render_change_group("Unstaged", unstaged))
    output.extend([""] + _render_change_group("Untracked", untracked))

    output.extend(["", "## Contexto operativo canónico"])
    for section_name in CHECKPOINT_SECTIONS:
        output.extend(
            [
                "",
                f"### {section_name}",
                *sections[section_name],
            ]
        )
    return "\n".join(output).rstrip() + "\n"


def build_checkpoint(
    command: str,
    *,
    root: Path = ROOT,
    state_path: Path | None = None,
) -> str:
    """Validate canonical state and build an ephemeral checkpoint.

    Valida el estado canónico y construye un checkpoint efímero.
    """
    canonical_path = state_path or root / "docs" / "estado-operativo.md"
    report = validate_operational_state(canonical_path)
    validate_against_git(report, root)
    snapshot = inspect_git(root)
    return render_checkpoint(command, canonical_path, snapshot)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare or resume an ephemeral conversation checkpoint."
    )
    parser.add_argument("command", choices=("prepare", "resume"))
    args = parser.parse_args()

    try:
        output = build_checkpoint(args.command)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(f"conversation checkpoint unavailable: {exc}")
    print(output, end="")


if __name__ == "__main__":
    main()
