"""Run a PostgreSQL recovery rehearsal in a disposable local cluster.

Ejecuta un ensayo de recuperación PostgreSQL en un clúster local desechable.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Callable, Mapping, Sequence
from urllib.parse import quote

from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from alembic.script.revision import ResolutionError
from alembic.util.exc import CommandError

from scripts.engineering.devsecops_gate import (
    calculate_sha256,
    load_safety_plan,
    validate_safety_plan,
)


MARKER_NAME = ".loguic-devsecops-managed"
FORBIDDEN_PORT = 5432
DEFAULT_TIMEOUT = 30
POSTGRES_BINARIES = {
    "psql": Path("/usr/bin/psql"),
    "pg_dump": Path("/usr/bin/pg_dump"),
    "pg_restore": Path("/usr/bin/pg_restore"),
    "createdb": Path("/usr/bin/createdb"),
    "dropdb": Path("/usr/bin/dropdb"),
    "initdb": Path("/usr/lib/postgresql/16/bin/initdb"),
    "pg_ctl": Path("/usr/lib/postgresql/16/bin/pg_ctl"),
    "postgres": Path("/usr/lib/postgresql/16/bin/postgres"),
}


class AdapterError(RuntimeError):
    """Report a fail-closed adapter error without connection details.

    Informa un fallo cerrado sin detalles de conexión.
    """

    def __init__(
        self,
        message: str,
        *,
        stage: str = "",
        returncode: int | None = None,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.workspace_path: Path | None = None
        self.postgresql_stopped: bool | None = None
        self.workspace_removed: bool | None = None


def sanitize_diagnostic(value: str) -> str:
    """Redact connection URLs while retaining actionable diagnostics.

    Oculta URLs de conexión y conserva el diagnóstico accionable.
    """
    without_urls = re.sub(
        r"(?i)\b(?:postgres(?:ql)?(?:\+\w+)?)://[^\s]+",
        "[REDACTED_URL]",
        value,
    )
    return re.sub(
        r"(?i)\b(?:password|passwd)=\S+",
        "[REDACTED_SECRET]",
        without_urls,
    )


@dataclass(frozen=True)
class PostgreSQLBinaries:
    psql: Path
    pg_dump: Path
    pg_restore: Path
    createdb: Path
    dropdb: Path
    initdb: Path
    pg_ctl: Path
    postgres: Path
    alembic: Path


@dataclass(frozen=True)
class AdapterConfig:
    environment: str
    port: int
    repository_root: Path
    authorized_temp_parent: Path
    initial_revision: str = "f81a78f8c1c4"
    target_revision: str | None = None
    timeout_seconds: int = DEFAULT_TIMEOUT


@dataclass(frozen=True)
class ResolvedMigrationRange:
    """Freeze one verified migration boundary for the complete rehearsal.

    Fija una frontera de migración verificada para todo el ensayo.
    """

    initial_revision: str
    target_revision: str


@dataclass(frozen=True)
class ManagedWorkspace:
    root: Path
    data: Path
    socket: Path
    backups: Path
    evidence: Path
    authorized_parent: Path


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str


@dataclass(frozen=True)
class RehearsalResult:
    source_database: str
    destination_database: str
    backup_sha256: str
    verified_row_count: int
    initial_revision: str
    final_revision: str
    restored_revision: str
    evidence: dict[str, object]
    gate_accepted: bool
    workspace_removed: bool


def discover_binaries(
    *,
    overrides: Mapping[str, Path] | None = None,
    repository_root: Path,
) -> PostgreSQLBinaries:
    """Resolve and validate required executable paths.

    Resuelve y valida las rutas de ejecutables requeridas.
    """
    paths = dict(POSTGRES_BINARIES)
    if overrides:
        paths.update(overrides)
    paths["alembic"] = repository_root / ".venv" / "bin" / "alembic"
    for name, path in paths.items():
        if not path.is_file() or not os.access(path, os.X_OK):
            raise AdapterError(f"required binary is unavailable: {name}")
    return PostgreSQLBinaries(**paths)


def validate_config(config: AdapterConfig) -> None:
    """Reject unsafe targets before creating any resource.

    Rechaza objetivos inseguros antes de crear recursos.
    """
    if config.environment == "production":
        raise AdapterError("production is always rejected")
    if config.environment != "test":
        raise AdapterError("S2 only permits the isolated test environment")
    if config.port == FORBIDDEN_PORT:
        raise AdapterError("the system PostgreSQL port is forbidden")
    if not 49152 <= config.port < 65536:
        raise AdapterError("a high dynamic port is required")
    if config.timeout_seconds <= 0:
        raise AdapterError("command timeout must be positive")
    parent = config.authorized_temp_parent.resolve()
    if parent != Path(tempfile.gettempdir()).resolve():
        raise AdapterError("temporary parent is not authorized")


def resolve_migration_range(
    config: AdapterConfig,
    *,
    script_directory_factory: Callable[
        [AlembicConfig], ScriptDirectory
    ] = ScriptDirectory.from_config,
) -> ResolvedMigrationRange:
    """Resolve one linear Alembic head without opening a database.

    Resuelve un único head lineal de Alembic sin abrir una base de datos.
    """
    alembic_config = AlembicConfig(
        str(config.repository_root / "alembic.ini")
    )
    alembic_config.set_main_option(
        "script_location",
        str(config.repository_root / "alembic"),
    )
    try:
        scripts = script_directory_factory(alembic_config)
        heads = tuple(scripts.get_heads())
    except Exception as exc:
        raise AdapterError("Alembic revision graph could not be loaded") from exc
    if len(heads) != 1:
        raise AdapterError("Alembic revision graph must have exactly one head")

    target_revision = heads[0]
    try:
        initial_script = scripts.get_revision(config.initial_revision)
        target_script = scripts.get_revision(target_revision)
    except (CommandError, ResolutionError) as exc:
        raise AdapterError("configured Alembic revision does not exist") from exc
    if initial_script is None or target_script is None:
        raise AdapterError("configured Alembic revision does not exist")

    if config.target_revision is not None:
        try:
            explicit_target = scripts.get_revision(config.target_revision)
        except (CommandError, ResolutionError) as exc:
            raise AdapterError(
                "configured target Alembic revision does not exist"
            ) from exc
        if explicit_target is None:
            raise AdapterError(
                "configured target Alembic revision does not exist"
            )
        if (
            config.target_revision != target_revision
            or explicit_target.revision != target_revision
        ):
            raise AdapterError(
                "configured target Alembic revision is not the current head"
            )

    if initial_script.revision == target_revision:
        raise AdapterError(
            "initial Alembic revision must precede the current head"
        )

    current = target_script
    while current.revision != initial_script.revision:
        parent = current.down_revision
        if parent is None or not isinstance(parent, str):
            raise AdapterError(
                "Alembic head is not on one linear path from initial revision"
            )
        try:
            current = scripts.get_revision(parent)
        except (CommandError, ResolutionError) as exc:
            raise AdapterError("Alembic revision chain is incomplete") from exc
        if current is None:
            raise AdapterError("Alembic revision chain is incomplete")

    return ResolvedMigrationRange(
        initial_revision=initial_script.revision,
        target_revision=target_revision,
    )


def create_workspace(authorized_parent: Path) -> ManagedWorkspace:
    """Create one marked workspace below the authorized temp parent.

    Crea un workspace marcado bajo el directorio temporal autorizado.
    """
    parent = authorized_parent.resolve()
    root = Path(tempfile.mkdtemp(prefix="loguic-pg-s2-", dir=parent))
    (root / MARKER_NAME).write_text("managed-by-loguic-s2\n", encoding="utf-8")
    paths = {
        name: root / name
        for name in ("data", "socket", "backups", "evidence")
    }
    for path in paths.values():
        path.mkdir(mode=0o700)
    return ManagedWorkspace(root=root, authorized_parent=parent, **paths)


def validate_managed_workspace(workspace: ManagedWorkspace) -> None:
    """Require containment and marker before destructive cleanup.

    Exige contención y marcador antes de una limpieza destructiva.
    """
    root = workspace.root.resolve()
    parent = workspace.authorized_parent.resolve()
    if root.parent != parent or not root.name.startswith("loguic-pg-s2-"):
        raise AdapterError("cleanup target is outside the authorized directory")
    marker = root / MARKER_NAME
    if not marker.is_file() or marker.is_symlink():
        raise AdapterError("cleanup target lacks the required marker")


def cleanup_workspace(workspace: ManagedWorkspace) -> None:
    """Remove only a validated adapter-owned workspace.

    Elimina únicamente un workspace validado y propiedad del adaptador.
    """
    validate_managed_workspace(workspace)
    shutil.rmtree(workspace.root)


class CommandRunner:
    """Execute bounded commands in isolated process groups.

    Ejecuta comandos acotados en grupos de proceso aislados.
    """

    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT) -> None:
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        command: Sequence[str | Path],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        label: str,
    ) -> CommandResult:
        safe_command = [str(part) for part in command]
        process = subprocess.Popen(
            safe_command,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=self.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            raise AdapterError(
                f"command timed out: {label}",
                stage=label,
                returncode=-signal.SIGKILL,
                stdout=stdout,
                stderr=stderr,
            ) from exc
        if process.returncode != 0:
            raise AdapterError(
                f"command failed: {label}",
                stage=label,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr,
            )
        return CommandResult(stdout=stdout, stderr=stderr)


class PostgreSQLCluster:
    """Manage one PostgreSQL cluster confined to a marked workspace.

    Administra un clúster PostgreSQL confinado a un workspace marcado.
    """

    def __init__(
        self,
        workspace: ManagedWorkspace,
        binaries: PostgreSQLBinaries,
        runner: CommandRunner,
        port: int,
    ) -> None:
        self.workspace = workspace
        self.binaries = binaries
        self.runner = runner
        self.port = port
        self.initialized = False
        self.start_attempted = False
        self.started = False

    @property
    def connection_args(self) -> list[str]:
        return [
            "-h",
            str(self.workspace.socket),
            "-p",
            str(self.port),
            "-U",
            "postgres",
        ]

    def initialize(self) -> None:
        self.runner.run(
            [
                self.binaries.initdb,
                "-D",
                self.workspace.data,
                "--username=postgres",
                "--auth=trust",
                "--no-instructions",
            ],
            label="initialize isolated PostgreSQL cluster",
        )
        self.initialized = True

    def start(self) -> None:
        options = (
            f"-c listen_addresses='' -c unix_socket_directories="
            f"'{self.workspace.socket}' -p {self.port}"
        )
        log_path = self.workspace.root / "postgres.log"
        self.start_attempted = True
        try:
            self.runner.run(
                [
                    self.binaries.pg_ctl,
                    "-D",
                    self.workspace.data,
                    "-l",
                    log_path,
                    "-o",
                    options,
                    "-w",
                    "start",
                ],
                label="start isolated PostgreSQL cluster",
            )
        except AdapterError as exc:
            diagnostic = ""
            try:
                diagnostic = log_path.read_text(encoding="utf-8").strip()
            except OSError:
                pass
            if diagnostic:
                raise AdapterError(
                    "isolated PostgreSQL start failed: "
                    + sanitize_diagnostic(diagnostic),
                    stage=exc.stage,
                    returncode=exc.returncode,
                    stdout=exc.stdout,
                    stderr=diagnostic,
                ) from exc
            raise
        self.started = True

    def _force_stop(self) -> None:
        pid_path = self.workspace.data / "postmaster.pid"
        try:
            first_line = pid_path.read_text(encoding="utf-8").splitlines()[0]
            pid = int(first_line)
        except (OSError, ValueError, IndexError):
            return
        if pid <= 1:
            raise AdapterError("invalid isolated PostgreSQL pid")
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        deadline = time.monotonic() + self.runner.timeout_seconds
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.05)
        os.kill(pid, signal.SIGKILL)

    def stop(self) -> bool:
        if not self.initialized or not self.start_attempted:
            self.started = False
            return True
        stop_error: Exception | None = None
        try:
            self.runner.run(
                [
                    self.binaries.pg_ctl,
                    "-D",
                    self.workspace.data,
                    "-m",
                    "immediate",
                    "-w",
                    "stop",
                ],
                label="stop isolated PostgreSQL cluster",
            )
        except Exception as exc:
            stop_error = exc
            self._force_stop()
        finally:
            self.started = False
        pid_path = self.workspace.data / "postmaster.pid"
        if pid_path.exists():
            if stop_error is not None:
                raise AdapterError("isolated PostgreSQL did not stop") from stop_error
            raise AdapterError("isolated PostgreSQL pid file remains after stop")
        return True


def _database_command(cluster: PostgreSQLCluster, binary: Path, database: str):
    return [binary, *cluster.connection_args, database]


def create_database(
    cluster: PostgreSQLCluster,
    database: str,
) -> None:
    cluster.runner.run(
        [cluster.binaries.createdb, *cluster.connection_args, database],
        label="create isolated database",
    )


def execute_sql(
    cluster: PostgreSQLCluster,
    database: str,
    sql: str,
) -> str:
    result = cluster.runner.run(
        [
            *_database_command(cluster, cluster.binaries.psql, database),
            "-v",
            "ON_ERROR_STOP=1",
            "-At",
            "-c",
            sql,
        ],
        label="execute deterministic SQL",
    )
    return result.stdout.strip()


def create_control_data(cluster: PostgreSQLCluster, database: str) -> None:
    execute_sql(
        cluster,
        database,
        "CREATE SCHEMA recovery_control; "
        "CREATE TABLE recovery_control.items "
        "(id integer PRIMARY KEY, label text NOT NULL); "
        "INSERT INTO recovery_control.items VALUES "
        "(1, 'alpha'), (2, 'beta'), (3, 'gamma');",
    )


def create_backup(
    cluster: PostgreSQLCluster,
    source_database: str,
    backup_path: Path,
) -> str:
    cluster.runner.run(
        [
            cluster.binaries.pg_dump,
            *cluster.connection_args,
            "--format=custom",
            "--file",
            backup_path,
            source_database,
        ],
        label="create isolated PostgreSQL backup",
    )
    if backup_path.is_symlink() or not backup_path.is_file():
        raise AdapterError("backup is not a regular file")
    if backup_path.stat().st_size <= 0:
        raise AdapterError("backup is empty")
    first_digest = calculate_sha256(backup_path)
    if calculate_sha256(backup_path) != first_digest:
        raise AdapterError("backup SHA-256 is not reproducible")
    return first_digest


def restore_backup(
    cluster: PostgreSQLCluster,
    destination_database: str,
    backup_path: Path,
) -> None:
    cluster.runner.run(
        [
            cluster.binaries.pg_restore,
            *cluster.connection_args,
            "--exit-on-error",
            "--dbname",
            destination_database,
            backup_path,
        ],
        label="restore isolated PostgreSQL backup",
    )


def verify_restoration(
    cluster: PostgreSQLCluster,
    destination_database: str,
) -> int:
    schema = execute_sql(
        cluster,
        destination_database,
        "SELECT to_regclass('recovery_control.items') IS NOT NULL;",
    )
    rows = execute_sql(
        cluster,
        destination_database,
        "SELECT string_agg(id::text || ':' || label, ',' ORDER BY id) "
        "FROM recovery_control.items;",
    )
    if schema != "t" or rows != "1:alpha,2:beta,3:gamma":
        raise AdapterError("restored schema or data differs")
    return 3


def _temporary_database_url(
    cluster: PostgreSQLCluster,
    database: str,
) -> str:
    socket_path = quote(str(cluster.workspace.socket), safe="")
    return (
        f"postgresql+psycopg://postgres@/{database}"
        f"?host={socket_path}&port={cluster.port}"
    )


def run_alembic(
    cluster: PostgreSQLCluster,
    database: str,
    action: str,
    revision: str,
    repository_root: Path,
) -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = _temporary_database_url(cluster, database)
    try:
        cluster.runner.run(
            [cluster.binaries.alembic, action, revision],
            cwd=repository_root,
            env=environment,
            label=f"Alembic {action} in isolated database",
        )
    except AdapterError as exc:
        diagnostic = exc.stderr.strip()
        if diagnostic:
            raise AdapterError(
                f"isolated Alembic {action} failed: "
                + sanitize_diagnostic(diagnostic),
                stage=exc.stage,
                returncode=exc.returncode,
                stdout=exc.stdout,
                stderr=exc.stderr,
            ) from exc
        raise


def current_revision(cluster: PostgreSQLCluster, database: str) -> str:
    return execute_sql(
        cluster,
        database,
        "SELECT version_num FROM alembic_version;",
    )


def write_evidence_plan(
    *,
    migration_range: ResolvedMigrationRange,
    workspace: ManagedWorkspace,
    backup_path: Path,
    backup_sha256: str,
    restoration_path: Path,
    timestamps: tuple[datetime, datetime, datetime],
) -> Path:
    backup_at, restoration_at, rehearsal_at = timestamps
    plan = {
        "environment": "test",
        "target": {
            "identifier": "isolated-postgresql-rehearsal",
            "fingerprint": hashlib.sha256(
                str(workspace.root).encode("utf-8")
            ).hexdigest(),
            "current_revision": migration_range.initial_revision,
            "target_revision": migration_range.target_revision,
        },
        "backup": {
            "artifact_path": str(backup_path),
            "sha256": backup_sha256,
            "created_at": backup_at.isoformat(),
        },
        "restoration": {
            "evidence_path": str(restoration_path),
            "restored_at": restoration_at.isoformat(),
            "backup_sha256": backup_sha256,
            "result": "succeeded",
        },
        "migration_rehearsal": {
            "environment_id": "isolated-postgresql-cluster",
            "initial_revision": migration_range.initial_revision,
            "final_revision": migration_range.target_revision,
            "upgrade_succeeded": True,
            "downgrade_succeeded": True,
            "performed_at": rehearsal_at.isoformat(),
        },
        "rollback": {
            "return_revision": migration_range.initial_revision,
            "procedure": "Run the reviewed downgrade in the isolated cluster.",
        },
    }
    path = workspace.evidence / "safety-plan.json"
    path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return path


def run_isolated_rehearsal(
    config: AdapterConfig,
    binaries: PostgreSQLBinaries,
    *,
    runner_factory: Callable[[int], CommandRunner] = CommandRunner,
) -> RehearsalResult:
    """Execute the complete S2 rehearsal and always clean its workspace.

    Ejecuta el ensayo S2 completo y limpia siempre su workspace.
    """
    validate_config(config)
    migration_range = resolve_migration_range(config)
    workspace = create_workspace(config.authorized_temp_parent)
    runner = runner_factory(config.timeout_seconds)
    cluster = PostgreSQLCluster(workspace, binaries, runner, config.port)
    source_database = "s2_source"
    destination_database = "s2_restored"
    backup_digest = ""
    evidence: dict[str, object] = {}
    result: RehearsalResult | None = None
    primary_error: Exception | None = None
    cleanup_error: Exception | None = None
    try:
        cluster.initialize()
        cluster.start()
        create_database(cluster, source_database)
        run_alembic(
            cluster,
            source_database,
            "upgrade",
            migration_range.initial_revision,
            config.repository_root,
        )
        create_control_data(cluster, source_database)
        backup_path = workspace.backups / "source.dump"
        backup_at = datetime.now(UTC)
        backup_digest = create_backup(
            cluster,
            source_database,
            backup_path,
        )
        create_database(cluster, destination_database)
        restore_backup(cluster, destination_database, backup_path)
        row_count = verify_restoration(cluster, destination_database)
        restoration_at = datetime.now(UTC)
        restoration_path = workspace.evidence / "restoration.json"
        restoration_path.write_text(
            json.dumps({"result": "succeeded", "rows": row_count}) + "\n",
            encoding="utf-8",
        )
        initial = current_revision(cluster, destination_database)
        if initial != migration_range.initial_revision:
            raise AdapterError("restored initial revision differs")
        run_alembic(
            cluster,
            destination_database,
            "upgrade",
            migration_range.target_revision,
            config.repository_root,
        )
        final = current_revision(cluster, destination_database)
        if final != migration_range.target_revision:
            raise AdapterError("isolated upgrade revision differs")
        run_alembic(
            cluster,
            destination_database,
            "downgrade",
            migration_range.initial_revision,
            config.repository_root,
        )
        restored = current_revision(cluster, destination_database)
        if restored != migration_range.initial_revision:
            raise AdapterError("isolated downgrade revision differs")
        rehearsal_at = datetime.now(UTC)
        plan_path = write_evidence_plan(
            migration_range=migration_range,
            workspace=workspace,
            backup_path=backup_path,
            backup_sha256=backup_digest,
            restoration_path=restoration_path,
            timestamps=(backup_at, restoration_at, rehearsal_at),
        )
        plan = load_safety_plan(plan_path)
        validate_safety_plan(
            plan,
            now=datetime.now(UTC),
            max_restoration_age=timedelta(hours=1),
        )
        evidence = json.loads(plan_path.read_text(encoding="utf-8"))
        result = RehearsalResult(
            source_database=source_database,
            destination_database=destination_database,
            backup_sha256=backup_digest,
            verified_row_count=row_count,
            initial_revision=initial,
            final_revision=final,
            restored_revision=restored,
            evidence=evidence,
            gate_accepted=True,
            workspace_removed=True,
        )
    except Exception as exc:
        primary_error = exc
    finally:
        postgresql_stopped = False
        workspace_removed = False
        try:
            postgresql_stopped = cluster.stop()
        except Exception as exc:
            cleanup_error = exc
        if postgresql_stopped:
            try:
                cleanup_workspace(workspace)
                workspace_removed = not workspace.root.exists()
            except Exception as exc:
                cleanup_error = cleanup_error or exc
    if primary_error is not None:
        if isinstance(primary_error, AdapterError):
            error = primary_error
        else:
            error = AdapterError("isolated rehearsal failed")
        error.workspace_path = workspace.root
        error.postgresql_stopped = postgresql_stopped
        error.workspace_removed = workspace_removed
        if cleanup_error is not None:
            combined = AdapterError(
                "isolated rehearsal failed and cleanup was incomplete",
                stage=error.stage,
                returncode=error.returncode,
                stdout=error.stdout,
                stderr=error.stderr,
            )
            combined.workspace_path = workspace.root
            combined.postgresql_stopped = postgresql_stopped
            combined.workspace_removed = workspace_removed
            raise combined from primary_error
        raise error
    if cleanup_error is not None:
        error = AdapterError("isolated resource cleanup failed")
        error.workspace_path = workspace.root
        error.postgresql_stopped = postgresql_stopped
        error.workspace_removed = workspace_removed
        raise error from cleanup_error
    if result is None:
        raise AdapterError("isolated rehearsal did not complete")
    return result
