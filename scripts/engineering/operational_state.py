from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


REQUIRED_SECTIONS = (
    "Dirección vigente",
    "Último bloque cerrado",
    "Bloque activo",
    "Automatización disponible",
    "Método operativo vigente",
    "Fronteras obligatorias",
    "Próximo objetivo",
    "Archivos clave",
)

SUMMARY_SECTIONS = (
    "Último bloque cerrado",
    "Bloque activo",
    "Próximo objetivo",
)

_UPDATED_AT_PATTERN = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
    r"T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"[+-][0-9]{2}:[0-9]{2}"
)

_GIT_BASELINE_PREFIX = "Baseline Git previa a este checkpoint: "
_FULL_OID_PATTERN = re.compile(r"[0-9a-f]{40}")
ROOT_GIT_BASELINE = "0" * 40
_RESERVED_LIVE_GIT_FIELD_PATTERN = re.compile(
    r"^(?:[-*] )?(?:"
    r"HEAD(?: actual| publicado)?|"
    r"branch(?: actual)?|rama(?: actual)?|"
    r"upstream(?: actual)?|"
    r"ahead/behind|"
    r"local relation|relaci[oó]n local|"
    r"working tree(?: actual)?|[aá]rbol de trabajo(?: actual)?"
    r"):",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OperationalStateReport:
    path: Path
    updated_at: datetime
    line_count: int
    sections: tuple[str, ...]
    git_baseline: str = ROOT_GIT_BASELINE


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _extract_update_timestamp(lines: list[str]) -> datetime:
    prefix = "Actualizado: "
    values = [
        line.removeprefix(prefix)
        for line in lines
        if line.startswith(prefix)
    ]
    if len(values) != 1:
        raise ValueError(
            "Operational state requires exactly one update timestamp"
        )
    value = values[0]
    if _UPDATED_AT_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "Operational state update timestamp must use "
            "YYYY-MM-DDTHH:MM:SS±HH:MM"
        )
    try:
        updated_at = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            "Operational state update timestamp is invalid"
        ) from exc
    if updated_at.tzinfo is None or updated_at.utcoffset() is None:
        raise ValueError(
            "Operational state update timestamp must be timezone-aware"
        )
    return updated_at


def _extract_sections(lines: list[str]) -> tuple[str, ...]:
    return tuple(
        line.removeprefix("## ").strip()
        for line in lines
        if line.startswith("## ")
    )


def _extract_git_baseline(lines: list[str]) -> str:
    values = [
        line.removeprefix(_GIT_BASELINE_PREFIX)
        for line in lines
        if line.startswith(_GIT_BASELINE_PREFIX)
    ]
    if len(values) != 1:
        raise ValueError(
            "Operational state requires exactly one prior Git baseline"
        )
    baseline = values[0]
    if _FULL_OID_PATTERN.fullmatch(baseline) is None:
        raise ValueError(
            "Operational state prior Git baseline must be one full lowercase OID"
        )
    return baseline


def _assert_no_live_git_fields(lines: list[str]) -> None:
    reserved = [
        line
        for line in lines
        if _RESERVED_LIVE_GIT_FIELD_PATTERN.match(line)
    ]
    if reserved:
        raise ValueError(
            "Operational state must not declare live Git fields: "
            + ", ".join(reserved)
        )


def validate_operational_state(
    path: Path,
    *,
    now: datetime | None = None,
    max_age_days: int = 14,
    max_lines: int = 140,
) -> OperationalStateReport:
    lines = path.read_text(encoding="utf-8").splitlines()

    if not lines or lines[0] != "# Estado operativo — LOGUIC English":
        raise ValueError("Operational state title is invalid")

    if len(lines) > max_lines:
        raise ValueError(
            f"Operational state exceeds {max_lines} lines"
        )

    sections = _extract_sections(lines)
    missing = [
        section
        for section in REQUIRED_SECTIONS
        if section not in sections
    ]
    if missing:
        raise ValueError(
            "Operational state is missing sections: "
            + ", ".join(missing)
        )

    _assert_no_live_git_fields(lines)
    git_baseline = _extract_git_baseline(lines)

    updated_at = _extract_update_timestamp(lines)
    reference_now = now or datetime.now().astimezone()
    if reference_now.tzinfo is None or reference_now.utcoffset() is None:
        raise ValueError("Operational state reference time must be timezone-aware")
    age = reference_now - updated_at

    if age < timedelta(0):
        raise ValueError("Operational state update timestamp is in the future")
    if age > timedelta(days=max_age_days):
        raise ValueError(
            f"Operational state is stale by {age.days} days"
        )

    return OperationalStateReport(
        path=path,
        updated_at=updated_at,
        git_baseline=git_baseline,
        line_count=len(lines),
        sections=sections,
    )


