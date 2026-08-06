from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationalDiagnosticActivity as ActivityModel,
    ConversationalDiagnosticContext as ContextModel,
    ConversationalDiagnosticSession as SessionModel,
)
from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticSession,
)
from app.schemas.conversational_diagnostic_persistence import (
    ConversationalDiagnosticSessionSetup,
)
from app.services.conversational_diagnostic_persistence_service import (
    ConversationalDiagnosticPersistenceError,
    DiagnosticPersistenceInvariantError,
    DiagnosticReferenceNotFoundError,
    DiagnosticSessionAlreadyExistsError,
    get_conversational_diagnostic_session_setup,
    save_conversational_diagnostic_session_setup,
)


STARTED_AT = datetime(2026, 8, 6, 10)


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


def build_setup(suffix="one", *, activity_count=2):
    session_id = f"session-{suffix}"
    context_id = f"context-{suffix}"
    session = ConversationalDiagnosticSession(
        diagnostic_session_id=session_id,
        user_id=f"user-{suffix}",
        age_profile="adult",
        status="in_progress",
        started_at=STARTED_AT,
    )
    context = ConversationalDiagnosticContext(
        context_id=context_id,
        diagnostic_session_id=session_id,
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["travel"],
        learning_goals=["conversation"],
        autonomy_level="independent",
        responsible_adult_present=None,
        audio_authorized=True,
    )
    activities = [
        ConversationalDiagnosticActivity(
            activity_id=f"activity-{suffix}-{order}",
            diagnostic_session_id=session_id,
            context_id=context_id,
            prompt_id=f"prompt-{suffix}-{order}",
            stage="initial_response",
            communicative_intention="Introduce yourself",
            modality="text",
            expected_evidence_type="spontaneous_production",
            available_supports=["visual"],
            sequence_order=order,
        )
        for order in range(1, activity_count + 1)
    ]
    return ConversationalDiagnosticSessionSetup(
        session=session,
        context=context,
        activities=activities,
    )


def test_round_trip_preserves_complete_setup(db):
    setup = build_setup()

    saved = save_conversational_diagnostic_session_setup(setup, db)
    loaded = get_conversational_diagnostic_session_setup(
        setup.session.diagnostic_session_id,
        db,
    )

    assert saved == setup
    assert loaded == setup
    assert db.query(SessionModel).count() == 1
    assert db.query(ContextModel).count() == 1
    assert db.query(ActivityModel).count() == 2


def test_get_orders_activities_stably(db):
    setup = build_setup(activity_count=3)
    save_conversational_diagnostic_session_setup(setup, db)

    loaded = get_conversational_diagnostic_session_setup(
        setup.session.diagnostic_session_id,
        db,
    )

    assert [item.sequence_order for item in loaded.activities] == [1, 2, 3]
    assert [item.activity_id for item in loaded.activities] == [
        "activity-one-1",
        "activity-one-2",
        "activity-one-3",
    ]


def test_reject_context_from_another_session():
    setup = build_setup()
    foreign_context = setup.context.model_copy(
        update={"diagnostic_session_id": "another-session"}
    )

    with pytest.raises(ValidationError, match="context"):
        ConversationalDiagnosticSessionSetup(
            session=setup.session,
            context=foreign_context,
            activities=setup.activities,
        )


def test_reject_activity_from_another_session():
    setup = build_setup()
    activities = [
        setup.activities[0].model_copy(
            update={"diagnostic_session_id": "another-session"}
        )
    ]

    with pytest.raises(ValidationError, match="activities"):
        ConversationalDiagnosticSessionSetup(
            session=setup.session,
            context=setup.context,
            activities=activities,
        )


