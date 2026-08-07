from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Query, sessionmaker

import app.services.direct_english_construction_execution_service as execution_service
from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission,
    DirectEnglishConstructionAttempt,
    DirectEnglishConstructionAttemptProduction,
    LearnerProduction,
)
from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptFinalize,
    DirectEnglishConstructionAttemptRecord,
    DirectEnglishConstructionAttemptStart,
)
from app.services.content_service import get_lesson_by_id
from app.services.direct_english_construction_execution_service import (
    SELECTOR_VERSION,
    DirectEnglishConstructionAttemptAlreadyExistsError,
    DirectEnglishConstructionExecutionError,
    DirectEnglishConstructionInvariantError,
    DirectEnglishConstructionReferenceNotFoundError,
    DirectEnglishConstructionStateConflictError,
    finalize_direct_english_construction_attempt,
    get_direct_english_construction_attempt,
    select_direct_english_transfer_variant,
    start_direct_english_construction_attempt,
)


NOW = datetime(2026, 8, 7, 10, 0, tzinfo=UTC)
FUNCTIONS = ("guided", "expanded", "transfer")


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def start_command(attempt_id="attempt-1", **updates):
    data = {
        "attempt_id": attempt_id,
        "user_id": "b180-user",
        "level_id": "A1",
        "unit_id": "a1-u1",
        "lesson_id": "a1-u1-l1",
        "started_at": NOW,
    }
    data.update(updates)
    return DirectEnglishConstructionAttemptStart.model_validate(data)


def capture_payload(
    function,
    *,
    modality="voice",
    support_used=None,
    user_id="b180-user",
    lesson_id="a1-u1-l1",
    conversation_id=None,
    prompt_id=None,
    turn_id=None,
    variant_id=None,
):
    configured = {
        "guided": "anchors",
        "expanded": "initial_word",
        "transfer": "none",
    }
    conversation_id = conversation_id or f"a1-u1-l1-c-direct-{function}"
    prompt_id = prompt_id or f"a1-u1-l1-p-{function}"
    turn_id = turn_id or f"{conversation_id}-t2"
    production = {
        "prompt_id": prompt_id,
        "turn_id": turn_id,
        "modality": modality,
    }
    if modality == "voice":
        production["audio_reference"] = f"audio/{function}.wav"
    else:
        production["response_text"] = f"text {function}"
    data = {
        "production_function": function,
        "submission": {
            "user_id": user_id,
            "level_id": "A1",
            "unit_id": "a1-u1",
            "lesson_id": lesson_id,
            "conversation_id": conversation_id,
            "productions": [production],
        },
        "support_used": support_used or configured[function],
    }
    if function == "transfer":
        data["transfer_variant_id"] = variant_id
    return data


def finalize_command(record, *, captures=None, finalized_at=None):
    if captures is None:
        captures = [
            capture_payload(
                function,
                variant_id=(
                    record.transfer_variant_id
                    if function == "transfer"
                    else None
                ),
            )
            for function in FUNCTIONS
        ]
    return DirectEnglishConstructionAttemptFinalize.model_validate(
        {
            "attempt_id": record.attempt_id,
            "captures": captures,
            "finalized_at": finalized_at or NOW + timedelta(minutes=5),
        }
    )


def counts(db):
    return (
        db.query(ConversationProductionSubmission).count(),
        db.query(LearnerProduction).count(),
        db.query(DirectEnglishConstructionAttemptProduction).count(),
    )


def test_selector_is_reproducible_auditable_and_uses_no_random():
    lesson = get_lesson_by_id("a1-u1-l1")
    assert lesson is not None

    first = select_direct_english_transfer_variant(lesson, "stable-attempt")
    second = select_direct_english_transfer_variant(lesson, "stable-attempt")
    bank_id, variant = first
    transfer_prompt = next(
        turn.production_prompt
        for conversation in lesson.conversations
        for turn in conversation.turns
        if turn.production_prompt is not None
        and turn.production_prompt.production_function == "transfer"
    )

    assert first == second
    assert bank_id == transfer_prompt.transfer_bank_id
    assert variant in transfer_prompt.transfer_variants
    assert SELECTOR_VERSION == "sha256-v1"
    assert "random" not in execution_service.__dict__


