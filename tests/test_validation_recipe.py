from __future__ import annotations

import argparse
from types import SimpleNamespace
from urllib.parse import parse_qsl

import pytest

from scripts.engineering import validation_recipe


_DEFAULT = object()


def _completed(returncode: int = 0, stdout: str = "", stderr: object = _DEFAULT):
    if stderr is _DEFAULT:
        stderr = ""
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def _run_recipe(
    monkeypatch: pytest.MonkeyPatch,
    results: list[SimpleNamespace],
) -> tuple[list[tuple[str, ...]], list[dict[str, object]]]:
    commands: list[tuple[str, ...]] = []
    options: list[dict[str, object]] = []

    def fake_run(command: tuple[str, ...], **kwargs: object) -> SimpleNamespace:
        commands.append(command)
        options.append(kwargs)
        return results[len(commands) - 1]

    monkeypatch.setattr(validation_recipe.subprocess, "run", fake_run)
    return commands, options


def test_happy_path_runs_exact_steps_in_order_and_emits_compact_pass(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    commands, options = _run_recipe(monkeypatch, [_completed() for _ in range(4)])

    assert validation_recipe.main([
        "approved-v1", "--focal", "tests/test focal.py",
        "--regression", "tests/test_regression.py",
    ]) == 0

    assert commands == [
        (
            ".venv/bin/python", "-m", "pytest", "tests/test focal.py",
            "tests/test_regression.py", "-q", "-p", "no:cacheprovider",
        ),
        ("git", "diff", "--check"),
        (validation_recipe.sys.executable, "scripts/engineering/operational_state.py", "validate"),
        (
            validation_recipe.sys.executable,
            "scripts/engineering/conversation_checkpoint.py", "prepare", "--format", "compact",
        ),
    ]
    assert all(option["cwd"] == validation_recipe.ROOT for option in options)
    assert all(option["stdin"] is validation_recipe.subprocess.DEVNULL for option in options)
    assert all(option["shell"] is False for option in options)
    assert all(option["check"] is False for option in options)
    assert parse_qsl(capsys.readouterr().out.strip()) == [
        ("VALIDATION_STATUS", "PASS"), ("RECIPE", "approved-v1"),
        ("STEPS", "4"), ("TEST_PATHS", "2"),
    ]


@pytest.mark.parametrize(
    ("failed_index", "failed_step"),
    [(0, "pytest"), (1, "diff-check"), (2, "operational-state"), (3, "checkpoint")],
)
def test_each_failed_step_stops_later_steps_and_preserves_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failed_index: int,
    failed_step: str,
) -> None:
    results = [_completed() for _ in range(failed_index)] + [
        _completed(7, "failure stdout\n", "failure stderr\n"),
    ]
    commands, _ = _run_recipe(monkeypatch, results)

    assert validation_recipe.main(["approved-v1", "--focal", "tests/test_one.py"]) == 7

    captured = capsys.readouterr()
    assert len(commands) == failed_index + 1
    assert "failure stdout" in captured.out
    assert "failure stderr" in captured.err
    assert parse_qsl(captured.err.splitlines()[-1]) == [
        ("VALIDATION_STATUS", "FAIL"), ("RECIPE", "approved-v1"),
        ("FAILED_STEP", failed_step), ("EXIT_CODE", "7"),
    ]


def test_verbose_forwards_success_output_before_compact_pass(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run_recipe(monkeypatch, [_completed(stdout="step out\n", stderr="step err\n") for _ in range(4)])

    assert validation_recipe.main([
        "approved-v1", "--focal", "tests/test_one.py", "--verbose",
    ]) == 0

    captured = capsys.readouterr()
    assert captured.out.count("step out") == 4
    assert captured.err.count("step err") == 4
    assert "VALIDATION_STATUS=PASS" in captured.out


def test_compact_pass_does_not_forward_success_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run_recipe(monkeypatch, [_completed(stdout="hidden out\n", stderr="hidden err\n") for _ in range(4)])

    assert validation_recipe.main(["approved-v1", "--focal", "tests/test_one.py"]) == 0

    captured = capsys.readouterr()
    assert captured.out.strip() == validation_recipe._pass_output(1)
    assert captured.err == ""


def test_regression_failure_is_inside_the_single_pytest_invocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    commands, _ = _run_recipe(monkeypatch, [_completed(1)])

    assert validation_recipe.main([
        "approved-v1", "--focal", "tests/test_focal.py",
        "--regression", "tests/test_regression.py",
    ]) == 1

    assert commands == [(
        ".venv/bin/python", "-m", "pytest", "tests/test_focal.py",
        "tests/test_regression.py", "-q", "-p", "no:cacheprovider",
    )]


@pytest.mark.parametrize(
    "value",
    ["/tmp/test.py", "tests/../outside.py", "-x", "tests/\0bad.py", "app/test.py"],
)
def test_cli_rejects_invalid_test_paths(value: str) -> None:
    with pytest.raises(SystemExit) as captured:
        validation_recipe.build_parser().parse_args([
            "approved-v1", "--focal", value,
        ])

    assert captured.value.code == 2


def test_cli_accepts_unicode_and_space_paths() -> None:
    args = validation_recipe.build_parser().parse_args([
        "approved-v1", "--focal", "tests/prueba á.py",
        "--regression", "tests/with space.py",
    ])

    assert args.focal == ["tests/prueba á.py"]
    assert args.regression == ["tests/with space.py"]


@pytest.mark.parametrize("option", ["--foc", "--verb", "--reg", "--unknown"])
def test_cli_rejects_abbreviated_and_unknown_options(option: str) -> None:
    with pytest.raises(SystemExit) as captured:
        validation_recipe.build_parser().parse_args([
            "approved-v1", option, "tests/test.py",
        ])

    assert captured.value.code == 2


def test_cli_accepts_only_complete_declared_options() -> None:
    args = validation_recipe.build_parser().parse_args([
        "approved-v1", "--focal", "tests/test_focal.py",
        "--regression", "tests/test_regression.py", "--verbose",
    ])

    assert args.focal == ["tests/test_focal.py"]
    assert args.regression == ["tests/test_regression.py"]
    assert args.verbose is True


def test_cli_rejects_unknown_recipe_and_missing_focal() -> None:
    with pytest.raises(SystemExit):
        validation_recipe.build_parser().parse_args(["other", "--focal", "tests/test.py"])

    assert validation_recipe.main(["approved-v1"]) == 2


def test_run_recipe_rejects_unknown_recipe_and_unvalidated_paths() -> None:
    with pytest.raises(ValueError, match="unknown recipe"):
        validation_recipe.run_recipe("other", focal_paths=["tests/test.py"], regression_paths=[])
    with pytest.raises(ValueError, match="at least one"):
        validation_recipe.run_recipe("approved-v1", focal_paths=[], regression_paths=[])
    with pytest.raises(argparse.ArgumentTypeError):
        validation_recipe.run_recipe("approved-v1", focal_paths=["/tmp/test.py"], regression_paths=[])


def test_recipe_commands_are_fixed_read_only_allowlist() -> None:
    commands = validation_recipe.build_steps(["tests/test_one.py"])

    assert [step.name for step in commands] == [
        "pytest", "diff-check", "operational-state", "checkpoint",
    ]
    rendered = " ".join(" ".join(step.command) for step in commands)
    for forbidden in ("git_close.py", "block_workflow.py", "git add", "git commit", "git push", "update-ref"):
        assert forbidden not in rendered
