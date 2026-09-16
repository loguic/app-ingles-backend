from __future__ import annotations

from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path
import signal
import subprocess

import pytest

from scripts.engineering import block_close, block_workflow
from scripts.engineering.operational_state import OperationalStateReport


class FakeProcess:
    def __init__(
        self,
        command: list[str],
        *,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
        first_error: BaseException | None = None,
        cleanup_timeout: bool = False,
    ) -> None:
        self.command = command
        self.final_returncode = returncode
        self.returncode: int | None = None
        self.stdout = stdout
        self.stderr = stderr
        self.first_error = first_error
        self.cleanup_timeout = cleanup_timeout
        self.communicate_calls: list[float | None] = []
        self.sent_signals: list[signal.Signals] = []
        self.pid = 4100

    def communicate(self, timeout: float | None = None) -> tuple[str, str]:
        self.communicate_calls.append(timeout)
        if len(self.communicate_calls) == 1 and self.first_error is not None:
            raise self.first_error
        if self.cleanup_timeout and len(self.communicate_calls) == 2:
            raise subprocess.TimeoutExpired(self.command, timeout)
        self.returncode = self.final_returncode
        return self.stdout, self.stderr

    def poll(self) -> int | None:
        return self.returncode

    def send_signal(self, group_signal: signal.Signals) -> None:
        self.sent_signals.append(group_signal)


def _valid_checkpoint(monkeypatch: pytest.MonkeyPatch, state_path: Path) -> None:
    report = OperationalStateReport(
        path=state_path,
        updated_at=datetime(2026, 9, 15, 20, 0, tzinfo=timezone.utc),
        line_count=106,
        sections=(),
    )
    monkeypatch.setattr(
        block_workflow,
        "validate_operational_state",
        lambda path: report,
    )
    monkeypatch.setattr(
        block_workflow,
        "validate_against_git",
        lambda current_report, root: None,
    )


def _workflow_kwargs(tmp_path: Path) -> dict[str, object]:
    return {
        "block_close_args": ["tests/test_block_workflow.py", "--full-suite"],
        "branch": "master",
        "upstream": "origin/master",
        "message": "tooling make closure workflow reliable",
        "files": [
            "scripts/engineering/block_workflow.py",
            "tests/test_block_workflow.py",
        ],
        "timeout_seconds": 37.0,
        "root": tmp_path,
        "state_path": tmp_path / "docs" / "estado-operativo.md",
    }


def _install_processes(
    monkeypatch: pytest.MonkeyPatch,
    specifications: list[dict[str, object]],
) -> tuple[list[FakeProcess], list[dict[str, object]]]:
    processes: list[FakeProcess] = []
    options: list[dict[str, object]] = []

    def fake_popen(command: list[str], **kwargs: object) -> FakeProcess:
        options.append(kwargs)
        process = FakeProcess(command, **specifications[len(processes)])
        processes.append(process)
        return process

    monkeypatch.setattr(block_workflow.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        block_workflow,
        "_process_group_exists",
        lambda process_group_id: False,
    )
    return processes, options


def _record_signals_for_disappeared_group(
    signals: list[signal.Signals],
):
    def fake_killpg(pid: int, group_signal: signal.Signals | int) -> None:
        if group_signal == 0:
            raise ProcessLookupError
        signals.append(signal.Signals(group_signal))

    return fake_killpg


