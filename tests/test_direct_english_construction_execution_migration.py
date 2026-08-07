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
BASE_REVISION = "3c4f1a2b7d90"
B180_REVISION = "7d8e9f0a1b2c"
ATTEMPTS_TABLE = "direct_english_construction_attempts"
PRODUCTIONS_TABLE = "direct_english_construction_attempt_productions"


def _table_exists(
    cluster: PostgreSQLCluster,
    database: str,
    table_name: str,
) -> bool:
    result = execute_sql(
        cluster,
        database,
        "SELECT to_regclass('public."
        + table_name
        + "') IS NOT NULL;",
    )
    return result == "t"


def _constraint_rows(
    cluster: PostgreSQLCluster,
    database: str,
    table_name: str,
) -> set[str]:
    output = execute_sql(
        cluster,
        database,
        "SELECT conname || '|' || contype::text || '|' || "
        "pg_get_constraintdef(oid) "
        "FROM pg_constraint "
        "WHERE conrelid = 'public."
        + table_name
        + "'::regclass "
        "ORDER BY conname;",
    )
    return set(output.splitlines()) if output else set()


def test_b180_migration_upgrade_and_downgrade_in_isolated_postgresql(
    monkeypatch,
):
    """Validate the B180 migration against adapter-owned PostgreSQL.

    Valida la migración B180 contra PostgreSQL administrado por el adaptador.
    """
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://must-not-be-used.invalid/forbidden",
    )
    authorized_parent = Path(tempfile.gettempdir())
    port = 56000 + (os.getpid() % 8000)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=B180_REVISION,
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
    database = "b180_migration_focus"

    try:
        try:
            cluster.initialize()
            cluster.start()
            create_database(cluster, database)

            run_alembic(cluster, database, "upgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert not _table_exists(cluster, database, ATTEMPTS_TABLE)
            assert not _table_exists(cluster, database, PRODUCTIONS_TABLE)

            run_alembic(cluster, database, "upgrade", B180_REVISION, ROOT)
            assert current_revision(cluster, database) == B180_REVISION
            assert _table_exists(cluster, database, ATTEMPTS_TABLE)
            assert _table_exists(cluster, database, PRODUCTIONS_TABLE)

            attempt_constraints = _constraint_rows(
                cluster,
                database,
                ATTEMPTS_TABLE,
            )
            production_constraints = _constraint_rows(
                cluster,
                database,
                PRODUCTIONS_TABLE,
            )
            assert any(
                row.startswith("ck_direct_english_attempt_status|c|")
                and "status" in row
                and "started" in row
                and "finalized" in row
                for row in attempt_constraints
            )
            assert any(
                row.startswith("ck_direct_english_attempt_finalization|c|")
                and "finalized_at" in row
                for row in attempt_constraints
            )
            assert any(
                row.startswith("ck_direct_english_attempt_timeline|c|")
                and "finalized_at >= started_at" in row
                for row in attempt_constraints
            )
            assert any(
                row.startswith(
                    "ck_direct_english_attempt_production_function|c|"
                )
                and all(
                    value in row
                    for value in ("guided", "expanded", "transfer")
                )
                for row in production_constraints
            )
            for constraint_name in (
                "ck_direct_english_attempt_configured_support",
                "ck_direct_english_attempt_support_used",
            ):
                assert any(
                    row.startswith(constraint_name + "|c|")
                    and all(
                        value in row
                        for value in (
                            "model",
                            "anchors",
                            "initial_word",
                            "none",
                        )
                    )
                    for row in production_constraints
                )
            assert any(
                "|f|" in row
                and "FOREIGN KEY (attempt_id)" in row
                and "REFERENCES direct_english_construction_attempts(attempt_id)"
                in row
                for row in production_constraints
            )
            assert any(
                "|f|" in row
                and "FOREIGN KEY (learner_production_id)" in row
                and "REFERENCES learner_productions(id)" in row
                for row in production_constraints
            )
            assert any(
                row.startswith("uq_direct_english_attempt_function|u|")
                and "UNIQUE (attempt_id, production_function)" in row
                for row in production_constraints
            )
            assert any(
                row.startswith(
                    "uq_direct_english_attempt_learner_production|u|"
                )
                and "UNIQUE (learner_production_id)" in row
                for row in production_constraints
            )

            run_alembic(cluster, database, "downgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert not _table_exists(cluster, database, PRODUCTIONS_TABLE)
            assert not _table_exists(cluster, database, ATTEMPTS_TABLE)
            assert _table_exists(cluster, database, "learner_productions")
            assert execute_sql(cluster, database, "SELECT 1;") == "1"
        except AdapterError as exc:
            pytest.fail(
                "isolated PostgreSQL diagnostic failed: "
                f"stage={exc.stage!r}; returncode={exc.returncode!r}; "
                f"stdout={sanitize_diagnostic(exc.stdout)!r}; "
                f"stderr={sanitize_diagnostic(exc.stderr)!r}",
                pytrace=False,
            )
    finally:
        try:
            cluster.stop()
        finally:
            cleanup_workspace(workspace)

    assert not workspace.root.exists()
