"""Resume LOGUIC English through its existing read-only authorities."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering import conversation_checkpoint, development_supervisor


DEFAULT_FRONTEND_ROOT = ROOT.parent.parent / "app_ingles_frontend" / "app_ingles"
COMPACT_LIMIT = 240
_ACTIVE_INCREMENT_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
_LOCAL_INCREMENT_STATUS = re.compile(r"^Estado:\s+.*\bLOCAL\b", re.MULTILINE)


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume LOGUIC English from canonical read-only authorities.",
        allow_abbrev=False,
    )
    parser.add_argument("command", choices=("resume",))
    parser.add_argument(
        "--frontend-root",
        type=Path,
        default=DEFAULT_FRONTEND_ROOT,
        help="Frontend repository; defaults to the project-relative confirmed location.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output, exit_code = resume(frontend_root=args.frontend_root)
    print(output, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
