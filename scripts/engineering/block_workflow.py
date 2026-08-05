from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering.operational_state import (
    validate_against_git,
    validate_operational_state,
)


def run_block_workflow(
    block_close_args: list[str],
    *,
    root: Path = ROOT,
    state_path: Path | None = None,
) -> None:
    """Validate context before delegating the technical workflow.

    Valida el contexto antes de delegar el flujo técnico.
    """
    checkpoint = (
        state_path
        if state_path is not None
        else root / "docs" / "estado-operativo.md"
    )
    report = validate_operational_state(checkpoint)
    validate_against_git(report, root)

    print(
        "Operational checkpoint OK: "
        f"{report.line_count} lines, "
        f"updated {report.updated_on.isoformat()}"
    )

    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "engineering" / "block_close.py"),
            *block_close_args,
        ],
        cwd=root,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the operational checkpoint and delegate "
            "to block_close.py."
        )
    )
    parser.add_argument(
        "--state-path",
        type=Path,
        default=None,
    )
    known, block_close_args = parser.parse_known_args()

    run_block_workflow(
        block_close_args,
        state_path=known.state_path,
    )


if __name__ == "__main__":
    main()
