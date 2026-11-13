"""Resume LOGUIC English through its existing read-only authorities."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering import conversation_checkpoint, development_supervisor


DEFAULT_FRONTEND_ROOT = ROOT.parent.parent / "app_ingles_frontend" / "app_ingles"
COMPACT_LIMIT = 240
_MATRIX_SECTION = "## Plan de innovación MVP — especificación documental provisional"
_MATRIX_STATES = ("IMPLEMENTADO", "PROTOTIPO", "DOCUMENTADO", "PROPUESTO", "NO VERIFICADO")
_DELIVERABLE_ID = re.compile(r"^[1-8]\.[1-3]$")
_OUTCOME_NAMES = (
    "PRE-A1 Y DIAGNÓSTICO", "EXPERIENCIAS A1", "ESCUCHA, HABLA Y PRONUNCIACIÓN",
    "TUTOR ADAPTATIVO", "FEEDBACK PEDAGÓGICO", "TRANSFERENCIA Y RETENCIÓN",
    "UX Y ACCESIBILIDAD", "PREPARACIÓN PARA LANZAMIENTO",
)
_STATE_SYMBOLS = {
    "IMPLEMENTADO": "✓",
    "PROTOTIPO": "◐",
    "DOCUMENTADO": "◌",
    "PROPUESTO": "?",
    "NO VERIFICADO": "!",
}
_STATE_LABELS = {
    "IMPLEMENTADO": "Impl.", "PROTOTIPO": "Proto.", "DOCUMENTADO": "Doc.",
    "PROPUESTO": "Prop.", "NO VERIFICADO": "No verif.",
}
_ANSI = {
    "title": "\033[1;36m", "good": "\033[32m", "warn": "\033[33m",
    "muted": "\033[2m", "reset": "\033[0m",
}
_ACTIVE_INCREMENT_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_LOCAL_INCREMENT_STATUS = re.compile(r"^Estado:\s+.*\bLOCAL\b", re.MULTILINE)
_LAST_ACHIEVEMENT = re.compile(r"(?m)^(.+?CLOSED / PUBLISHED / SYNCED.+)$")


@dataclass(frozen=True)
class ProgressDeliverable:
    identifier: str
    state: str


def _compact(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    if len(normalized) <= COMPACT_LIMIT:
        return normalized
    return normalized[: COMPACT_LIMIT - 1].rstrip() + "…"


def _repository_summary(
    repository: development_supervisor.RepositoryState | None,
) -> str:
    if repository is None:
        return "UNAVAILABLE"
    return ";".join((
        f"HEAD={repository.head}",
        f"BRANCH={repository.branch or 'DETACHED'}",
        f"UPSTREAM={repository.upstream or 'UNAVAILABLE'}",
        f"AHEAD={repository.ahead}",
        f"BEHIND={repository.behind}",
        f"DIRTY={','.join(repository.dirty_paths) or 'NONE'}",
    ))


def _blocked_output(error: str) -> str:
    return "\n".join((
        "CHECKPOINT=BLOCKED",
        "BACKEND=UNAVAILABLE",
        "FRONTEND=UNAVAILABLE",
        "ACTIVE_INCREMENT=UNAVAILABLE",
        "RESTRICTIONS=UNAVAILABLE",
        "NEXT=UNAVAILABLE",
        "RECOMMENDED_ACTOR=HUMAN",
        "ROUTING=NONE",
        "ERROR=" + _compact(error),
        "",
    ))


def _active_increment(active_block: str) -> str:
    """Return exactly one locally active increment declared in canonical state."""
    headings = list(_ACTIVE_INCREMENT_HEADING.finditer(active_block))
    candidates = []
    for index, heading in enumerate(headings):
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(active_block)
        if _LOCAL_INCREMENT_STATUS.search(active_block[heading.end():body_end]):
            candidates.append(heading.group(1))
    if not candidates:
        raise ValueError("canonical state has no active local increment")
    if len(candidates) != 1:
        raise ValueError("canonical state has ambiguous active increments")
    return candidates[0]


def resume(*, root: Path = ROOT, frontend_root: Path) -> tuple[str, int]:
    """Return a compact read-only recovery view or a fail-closed result."""
    try:
        checkpoint = json.loads(conversation_checkpoint.build_checkpoint(
            "resume", root=root, output_format="json"
        ))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        return _blocked_output(str(error)), 1

    if checkpoint.get("checkpoint_status") != "PASS":
        return _blocked_output("checkpoint did not report PASS"), 1

    supervisor = development_supervisor.build_supervisor(
        root=root,
        frontend_root=frontend_root,
    )
    try:
        active_increment = _active_increment(supervisor.active_block)
    except ValueError as error:
        return _blocked_output(str(error)), 1

    lines = (
        "CHECKPOINT=PASS",
        "BACKEND=" + _repository_summary(supervisor.backend),
        "FRONTEND=" + _repository_summary(supervisor.frontend),
        "ACTIVE_INCREMENT=" + _compact(active_increment),
        "RESTRICTIONS=" + _compact(supervisor.restrictions),
        "NEXT=" + _compact(supervisor.next_objective),
        "RECOMMENDED_ACTOR=" + supervisor.actor,
        "ROUTING=" + (supervisor.routing or "NONE"),
    )
    if supervisor.error:
        return "\n".join((*lines, "ERROR=" + _compact(supervisor.error), "")), 1
    return "\n".join((*lines, "")), 0


def render_resume(*, root: Path = ROOT, frontend_root: Path) -> str:
    """Render a successful resume view for callers that require continuity."""
    output, exit_code = resume(root=root, frontend_root=frontend_root)
    if exit_code:
        raise ValueError(output)
    return output


def _progress_matrix(roadmap_path: Path) -> tuple[ProgressDeliverable, ...]:
    """Read the sole V0 qualitative matrix and reject incomplete authority."""
    text = roadmap_path.read_text(encoding="utf-8")
    sections = text.split(_MATRIX_SECTION)
    if len(sections) != 2:
        raise ValueError("roadmap has ambiguous or missing V0 matrix section")
    section = sections[1].split("\n## ", 1)[0]
    lines = section.splitlines()
    headers = [index for index, line in enumerate(lines) if line.startswith("| ID |")]
    if len(headers) != 1:
        raise ValueError("roadmap has ambiguous or missing V0 matrix table")
    header = headers[0]
    if header + 1 >= len(lines) or not lines[header + 1].startswith("|-"):
        raise ValueError("V0 matrix header separator is malformed")
    rows = []
    for line in lines[header + 2:]:
        if not line.startswith("|"):
            break
        rows.append(line)
    if not rows:
        raise ValueError("roadmap has ambiguous or missing V0 matrix table")

    deliverables = []
    for line in rows:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            raise ValueError("V0 matrix row is malformed")
        identifier, status = cells[0], cells[-1]
        if _DELIVERABLE_ID.fullmatch(identifier) is None:
            raise ValueError(f"V0 matrix has invalid deliverable ID: {identifier}")
        states = [state for state in _MATRIX_STATES if status.startswith(state)]
        if len(states) != 1:
            raise ValueError(f"V0 matrix has ambiguous qualitative state for {identifier}")
        deliverables.append(ProgressDeliverable(identifier, states[0]))

    expected = {f"{outcome}.{delivery}" for outcome in range(1, 9) for delivery in range(1, 4)}
    actual = [item.identifier for item in deliverables]
    if len(deliverables) != 24 or set(actual) != expected or len(set(actual)) != len(actual):
        raise ValueError("V0 matrix must contain exactly 24 deliverables (1.1–8.3)")
    return tuple(deliverables)


def _render_progress_matrix(matrix: tuple[ProgressDeliverable, ...]) -> str:
    """Render qualitative V0 facts without converting them into progress."""
    rendered = [
        "MATRIX=24 CUALITATIVOS / 8 RESULTADOS",
        "MVP=NO MEDIBLE",
        "PRODUCTO_ACREDITADO=SIN ACREDITAR INDIVIDUALMENTE",
        "EXPERIENCIA_UTILIZABLE=PENDIENTE DE VALIDACIÓN",
    ]
    for outcome, name in enumerate(_OUTCOME_NAMES, start=1):
        counts = Counter(item.state for item in matrix if item.identifier.startswith(f"{outcome}."))
        technical = " ".join(
            f"{state}:{counts[state]}" for state in _MATRIX_STATES if counts[state]
        )
        rendered.append(f"RESULTADO {outcome} — {name} | TÉCNICO={technical}")
    return "\n".join(rendered)


def _fit(value: str, width: int) -> str:
    return value if len(value) <= width else value[:width - 1].rstrip() + "…"


def _paint(value: str, style: str, *, color: bool) -> str:
    return f"{_ANSI[style]}{value}{_ANSI['reset']}" if color else value


def _dashboard_section(title: str, rows: list[str], *, width: int, color: bool) -> list[str]:
    title = _paint(title, "title", color=color)
    plain_title = title if not color else re.sub(r"\033\[[0-9;]*m", "", title)
    top = "╭─ " + plain_title + " " + "─" * max(0, width - len(plain_title) - 4)
    rendered = [top]
    for row in rows:
        wrapped = textwrap.wrap(
            row, width=width - 4, break_long_words=False, break_on_hyphens=False,
        ) or [""]
        rendered.extend(f"│ {line:<{width - 4}} │" for line in wrapped)
    rendered.append("╰" + "─" * (width - 2) + "╯")
    if color:
        rendered[0] = rendered[0].replace(plain_title, title)
    return rendered


def _render_progress_dashboard(
    matrix: tuple[ProgressDeliverable, ...],
    *,
    active_increment: str,
    next_objective: str,
    product_achievement: str,
    technical_closure: str | None,
    color: bool,
    width: int,
) -> str:
    """Render the qualitative view as a compact, terminal-safe dashboard."""
    width = max(56, min(width, 100))
    counts = Counter(item.state for item in matrix)
    legend_entries = [
        f"{_STATE_SYMBOLS[state]} {state}:{counts[state]}"
        for state in _MATRIX_STATES if counts[state]
    ]
    legend_rows = []
    current = "LEYENDA · "
    for entry in legend_entries:
        candidate = current + entry if current == "LEYENDA · " else current + "  " + entry
        if len(candidate) > width - 4 and current != "LEYENDA · ":
            legend_rows.append(current)
            current = "          " + entry
        else:
            current = candidate
    legend_rows.append(current)
    results = []
    for outcome, name in enumerate(_OUTCOME_NAMES, start=1):
        state_counts = Counter(item.state for item in matrix if item.identifier.startswith(f"{outcome}."))
        markers = " ".join(
            f"{_STATE_SYMBOLS[state]} {_STATE_LABELS[state]} {state_counts[state]}"
            for state in _MATRIX_STATES if state_counts[state]
        )
        results.append(f"{outcome} · {name}  |  {markers}")

    header = _paint("LOGUIC ENGLISH · MISSION CONTROL", "title", color=color)
    lines = [header, "=" * width]
    lines += _dashboard_section("PRODUCTO", [
        _paint("MVP · NO MEDIBLE", "warn", color=color),
        "ACREDITACIÓN · SIN ACREDITAR INDIVIDUALMENTE",
        "NO EVALUADO ≠ SIN ACREDITAR",
    ], width=width, color=color)
    lines += _dashboard_section("INGENIERÍA", [
        "MATRIZ · 24 ENTREGABLES / 8 RESULTADOS",
        *legend_rows,
    ], width=width, color=color)
    lines += _dashboard_section("EXPERIENCIA DEL ESTUDIANTE", [
        "USABILIDAD · PENDIENTE DE VALIDACIÓN",
        "EVIDENCIA PEDAGÓGICA · PENDIENTE DE ACREDITACIÓN",
    ], width=width, color=color)
    lines += _dashboard_section("RESULTADOS FUNCIONALES", results, width=width, color=color)
    lines += _dashboard_section("MISIÓN ACTUAL", [
        "INCREMENTO · " + active_increment,
        "NEXT · " + next_objective,
    ], width=width, color=color)
    lines += _dashboard_section(
        "ÚLTIMO HITO DE PRODUCTO", [product_achievement], width=width, color=color,
    )
    lines += _dashboard_section(
        "ÚLTIMO CIERRE TÉCNICO", [technical_closure or "NO VERIFICADO"], width=width, color=color,
    )
    return "\n".join(lines)


def _latest_achievement(root: Path) -> str | None:
    """Return a closed canonical achievement only when explicitly recorded."""
    sections = development_supervisor._sections(root / "docs" / "estado-operativo.md")
    match = _LAST_ACHIEVEMENT.search("\n".join(sections["Último bloque cerrado"]))
    if match is None:
        return None
    record = match.group(1).replace("**", "")
    closure = re.search(r"^(.+?CLOSED / PUBLISHED / SYNCED por este Closure Gate\.)", record)
    return closure.group(1) if closure else record


def _product_achievement(active_block: str) -> str:
    """State the absent product accreditation without inferring a milestone."""
    if "no implica cumplimiento ni acreditación nueva" in active_block.casefold():
        return "NO VERIFICADO · autoridad canónica sin acreditación individual."
    return "NO VERIFICADO · sin hito de producto acreditado canónico."


def _progress_blocked(error: str) -> tuple[str, int]:
    return "\n".join(("PROGRESS=BLOCKED", "ERROR=" + _compact(error), "")), 1


def progress(
    *,
    root: Path = ROOT,
    frontend_root: Path,
    roadmap_path: Path | None = None,
    color: bool | None = None,
    width: int | None = None,
) -> tuple[str, int]:
    """Return the read-only qualitative MVP view from canonical authorities."""
    try:
        matrix = _progress_matrix(roadmap_path or root / "docs" / "roadmap.md")
    except (OSError, ValueError) as error:
        return _progress_blocked(str(error))
    supervisor = development_supervisor.build_supervisor(root=root, frontend_root=frontend_root)
    if supervisor.supervisor_status != "PASS":
        return _progress_blocked(supervisor.error or "canonical supervisor is not PASS")
    try:
        active_increment = _active_increment(supervisor.active_block)
    except ValueError as error:
        return _progress_blocked(str(error))
    try:
        latest_achievement = _latest_achievement(root)
    except (OSError, ValueError, KeyError) as error:
        return _progress_blocked(str(error))
    dashboard = _render_progress_dashboard(
        matrix,
        active_increment=_compact(active_increment),
        next_objective=re.sub(r"\s+", " ", supervisor.next_objective).strip(),
        product_achievement=_product_achievement(supervisor.active_block),
        technical_closure=latest_achievement,
        color=sys.stdout.isatty() if color is None else color,
        width=width or shutil.get_terminal_size(fallback=(80, 24)).columns,
    )
    return "\n".join(("PROGRESS=READ_ONLY", dashboard, "")), 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume LOGUIC English from canonical read-only authorities.",
        allow_abbrev=False,
    )
    parser.add_argument("command", choices=("resume", "progress"))
    parser.add_argument(
        "--frontend-root",
        type=Path,
        default=DEFAULT_FRONTEND_ROOT,
        help="Frontend repository; defaults to the project-relative confirmed location.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "resume":
        output, exit_code = resume(frontend_root=args.frontend_root)
    else:
        output, exit_code = progress(frontend_root=args.frontend_root)
    print(output, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