def test_start_persists_exact_snapshot_and_one_commit(db, monkeypatch):
    commits = 0
    original_commit = db.commit

    def count_commit():
        nonlocal commits
        commits += 1
        original_commit()

    monkeypatch.setattr(db, "commit", count_commit)
    record = start_direct_english_construction_attempt(start_command(), db)

    assert commits == 1
    assert record.status == "started"
    assert record.productions == []
    assert record.completion_requirements_met is False
    assert record.selector_version == SELECTOR_VERSION
    lesson = get_lesson_by_id("a1-u1-l1")
    assert lesson is not None
    _bank_id, expected = select_direct_english_transfer_variant(
        lesson, record.attempt_id
    )
    assert record.transfer_variant_id == expected.id
    assert record.transfer_prompt_snapshot == expected.prompt


def test_start_rejects_invalid_direct_content(db, monkeypatch):
    def reject_content(_lesson):
        raise ValueError("forced invalid B180 content")

    monkeypatch.setattr(
        execution_service,
        "validate_direct_english_construction_lesson",
        reject_content,
    )
    with pytest.raises(DirectEnglishConstructionInvariantError) as exc_info:
        start_direct_english_construction_attempt(start_command(), db)

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert db.query(DirectEnglishConstructionAttempt).count() == 0


def test_start_rejects_duplicate_and_incompatible_hierarchy(db):
    first = start_direct_english_construction_attempt(start_command(), db)
    with pytest.raises(DirectEnglishConstructionAttemptAlreadyExistsError):
        start_direct_english_construction_attempt(start_command(), db)
    assert (
        get_direct_english_construction_attempt(first.attempt_id, db)
        .transfer_variant_id
        == first.transfer_variant_id
    )

    with pytest.raises(DirectEnglishConstructionInvariantError):
        start_direct_english_construction_attempt(
            start_command("attempt-2", lesson_id="a1-u1-l2"), db
        )


def test_start_rolls_back_database_failure(db, monkeypatch):
    def fail_commit():
        raise SQLAlchemyError("forced start failure")

    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(DirectEnglishConstructionExecutionError) as exc_info:
        start_direct_english_construction_attempt(start_command(), db)

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert db.query(DirectEnglishConstructionAttempt).count() == 0


def test_finalize_round_trip_orders_functions_and_commits_once(db, monkeypatch):
    started = start_direct_english_construction_attempt(start_command(), db)
    command = finalize_command(
        started,
        captures=[
            capture_payload("transfer", variant_id=started.transfer_variant_id),
            capture_payload("guided"),
            capture_payload("expanded"),
        ],
    )
    commits = 0
    original_commit = db.commit

    def count_commit():
        nonlocal commits
        commits += 1
        original_commit()

    monkeypatch.setattr(db, "commit", count_commit)
    record = finalize_direct_english_construction_attempt(command, db)

    assert commits == 1
    assert record.status == "finalized"
    assert [item.production_function for item in record.productions] == list(
        FUNCTIONS
    )
    assert all(item.modality_used == "voice" for item in record.productions)
    assert record.completion_requirements_met is True
    assert record.transfer_variant_id == started.transfer_variant_id
    assert record.transfer_prompt_snapshot == started.transfer_prompt_snapshot