def latest_git_commit_timestamp(
    root: Path,
    revision: str = "HEAD",
) -> datetime:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", revision],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return datetime.fromisoformat(result.stdout.strip())


def _head_modifies_state_path(root: Path, state_path: Path) -> bool:
    path = state_path if state_path.is_absolute() else root / state_path
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        return False
    result = subprocess.run(
        [
            "git",
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-only",
            "-r",
            "HEAD",
            "--",
            relative_path.as_posix(),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _head_has_parent(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    parents = result.stdout.split()
    if not parents:
        raise ValueError("Git HEAD parent output is malformed")
    return len(parents) > 1


def _head_oid(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    oid = result.stdout.strip()
    if _FULL_OID_PATTERN.fullmatch(oid) is None:
        raise ValueError("Git HEAD is not one full lowercase OID")
    return oid


def _head_parent_oid(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    values = result.stdout.split()
    if not values:
        raise ValueError("Git HEAD parent output is malformed")
    if len(values) == 1:
        return None
    if len(values) != 2:
        raise ValueError("Merge HEAD is unsupported for checkpoint baseline")
    parent = values[1]
    if _FULL_OID_PATTERN.fullmatch(parent) is None:
        raise ValueError("Git HEAD parent is not one full lowercase OID")
    return parent


def _state_is_locally_modified(root: Path, state_path: Path) -> bool:
    path = state_path if state_path.is_absolute() else root / state_path
    try:
        relative_path = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Operational state path is outside repository") from exc
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
            "--",
            relative_path.as_posix(),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout)


def git_baseline_oid(root: Path, state_path: Path) -> str:
    """Return the only valid non-circular baseline for the checkpoint state."""
    head = _head_oid(root)
    if _state_is_locally_modified(root, state_path):
        return head
    if not _head_modifies_state_path(root, state_path):
        raise ValueError(
            "Operational state is stale: Git HEAD does not incorporate checkpoint"
        )
    parent = _head_parent_oid(root)
    return ROOT_GIT_BASELINE if parent is None else parent


def git_baseline_timestamp(
    root: Path,
    state_path: Path,
) -> datetime | None:
    baseline = git_baseline_oid(root, state_path)
    if baseline == ROOT_GIT_BASELINE:
        return None
    return latest_git_commit_timestamp(root, baseline)


def validate_against_git(
    report: OperationalStateReport,
    root: Path,
) -> None:
    expected_baseline = git_baseline_oid(root, report.path)
    if report.git_baseline != expected_baseline:
        raise ValueError(
            "Operational state prior Git baseline is incompatible with repository"
        )
    baseline_timestamp = git_baseline_timestamp(root, report.path)
    if (
        baseline_timestamp is not None
        and report.updated_at < baseline_timestamp
    ):
        raise ValueError(
            "Operational state is older than the Git baseline"
        )


def render_operational_summary(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in lines:
        if line.startswith("## "):
            current = line.removeprefix("## ").strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)

    output = ["# Resumen operativo"]
    for section in SUMMARY_SECTIONS:
        output.extend(
            [
                "",
                f"## {section}",
                *sections.get(section, []),
            ]
        )

    return "\n".join(output).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("validate", "summary"),
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=repository_root() / "docs" / "estado-operativo.md",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=14,
    )
    args = parser.parse_args()

    if args.command == "summary":
        print(render_operational_summary(args.path), end="")
        return

    try:
        report = validate_operational_state(
            args.path,
            max_age_days=args.max_age_days,
        )
        validate_against_git(report, repository_root())
    except ValueError as exc:
        parser.error(str(exc))

    print(
        f"OK: {report.path} "
        f"({report.line_count} lines, "
        f"updated {report.updated_at.isoformat()})"
    )


if __name__ == "__main__":
    main()
