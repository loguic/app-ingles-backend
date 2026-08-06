import os
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.engineering.postgresql_devsecops_adapter import (
    AdapterConfig,
    AdapterError,
    CommandRunner,
    ManagedWorkspace,
    PostgreSQLBinaries,
    PostgreSQLCluster,
    _temporary_database_url,
    cleanup_workspace,
    create_backup,
    create_workspace,
    run_isolated_rehearsal,
    run_alembic,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]


def config(**changes):
    values = {
        "environment": "test",
        "port": 55439,
        "repository_root": ROOT,
        "authorized_temp_parent": Path(tempfile.gettempdir()),
        "timeout_seconds": 20,
    }
    values.update(changes)
    return AdapterConfig(**values)


def binaries(**changes):
    values = {
        "psql": Path("/usr/bin/psql"),
        "pg_dump": Path("/usr/bin/pg_dump"),
        "pg_restore": Path("/usr/bin/pg_restore"),
        "createdb": Path("/usr/bin/createdb"),
        "dropdb": Path("/usr/bin/dropdb"),
        "initdb": Path("/usr/lib/postgresql/16/bin/initdb"),
        "pg_ctl": Path("/usr/lib/postgresql/16/bin/pg_ctl"),
        "postgres": Path("/usr/lib/postgresql/16/bin/postgres"),
        "alembic": ROOT / ".venv" / "bin" / "alembic",
    }
    values.update(changes)
    return PostgreSQLBinaries(**values)


def test_reject_system_postgresql_port():
    with pytest.raises(AdapterError, match="port is forbidden"):
        validate_config(config(port=5432))


def test_reject_port_outside_dynamic_range():
    with pytest.raises(AdapterError, match="high dynamic port"):
        validate_config(config(port=15432))


def test_reject_production():
    with pytest.raises(AdapterError, match="production"):
        validate_config(config(environment="production"))


def test_reject_cleanup_without_marker(tmp_path):
    root = tmp_path / "loguic-pg-s2-unmarked"
    root.mkdir()
    workspace = ManagedWorkspace(
        root=root,
        data=root / "data",
        socket=root / "socket",
        backups=root / "backups",
        evidence=root / "evidence",
        authorized_parent=tmp_path,
    )
    with pytest.raises(AdapterError, match="marker"):
        cleanup_workspace(workspace)
    assert root.exists()


def test_reject_cleanup_outside_authorized_parent(tmp_path):
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    outside = tmp_path / "loguic-pg-s2-outside"
    outside.mkdir()
    (outside / ".loguic-devsecops-managed").write_text("marker\n")
    workspace = ManagedWorkspace(
        root=outside,
        data=outside / "data",
        socket=outside / "socket",
        backups=outside / "backups",
        evidence=outside / "evidence",
        authorized_parent=authorized,
    )
    with pytest.raises(AdapterError, match="outside"):
        cleanup_workspace(workspace)
    assert outside.exists()


def test_command_runner_uses_no_shell_and_sets_timeout(monkeypatch):
    observed = {}

    class FakeProcess:
        pid = 12345
        returncode = 0

        def communicate(self, timeout=None):
            observed["timeout"] = timeout
            return "ok", ""

    def fake_popen(command, **kwargs):
        observed.update(kwargs)
        return FakeProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    result = CommandRunner(timeout_seconds=19).run(
        ["safe", "argument"],
        label="unit command",
    )

    assert result.stdout == "ok"
    assert observed["shell"] is False
    assert observed["start_new_session"] is True
    assert observed["timeout"] == 19


def test_stop_and_cleanup_when_stage_fails(monkeypatch, tmp_path):
    workspace = create_workspace(tmp_path)
    stopped = []

    class FailingRunner:
        def __init__(self, timeout):
            self.calls = 0

        def run(self, command, **kwargs):
            self.calls += 1
            if self.calls == 2:
                return SimpleNamespace(stdout="", stderr="")
            if self.calls == 3:
                raise AdapterError("injected failure")
            return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(
        "scripts.engineering.postgresql_devsecops_adapter.create_workspace",
        lambda parent: workspace,
    )
    monkeypatch.setattr(
        PostgreSQLCluster,
        "stop",
        lambda self: stopped.append(True) or True,
    )

    with pytest.raises(AdapterError, match="injected failure") as captured:
        run_isolated_rehearsal(
            config(),
            binaries(),
            runner_factory=FailingRunner,
        )

    assert stopped == [True]
    assert not workspace.root.exists()
    assert captured.value.workspace_path == workspace.root
    assert captured.value.postgresql_stopped is True
    assert captured.value.workspace_removed is True