def test_happy_path_runs_three_phases_in_order_with_exact_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    processes, options = _install_processes(monkeypatch, [{}, {}, {}])

    block_workflow.run_block_workflow(**kwargs)

    scripts = tmp_path / "scripts" / "engineering"
    assert [process.command for process in processes] == [
        [
            block_workflow.sys.executable,
            str(scripts / "block_close.py"),
            "tests/test_block_workflow.py",
            "--full-suite",
        ],
        [
            block_workflow.sys.executable,
            str(scripts / "git_close.py"),
            "--branch",
            "master",
            "--upstream",
            "origin/master",
            "--message",
            "tooling make closure workflow reliable",
            "--file",
            "scripts/engineering/block_workflow.py",
            "--file",
            "tests/test_block_workflow.py",
        ],
        [
            block_workflow.sys.executable,
            str(scripts / "conversation_checkpoint.py"),
            "prepare",
        ],
    ]
    assert all(process.communicate_calls == [37.0] for process in processes)
    assert all(option["stdin"] is subprocess.DEVNULL for option in options)
    assert all(option["stdout"] is subprocess.PIPE for option in options)
    assert all(option["stderr"] is subprocess.PIPE for option in options)
    assert all(option["start_new_session"] is True for option in options)
    assert all(option["shell"] is False for option in options)
    assert all(process.command[0] != "git" for process in processes)


