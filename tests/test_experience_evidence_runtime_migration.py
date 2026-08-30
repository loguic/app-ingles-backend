import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
import tempfile
from threading import Barrier

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.db.models import ExperienceAttempt, ExperienceEvidenceState
from app.schemas.content import Lesson
from app.schemas.conversation_attempt import ConversationAttemptCreate
from app.schemas.experience_attempt import ExperienceAttemptStart
from app.services.conversation_attempt_service import save_conversation_attempt
from app.services.experience_attempt_service import (
    save_experience_comprehension_response,
    start_or_resume_experience_attempt,
)
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
BASE_REVISION = "d1841ea7f0c1"
B184_2_REVISION = "22c69d857dc6"


def _runtime_lesson() -> Lesson:
    return Lesson.model_validate(
        {
            "id": "migration-runtime-lesson",
            "title": "Migration runtime lesson",
            "conversations": [
                {
                    "id": "migration-context",
                    "title": "Context",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "migration-context-turn",
                            "speaker": "partner",
                            "en": "Hello.",
                        }
                    ],
                },
                {
                    "id": "migration-final",
                    "title": "Final",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "migration-final-turn",
                            "speaker": "partner",
                            "en": "Goodbye.",
                        }
                    ],
                },
            ],
            "exercises": [
                {
                    "id": "migration-question",
                    "type": "mcq",
                    "prompt": "What was said?",
                    "options": ["Hello", "Thanks"],
                    "answer_index": 0,
                    "skill_ids": ["migration-skill"],
                }
            ],
            "experience": {
                "contract_version": "2.0",
                "mission": {
                    "id": "migration-mission",
                    "title": "Understand and respond",
                    "situation": "Listen and finish.",
                    "observable_outcome": "Complete both sources.",
                    "success_criteria": ["Complete both sources."],
                },
                "skill_ids": ["migration-skill"],
                "stages": [
                    {
                        "id": "migration-stage-context",
                        "type": "comprehension",
                        "instruction": "Understand.",
                        "activity_ids": ["migration-context"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "migration-stage-final",
                        "type": "applied_conversation",
                        "instruction": "Finish.",
                        "activity_ids": ["migration-final"],
                        "completion_condition": "evidence_recorded",
                    },
                ],
                "evidence_definitions": [
                    {
                        "id": "migration-comprehension",
                        "skill_ids": ["migration-skill"],
                        "stage_id": "migration-stage-context",
                        "activity_id": "migration-context",
                        "comprehension_exercise_id": "migration-question",
                        "evidence_type": "comprehension_result",
                        "measurement_mode": "binary",
                    },
                    {
                        "id": "migration-conversation",
                        "skill_ids": ["migration-skill"],
                        "stage_id": "migration-stage-final",
                        "activity_id": "migration-final",
                        "evidence_type": "conversation_completion",
                        "measurement_mode": "completion",
                    },
                ],
                "completion_policy": {
                    "practiced_stage_ids": [
                        "migration-stage-context",
                        "migration-stage-final",
                    ],
                    "required_evidence_ids": [
                        "migration-comprehension",
                        "migration-conversation",
                    ],
                },
            },
        }
    )


def _insert_attempt_sql(attempt_id: str, user_id: str) -> str:
    return (
        "INSERT INTO experience_attempts VALUES "
        f"('{attempt_id}', '{user_id}', 'A1', 'migration-unit', "
        "'migration-runtime-lesson', '2.0', 'in_progress', now(), NULL);"
    )