def test_service_translates_cross_contract_error_with_cause(db):
    setup = build_setup()
    invalid = setup.model_copy(
        update={
            "context": setup.context.model_copy(
                update={"diagnostic_session_id": "another-session"}
            )
        }
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(invalid, db)

    assert isinstance(captured.value.__cause__, ValueError)
    assert db.query(SessionModel).count() == 0


def test_reject_duplicate_activity_identifiers():
    setup = build_setup()
    duplicate = setup.activities[1].model_copy(
        update={"activity_id": setup.activities[0].activity_id}
    )

    with pytest.raises(ValidationError, match="unique identifiers"):
        ConversationalDiagnosticSessionSetup(
            session=setup.session,
            context=setup.context,
            activities=[setup.activities[0], duplicate],
        )


def test_reject_duplicate_sequence_orders():
    setup = build_setup()
    duplicate = setup.activities[1].model_copy(update={"sequence_order": 1})

    with pytest.raises(ValidationError, match="unique sequence orders"):
        ConversationalDiagnosticSessionSetup(
            session=setup.session,
            context=setup.context,
            activities=[setup.activities[0], duplicate],
        )


def test_reject_existing_session_identifier(db):
    setup = build_setup()
    save_conversational_diagnostic_session_setup(setup, db)

    with pytest.raises(DiagnosticSessionAlreadyExistsError):
        save_conversational_diagnostic_session_setup(setup, db)

    assert db.query(SessionModel).count() == 1


def test_reject_existing_context_identifier(db):
    first = build_setup("first")
    save_conversational_diagnostic_session_setup(first, db)
    second = build_setup("second").model_copy(
        update={
            "context": build_setup("second").context.model_copy(
                update={"context_id": first.context.context_id}
            ),
            "activities": [
                item.model_copy(update={"context_id": first.context.context_id})
                for item in build_setup("second").activities
            ],
        }
    )

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="context identifier",
    ):
        save_conversational_diagnostic_session_setup(second, db)

    assert db.query(SessionModel).count() == 1


def test_reject_existing_activity_identifier(db):
    first = build_setup("first")
    save_conversational_diagnostic_session_setup(first, db)
    original_second = build_setup("second")
    conflicting_activity = original_second.activities[0].model_copy(
        update={"activity_id": first.activities[0].activity_id}
    )
    second = original_second.model_copy(
        update={
            "activities": [
                conflicting_activity,
                original_second.activities[1],
            ]
        }
    )

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="activity identifier",
    ):
        save_conversational_diagnostic_session_setup(second, db)

    assert db.query(SessionModel).count() == 1


def test_get_rejects_unknown_session(db):
    with pytest.raises(
        DiagnosticReferenceNotFoundError,
        match="does not exist",
    ):
        get_conversational_diagnostic_session_setup("unknown", db)


def test_sessions_are_isolated(db):
    first = build_setup("first")
    second = build_setup("second")
    save_conversational_diagnostic_session_setup(first, db)
    save_conversational_diagnostic_session_setup(second, db)

    loaded_first = get_conversational_diagnostic_session_setup(
        first.session.diagnostic_session_id,
        db,
    )
    loaded_second = get_conversational_diagnostic_session_setup(
        second.session.diagnostic_session_id,
        db,
    )

    assert loaded_first == first
    assert loaded_second == second
    assert {
        item.diagnostic_session_id for item in loaded_first.activities
    } == {first.session.diagnostic_session_id}


def test_save_commits_exactly_once(db, monkeypatch):
    commits = 0
    original_commit = db.commit

    def counted_commit():
        nonlocal commits
        commits += 1
        return original_commit()

    monkeypatch.setattr(db, "commit", counted_commit)

    save_conversational_diagnostic_session_setup(build_setup(), db)

    assert commits == 1


def test_flush_failure_rolls_back_without_residual_records(db, monkeypatch):
    original_flush = db.flush
    calls = 0

    def failing_flush(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise SQLAlchemyError("injected flush failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db, "flush", failing_flush)

    with pytest.raises(ConversationalDiagnosticPersistenceError) as captured:
        save_conversational_diagnostic_session_setup(build_setup(), db)

    assert isinstance(captured.value.__cause__, SQLAlchemyError)
    assert db.query(SessionModel).count() == 0
    assert db.query(ContextModel).count() == 0
    assert db.query(ActivityModel).count() == 0


def test_commit_failure_rolls_back_without_residual_records(db, monkeypatch):
    def failing_commit():
        raise SQLAlchemyError("injected commit failure")

    monkeypatch.setattr(db, "commit", failing_commit)

    with pytest.raises(ConversationalDiagnosticPersistenceError) as captured:
        save_conversational_diagnostic_session_setup(build_setup(), db)

    assert isinstance(captured.value.__cause__, SQLAlchemyError)
    assert db.query(SessionModel).count() == 0
    assert db.query(ContextModel).count() == 0
    assert db.query(ActivityModel).count() == 0


def test_get_never_commits(db, monkeypatch):
    setup = build_setup()
    save_conversational_diagnostic_session_setup(setup, db)
    commits = 0

    def counted_commit():
        nonlocal commits
        commits += 1

    monkeypatch.setattr(db, "commit", counted_commit)

    assert get_conversational_diagnostic_session_setup(
        setup.session.diagnostic_session_id,
        db,
    ) == setup
    assert commits == 0