@pytest.mark.parametrize("function", FUNCTIONS)
def test_text_is_persisted_but_never_counts_as_oral_evidence(db, function):
    started = start_direct_english_construction_attempt(start_command(), db)
    captures = [
        capture_payload(
            item,
            modality="text" if item == function else "voice",
            variant_id=(
                started.transfer_variant_id if item == "transfer" else None
            ),
        )
        for item in FUNCTIONS
    ]
    record = finalize_direct_english_construction_attempt(
        finalize_command(started, captures=captures), db
    )

    actual = next(
        item for item in record.productions if item.production_function == function
    )
    assert actual.modality_used == "text"
    assert record.completion_requirements_met is False


@pytest.mark.parametrize(
    ("function", "support_used"),
    [("expanded", "anchors"), ("transfer", "initial_word")],
)
def test_excess_support_is_recorded_and_makes_completion_false(
    db, function, support_used
):
    started = start_direct_english_construction_attempt(start_command(), db)
    captures = [
        capture_payload(
            item,
            support_used=support_used if item == function else None,
            variant_id=(
                started.transfer_variant_id if item == "transfer" else None
            ),
        )
        for item in FUNCTIONS
    ]
    record = finalize_direct_english_construction_attempt(
        finalize_command(started, captures=captures), db
    )

    actual = next(
        item for item in record.productions if item.production_function == function
    )
    assert actual.support_used == support_used
    assert actual.configured_support_level != support_used
    assert record.completion_requirements_met is False


def test_less_support_than_configured_keeps_structural_completion(db):
    started = start_direct_english_construction_attempt(start_command(), db)
    captures = [
        capture_payload(
            item,
            support_used="initial_word" if item == "guided" else None,
            variant_id=(
                started.transfer_variant_id if item == "transfer" else None
            ),
        )
        for item in FUNCTIONS
    ]
    record = finalize_direct_english_construction_attempt(
        finalize_command(started, captures=captures), db
    )

    assert record.completion_requirements_met is True


@pytest.mark.parametrize(
    ("changed_function", "updates", "message"),
    [
        ("guided", {"prompt_id": "wrong-prompt"}, "prompt or turn"),
        ("expanded", {"turn_id": "wrong-turn"}, "prompt or turn"),
        ("guided", {"conversation_id": "wrong-conversation"}, "conversation"),
        ("expanded", {"user_id": "other-user"}, "hierarchy or user"),
        ("guided", {"lesson_id": "a1-u1-l2"}, "hierarchy or user"),
    ],
)
def test_finalize_rejects_crossed_references(
    db, changed_function, updates, message
):
    started = start_direct_english_construction_attempt(start_command(), db)
    captures = [
        capture_payload(
            item,
            variant_id=(
                started.transfer_variant_id if item == "transfer" else None
            ),
            **(updates if item == changed_function else {}),
        )
        for item in FUNCTIONS
    ]

    with pytest.raises(DirectEnglishConstructionInvariantError, match=message):
        finalize_direct_english_construction_attempt(
            finalize_command(started, captures=captures), db
        )
    assert counts(db) == (0, 0, 0)


def test_finalize_rejects_variant_other_than_started_snapshot(db):
    started = start_direct_english_construction_attempt(start_command(), db)
    captures = [
        capture_payload(
            item,
            variant_id="different-variant" if item == "transfer" else None,
        )
        for item in FUNCTIONS
    ]

    with pytest.raises(DirectEnglishConstructionInvariantError, match="selected variant"):
        finalize_direct_english_construction_attempt(
            finalize_command(started, captures=captures), db
        )


def test_finalize_rejects_finalized_attempt_without_overwrite(db):
    started = start_direct_english_construction_attempt(start_command(), db)
    command = finalize_command(started)
    first = finalize_direct_english_construction_attempt(command, db)

    with pytest.raises(DirectEnglishConstructionStateConflictError):
        finalize_direct_english_construction_attempt(command, db)

    assert get_direct_english_construction_attempt(started.attempt_id, db) == first
    assert counts(db) == (3, 3, 3)


