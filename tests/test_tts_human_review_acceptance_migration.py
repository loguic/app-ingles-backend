"""Verify the TTS acceptance storage in isolated PostgreSQL and SQLite."""

import os
from pathlib import Path
import sqlite3
import subprocess
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
BASE_REVISION = "d1842b7f3a91"
ACCEPTANCE_REVISION = "e6c42a9b1d70"
TABLE = "tts_human_review_acceptances"
SLOT_VERSION = "loguic-tts-public-review-slot/1.0"
HANDOFF = '{"review":{"perceived_transcription":"café"}}'.encode("utf-8")


def _insert_sql(
    *,
    slot: str = "review-slot-1",
    handoff: str = "review-handoff-1",
    version: str = SLOT_VERSION,
    payload: bytes = HANDOFF,
) -> str:
    return (
        f"INSERT INTO {TABLE} "
        "(review_slot_id, review_slot_version, package_id, handoff_id, "
        "lock_transition_id, review_id, canonical_handoff) VALUES "
        f"('{slot}', '{version}', 'review-package-1', '{handoff}', "
        f"'review-lock-1', 'review-1', decode('{payload.hex()}', 'hex'));"
    )


def test_tts_acceptance_migration_and_append_only_in_isolated_postgresql(
    monkeypatch,
):
    monkeypatch.setenv("DATABASE_URL", "postgresql://must-not-be-used.invalid/forbidden")
    authorized_parent = Path(tempfile.gettempdir())
    port = 57000 + (os.getpid() % 7000)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=ACCEPTANCE_REVISION,
    )
    validate_config(config)
    workspace = create_workspace(authorized_parent)
    cluster = PostgreSQLCluster(
        workspace,
        discover_binaries(repository_root=ROOT),
        CommandRunner(config.timeout_seconds),
        port,
    )
    database = "tts_human_review_acceptance_focus"

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

            run_alembic(cluster, database, "upgrade", ACCEPTANCE_REVISION, ROOT)
            assert current_revision(cluster, database) == ACCEPTANCE_REVISION
            assert execute_sql(
                cluster,
                database,
                f"SELECT to_regclass('public.{TABLE}') IS NOT NULL;",
            ) == "t"

            columns = execute_sql(
                cluster,
                database,
                "SELECT column_name || '|' || data_type || '|' || is_nullable "
                "FROM information_schema.columns "
                f"WHERE table_name = '{TABLE}' ORDER BY ordinal_position;",
            ).splitlines()
            assert columns == [
                "review_slot_id|character varying|NO",
                "review_slot_version|character varying|NO",
                "package_id|character varying|NO",
                "handoff_id|character varying|NO",
                "lock_transition_id|character varying|NO",
                "review_id|character varying|NO",
                "canonical_handoff|bytea|NO",
                "accepted_at|timestamp with time zone|NO",
            ]
            constraints = execute_sql(
                cluster,
                database,
                "SELECT conname || '|' || contype::text FROM pg_constraint "
                f"WHERE conrelid = 'public.{TABLE}'::regclass ORDER BY conname;",
            ).splitlines()
            assert set(constraints) == {
                "tts_human_review_acceptances_pkey|p",
                "uq_tts_human_review_acceptances_handoff_id|u",
                "ck_tts_human_review_acceptances_slot_version|c",
                "ck_tts_human_review_acceptances_handoff_not_empty|c",
            }
            indexes = execute_sql(
                cluster,
                database,
                "SELECT indexname FROM pg_indexes "
                f"WHERE tablename = '{TABLE}' ORDER BY indexname;",
            ).splitlines()
            assert indexes == [
                "tts_human_review_acceptances_pkey",
                "uq_tts_human_review_acceptances_handoff_id",
            ]
            triggers = execute_sql(
                cluster,
                database,
                "SELECT tgname FROM pg_trigger "
                f"WHERE tgrelid = 'public.{TABLE}'::regclass "
                "AND NOT tgisinternal ORDER BY tgname;",
            ).splitlines()
            assert triggers == [
                "trg_tts_human_review_acceptance_no_row_mutation",
                "trg_tts_human_review_acceptance_no_truncate",
            ]

            execute_sql(cluster, database, _insert_sql())
            original = execute_sql(
                cluster,
                database,
                f"SELECT review_slot_id, handoff_id, review_id, "
                f"encode(canonical_handoff, 'hex'), accepted_at::text "
                f"FROM {TABLE};",
            )
            assert original.startswith(
                f"review-slot-1|review-handoff-1|review-1|{HANDOFF.hex()}|"
            )
            assert original.rsplit("|", 1)[1]

            rejected = (
                (
                    _insert_sql(slot="review-slot-1", handoff="review-handoff-2"),
                    "tts_human_review_acceptances_pkey",
                ),
                (
                    _insert_sql(slot="review-slot-2", handoff="review-handoff-1"),
                    "uq_tts_human_review_acceptances_handoff_id",
                ),
                (
                    _insert_sql(
                        slot="review-slot-2",
                        handoff="review-handoff-2",
                        version="wrong-version",
                    ),
                    "ck_tts_human_review_acceptances_slot_version",
                ),
                (
                    _insert_sql(
                        slot="review-slot-2",
                        handoff="review-handoff-2",
                        payload=b"",
                    ),
                    "ck_tts_human_review_acceptances_handoff_not_empty",
                ),
                (
                    f"UPDATE {TABLE} SET review_id = 'changed' "
                    "WHERE review_slot_id = 'review-slot-1';",
                    "TTS human review acceptances are append-only",
                ),
                (
                    f"DELETE FROM {TABLE} WHERE review_slot_id = 'review-slot-1';",
                    "TTS human review acceptances are append-only",
                ),
                (
                    f"TRUNCATE {TABLE};",
                    "TTS human review acceptances are append-only",
                ),
            )
            for sql, expected_error in rejected:
                with pytest.raises(AdapterError) as error:
                    execute_sql(cluster, database, sql)
                assert expected_error in error.value.stderr
                assert execute_sql(
                    cluster,
                    database,
                    f"SELECT review_slot_id, handoff_id, review_id, "
                    f"encode(canonical_handoff, 'hex'), accepted_at::text "
                    f"FROM {TABLE};",
                ) == original

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
                "SELECT to_regprocedure("
                "'reject_tts_human_review_acceptance_mutation()') IS NULL;",
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


def test_tts_acceptance_migration_preserves_sqlite_upgrade_head(tmp_path):
    database_path = tmp_path / "tts-acceptances.sqlite"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"

    upgrade = subprocess.run(
        [".venv/bin/alembic", "upgrade", "head"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert upgrade.returncode == 0, upgrade.stderr
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (TABLE,),
        ).fetchone() == (TABLE,)

    downgrade = subprocess.run(
        [".venv/bin/alembic", "downgrade", BASE_REVISION],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert downgrade.returncode == 0, downgrade.stderr
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (TABLE,),
        ).fetchone() is None