def test_compact_prepare_runs_once_with_exact_format_argument(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    kwargs["checkpoint_prepare_format"] = "compact"
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    processes, _ = _install_processes(monkeypatch, [{}, {}, {}])

    block_workflow.run_block_workflow(**kwargs)

    assert [process.command for process in processes[-1:]] == [[
        block_workflow.sys.executable,
        str(tmp_path / "scripts" / "engineering" / "conversation_checkpoint.py"),
        "prepare",
        "--format",
        "compact",
    ]]
    assert len(processes) == 3


def test_compact_prepare_failure_preserves_output_without_markdown_retry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    kwargs["checkpoint_prepare_format"] = "compact"
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    processes, _ = _install_processes(
        monkeypatch,
        [
            {},
            {},
            {
                "returncode": 7,
                "stdout": "CHECKPOINT_FORMAT=compact-v1&detail=partial\n",
                "stderr": "prepare compact diagnostic\n",
            },
        ],
    )

    with pytest.raises(block_workflow.WorkflowPhaseError) as captured:
        block_workflow.run_block_workflow(**kwargs)

    output = capsys.readouterr()
    assert captured.value.phase == "checkpoint-prepare"
    assert "PARTIAL CLOSURE: Git close already completed" in captured.value.detail
    assert "CHECKPOINT_FORMAT=compact-v1&detail=partial" in output.out
    assert "prepare compact diagnostic" in output.err
    assert len(processes) == 3
    assert processes[-1].command[-2:] == ["--format", "compact"]
    assert sum("conversation_checkpoint.py" in process.command[1] for process in processes) == 1


@pytest.mark.parametrize(
    ("returncodes", "failed_phase", "started_count"),
    [
        ([9], "block-close", 1),
        ([0, 8], "git-close", 2),
        ([0, 0, 7], "checkpoint-prepare", 3),
    ],
)
def test_phase_failure_is_global_and_stops_later_phases(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    returncodes: list[int],
    failed_phase: str,
    started_count: int,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    processes, _ = _install_processes(
        monkeypatch,
        [{"returncode": returncode} for returncode in returncodes],
    )

    with pytest.raises(block_workflow.WorkflowPhaseError) as captured:
        block_workflow.run_block_workflow(**kwargs)

    assert captured.value.phase == failed_phase
    assert len(processes) == started_count


def test_checkpoint_failure_stops_before_any_child(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    monkeypatch.setattr(
        block_workflow,
        "validate_operational_state",
        lambda path: (_ for _ in ()).throw(ValueError("checkpoint stale")),
    )
    processes, _ = _install_processes(monkeypatch, [])

    with pytest.raises(block_workflow.WorkflowPhaseError) as captured:
        block_workflow.run_block_workflow(**kwargs)

    assert captured.value.phase == "checkpoint"
    assert processes == []


def test_stdout_and_stderr_are_preserved(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    _install_processes(
        monkeypatch,
        [
            {"stdout": "technical output\n", "stderr": "technical warning\n"},
            {"stdout": "git output\n", "stderr": "git warning\n"},
            {"stdout": "checkpoint output\n", "stderr": "checkpoint warning\n"},
        ],
    )

    block_workflow.run_block_workflow(**kwargs)

    captured = capsys.readouterr()
    assert "technical output\n" in captured.out
    assert "git output\n" in captured.out
    assert "checkpoint output\n" in captured.out
    assert "technical warning\n" in captured.err
    assert "git warning\n" in captured.err
    assert "checkpoint warning\n" in captured.err


def test_timeout_terminates_and_reaps_the_child_group(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    timeout = subprocess.TimeoutExpired(["helper"], 37.0)
    process = FakeProcess(
        ["helper"],
        returncode=-signal.SIGTERM,
        stdout="partial stdout\n",
        stderr="partial stderr\n",
        first_error=timeout,
    )
    signals: list[signal.Signals] = []
    monkeypatch.setattr(
        block_workflow.subprocess,
        "Popen",
        lambda command, **kwargs: process,
    )
    monkeypatch.setattr(
        block_workflow.os,
        "killpg",
        _record_signals_for_disappeared_group(signals),
    )

    with pytest.raises(block_workflow.WorkflowPhaseError, match="timed out"):
        block_workflow._run_phase(
            "block-close",
            ["helper"],
            root=tmp_path,
            timeout_seconds=37.0,
        )

    assert signals == [signal.SIGTERM]
    assert process.communicate_calls == [37.0, block_workflow.TERMINATION_GRACE_SECONDS]
    assert process.returncode == -signal.SIGTERM


def test_stubborn_child_group_is_killed_and_reaped(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process = FakeProcess(
        ["helper"],
        returncode=-signal.SIGKILL,
        first_error=subprocess.TimeoutExpired(["helper"], 1.0),
        cleanup_timeout=True,
    )
    signals: list[signal.Signals] = []
    monkeypatch.setattr(
        block_workflow.subprocess,
        "Popen",
        lambda command, **kwargs: process,
    )
    monkeypatch.setattr(
        block_workflow.os,
        "killpg",
        lambda pid, group_signal: signals.append(signal.Signals(group_signal)),
    )
    monkeypatch.setattr(
        block_workflow,
        "_wait_for_process_group_exit",
        lambda process_group_id, timeout_seconds: True,
    )

    with pytest.raises(block_workflow.WorkflowPhaseError, match="child group terminated"):
        block_workflow._run_phase(
            "git-close",
            ["helper"],
            root=tmp_path,
            timeout_seconds=1.0,
        )

    assert signals == [signal.SIGTERM, signal.SIGKILL]
    assert process.communicate_calls[:2] == [
        1.0,
        block_workflow.TERMINATION_GRACE_SECONDS,
    ]
    assert 0 < process.communicate_calls[2] <= block_workflow.TERMINATION_GRACE_SECONDS
    assert process.returncode == -signal.SIGKILL


def test_residual_process_group_is_signalled_after_leader_exited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signals: list[signal.Signals] = []
    monkeypatch.setattr(
        block_workflow.os,
        "killpg",
        lambda pid, group_signal: signals.append(signal.Signals(group_signal)),
    )
    monkeypatch.setattr(
        block_workflow,
        "_wait_for_process_group_exit",
        lambda process_group_id, timeout_seconds: True,
    )

    assert block_workflow._terminate_residual_process_group(4100) is True

    assert signals == [signal.SIGTERM]


def test_timeout_reaps_a_real_child_and_preserves_partial_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real_popen = subprocess.Popen
    processes: list[subprocess.Popen[str]] = []

    def capture_popen(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.Popen[str]:
        process = real_popen(command, **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr(block_workflow.subprocess, "Popen", capture_popen)

    with pytest.raises(block_workflow.WorkflowPhaseError, match="timed out"):
        block_workflow._run_phase(
            "block-close",
            [
                block_workflow.sys.executable,
                "-c",
                (
                    "import time; "
                    "print('child started', flush=True); "
                    "time.sleep(60)"
                ),
            ],
            root=tmp_path,
            timeout_seconds=0.1,
        )

    assert len(processes) == 1
    assert processes[0].poll() is not None
    assert "child started" in capsys.readouterr().out


def test_successful_leader_with_live_descendant_fails_and_cleans_group(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    marker = tmp_path / "descendant.pid"
    leader_code = (
        "import subprocess, sys; "
        "child = subprocess.Popen("
        "[sys.executable, '-c', 'import time; time.sleep(60)'], "
        "stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, "
        "stderr=subprocess.DEVNULL); "
        "open(sys.argv[1], 'w').write(str(child.pid))"
    )

    with pytest.raises(
        block_workflow.WorkflowPhaseError,
        match="leader exited with status 0 but left live descendants",
    ):
        block_workflow._run_phase(
            "block-close",
            [block_workflow.sys.executable, "-c", leader_code, str(marker)],
            root=tmp_path,
            timeout_seconds=2.0,
        )

    descendant_pid = int(marker.read_text())
    with pytest.raises(ProcessLookupError):
        block_workflow.os.kill(descendant_pid, 0)
    assert "[block-close] PASS" not in capsys.readouterr().out


def test_real_leader_killed_by_signal_is_reported_as_failure(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        block_workflow.WorkflowPhaseError,
        match="helper exited with status -15",
    ):
        block_workflow._run_phase(
            "git-close",
            [
                block_workflow.sys.executable,
                "-c",
                "import os, signal; os.kill(os.getpid(), signal.SIGTERM)",
            ],
            root=tmp_path,
            timeout_seconds=2.0,
        )


def test_keyboard_interrupt_terminates_and_reaps_child_group(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process = FakeProcess(
        ["helper"],
        returncode=-signal.SIGTERM,
        first_error=KeyboardInterrupt(),
    )
    signals: list[signal.Signals] = []
    monkeypatch.setattr(
        block_workflow.subprocess,
        "Popen",
        lambda command, **kwargs: process,
    )
    monkeypatch.setattr(
        block_workflow.os,
        "killpg",
        _record_signals_for_disappeared_group(signals),
    )

    with pytest.raises(block_workflow.WorkflowInterrupted):
        block_workflow._run_phase(
            "checkpoint-prepare",
            ["helper"],
            root=tmp_path,
            timeout_seconds=12.0,
        )

    assert signals == [signal.SIGTERM]
    assert process.communicate_calls == [12.0, block_workflow.TERMINATION_GRACE_SECONDS]


def test_launcher_failure_stops_workflow_before_later_phases(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    launch_attempts: list[list[str]] = []

    def reject_launch(command: list[str], **options: object) -> FakeProcess:
        launch_attempts.append(command)
        raise OSError("launcher unavailable")

    monkeypatch.setattr(block_workflow.subprocess, "Popen", reject_launch)

    with pytest.raises(block_workflow.WorkflowPhaseError) as captured:
        block_workflow.run_block_workflow(**kwargs)

    assert captured.value.phase == "block-close"
    assert "could not start helper" in captured.value.detail
    assert len(launch_attempts) == 1


def test_prepare_failure_after_published_git_close_is_partial_closure_without_retry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    _valid_checkpoint(monkeypatch, kwargs["state_path"])
    phases: list[str] = []
    published = False

    def run_phase(
        phase: str,
        command: list[str],
        **options: object,
    ) -> None:
        nonlocal published
        phases.append(phase)
        if phase == "git-close":
            published = True
        if phase == "checkpoint-prepare":
            raise block_workflow.WorkflowPhaseError(
                phase,
                "prepare failed after published Git close",
            )

    monkeypatch.setattr(block_workflow, "_run_phase", run_phase)

    with pytest.raises(block_workflow.WorkflowPhaseError) as captured:
        block_workflow.run_block_workflow(**kwargs)

    assert published is True
    assert captured.value.phase == "checkpoint-prepare"
    assert "PARTIAL CLOSURE: Git close already completed" in captured.value.detail
    assert "no rollback or Git close retry was attempted" in captured.value.detail
    assert phases == ["block-close", "git-close", "checkpoint-prepare"]
    assert phases.count("git-close") == 1


def test_cli_separates_workflow_options_from_block_close_arguments() -> None:
    args = block_workflow.build_parser().parse_args(
        [
            "--branch",
            "master",
            "--upstream",
            "origin/master",
            "--message",
            "close exact scope",
            "--file",
            "app/example.py",
            "--file",
            "tests/test_example.py",
            "--timeout-seconds",
            "42",
            "--checkpoint-prepare-format",
            "compact",
            "--block-close-args",
            "tests/test_example.py",
            "--full-suite",
        ]
    )

    assert args.branch == "master"
    assert args.upstream == "origin/master"
    assert args.message == "close exact scope"
    assert args.files == ["app/example.py", "tests/test_example.py"]
    assert args.timeout_seconds == 42.0
    assert args.checkpoint_prepare_format == "compact"
    assert args.block_close_args == ["tests/test_example.py", "--full-suite"]


def test_cli_defaults_prepare_format_to_markdown() -> None:
    args = block_workflow.build_parser().parse_args(
        [
            "--branch", "master", "--upstream", "origin/master",
            "--message", "close", "--file", "example.py",
            "--block-close-args", "tests/test_example.py",
        ]
    )

    assert args.checkpoint_prepare_format == "markdown"


def test_cli_help_describes_external_decisions_and_prepare_scope() -> None:
    help_text = block_workflow.build_parser().format_help()

    assert "checkpoint validation -> block_close.py" in help_text
    assert "git_close.py" in help_text
    assert "conversation_checkpoint.py prepare" in help_text
    assert "readiness, postflight," in help_text
    assert "documentation, scope/allowlist" in help_text
    assert "scope/allowlist" in help_text
    assert "default: markdown" in help_text
    assert "prepare only" in help_text


def test_block_close_help_explains_technical_staging() -> None:
    help_text = block_close.build_parser().format_help()

    assert "Enable staging of previously validated technical" in help_text
    assert "files." in help_text


def test_cli_rejects_invalid_checkpoint_prepare_format() -> None:
    with pytest.raises(SystemExit) as captured:
        block_workflow.build_parser().parse_args(
            [
                "--branch", "master", "--upstream", "origin/master",
                "--message", "close", "--file", "example.py",
                "--checkpoint-prepare-format", "json",
                "--block-close-args", "tests/test_example.py",
            ]
        )

    assert captured.value.code == 2


def test_workflow_rejects_unknown_prepare_format_before_any_child(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kwargs = _workflow_kwargs(tmp_path)
    kwargs["checkpoint_prepare_format"] = "json"
    processes, _ = _install_processes(monkeypatch, [])

    with pytest.raises(ValueError, match="checkpoint_prepare_format"):
        block_workflow.run_block_workflow(**kwargs)

    assert processes == []


@pytest.mark.parametrize(
    ("error", "expected_code"),
    [
        (block_workflow.WorkflowPhaseError("git-close", "failed"), 1),
        (block_workflow.WorkflowInterrupted("git-close", "interrupted"), 130),
    ],
)
def test_main_returns_nonzero_for_failure_and_interruption(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_code: int,
) -> None:
    monkeypatch.setattr(
        block_workflow,
        "build_parser",
        lambda: type(
            "Parser",
            (),
            {
                "parse_args": lambda self: Namespace(
                    block_close_args=[],
                    branch="master",
                    upstream="origin/master",
                    message="close",
                    files=["example.py"],
                    checkpoint_prepare_format="markdown",
                    timeout_seconds=10.0,
                    state_path=None,
                )
            },
        )(),
    )
    monkeypatch.setattr(
        block_workflow,
        "run_block_workflow",
        lambda **kwargs: (_ for _ in ()).throw(error),
    )

    assert block_workflow.main() == expected_code
