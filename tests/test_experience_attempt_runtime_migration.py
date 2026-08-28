import os
from pathlib import Path
import tempfile

import pytest

from scripts.engineering.postgresql_devsecops_adapter import (
    AdapterConfig,
    AdapterError,
    CommandRunner,
    PostgreSQLCluster,
    cleanup_workspace,
    create_database,
    create_workspace,
    current_revision,
    discover_binaries,
    execute_sql,
    run_alembic,
    sanitize_diagnostic,
    validate_config,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "b181c3e4f5a6"
B184_1_REVISION = "d1841ea7f0c1"
TABLE = "experience_attempts"


def test_b184_1_migration_is_reversible_in_isolated_postgresql(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://must-not-be-used.invalid/forbidden",
    )
    authorized_parent = Path(tempfile.gettempdir())
    port = 58000 + (os.getpid() % 1500)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=B184_1_REVISION,
    )
    validate_config(config)
    binaries = discover_binaries(repository_root=ROOT)
    workspace = create_workspace(authorized_parent)
    cluster = PostgreSQLCluster(
        workspace,
        binaries,
        CommandRunner(config.timeout_seconds),
        port,
    )
    database = "b184_1_experience_attempt_migration"

    try:
        try:
            cluster.initialize()
            cluster.start()
            create_database(cluster, database)
            run_alembic(cluster, database, "upgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NULL;",
            ) == "t"

            run_alembic(cluster, database, "upgrade", B184_1_REVISION, ROOT)
            assert current_revision(cluster, database) == B184_1_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NOT NULL;",
            ) == "t"

            columns = execute_sql(
                cluster,
                database,
                "SELECT column_name || '|' || is_nullable "
                "FROM information_schema.columns "
                f"WHERE table_name = '{TABLE}' ORDER BY ordinal_position;",
            ).splitlines()
            assert columns == [
                "attempt_id|NO",
                "user_id|NO",
                "level_id|NO",
                "unit_id|NO",
                "lesson_id|NO",
                "experience_contract_version|NO",
                "status|NO",
                "started_at|NO",
                "completed_at|YES",
            ]

            constraints = execute_sql(
                cluster,
                database,
                "SELECT conname || '|' || contype::text || '|' || "
                "pg_get_constraintdef(oid) FROM pg_constraint "
                f"WHERE conrelid = 'public.{TABLE}'::regclass "
                "ORDER BY conname;",
            ).splitlines()
            assert any(
                row.startswith("ck_experience_attempt_status|c|")
                and "in_progress" in row
                and "completed" in row
                for row in constraints
            )
            assert any(
                row.startswith("ck_experience_attempt_completion|c|")
                for row in constraints
            )
            assert any(
                row.startswith("ck_experience_attempt_timeline|c|")
                for row in constraints
            )

            index_definition = execute_sql(
                cluster,
                database,
                "SELECT indexdef FROM pg_indexes "
                f"WHERE tablename = '{TABLE}' "
                "AND indexname = 'uq_experience_attempt_active_context';",
            )
            assert "UNIQUE INDEX uq_experience_attempt_active_context" in index_definition
            assert "WHERE" in index_definition
            assert "status" in index_definition
            assert "in_progress" in index_definition

            valid = (
                "('active-one', 'migration-user', 'A1', 'a1-u1', "
                "'a1-u1-l1', '2.0', 'in_progress', now(), NULL)"
            )
            execute_sql(
                cluster,
                database,
                f"INSERT INTO {TABLE} VALUES {valid};",
            )
            with pytest.raises(AdapterError):
                execute_sql(
                    cluster,
                    database,
                    f"INSERT INTO {TABLE} VALUES "
                    "('active-two', 'migration-user', 'A1', 'a1-u1', "
                    "'a1-u1-l1', '2.0', 'in_progress', now(), NULL);",
                )
            execute_sql(
                cluster,
                database,
                f"INSERT INTO {TABLE} VALUES "
                "('completed-history', 'migration-user', 'A1', 'a1-u1', "
                "'a1-u1-l1', '2.0', 'completed', now(), now());",
            )
            assert execute_sql(
                cluster,
                database,
                f"SELECT count(*) FROM {TABLE};",
            ) == "2"

            run_alembic(cluster, database, "downgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NULL;",
            ) == "t"
        except AdapterError as error:
            pytest.fail(
                "isolated PostgreSQL diagnostic failed: "
                f"stage={error.stage!r}; returncode={error.returncode!r}; "
                f"stdout={sanitize_diagnostic(error.stdout)!r}; "
                f"stderr={sanitize_diagnostic(error.stderr)!r}",
                pytrace=False,
            )
    finally:
        try:
            cluster.stop()
        finally:
            cleanup_workspace(workspace)

    assert not workspace.root.exists()
