from __future__ import annotations

import argparse
import ctypes
import math
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.engineering.operational_state import (
    validate_against_git,
    validate_operational_state,
)


DEFAULT_TIMEOUT_SECONDS = 1800.0
TERMINATION_GRACE_SECONDS = 5.0
PROCESS_GROUP_POLL_SECONDS = 0.01
PR_SET_CHILD_SUBREAPER = 36
_SUBREAPER_ENABLED = False


class WorkflowPhaseError(RuntimeError):
    """Describe a fail-closed Closure Gate phase failure."""

    def __init__(self, phase: str, detail: str) -> None:
        super().__init__(detail)
        self.phase = phase
        self.detail = detail


class WorkflowInterrupted(WorkflowPhaseError):
    """Report an interruption after the active child group has been reaped."""


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


def _enable_child_subreaper() -> None:
    global _SUBREAPER_ENABLED
    if _SUBREAPER_ENABLED:
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))
    _SUBREAPER_ENABLED = True


def _signal_process_group(
    process_group_id: int,
    group_signal: signal.Signals,
) -> None:
    try:
        os.killpg(process_group_id, group_signal)
    except ProcessLookupError:
        return


def _process_group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _reap_process_group_children(process_group_id: int) -> None:
    while True:
        try:
            child_pid, _ = os.waitpid(-process_group_id, os.WNOHANG)
        except ChildProcessError:
            return
        if child_pid == 0:
            return


