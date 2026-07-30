import argparse
import subprocess
from pathlib import Path


REQUIRED_PATHS = (
    Path("app"),
    Path("tests"),
    Path("docs"),
    Path("pytest.ini"),
)


def validate_repository_root() -> None:
    """Validate execution from the backend repository root.

    Valida la ejecución desde la raíz del repositorio backend.
    """
    missing = [str(path) for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        raise SystemExit(
            "Repository root validation failed; missing: " + ", ".join(missing)
        )


def validate_diff() -> None:
    """Require a clean Git diff according to git diff --check.

    Exige un diff Git limpio según git diff --check.
    """
    result = subprocess.run(
        ["git", "diff", "--check"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip()
        raise SystemExit("Git diff validation failed:\n" + output)



def validate_technical_changes() -> list[str]:
    """Require technical changes without documentation files.

    Exige cambios técnicos sin incluir archivos de documentación.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit("Git status inspection failed")

    changed_paths = sorted(
        line[3:].strip()
        for line in result.stdout.splitlines()
        if line.strip()
    )
    if not changed_paths:
        raise SystemExit("No technical changes found")

    documentation_paths = [
        path for path in changed_paths if path.startswith("docs/")
    ]
    if documentation_paths:
        raise SystemExit(
            "Technical changes include documentation: "
            + ", ".join(documentation_paths)
        )

    print(
        f"Technical change guard: passed ({len(changed_paths)} files)",
        flush=True,
    )
    return changed_paths


def stage_technical_changes(changed_paths: list[str]) -> None:
    """Stage only the previously validated technical paths.

    Prepara en Git únicamente las rutas técnicas previamente validadas.
    """
    if not changed_paths:
        raise SystemExit("No validated technical paths to stage")

    result = subprocess.run(
        ["git", "add", "--", *changed_paths],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Technical staging failed")

    print(
        f"Technical staging: completed ({len(changed_paths)} files)",
        flush=True,
    )


def run_specific_tests(test_paths: list[str]) -> None:
    """Run the specific tests supplied for the current block.

    Ejecuta las pruebas específicas indicadas para el bloque actual.
    """
    if not test_paths:
        raise SystemExit("At least one specific test path is required")

    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", *test_paths, "-q"],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Specific tests failed")

    print("Specific tests: passed", flush=True)


def run_phonetic_regression() -> None:
    """Run the complete phonetic calibration regression deterministically.

    Ejecuta de forma determinista la regresión completa de calibración fonética.
    """
    test_paths = sorted(
        str(path)
        for path in Path("tests").glob("test_phonetic_calibration_*.py")
    )
    if not test_paths:
        raise SystemExit("No phonetic calibration regression tests found")

    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", *test_paths, "-q"],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Phonetic calibration regression failed")

    print(
        f"Phonetic calibration regression: passed ({len(test_paths)} files)",
        flush=True,
    )


def run_full_suite() -> None:
    """Run the complete backend test suite.

    Ejecuta la suite completa de pruebas del backend.
    """
    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "-q"],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("Full backend suite failed")

    print("Full backend suite: passed", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tests", nargs="*")
    parser.add_argument(
        "--phonetic-regression",
        action="store_true",
    )
    parser.add_argument(
        "--full-suite",
        action="store_true",
    )
    parser.add_argument(
        "--technical-preflight",
        action="store_true",
    )
    parser.add_argument(
        "--stage-technical",
        action="store_true",
    )
    args = parser.parse_args()

    validate_repository_root()
    validate_diff()

    if args.technical_preflight and not args.tests:
        raise SystemExit(
            "Technical preflight requires at least one specific test path"
        )

    if args.stage_technical and not args.technical_preflight:
        raise SystemExit(
            "Technical staging requires --technical-preflight"
        )

    changed_paths = []
    if args.technical_preflight:
        changed_paths = validate_technical_changes()

    if args.tests:
        run_specific_tests(args.tests)

    if args.phonetic_regression or args.technical_preflight:
        run_phonetic_regression()

    if args.full_suite:
        run_full_suite()

    if args.stage_technical:
        stage_technical_changes(changed_paths)

    print("Git diff check: clean", flush=True)
    print("Block close preflight passed", flush=True)


if __name__ == "__main__":
    main()
