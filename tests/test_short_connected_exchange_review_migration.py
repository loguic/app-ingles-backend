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
BASE_REVISION = "a4c8e2f6b901"
B181_REVIEW_REVISION = "b181c3e4f5a6"
TABLE = "short_connected_exchange_production_reviews"


def test_b181_review_migration_is_reversible_in_isolated_postgresql(
    monkeypatch,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://must-not-be-used.invalid/forbidden",
    )
    authorized_parent = Path(tempfile.gettempdir())
    port = 57000 + (os.getpid() % 7000)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=B181_REVIEW_REVISION,
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
    database = "b181_review_migration_focus"
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

            run_alembic(
                cluster,
                database,
                "upgrade",
                B181_REVIEW_REVISION,
                ROOT,
            )
            assert current_revision(cluster, database) == B181_REVIEW_REVISION
            constraints = execute_sql(
                cluster,
                database,
                "SELECT conname || '|' || contype::text || '|' || "
                "pg_get_constraintdef(oid) FROM pg_constraint "
                f"WHERE conrelid = 'public.{TABLE}'::regclass "
                "ORDER BY conname;",
            )
            for name in (
                "ck_short_exchange_review_id_not_blank",
                "ck_short_exchange_review_dimension",
                "ck_short_exchange_review_result",
                "ck_short_exchange_review_source_type",
                "ck_short_exchange_review_source_id",
                "ck_short_exchange_review_source_version",
            ):
                assert any(
                    row.startswith(name + "|c|")
                    for row in constraints.splitlines()
                )
            assert "FOREIGN KEY (production_id) REFERENCES learner_productions(id) ON DELETE CASCADE" in constraints
            assert not any(
                "UNIQUE (production_id, dimension)" in row
                for row in constraints.splitlines()
            )
            indexes = execute_sql(
                cluster,
                database,
                "SELECT indexname FROM pg_indexes "
                f"WHERE tablename = '{TABLE}' ORDER BY indexname;",
            ).splitlines()
            assert "ix_short_connected_exchange_production_reviews_production_id" in indexes
            assert "ix_short_exchange_review_history" in indexes

            execute_sql(
                cluster,
                database,
                "INSERT INTO conversation_production_submissions "
                "(user_id, level_id, unit_id, lesson_id, conversation_id) "
                "VALUES ('migration-user', 'A1', 'a1-u1', 'a1-u1-l2', "
                "'a1-u1-l2-c1');",
            )
            execute_sql(
                cluster,
                database,
                "INSERT INTO learner_productions "
                "(submission_id, prompt_id, turn_id, modality, audio_reference) "
                "SELECT id, 'a1-u1-l2-p-place', 'a1-u1-l2-c1-t2', "
                "'voice', 'production-audio://migration' "
                "FROM conversation_production_submissions "
                "WHERE user_id = 'migration-user';",
            )
            execute_sql(
                cluster,
                database,
                f"INSERT INTO {TABLE} "
                "(review_id, production_id, dimension, result, source_type, "
                "source_id, source_version, reviewed_at) "
                "SELECT 'review-valid', id, 'intention_understanding', "
                "'pending', 'human', 'reviewer', NULL, now() "
                "FROM learner_productions WHERE prompt_id = "
                "'a1-u1-l2-p-place';",
            )
            assert execute_sql(
                cluster,
                database,
                f"SELECT count(*) FROM {TABLE};",
            ) == "1"
            with pytest.raises(AdapterError):
                execute_sql(
                    cluster,
                    database,
                    f"INSERT INTO {TABLE} VALUES "
                    "('invalid-fk', 999999, 'intention_understanding', "
                    "'pending', 'human', 'reviewer', NULL, now());",
                )
            with pytest.raises(AdapterError):
                execute_sql(
                    cluster,
                    database,
                    f"INSERT INTO {TABLE} "
                    "SELECT 'invalid-result', id, 'contingent_response', "
                    "'passed', 'human', 'reviewer', NULL, now() "
                    "FROM learner_productions LIMIT 1;",
                )

            run_alembic(cluster, database, "downgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NULL;",
            ) == "t"
            assert execute_sql(cluster, database, "SELECT 1;") == "1"
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
