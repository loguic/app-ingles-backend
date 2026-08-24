from datetime import datetime, timezone
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from scripts.engineering import block_workflow
from scripts.engineering.operational_state import OperationalStateReport


def test_delegate_after_valid_checkpoint(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "estado-operativo.md"
    state_path.write_text("checkpoint", encoding="utf-8")
    calls: list[tuple[list[str], Path]] = []

    report = OperationalStateReport(
        path=state_path,
        updated_at=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        line_count=101,
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

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        check: bool,
    ) -> CompletedProcess[str]:
        assert check is True
        calls.append((command, cwd))
        return CompletedProcess(command, 0)

    monkeypatch.setattr(block_workflow.subprocess, "run", fake_run)

    block_workflow.run_block_workflow(
        ["--technical-preflight"],
        root=tmp_path,
        state_path=state_path,
    )

    assert calls == [
        (
            [
                block_workflow.sys.executable,
                str(
                    tmp_path
                    / "scripts"
                    / "engineering"
                    / "block_close.py"
                ),
                "--technical-preflight",
            ],
            tmp_path,
        )
    ]


def test_stop_before_delegation_when_checkpoint_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "estado-operativo.md"
    delegated = False

    def reject_checkpoint(path: Path) -> None:
        raise ValueError("Operational state is stale")

    def fake_run(*args: object, **kwargs: object) -> None:
        nonlocal delegated
        delegated = True

    monkeypatch.setattr(
        block_workflow,
        "validate_operational_state",
        reject_checkpoint,
    )
    monkeypatch.setattr(block_workflow.subprocess, "run", fake_run)

    with pytest.raises(
        ValueError,
        match="Operational state is stale",
    ):
        block_workflow.run_block_workflow(
            ["--technical-preflight"],
            root=tmp_path,
            state_path=state_path,
        )

    assert delegated is False


def test_forward_all_block_close_arguments(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    state_path = tmp_path / "estado-operativo.md"
    report = OperationalStateReport(
        path=state_path,
        updated_at=datetime(2026, 8, 5, 12, 0, tzinfo=timezone.utc),
        line_count=101,
        sections=(),
    )
    received: list[str] = []

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

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> CompletedProcess[str]:
        received.extend(command)
        return CompletedProcess(command, 0)

    monkeypatch.setattr(block_workflow.subprocess, "run", fake_run)

    block_workflow.run_block_workflow(
        [
            "--technical-preflight",
            "--specific-test",
            "tests/test_example.py",
        ],
        root=tmp_path,
        state_path=state_path,
    )

    assert received[-3:] == [
        "--technical-preflight",
        "--specific-test",
        "tests/test_example.py",
    ]
