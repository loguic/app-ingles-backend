from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.engineering import block_close


def completed(returncode=0, stdout="", stderr=""):
    return SimpleNamespace(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_validate_diff_accepts_clean_diff(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(),
    )

    block_close.validate_diff()


def test_validate_diff_rejects_invalid_diff(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(
            returncode=1,
            stdout="trailing whitespace",
        ),
    )

    with pytest.raises(SystemExit, match="Git diff validation failed"):
        block_close.validate_diff()


def test_run_specific_tests_uses_backend_python(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return completed()

    monkeypatch.setattr(block_close.subprocess, "run", fake_run)

    block_close.run_specific_tests(["tests/test_example.py"])

    assert calls == [[
        ".venv/bin/python",
        "-m",
        "pytest",
        "tests/test_example.py",
        "-q",
    ]]


def test_run_phonetic_regression_discovers_tests(monkeypatch):
    monkeypatch.setattr(
        block_close.Path,
        "glob",
        lambda self, pattern: [
            Path("tests/test_phonetic_calibration_b.py"),
            Path("tests/test_phonetic_calibration_a.py"),
        ],
    )
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return completed()

    monkeypatch.setattr(block_close.subprocess, "run", fake_run)

    block_close.run_phonetic_regression()

    assert calls[0][3:5] == [
        "tests/test_phonetic_calibration_a.py",
        "tests/test_phonetic_calibration_b.py",
    ]


def test_run_full_suite_uses_backend_python(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return completed()

    monkeypatch.setattr(block_close.subprocess, "run", fake_run)

    block_close.run_full_suite()

    assert calls == [[
        ".venv/bin/python",
        "-m",
        "pytest",
        "-q",
    ]]


def test_run_specific_tests_rejects_failure(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(returncode=1),
    )

    with pytest.raises(SystemExit, match="Specific tests failed"):
        block_close.run_specific_tests(["tests/test_example.py"])


def test_run_phonetic_regression_rejects_failure(monkeypatch):
    monkeypatch.setattr(
        block_close.Path,
        "glob",
        lambda self, pattern: [
            Path("tests/test_phonetic_calibration_example.py"),
        ],
    )
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(returncode=1),
    )

    with pytest.raises(
        SystemExit,
        match="Phonetic calibration regression failed",
    ):
        block_close.run_phonetic_regression()


def test_run_phonetic_regression_requires_tests(monkeypatch):
    monkeypatch.setattr(
        block_close.Path,
        "glob",
        lambda self, pattern: [],
    )

    with pytest.raises(
        SystemExit,
        match="No phonetic calibration regression tests found",
    ):
        block_close.run_phonetic_regression()


def test_run_full_suite_rejects_failure(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(returncode=1),
    )

    with pytest.raises(SystemExit, match="Full backend suite failed"):
        block_close.run_full_suite()


def test_validate_repository_root_rejects_missing_paths(monkeypatch):
    monkeypatch.setattr(
        block_close.Path,
        "exists",
        lambda self: self != Path("docs"),
    )

    with pytest.raises(
        SystemExit,
        match="Repository root validation failed; missing: docs",
    ):
        block_close.validate_repository_root()


def test_technical_preflight_requires_specific_tests(monkeypatch):
    monkeypatch.setattr(
        block_close,
        "validate_repository_root",
        lambda: None,
    )
    monkeypatch.setattr(
        block_close,
        "validate_diff",
        lambda: None,
    )
    monkeypatch.setattr(
        block_close.argparse.ArgumentParser,
        "parse_args",
        lambda self: SimpleNamespace(
            tests=[],
            phonetic_regression=False,
            full_suite=False,
            technical_preflight=True,
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Technical preflight requires at least one specific test path",
    ):
        block_close.main()


def test_technical_preflight_runs_specific_and_regression(monkeypatch):
    calls = []

    monkeypatch.setattr(
        block_close,
        "validate_repository_root",
        lambda: calls.append("root"),
    )
    monkeypatch.setattr(
        block_close,
        "validate_diff",
        lambda: calls.append("diff"),
    )
    monkeypatch.setattr(
        block_close,
        "validate_technical_changes",
        lambda: calls.append("changes"),
    )
    monkeypatch.setattr(
        block_close,
        "run_specific_tests",
        lambda tests: calls.append(("specific", tests)),
    )
    monkeypatch.setattr(
        block_close,
        "run_phonetic_regression",
        lambda: calls.append("regression"),
    )
    monkeypatch.setattr(
        block_close,
        "run_full_suite",
        lambda: calls.append("full"),
    )
    monkeypatch.setattr(
        block_close.argparse.ArgumentParser,
        "parse_args",
        lambda self: SimpleNamespace(
            tests=["tests/test_example.py"],
            phonetic_regression=False,
            full_suite=False,
            technical_preflight=True,
            stage_technical=False,
        ),
    )

    block_close.main()

    assert calls == [
        "root",
        "diff",
        "changes",
        ("specific", ["tests/test_example.py"]),
        "regression",
    ]


def test_validate_technical_changes_accepts_technical_files(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(
            stdout=" M app/example.py\n?? tests/test_example.py\n",
        ),
    )

    assert block_close.validate_technical_changes() == [
        "app/example.py",
        "tests/test_example.py",
    ]


def test_validate_technical_changes_requires_changes(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(stdout=""),
    )

    with pytest.raises(SystemExit, match="No technical changes found"):
        block_close.validate_technical_changes()


def test_validate_technical_changes_rejects_documentation(monkeypatch):
    monkeypatch.setattr(
        block_close.subprocess,
        "run",
        lambda *args, **kwargs: completed(
            stdout=" M app/example.py\n M docs/bitacora.md\n",
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Technical changes include documentation: docs/bitacora.md",
    ):
        block_close.validate_technical_changes()


def test_stage_technical_changes_stages_only_validated_paths(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return completed()

    monkeypatch.setattr(block_close.subprocess, "run", fake_run)

    block_close.stage_technical_changes([
        "scripts/engineering/block_close.py",
        "tests/test_block_close.py",
    ])

    assert calls == [[
        "git",
        "add",
        "--",
        "scripts/engineering/block_close.py",
        "tests/test_block_close.py",
    ]]


def test_stage_technical_changes_requires_validated_paths():
    with pytest.raises(
        SystemExit,
        match="No validated technical paths to stage",
    ):
        block_close.stage_technical_changes([])


def test_stage_technical_requires_preflight(monkeypatch):
    monkeypatch.setattr(
        block_close,
        "validate_repository_root",
        lambda: None,
    )
    monkeypatch.setattr(
        block_close,
        "validate_diff",
        lambda: None,
    )
    monkeypatch.setattr(
        block_close.argparse.ArgumentParser,
        "parse_args",
        lambda self: SimpleNamespace(
            tests=[],
            phonetic_regression=False,
            full_suite=False,
            technical_preflight=False,
            stage_technical=True,
        ),
    )

    with pytest.raises(
        SystemExit,
        match="Technical staging requires --technical-preflight",
    ):
        block_close.main()


def test_stage_technical_runs_after_preflight(monkeypatch):
    calls = []

    monkeypatch.setattr(
        block_close,
        "validate_repository_root",
        lambda: calls.append("root"),
    )
    monkeypatch.setattr(
        block_close,
        "validate_diff",
        lambda: calls.append("diff"),
    )
    monkeypatch.setattr(
        block_close,
        "validate_technical_changes",
        lambda: [
            "scripts/engineering/block_close.py",
            "tests/test_block_close.py",
        ],
    )
    monkeypatch.setattr(
        block_close,
        "run_specific_tests",
        lambda tests: calls.append("specific"),
    )
    monkeypatch.setattr(
        block_close,
        "run_phonetic_regression",
        lambda: calls.append("regression"),
    )
    monkeypatch.setattr(
        block_close,
        "run_full_suite",
        lambda: calls.append("full"),
    )
    monkeypatch.setattr(
        block_close,
        "stage_technical_changes",
        lambda paths: calls.append(("stage", paths)),
    )
    monkeypatch.setattr(
        block_close.argparse.ArgumentParser,
        "parse_args",
        lambda self: SimpleNamespace(
            tests=["tests/test_block_close.py"],
            phonetic_regression=False,
            full_suite=False,
            technical_preflight=True,
            stage_technical=True,
        ),
    )

    block_close.main()

    assert calls == [
        "root",
        "diff",
        "specific",
        "regression",
        (
            "stage",
            [
                "scripts/engineering/block_close.py",
                "tests/test_block_close.py",
            ],
        ),
    ]
