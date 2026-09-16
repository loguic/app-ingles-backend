"""Run the approved read-only validation recipe without selecting its tests."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[2]
RECIPE_ID = "approved-v1"


@dataclass(frozen=True)
class RecipeStep:
    name: str
    command: tuple[str, ...]


class RecipeFailure(RuntimeError):
    def __init__(self, step: str, exit_code: int) -> None:
        super().__init__(step)
        self.step = step
        self.exit_code = exit_code


def _validate_test_path(value: str) -> str:
    if not value or "\0" in value or value.startswith("-"):
        raise argparse.ArgumentTypeError("test path is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise argparse.ArgumentTypeError("test path must be relative without '..'")
    if path.parts[0] != "tests":
        raise argparse.ArgumentTypeError("test path must be under tests/")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the approved read-only validation recipe.",
        allow_abbrev=False,
    )
    parser.add_argument("recipe", choices=(RECIPE_ID,))
    parser.add_argument("--focal", action="append", type=_validate_test_path)
    parser.add_argument("--regression", action="append", type=_validate_test_path)
    parser.add_argument("--verbose", action="store_true")
    return parser


def build_steps(test_paths: list[str]) -> tuple[RecipeStep, ...]:
    return (
        RecipeStep(
            "pytest",
            (".venv/bin/python", "-m", "pytest", *test_paths, "-q", "-p", "no:cacheprovider"),
        ),
        RecipeStep("diff-check", ("git", "diff", "--check")),
        RecipeStep(
            "operational-state",
            (sys.executable, "scripts/engineering/operational_state.py", "validate"),
        ),
        RecipeStep(
            "checkpoint",
            (
                sys.executable,
                "scripts/engineering/conversation_checkpoint.py",
                "prepare",
                "--format",
                "compact",
            ),
        ),
    )


def _forward_output(stdout: str, stderr: str) -> None:
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n", flush=True)
    if stderr:
        print(
            stderr,
            end="" if stderr.endswith("\n") else "\n",
            file=sys.stderr,
            flush=True,
        )


def _run_step(step: RecipeStep, *, root: Path, verbose: bool) -> None:
    result = subprocess.run(
        step.command,
        cwd=root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        _forward_output(result.stdout, result.stderr)
        raise RecipeFailure(step.name, result.returncode)
    if verbose:
        _forward_output(result.stdout, result.stderr)


def run_recipe(
    recipe: str,
    *,
    focal_paths: list[str],
    regression_paths: list[str],
    verbose: bool = False,
    root: Path = ROOT,
) -> None:
    if recipe != RECIPE_ID:
        raise ValueError("unknown recipe")
    if not focal_paths:
        raise ValueError("at least one --focal is required")
    test_paths = [*focal_paths, *regression_paths]
    for path in test_paths:
        _validate_test_path(path)
    for step in build_steps(test_paths):
        _run_step(step, root=root, verbose=verbose)


def _pass_output(test_paths: int) -> str:
    return urlencode(
        (
            ("VALIDATION_STATUS", "PASS"),
            ("RECIPE", RECIPE_ID),
            ("STEPS", "4"),
            ("TEST_PATHS", str(test_paths)),
        )
    )


def _fail_output(step: str, exit_code: int) -> str:
    return urlencode(
        (
            ("VALIDATION_STATUS", "FAIL"),
            ("RECIPE", RECIPE_ID),
            ("FAILED_STEP", step),
            ("EXIT_CODE", str(exit_code)),
        )
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    focal_paths = args.focal or []
    regression_paths = args.regression or []
    try:
        run_recipe(
            args.recipe,
            focal_paths=focal_paths,
            regression_paths=regression_paths,
            verbose=args.verbose,
        )
    except RecipeFailure as error:
        print(_fail_output(error.step, error.exit_code), file=sys.stderr)
        return error.exit_code if error.exit_code != 0 else 1
    except ValueError as error:
        print(f"validation recipe error: {error}", file=sys.stderr)
        return 2
    print(_pass_output(len(focal_paths) + len(regression_paths)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