def test_b184_2_migration_and_concurrency_in_isolated_postgresql(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://must-not-be-used.invalid/forbidden",
    )
    authorized_parent = Path(tempfile.gettempdir())
    port = 59500 + (os.getpid() % 500)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=B184_2_REVISION,
    )
    validate_config(config)
    workspace = create_workspace(authorized_parent)
    cluster = PostgreSQLCluster(
        workspace,
        discover_binaries(repository_root=ROOT),
        CommandRunner(config.timeout_seconds),
        port,
    )
    database = "b184_2_evidence_runtime"
    engine = None

    try:
        try:
            cluster.initialize()
            cluster.start()
            create_database(cluster, database)
            run_alembic(cluster, database, "upgrade", BASE_REVISION, ROOT)
            execute_sql(
                cluster,
                database,
                "INSERT INTO conversation_attempts "
                "(user_id, level_id, unit_id, lesson_id, conversation_id, "
                "mode, visited_turn_ids, selected_choice_ids) VALUES "
                "('legacy-user', 'A1', 'legacy-unit', 'legacy-lesson', "
                "'legacy-conversation', 'guided', '[]', '[]');",
            )

            run_alembic(cluster, database, "upgrade", B184_2_REVISION, ROOT)
            assert current_revision(cluster, database) == B184_2_REVISION
            assert execute_sql(
                cluster,
                database,
                "SELECT to_regclass('public.experience_comprehension_responses') "
                "IS NOT NULL AND "
                "to_regclass('public.experience_evidence_states') IS NOT NULL;",
            ) == "t"
            assert execute_sql(
                cluster,
                database,
                "SELECT count(*) FROM information_schema.columns WHERE "
                "column_name = 'experience_attempt_id' AND is_nullable = 'YES' "
                "AND table_name IN ('conversation_attempts', "
                "'conversation_production_submissions', "
                "'direct_english_construction_attempts');",
            ) == "3"
            assert execute_sql(
                cluster,
                database,
                "SELECT experience_attempt_id IS NULL FROM "
                "conversation_attempts WHERE user_id = 'legacy-user';",
            ) == "t"

            constraints = execute_sql(
                cluster,
                database,
                "SELECT conname FROM pg_constraint WHERE conrelid = "
                "'experience_evidence_states'::regclass ORDER BY conname;",
            ).splitlines()
            assert {
                "ck_experience_evidence_state_status",
                "ck_experience_evidence_state_type",
                "ck_experience_evidence_source_type",
                "ck_experience_evidence_exactly_one_source",
                "ck_experience_evidence_source_reference",
                "ck_experience_evidence_source_compatibility",
                "fk_evidence_state_comprehension_source",
                "fk_evidence_state_submission_source",
                "fk_evidence_state_conversation_source",
                "fk_evidence_state_direct_english_source",
            }.issubset(constraints)

            execute_sql(cluster, database, _insert_attempt_sql("db-one", "db-user-one"))
            execute_sql(cluster, database, _insert_attempt_sql("db-two", "db-user-two"))
            for response_id, attempt_id in (("response-one", "db-one"), ("response-two", "db-two")):
                execute_sql(
                    cluster,
                    database,
                    "INSERT INTO experience_comprehension_responses VALUES "
                    f"('{response_id}', '{attempt_id}', 'evidence-one', "
                    "'activity-one', 'exercise-one', 0, true, now());",
                )
            execute_sql(
                cluster,
                database,
                "INSERT INTO experience_comprehension_responses VALUES "
                "('response-retry', 'db-one', 'evidence-one', "
                "'activity-one', 'exercise-one', 0, true, now());",
            )
            assert execute_sql(
                cluster,
                database,
                "SELECT count(*) FROM experience_comprehension_responses "
                "WHERE experience_attempt_id = 'db-one';",
            ) == "2"
            execute_sql(
                cluster,
                database,
                "INSERT INTO experience_evidence_states "
                "(experience_attempt_id, evidence_definition_id, evidence_type, "
                "status, source_type, comprehension_response_id, accredited_at) "
                "VALUES ('db-one', 'evidence-one', 'comprehension_result', "
                "'satisfied', 'comprehension_response', 'response-one', now());",
            )
            with pytest.raises(AdapterError):
                execute_sql(
                    cluster,
                    database,
                    "INSERT INTO experience_evidence_states "
                    "(experience_attempt_id, evidence_definition_id, evidence_type, "
                    "status, source_type, comprehension_response_id, accredited_at) "
                    "VALUES ('db-one', 'cross-attempt', 'comprehension_result', "
                    "'satisfied', 'comprehension_response', 'response-two', now());",
                )
            for invalid_values in (
                "('db-two', 'bad-status', 'comprehension_result', 'wrong', "
                "'comprehension_response', 'response-two', now())",
                "('db-two', 'bad-type', 'exercise_result', 'pending', "
                "'comprehension_response', 'response-two', now())",
                "('db-two', 'bad-matrix', 'guided_production', 'pending', "
                "'comprehension_response', 'response-two', now())",
            ):
                with pytest.raises(AdapterError):
                    execute_sql(
                        cluster,
                        database,
                        "INSERT INTO experience_evidence_states "
                        "(experience_attempt_id, evidence_definition_id, "
                        "evidence_type, status, source_type, "
                        "comprehension_response_id, accredited_at) VALUES "
                        + invalid_values
                        + ";",
                    )

            engine = create_engine(
                f"postgresql+psycopg://postgres@/{database}",
                connect_args={
                    "host": str(workspace.socket),
                    "port": port,
                },
            )
            SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
            lesson = _runtime_lesson()

            def lesson_context(lesson_id):
                if lesson_id == lesson.id:
                    return "A1", "migration-unit", lesson
                return None

            monkeypatch.setattr(
                "app.services.experience_evidence_service."
                "get_lesson_context_by_id",
                lesson_context,
            )
            monkeypatch.setattr(
                "app.services.experience_attempt_service."
                "get_lesson_context_by_id",
                lesson_context,
            )
            monkeypatch.setattr(
                "app.services.conversation_attempt_service."
                "get_conversation_context_by_id",
                lambda conversation_id: (
                    "A1",
                    "migration-unit",
                    lesson.id,
                    next(
                        item
                        for item in lesson.conversations
                        if item.id == conversation_id
                    ),
                )
                if conversation_id
                in {item.id for item in lesson.conversations}
                else None,
            )

            execute_sql(
                cluster,
                database,
                _insert_attempt_sql("concurrent-different", "concurrent-user"),
            )
            barrier = Barrier(2)

            def save_comprehension():
                with SessionLocal() as session:
                    barrier.wait()
                    return save_experience_comprehension_response(
                        "concurrent-different",
                        "migration-question",
                        0,
                        session,
                    )

            def save_conversation():
                with SessionLocal() as session:
                    barrier.wait()
                    return save_conversation_attempt(
                        ConversationAttemptCreate(
                            user_id="concurrent-user",
                            level_id="A1",
                            unit_id="migration-unit",
                            lesson_id=lesson.id,
                            conversation_id="migration-final",
                            mode="guided",
                            visited_turn_ids=["migration-final-turn"],
                            experience_attempt_id="concurrent-different",
                        ),
                        session,
                    )

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(save_comprehension), pool.submit(save_conversation)]
                for future in futures:
                    future.result(timeout=20)
            with SessionLocal() as session:
                completed = session.get(ExperienceAttempt, "concurrent-different")
                assert completed.status == "completed"
                assert completed.completed_at is not None
                assert (
                    session.query(ExperienceEvidenceState)
                    .filter_by(experience_attempt_id="concurrent-different")
                    .count()
                    == 2
                )

            execute_sql(
                cluster,
                database,
                _insert_attempt_sql("concurrent-equivalent", "equivalent-user"),
            )
            barrier = Barrier(2)

            def save_equivalent():
                with SessionLocal() as session:
                    barrier.wait()
                    return save_experience_comprehension_response(
                        "concurrent-equivalent",
                        "migration-question",
                        0,
                        session,
                    )

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(save_equivalent), pool.submit(save_equivalent)]
                for future in futures:
                    future.result(timeout=20)
            with SessionLocal() as session:
                assert (
                    session.query(ExperienceEvidenceState)
                    .filter_by(experience_attempt_id="concurrent-equivalent")
                    .count()
                    == 1
                )

            execute_sql(
                cluster,
                database,
                _insert_attempt_sql("completion-race", "race-user"),
            )
            lock_session = SessionLocal()
            locked = (
                lock_session.query(ExperienceAttempt)
                .filter_by(attempt_id="completion-race")
                .with_for_update()
                .one()
            )
            locked.status = "completed"
            locked.completed_at = datetime.now(UTC)

            def start_after_completion():
                with SessionLocal() as session:
                    return start_or_resume_experience_attempt(
                        ExperienceAttemptStart(
                            user_id="race-user",
                            level_id="A1",
                            unit_id="migration-unit",
                            lesson_id=lesson.id,
                        ),
                        session,
                    )

            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(start_after_completion)
                lock_session.commit()
                replacement = future.result(timeout=20)
            lock_session.close()
            assert replacement.attempt_id != "completion-race"
            assert replacement.status == "in_progress"

            if engine is not None:
                engine.dispose()
                engine = None
            run_alembic(cluster, database, "downgrade", BASE_REVISION, ROOT)
            assert current_revision(cluster, database) == BASE_REVISION
            assert execute_sql(
                cluster,
                database,
                "SELECT to_regclass('public.experience_attempts') IS NOT NULL "
                "AND to_regclass('public.experience_evidence_states') IS NULL "
                "AND to_regclass('public.experience_comprehension_responses') "
                "IS NULL;",
            ) == "t"
            assert execute_sql(
                cluster,
                database,
                "SELECT count(*) FROM information_schema.columns WHERE "
                "column_name = 'experience_attempt_id' AND table_name IN "
                "('conversation_attempts', "
                "'conversation_production_submissions', "
                "'direct_english_construction_attempts');",
            ) == "0"
        except AdapterError as error:
            pytest.fail(
                "isolated PostgreSQL diagnostic failed: "
                f"stage={error.stage!r}; returncode={error.returncode!r}; "
                f"stdout={sanitize_diagnostic(error.stdout)!r}; "
                f"stderr={sanitize_diagnostic(error.stderr)!r}",
                pytrace=False,
            )
    finally:
        if engine is not None:
            engine.dispose()
        try:
            cluster.stop()
        finally:
            cleanup_workspace(workspace)

    assert not workspace.root.exists()


def test_b184_2_migration_is_reversible_in_sqlite(tmp_path, monkeypatch):
    database_path = tmp_path / "b184-2.sqlite"
    database_url = f"sqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setattr("app.db.database.DATABASE_URL", database_url)
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "alembic"))

    command.upgrade(config, B184_2_REVISION)
    engine = create_engine(f"sqlite:///{database_path}")
    inspector = inspect(engine)
    assert {
        "experience_comprehension_responses",
        "experience_evidence_states",
    }.issubset(inspector.get_table_names())
    for table_name in (
        "conversation_attempts",
        "conversation_production_submissions",
        "direct_english_construction_attempts",
    ):
        columns = {item["name"]: item for item in inspector.get_columns(table_name)}
        assert columns["experience_attempt_id"]["nullable"] is True

    command.downgrade(config, BASE_REVISION)
    inspector = inspect(engine)
    assert "experience_attempts" in inspector.get_table_names()
    assert "experience_evidence_states" not in inspector.get_table_names()
    engine.dispose()
