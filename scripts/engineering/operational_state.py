from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from datetime import date
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


@dataclass(frozen=True)
class OperationalStateReport:
    path: Path
    updated_on: date
    line_count: int
    sections: tuple[str, ...]


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _extract_update_date(lines: list[str]) -> date:
    prefix = "Actualizado: "
    values = [
        line.removeprefix(prefix).strip()
        for line in lines
        if line.startswith(prefix)
    ]
    if len(values) != 1:
        raise ValueError(
            "Operational state requires exactly one update date"
        )
    try:
        return date.fromisoformat(values[0])
    except ValueError as exc:
        raise ValueError(
            "Operational state update date must use YYYY-MM-DD"
        ) from exc


def _extract_sections(lines: list[str]) -> tuple[str, ...]:
    return tuple(
        line.removeprefix("## ").strip()
        for line in lines
        if line.startswith("## ")
    )


def validate_operational_state(
    path: Path,
    *,
    today: date | None = None,
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

    updated_on = _extract_update_date(lines)
    reference_date = today or date.today()
    age_days = (reference_date - updated_on).days

    if age_days < 0:
        raise ValueError("Operational state update date is in the future")
    if age_days > max_age_days:
        raise ValueError(
            f"Operational state is stale by {age_days} days"
        )

    return OperationalStateReport(
        path=path,
        updated_on=updated_on,
        line_count=len(lines),
        sections=sections,
    )


def latest_git_commit_date(root: Path) -> date:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return date.fromisoformat(result.stdout.strip())


def validate_against_git(
    report: OperationalStateReport,
    root: Path,
) -> None:
    commit_date = latest_git_commit_date(root)
    if report.updated_on < commit_date:
        raise ValueError(
            "Operational state is older than the latest Git commit"
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
        f"updated {report.updated_on.isoformat()})"
    )


if __name__ == "__main__":
    main()