def _wait_for_process_group_exit(
    process_group_id: int,
    timeout_seconds: float,
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while True:
        _reap_process_group_children(process_group_id)
        if not _process_group_exists(process_group_id):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(PROCESS_GROUP_POLL_SECONDS)


def _terminate_residual_process_group(process_group_id: int) -> bool:
    _signal_process_group(process_group_id, signal.SIGTERM)
    if _wait_for_process_group_exit(
        process_group_id,
        TERMINATION_GRACE_SECONDS,
    ):
        return True
    _signal_process_group(process_group_id, signal.SIGKILL)
    return _wait_for_process_group_exit(
        process_group_id,
        TERMINATION_GRACE_SECONDS,
    )


def _terminate_and_reap(
    process: subprocess.Popen[str],
) -> tuple[str, str, bool]:
    _signal_process_group(process.pid, signal.SIGTERM)
    try:
        stdout, stderr = process.communicate(timeout=TERMINATION_GRACE_SECONDS)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        _signal_process_group(process.pid, signal.SIGKILL)
        deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return "", "", False
            try:
                stdout, stderr = process.communicate(timeout=remaining)
                break
            except KeyboardInterrupt:
                continue
            except subprocess.TimeoutExpired:
                return "", "", False
    group_terminated = _wait_for_process_group_exit(
        process.pid,
        TERMINATION_GRACE_SECONDS,
    )
    if not group_terminated:
        _signal_process_group(process.pid, signal.SIGKILL)
        group_terminated = _wait_for_process_group_exit(
            process.pid,
            TERMINATION_GRACE_SECONDS,
        )
    return stdout, stderr, group_terminated


def _raise_phase_failure(phase: str, detail: str) -> NoReturn:
    raise WorkflowPhaseError(phase, detail)


def _run_phase(
    phase: str,
    command: list[str],
    *,
    root: Path,
    timeout_seconds: float,
) -> None:
    print(f"[{phase}] START", flush=True)
    try:
        _enable_child_subreaper()
        process = subprocess.Popen(
            command,
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            start_new_session=True,
        )
    except OSError as error:
        _raise_phase_failure(phase, f"could not start helper: {error}")

    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        stdout, stderr, group_terminated = _terminate_and_reap(process)
        _forward_output(stdout, stderr)
        cleanup = (
            "child group terminated"
            if group_terminated
            else "child group termination could not be confirmed"
        )
        _raise_phase_failure(
            phase,
            f"timed out after {timeout_seconds:g} seconds; {cleanup}",
        )
    except KeyboardInterrupt as error:
        stdout, stderr, group_terminated = _terminate_and_reap(process)
        _forward_output(stdout, stderr)
        cleanup = (
            "child group terminated"
            if group_terminated
            else "child group termination could not be confirmed"
        )
        raise WorkflowInterrupted(
            phase,
            f"interrupted; {cleanup}",
        ) from error
    except Exception as error:
        stdout, stderr, group_terminated = _terminate_and_reap(process)
        _forward_output(stdout, stderr)
        cleanup = (
            "child group terminated"
            if group_terminated
            else "child group termination could not be confirmed"
        )
        _raise_phase_failure(
            phase,
            f"helper communication failed; {cleanup}: {error}",
        )

    _forward_output(stdout, stderr)
    if _process_group_exists(process.pid):
        group_terminated = _terminate_residual_process_group(process.pid)
        cleanup = (
            "residual group terminated"
            if group_terminated
            else "residual group termination could not be confirmed"
        )
        _raise_phase_failure(
            phase,
            "helper leader exited with status "
            f"{process.returncode} but left live descendants; {cleanup}",
        )
    if process.returncode != 0:
        _raise_phase_failure(
            phase,
            f"helper exited with status {process.returncode}",
        )
    print(f"[{phase}] PASS", flush=True)


def run_block_workflow(
    *,
    block_close_args: list[str],
    branch: str,
    upstream: str,
    message: str,
    files: list[str],
    checkpoint_prepare_format: str = "markdown",
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    root: Path = ROOT,
    state_path: Path | None = None,
) -> None:
    """Run the deterministic Closure Gate after its human decisions are complete."""
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    if not files:
        raise ValueError("At least one closure file is required")
    if checkpoint_prepare_format not in {"markdown", "compact"}:
        raise ValueError(
            "checkpoint_prepare_format must be 'markdown' or 'compact'"
        )

    checkpoint = (
        state_path
        if state_path is not None
        else root / "docs" / "estado-operativo.md"
    )
    print("[checkpoint] START", flush=True)
    try:
        report = validate_operational_state(checkpoint)
        validate_against_git(report, root)
    except (OSError, ValueError) as error:
        _raise_phase_failure("checkpoint", str(error))
    print(
        "[checkpoint] PASS: "
        f"{report.line_count} lines, updated {report.updated_at.isoformat()}",
        flush=True,
    )

    scripts = root / "scripts" / "engineering"
    _run_phase(
        "block-close",
        [sys.executable, str(scripts / "block_close.py"), *block_close_args],
        root=root,
        timeout_seconds=timeout_seconds,
    )
    git_close_command = [
        sys.executable,
        str(scripts / "git_close.py"),
        "--branch",
        branch,
        "--upstream",
        upstream,
        "--message",
        message,
    ]
    for path in files:
        git_close_command.extend(("--file", path))
    _run_phase(
        "git-close",
        git_close_command,
        root=root,
        timeout_seconds=timeout_seconds,
    )
    checkpoint_prepare_command = [
        sys.executable,
        str(scripts / "conversation_checkpoint.py"),
        "prepare",
    ]
    if checkpoint_prepare_format == "compact":
        checkpoint_prepare_command.extend(("--format", "compact"))
    try:
        _run_phase(
            "checkpoint-prepare",
            checkpoint_prepare_command,
            root=root,
            timeout_seconds=timeout_seconds,
        )
    except WorkflowInterrupted as error:
        raise WorkflowInterrupted(
            error.phase,
            f"{error.detail}; PARTIAL CLOSURE: Git close already completed; "
            "no rollback or Git close retry was attempted",
        ) from error
    except WorkflowPhaseError as error:
        raise WorkflowPhaseError(
            error.phase,
            f"{error.detail}; PARTIAL CLOSURE: Git close already completed; "
            "no rollback or Git close retry was attempted",
        ) from error


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("timeout must be a number") from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than zero")
    return timeout


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the approved deterministic Closure Gate after readiness, "
            "postflight, documentation, scope/allowlist, and commit message "
            "are decided externally: checkpoint validation -> block_close.py "
            "-> git_close.py -> conversation_checkpoint.py prepare."
        )
    )
    parser.add_argument("--state-path", type=Path)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--file", action="append", required=True, dest="files")
    parser.add_argument(
        "--timeout-seconds",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum runtime for each helper phase.",
    )
    parser.add_argument(
        "--checkpoint-prepare-format",
        choices=("markdown", "compact"),
        default="markdown",
        help=(
            "Output format for the final conversation_checkpoint.py prepare "
            "only (default: markdown)."
        ),
    )
    parser.add_argument(
        "--block-close-args",
        nargs=argparse.REMAINDER,
        required=True,
        help="Arguments passed only to block_close.py; this option must be last.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        run_block_workflow(
            block_close_args=args.block_close_args,
            branch=args.branch,
            upstream=args.upstream,
            message=args.message,
            files=args.files,
            checkpoint_prepare_format=args.checkpoint_prepare_format,
            timeout_seconds=args.timeout_seconds,
            state_path=args.state_path,
        )
    except WorkflowInterrupted as error:
        print(f"[{error.phase}] INTERRUPTED: {error.detail}", file=sys.stderr)
        return 130
    except (WorkflowPhaseError, ValueError) as error:
        if isinstance(error, WorkflowPhaseError):
            print(f"[{error.phase}] FAIL: {error.detail}", file=sys.stderr)
        else:
            print(f"[workflow] FAIL: {error}", file=sys.stderr)
        return 1
    print("[closure-gate] PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
