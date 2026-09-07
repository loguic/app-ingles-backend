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
BASE_REVISION = "c1844e9f2a31"
REVIEW_REVISION = "d1842b7f3a91"
TABLE = "direct_english_construction_production_reviews"


def test_direct_english_review_migration_is_reversible_in_isolated_postgresql(
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
        target_revision=REVIEW_REVISION,
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
    database = "direct_english_review_migration_focus"
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
                REVIEW_REVISION,
                ROOT,
            )
            assert current_revision(cluster, database) == REVIEW_REVISION
            constraints = execute_sql(
                cluster,
                database,
                "SELECT conname || '|' || contype::text || '|' || "
                "pg_get_constraintdef(oid) FROM pg_constraint "
                f"WHERE conrelid = 'public.{TABLE}'::regclass "
                "ORDER BY conname;",
            )
            for name in (
                "ck_direct_english_review_id_not_blank",
                "ck_direct_english_review_dimension",
                "ck_direct_english_review_result",
                "ck_direct_english_review_source_type",
                "ck_direct_english_review_source_id",
                "ck_direct_english_review_source_version",
            ):
                assert any(
                    row.startswith(name + "|c|")
                    for row in constraints.splitlines()
                )
            assert (
                "FOREIGN KEY (attempt_production_id) REFERENCES "
                "direct_english_construction_attempt_productions(id) "
                "ON DELETE CASCADE"
            ) in constraints
            assert not any(
                "UNIQUE (attempt_production_id, dimension)" in row
                for row in constraints.splitlines()
            )
            indexes = execute_sql(
                cluster,
                database,
                "SELECT indexname FROM pg_indexes "
                f"WHERE tablename = '{TABLE}' ORDER BY indexname;",
            ).splitlines()
            assert "ix_direct_english_review_history" in indexes

            execute_sql(
                cluster,
                database,
                "INSERT INTO experience_attempts "
                "(attempt_id, user_id, level_id, unit_id, lesson_id, "
                "experience_contract_version, status, started_at, completed_at) "
                "VALUES ('migration-experience', 'migration-user', 'A1', "
                "'a1-u1', 'a1-u1-l1', '3.0', 'in_progress', now(), NULL);",
            )
            execute_sql(
                cluster,
                database,
                "INSERT INTO direct_english_construction_attempts "
                "(attempt_id, user_id, level_id, unit_id, lesson_id, "
                "experience_attempt_id, evidence_definition_id, transfer_bank_id, "
                "transfer_variant_id, transfer_prompt_snapshot, selector_version, "
                "status, started_at, finalized_at) VALUES "
                "('migration-direct', 'migration-user', 'A1', 'a1-u1', "
                "'a1-u1-l1', 'migration-experience', 'migration-evidence', "
                "'bank', 'variant', 'prompt', 'sha256-v1', 'finalized', "
                "now() - interval '1 minute', now());",
            )
            execute_sql(
                cluster,
                database,
                "INSERT INTO conversation_production_submissions "
                "(user_id, level_id, unit_id, lesson_id, conversation_id, "
                "experience_attempt_id) VALUES ('migration-user', 'A1', "
                "'a1-u1', 'a1-u1-l1', 'migration-conversation', "
                "'migration-experience');",
            )
            execute_sql(
                cluster,
                database,
                "INSERT INTO learner_productions "
                "(submission_id, prompt_id, turn_id, modality, audio_reference) "
                "SELECT id, 'migration-prompt', 'migration-turn', 'voice', "
                "'audio://migration' FROM conversation_production_submissions "
                "WHERE conversation_id = 'migration-conversation';",
            )
            execute_sql(
                cluster,
                database,
                "INSERT INTO direct_english_construction_attempt_productions "
                "(attempt_id, learner_production_id, production_function, "
                "evidence_id, configured_support_level, support_used) "
                "SELECT 'migration-direct', id, 'guided', 'migration-evidence', "
                "'anchors', 'anchors' FROM learner_productions "
                "WHERE prompt_id = 'migration-prompt';",
            )
            execute_sql(
                cluster,
                database,
                f"INSERT INTO {TABLE} "
                "(review_id, attempt_production_id, dimension, result, source_type, "
                "source_id, source_version, reviewed_at) "
                "SELECT 'review-valid', id, 'relevance', 'pending', "
                "'external', 'review-system', 'v1', now() "
                "FROM direct_english_construction_attempt_productions "
                "WHERE attempt_id = 'migration-direct';",
            )
            assert execute_sql(
                cluster,
                database,
                f"SELECT count(*) FROM {TABLE};",
            ) == "1"
            for statement in (
                f"INSERT INTO {TABLE} VALUES "
                "('invalid-fk', 999999, 'relevance', 'pending', "
                "'human', 'reviewer', NULL, now());",
                f"INSERT INTO {TABLE} "
                "SELECT 'invalid-dimension', id, 'semantic', 'pending', "
                "'human', 'reviewer', NULL, now() "
                "FROM direct_english_construction_attempt_productions LIMIT 1;",
                f"INSERT INTO {TABLE} "
                "SELECT 'invalid-result', id, 'relevance', 'passed', "
                "'human', 'reviewer', NULL, now() "
                "FROM direct_english_construction_attempt_productions LIMIT 1;",
                f"INSERT INTO {TABLE} "
                "SELECT 'invalid-source', id, 'relevance', 'pending', "
                "'automatic', 'reviewer', NULL, now() "
                "FROM direct_english_construction_attempt_productions LIMIT 1;",
                f"INSERT INTO {TABLE} "
                "SELECT 'invalid-external', id, 'relevance', 'pending', "
                "'external', 'reviewer', NULL, now() "
                "FROM direct_english_construction_attempt_productions LIMIT 1;",
            ):
                with pytest.raises(AdapterError):
                    execute_sql(cluster, database, statement)

            run_alembic(cluster, database, "downgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NULL;",
            ) == "t"
            assert execute_sql(
                cluster,
                database,
                "SELECT to_regclass('public.direct_english_construction_attempts') "
                "IS NOT NULL;",
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
