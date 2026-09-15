from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode


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
OUTPUT_FORMATS = ("markdown", "compact", "json")
COMPACT_TEXT_LIMIT = 240


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
    head = _run_git(root, "rev-parse", "HEAD").stdout.strip()
    subject = _run_git(root, "log", "-1", "--format=%s").stdout.strip()
    branch = _optional_git(root, "symbolic-ref", "--short", "HEAD")
    upstream = _optional_git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if upstream is None:
        raise ValueError("Git upstream is missing or cannot be resolved")

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


def _semantic_text(lines: list[str]) -> str:
    """Return the complete canonical text of one semantic section.

    Devuelve el texto canónico completo de una sección semántica.
    """
    return "\n".join(lines).strip()


def _compact_text(value: str) -> tuple[str, bool, int]:
    """Render complete semantic text as bounded single-line text.

    Renderiza texto semántico completo como texto acotado de una línea.
    """
    original_length = len(value)
    text = re.sub(r"\s+", " ", value).strip()
    if len(text) <= COMPACT_TEXT_LIMIT:
        return text, False, original_length
    return text[: COMPACT_TEXT_LIMIT - 1].rstrip() + "…", True, original_length


def checkpoint_facts(
    command: str,
    sections: dict[str, list[str]],
    snapshot: GitSnapshot,
    git_baseline: str,
) -> dict[str, object]:
    """Return the validated facts shared by every checkpoint representation.

    Devuelve los hechos validados compartidos por cada representación.
    """
    dirty_count = len(snapshot.changes)
    return {
        "checkpoint_status": "PASS",
        "command": command,
        "head": snapshot.head,
        "branch": snapshot.branch,
        "upstream": snapshot.upstream,
        "ahead": snapshot.ahead,
        "behind": snapshot.behind,
        "tree": "CLEAN" if dirty_count == 0 else "DIRTY",
        "baseline": git_baseline,
        "dirty_count": dirty_count,
        "active_block": _semantic_text(sections["Bloque activo"]),
        "next": _semantic_text(sections["Próximo objetivo"]),
    }


def render_compact_checkpoint(facts: dict[str, object]) -> str:
    """Render one stable human-readable line from validated checkpoint facts.

    Renderiza una línea humana estable desde hechos validados del checkpoint.
    """
    active_block, active_truncated, active_length = _compact_text(
        str(facts["active_block"])
    )
    next_objective, next_truncated, next_length = _compact_text(
        str(facts["next"])
    )
    fields = (
        ("CHECKPOINT_FORMAT", "compact-v1"),
        ("CHECKPOINT_STATUS", facts["checkpoint_status"]),
        ("COMMAND", facts["command"]),
        ("HEAD", facts["head"]),
        ("BRANCH", facts["branch"]),
        ("UPSTREAM", facts["upstream"]),
        ("AHEAD", facts["ahead"]),
        ("BEHIND", facts["behind"]),
        ("TREE", facts["tree"]),
        ("BASELINE", facts["baseline"]),
        ("DIRTY", facts["dirty_count"]),
        ("ACTIVE_BLOCK", active_block),
        ("ACTIVE_BLOCK_TRUNCATED", str(active_truncated).lower()),
        ("ACTIVE_BLOCK_LENGTH", active_length),
        ("NEXT", next_objective),
        ("NEXT_TRUNCATED", str(next_truncated).lower()),
        ("NEXT_LENGTH", next_length),
    )
    return urlencode(fields) + "\n"


def render_json_checkpoint(facts: dict[str, object]) -> str:
    """Render validated checkpoint facts as deterministic JSON.

    Renderiza hechos validados del checkpoint como JSON determinista.
    """
    return json.dumps(facts, ensure_ascii=True, sort_keys=True) + "\n"


def render_checkpoint(
    command: str,
    sections: dict[str, list[str]],
    snapshot: GitSnapshot,
    git_baseline: str,
) -> str:
    """Render a deterministic ephemeral Markdown checkpoint.

    Renderiza un checkpoint Markdown efímero y determinista.
    """
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
        "- Autoridad semántica: `docs/estado-operativo.md`.",
        "- Autoridad Git viva: inspección read-only de Git.",
        f"- Baseline Git semántica: `{git_baseline}`.",
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
    output_format: str = "markdown",
) -> str:
    """Validate canonical state and build an ephemeral checkpoint.

    Valida el estado canónico y construye un checkpoint efímero.
    """
    if output_format not in OUTPUT_FORMATS:
        raise ValueError(f"Unsupported checkpoint output format: {output_format}")
    canonical_path = state_path or root / "docs" / "estado-operativo.md"
    report = validate_operational_state(canonical_path)
    validate_against_git(report, root)
    snapshot = inspect_git(root)
    sections = _read_sections(canonical_path)
    _validate_local_paths(sections, snapshot.changes)
    if output_format == "markdown":
        return render_checkpoint(command, sections, snapshot, report.git_baseline)
    facts = checkpoint_facts(command, sections, snapshot, report.git_baseline)
    if output_format == "compact":
        return render_compact_checkpoint(facts)
    return render_json_checkpoint(facts)


def build_parser() -> argparse.ArgumentParser:
    """Build the stable read-only checkpoint command-line interface.

    Construye la interfaz estable y read-only del checkpoint.
    """
    parser = argparse.ArgumentParser(
        description="Prepare or resume an ephemeral conversation checkpoint."
    )
    parser.add_argument("command", choices=("prepare", "resume"))
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default="markdown",
        dest="output_format",
        help="Representation only; validation and Git inspection are unchanged.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        output = build_checkpoint(args.command, output_format=args.output_format)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(f"conversation checkpoint unavailable: {exc}")
    print(output, end="")


if __name__ == "__main__":
    main()