@pytest.mark.parametrize("failure_flush", [1, 7])
def test_finalize_rolls_back_every_created_row_after_flush_failure(
    db, monkeypatch, failure_flush
):
    started = start_direct_english_construction_attempt(start_command(), db)
    original_flush = db.flush
    calls = 0

    def fail_selected_flush(*args, **kwargs):
        nonlocal calls
        if not db.new:
            return original_flush(*args, **kwargs)
        calls += 1
        if calls == failure_flush:
            raise SQLAlchemyError("forced finalize flush failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db, "flush", fail_selected_flush)
    with pytest.raises(DirectEnglishConstructionExecutionError) as exc_info:
        finalize_direct_english_construction_attempt(
            finalize_command(started), db
        )
    monkeypatch.setattr(db, "flush", original_flush)

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert counts(db) == (0, 0, 0)
    assert get_direct_english_construction_attempt(
        started.attempt_id, db
    ).status == "started"


def test_concurrent_state_conflict_rolls_back_all_rows(db, monkeypatch):
    started = start_direct_english_construction_attempt(start_command(), db)
    original_update = Query.update

    def return_no_rows(self, values, **kwargs):
        if "direct_english_construction_attempts" in str(self):
            return 0
        return original_update(self, values, **kwargs)

    monkeypatch.setattr(Query, "update", return_no_rows)
    with pytest.raises(DirectEnglishConstructionStateConflictError):
        finalize_direct_english_construction_attempt(
            finalize_command(started), db
        )

    assert counts(db) == (0, 0, 0)


def test_finalize_commit_failure_rolls_back_all_rows(db, monkeypatch):
    started = start_direct_english_construction_attempt(start_command(), db)

    def fail_commit():
        raise SQLAlchemyError("forced finalize commit failure")

    monkeypatch.setattr(db, "commit", fail_commit)
    with pytest.raises(DirectEnglishConstructionExecutionError) as exc_info:
        finalize_direct_english_construction_attempt(
            finalize_command(started), db
        )

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)
    assert counts(db) == (0, 0, 0)


def test_database_prevents_reusing_one_production_between_attempts(db):
    first = start_direct_english_construction_attempt(start_command("attempt-1"), db)
    finalized = finalize_direct_english_construction_attempt(
        finalize_command(first), db
    )
    second = start_direct_english_construction_attempt(start_command("attempt-2"), db)
    production_id = finalized.productions[0].production_id
    db.add(
        DirectEnglishConstructionAttemptProduction(
            attempt_id=second.attempt_id,
            learner_production_id=production_id,
            production_function="guided",
            evidence_id="a1-u1-l1-ev-guided",
            configured_support_level="anchors",
            support_used="anchors",
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_get_does_not_commit_and_retries_are_append_only(db, monkeypatch):
    first = start_direct_english_construction_attempt(start_command("attempt-1"), db)
    second = start_direct_english_construction_attempt(start_command("attempt-2"), db)
    finalize_direct_english_construction_attempt(finalize_command(first), db)
    finalize_direct_english_construction_attempt(finalize_command(second), db)

    def forbidden_commit():
        raise AssertionError("get must not commit")

    monkeypatch.setattr(db, "commit", forbidden_commit)
    recovered_first = get_direct_english_construction_attempt("attempt-1", db)
    recovered_second = get_direct_english_construction_attempt("attempt-2", db)

    assert recovered_first.attempt_id != recovered_second.attempt_id
    assert {item.production_id for item in recovered_first.productions}.isdisjoint(
        {item.production_id for item in recovered_second.productions}
    )
    assert counts(db) == (6, 6, 6)


def test_get_missing_attempt_and_no_semantic_or_mastery_fields(db):
    with pytest.raises(DirectEnglishConstructionReferenceNotFoundError):
        get_direct_english_construction_attempt("missing", db)

    record_fields = set(DirectEnglishConstructionAttemptRecord.model_fields)
    assert "progress" not in record_fields
    assert "mastery" not in record_fields
    assert "semantic_result" not in record_fields
    assert "correction" not in record_fields