def test_command_failure_preserves_observability_without_exposing_url(
    monkeypatch,
):
    class FailedProcess:
        pid = 12345
        returncode = 7

        def communicate(self, timeout=None):
            return "partial stdout", "failed postgresql://secret@host/database"

    monkeypatch.setattr(
        subprocess,
        "Popen",
        lambda *args, **kwargs: FailedProcess(),
    )

    with pytest.raises(AdapterError, match="command failed") as captured:
        CommandRunner(timeout_seconds=11).run(
            ["safe-command"],
            label="isolated unit stage",
        )

    assert captured.value.stage == "isolated unit stage"
    assert captured.value.returncode == 7
    assert captured.value.stdout == "partial stdout"
    assert "postgresql://secret@host/database" in captured.value.stderr
    assert "postgresql://" not in str(captured.value)


def test_temporary_alembic_url_uses_psycopg3(tmp_path):
    cluster = SimpleNamespace(
        workspace=SimpleNamespace(socket=tmp_path / "socket"),
        port=55439,
    )

    url = _temporary_database_url(cluster, "isolated_database")

    assert url.startswith("postgresql+psycopg://")
    assert "postgresql+psycopg2" not in url


def test_alembic_overrides_environment_url_and_redacts_failure(
    monkeypatch,
    tmp_path,
):
    inherited_url = "postgresql://inherited-secret@forbidden/real"
    monkeypatch.setenv("DATABASE_URL", inherited_url)
    observed = {}

    class FailingRunner:
        def run(self, command, **kwargs):
            observed.update(kwargs)
            temporary_url = kwargs["env"]["DATABASE_URL"]
            raise AdapterError(
                "command failed",
                stage="Alembic upgrade in isolated database",
                returncode=2,
                stdout="partial Alembic stdout",
                stderr="connection failed for " + temporary_url,
            )

    cluster = SimpleNamespace(
        workspace=SimpleNamespace(socket=tmp_path / "socket"),
        port=55439,
        runner=FailingRunner(),
        binaries=SimpleNamespace(alembic=Path("alembic")),
    )

    with pytest.raises(AdapterError, match="REDACTED_URL") as captured:
        run_alembic(
            cluster,
            "isolated_database",
            "upgrade",
            "revision-id",
            ROOT,
        )

    temporary_url = observed["env"]["DATABASE_URL"]
    assert temporary_url.startswith("postgresql+psycopg://")
    assert temporary_url != inherited_url
    assert inherited_url not in str(captured.value)
    assert temporary_url not in str(captured.value)
    assert captured.value.returncode == 2
    assert captured.value.stdout == "partial Alembic stdout"


def test_backup_must_be_regular_and_nonempty(tmp_path):
    workspace = create_workspace(tmp_path)

    class EmptyBackupRunner:
        def run(self, command, **kwargs):
            Path(command[command.index("--file") + 1]).write_bytes(b"")
            return SimpleNamespace(stdout="", stderr="")

    cluster = SimpleNamespace(
        runner=EmptyBackupRunner(),
        binaries=SimpleNamespace(pg_dump=Path("pg_dump")),
        connection_args=[],
    )
    try:
        with pytest.raises(AdapterError, match="empty"):
            create_backup(cluster, "source", workspace.backups / "source.dump")
    finally:
        cleanup_workspace(workspace)


def test_sha256_is_reproducible_for_backup(tmp_path):
    workspace = create_workspace(tmp_path)

    class BackupRunner:
        def run(self, command, **kwargs):
            Path(command[command.index("--file") + 1]).write_bytes(
                b"deterministic custom backup"
            )
            return SimpleNamespace(stdout="", stderr="")

    cluster = SimpleNamespace(
        runner=BackupRunner(),
        binaries=SimpleNamespace(pg_dump=Path("pg_dump")),
        connection_args=[],
    )
    try:
        first = create_backup(cluster, "source", workspace.backups / "source.dump")
        second = create_backup(cluster, "source", workspace.backups / "source.dump")
        assert first == second
    finally:
        cleanup_workspace(workspace)


def test_real_isolated_postgresql_backup_restore_and_alembic(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://must-not-be-used.invalid/forbidden",
    )
    port = 55000 + (os.getpid() % 9000)
    assert port != 5432

    result = run_isolated_rehearsal(config(port=port), binaries())

    assert result.source_database != result.destination_database
    assert result.verified_row_count == 3
    assert result.gate_accepted is True
    assert result.initial_revision == "f81a78f8c1c4"
    assert result.final_revision == "3c4f1a2b7d90"
    assert result.restored_revision == "f81a78f8c1c4"
    assert result.evidence["environment"] == "test"
    assert result.workspace_removed is True
