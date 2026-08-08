"""Run pytest against one disposable PostgreSQL database managed like S2."""

from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Sequence
from urllib.parse import parse_qs, urlparse


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from scripts.engineering.postgresql_devsecops_adapter import (
    AdapterConfig,
    AdapterError,
    CommandRunner,
    ManagedWorkspace,
    PostgreSQLCluster,
    _temporary_database_url,
    cleanup_workspace,
    create_database,
    create_workspace,
    discover_binaries,
    run_alembic,
    validate_config,
    validate_managed_workspace,
)


DATABASE_NAME = "isolated_pytest"
FORBIDDEN_DATABASE_NAME = "app_ingles_db"
FORBIDDEN_PORT = 5432
MIN_DYNAMIC_PORT = 49152
MAX_DYNAMIC_PORT = 65535


def choose_dynamic_port() -> int:
    """Choose a high PostgreSQL socket port without consulting external state."""
    return MIN_DYNAMIC_PORT + secrets.randbelow(
        MAX_DYNAMIC_PORT - MIN_DYNAMIC_PORT + 1
    )


def _validate_database_name(database: str) -> None:
    if database == FORBIDDEN_DATABASE_NAME:
        raise AdapterError("the development database is always rejected")
    if not database or any(
        character not in "abcdefghijklmnopqrstuvwxyz0123456789_"
        for character in database
    ):
        raise AdapterError("isolated pytest database name is invalid")


def _validate_workspace_target(
    workspace: ManagedWorkspace,
    *,
    port: int,
    database: str,
) -> None:
    validate_managed_workspace(workspace)
    root = workspace.root.resolve()
    socket = workspace.socket.resolve()
    if root.parent != Path(tempfile.gettempdir()).resolve():
        raise AdapterError("isolated pytest workspace is not temporary")
    if socket.parent != root or not workspace.socket.is_dir():
        raise AdapterError("PostgreSQL socket is outside the managed workspace")
    if workspace.socket.is_symlink():
        raise AdapterError("PostgreSQL socket directory cannot be a symlink")
    if port == FORBIDDEN_PORT:
        raise AdapterError("the system PostgreSQL port is forbidden")
    if not MIN_DYNAMIC_PORT <= port <= MAX_DYNAMIC_PORT:
        raise AdapterError("a high dynamic port is required")
    _validate_database_name(database)


def _validate_temporary_database_url(
    database_url: str,
    workspace: ManagedWorkspace,
    *,
    port: int,
    database: str,
) -> None:
    parsed = urlparse(database_url)
    query = parse_qs(parsed.query, strict_parsing=True)
    hosts = query.get("host", [])
    ports = query.get("port", [])
    if (
        parsed.scheme != "postgresql+psycopg"
        or parsed.username != "postgres"
        or parsed.hostname is not None
        or parsed.path != f"/{database}"
        or hosts != [str(workspace.socket.resolve())]
        or ports != [str(port)]
    ):
        raise AdapterError("DATABASE_URL is not the managed temporary database")
    if database == FORBIDDEN_DATABASE_NAME or "localhost" in database_url:
        raise AdapterError("DATABASE_URL targets a forbidden database")
    socket = Path(hosts[0]).resolve()
    if socket.parent != workspace.root.resolve():
        raise AdapterError("DATABASE_URL socket is outside the managed workspace")


def run_isolated_pytest(
    pytest_args: Sequence[str],
    *,
    port: int | None = None,
    database: str = DATABASE_NAME,
    repository_root: Path | None = None,
    workspace_factory=create_workspace,
    workspace_cleanup=cleanup_workspace,
    binaries_discoverer=discover_binaries,
    cluster_factory=PostgreSQLCluster,
    database_creator=create_database,
    alembic_runner=run_alembic,
    process_runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> int:
    """Run pytest in a fresh migrated database and always remove the cluster."""
    root = repository_root or REPOSITORY_ROOT
    selected_port = port if port is not None else choose_dynamic_port()
    _validate_database_name(database)
    config = AdapterConfig(
        environment="test",
        port=selected_port,
        repository_root=root,
        authorized_temp_parent=Path(tempfile.gettempdir()),
    )
    validate_config(config)
    binaries = binaries_discoverer(repository_root=root)
    workspace = workspace_factory(config.authorized_temp_parent)
    cluster = None
    try:
        _validate_workspace_target(
            workspace,
            port=selected_port,
            database=database,
        )
        cluster = cluster_factory(
            workspace,
            binaries,
            CommandRunner(config.timeout_seconds),
            selected_port,
        )
        cluster.initialize()
        cluster.start()
        database_creator(cluster, database)
        database_url = _temporary_database_url(cluster, database)
        _validate_temporary_database_url(
            database_url,
            workspace,
            port=selected_port,
            database=database,
        )
        alembic_runner(cluster, database, "upgrade", "head", root)
        environment = os.environ.copy()
        environment["DATABASE_URL"] = database_url
        completed = process_runner(
            [sys.executable, "-m", "pytest", *pytest_args],
            cwd=root,
            env=environment,
            check=False,
            shell=False,
        )
        return completed.returncode
    finally:
        try:
            if cluster is not None:
                cluster.stop()
        finally:
            workspace_cleanup(workspace)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run pytest against an isolated disposable PostgreSQL cluster."
    )
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pytest_args = list(args.pytest_args)
    if pytest_args and pytest_args[0] == "--":
        pytest_args.pop(0)
    try:
        return run_isolated_pytest(pytest_args)
    except KeyboardInterrupt:
        return 130
    except Exception as error:
        print(f"Isolated PostgreSQL pytest failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
