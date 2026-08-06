from datetime import datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    ConversationalDiagnosticActivity as ActivityModel,
    ConversationalDiagnosticActivityProduction as ActivityProductionModel,
    ConversationalDiagnosticContext as ContextModel,
    ConversationalDiagnosticSession as SessionModel,
    ConversationalDiagnosticSupportUsage as SupportUsageModel,
    LearnerProduction as LearnerProductionModel,
)
from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
)
from app.schemas.conversational_diagnostic_persistence import (
    ConversationalDiagnosticActivityProductionSetup,
    ConversationalDiagnosticProductionSupportsBatch,
    ConversationalDiagnosticSessionSetup,
)
from app.services.conversational_diagnostic_persistence_service import (
    ConversationalDiagnosticPersistenceError,
    DiagnosticPersistenceInvariantError,
    DiagnosticReferenceNotFoundError,
    DiagnosticSessionAlreadyExistsError,
    get_conversational_diagnostic_session_setup,
    save_conversational_diagnostic_production_supports,
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


def add_production(
    db,
    *,
    prompt_id="prompt-one-1",
    modality="text",
    suffix="one",
):
    submission = SubmissionModel(
        user_id=f"user-{suffix}",
        level_id="level-1",
        unit_id="unit-1",
        lesson_id="lesson-1",
        conversation_id=f"conversation-{suffix}",
    )
    db.add(submission)
    db.flush()
    production = LearnerProductionModel(
        submission_id=submission.id,
        prompt_id=prompt_id,
        turn_id=f"turn-{suffix}",
        modality=modality,
        response_text="Hello" if modality == "text" else None,
        audio_reference="audio-ref" if modality == "voice" else None,
    )
    db.add(production)
    db.commit()
    return production


def build_association(
    production_id,
    *,
    session_id="session-one",
    activity_id="activity-one-1",
    supports=True,
):
    usages = []
    if supports:
        usages = [
            DiagnosticSupportUsage(
                diagnostic_session_id=session_id,
                activity_id=activity_id,
                production_id=production_id,
                support_type="visual",
                support_level="minimal",
                sequence_order=1,
                provided_at=STARTED_AT,
            )
        ]
    return ConversationalDiagnosticActivityProductionSetup(
        diagnostic_session_id=session_id,
        activity_id=activity_id,
        production_id=production_id,
        support_usages=usages,
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


def test_increment_one_setup_remains_exactly_compatible():
    setup = build_setup()

    assert setup.production_supports == []
    assert ConversationalDiagnosticSessionSetup.model_validate(
        setup.model_dump()
    ) == setup


def test_initial_save_round_trips_production_supports(db):
    production = add_production(db)
    association = build_association(production.id)
    setup = build_setup().model_copy(
        update={"production_supports": [association]}
    )

    saved = save_conversational_diagnostic_session_setup(setup, db)
    loaded = get_conversational_diagnostic_session_setup(
        setup.session.diagnostic_session_id,
        db,
    )

    assert saved == setup
    assert loaded == setup
    assert db.query(ActivityProductionModel).count() == 1
    assert db.query(SupportUsageModel).count() == 1


def test_enriches_existing_session_atomically(db):
    setup = build_setup()
    production = add_production(db)
    save_conversational_diagnostic_session_setup(setup, db)
    batch = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id=setup.session.diagnostic_session_id,
        associations=[build_association(production.id)],
    )

    enriched = save_conversational_diagnostic_production_supports(batch, db)

    assert enriched.production_supports == batch.associations
    assert db.query(SessionModel).count() == 1
    assert db.query(ActivityModel).count() == 2


def test_get_orders_associations_and_supports_stably(db):
    first = add_production(db, suffix="first")
    second = add_production(db, suffix="second")
    late = DiagnosticSupportUsage(
        diagnostic_session_id="session-one",
        activity_id="activity-one-1",
        production_id=second.id,
        support_type="visual",
        support_level="minimal",
        sequence_order=3,
        provided_at=STARTED_AT,
    )
    early = late.model_copy(update={"sequence_order": 2})
    associations = [
        ConversationalDiagnosticActivityProductionSetup(
            diagnostic_session_id="session-one",
            activity_id="activity-one-1",
            production_id=second.id,
            support_usages=[early, late],
        ),
        build_association(first.id),
    ]
    setup = build_setup().model_copy(
        update={"production_supports": associations}
    )

    save_conversational_diagnostic_session_setup(setup, db)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)

    assert [
        association.production_id
        for association in loaded.production_supports
    ] == sorted([first.id, second.id])
    second_loaded = next(
        association
        for association in loaded.production_supports
        if association.production_id == second.id
    )
    assert [
        usage.sequence_order for usage in second_loaded.support_usages
    ] == [2, 3]


def test_rejects_missing_production_without_residual_setup(db):
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(999)]}
    )

    with pytest.raises(DiagnosticReferenceNotFoundError):
        save_conversational_diagnostic_session_setup(setup, db)

    assert db.query(SessionModel).count() == 0
    assert db.query(ActivityProductionModel).count() == 0


@pytest.mark.parametrize(
    ("prompt_id", "modality", "message"),
    [
        ("another-prompt", "text", "prompt"),
        ("prompt-one-1", "voice", "modality"),
    ],
)
def test_rejects_incompatible_production(
    db,
    prompt_id,
    modality,
    message,
):
    production = add_production(
        db,
        prompt_id=prompt_id,
        modality=modality,
    )
    setup = build_setup().model_copy(
        update={
            "production_supports": [
                build_association(production.id, supports=False)
            ]
        }
    )

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="violates",
    ) as captured:
        save_conversational_diagnostic_session_setup(setup, db)

    assert message in str(captured.value.__cause__)
    assert db.query(ActivityProductionModel).count() == 0


def test_batch_rejects_duplicate_or_reused_production():
    association = build_association(1, supports=False)

    with pytest.raises(ValidationError, match="multiple activities"):
        ConversationalDiagnosticProductionSupportsBatch(
            diagnostic_session_id="session-one",
            associations=[
                association,
                association.model_copy(
                    update={"activity_id": "activity-one-2"}
                ),
            ],
        )


def test_rejects_production_already_associated(db):
    production = add_production(db)
    setup = build_setup()
    save_conversational_diagnostic_session_setup(setup, db)
    batch = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id="session-one",
        associations=[build_association(production.id, supports=False)],
    )
    save_conversational_diagnostic_production_supports(batch, db)

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="already associated",
    ):
        save_conversational_diagnostic_production_supports(batch, db)

    assert db.query(ActivityProductionModel).count() == 1


def test_database_rejects_reusing_production_between_activities(db):
    production = add_production(db)
    save_conversational_diagnostic_session_setup(build_setup(), db)
    first = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id="session-one",
        associations=[build_association(production.id, supports=False)],
    )
    save_conversational_diagnostic_production_supports(first, db)
    second = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id="session-one",
        associations=[
            build_association(
                production.id,
                activity_id="activity-one-2",
                supports=False,
            )
        ],
    )

    with pytest.raises(DiagnosticPersistenceInvariantError):
        save_conversational_diagnostic_production_supports(second, db)


def test_rejects_unavailable_support_with_cause(db):
    production = add_production(db)
    association = build_association(production.id)
    invalid_usage = association.support_usages[0].model_copy(
        update={"support_type": "keyword"}
    )
    invalid = association.model_copy(
        update={"support_usages": [invalid_usage]}
    )
    setup = build_setup().model_copy(
        update={"production_supports": [invalid]}
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(setup, db)

    assert isinstance(captured.value.__cause__, ValueError)
    assert "available" in str(captured.value.__cause__)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("diagnostic_session_id", "another-session", "session"),
        ("activity_id", "activity-one-2", "activity"),
        ("production_id", 999, "production"),
    ],
)
def test_association_rejects_crossed_support_identifiers(
    field,
    value,
    message,
):
    usage = build_association(1).support_usages[0].model_copy(
        update={field: value}
    )

    with pytest.raises(ValidationError, match=message):
        ConversationalDiagnosticActivityProductionSetup(
            diagnostic_session_id="session-one",
            activity_id="activity-one-1",
            production_id=1,
            support_usages=[usage],
        )


def test_association_rejects_duplicate_support_sequence():
    association = build_association(1)
    duplicate = association.support_usages[0].model_copy()

    with pytest.raises(ValidationError, match="unique sequence"):
        ConversationalDiagnosticActivityProductionSetup(
            diagnostic_session_id="session-one",
            activity_id="activity-one-1",
            production_id=1,
            support_usages=[association.support_usages[0], duplicate],
        )


def test_association_rejects_unordered_support_sequence():
    association = build_association(1)
    first = association.support_usages[0].model_copy(
        update={"sequence_order": 2}
    )
    second = association.support_usages[0].model_copy(
        update={"sequence_order": 1}
    )

    with pytest.raises(ValidationError, match="follow sequence order"):
        ConversationalDiagnosticActivityProductionSetup(
            diagnostic_session_id="session-one",
            activity_id="activity-one-1",
            production_id=1,
            support_usages=[first, second],
        )


def test_rejects_duplicate_support_sequence_across_productions(db):
    first = add_production(db, suffix="first")
    second = add_production(db, suffix="second")
    setup = build_setup().model_copy(
        update={
            "production_supports": [
                build_association(first.id),
                build_association(second.id),
            ]
        }
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(setup, db)

    assert "unique sequence orders" in str(captured.value.__cause__)


def test_enriched_sessions_remain_isolated(db):
    first_production = add_production(
        db,
        prompt_id="prompt-first-1",
        suffix="first",
    )
    second_production = add_production(
        db,
        prompt_id="prompt-second-1",
        suffix="second",
    )
    first_setup = build_setup("first")
    second_setup = build_setup("second")
    save_conversational_diagnostic_session_setup(first_setup, db)
    save_conversational_diagnostic_session_setup(second_setup, db)
    save_conversational_diagnostic_production_supports(
        ConversationalDiagnosticProductionSupportsBatch(
            diagnostic_session_id="session-first",
            associations=[
                build_association(
                    first_production.id,
                    session_id="session-first",
                    activity_id="activity-first-1",
                )
            ],
        ),
        db,
    )
    save_conversational_diagnostic_production_supports(
        ConversationalDiagnosticProductionSupportsBatch(
            diagnostic_session_id="session-second",
            associations=[
                build_association(
                    second_production.id,
                    session_id="session-second",
                    activity_id="activity-second-1",
                )
            ],
        ),
        db,
    )

    loaded = get_conversational_diagnostic_session_setup(
        "session-first", db
    )

    assert [
        association.production_id
        for association in loaded.production_supports
    ] == [first_production.id]


def test_rejects_invalid_support_withdrawal_sequence(db):
    production = add_production(db)
    association = build_association(production.id)
    withdrawn = association.support_usages[0].model_copy(
        update={"withdrawn_afterward": True}
    )
    setup = build_setup().model_copy(
        update={
            "production_supports": [
                association.model_copy(update={"support_usages": [withdrawn]})
            ]
        }
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(setup, db)

    assert "later production" in str(captured.value.__cause__)


@pytest.mark.parametrize("enrichment", [False, True])
def test_writes_commit_exactly_once_with_production_supports(
    db,
    monkeypatch,
    enrichment,
):
    production = add_production(db)
    setup = build_setup()
    association = build_association(production.id)
    if enrichment:
        save_conversational_diagnostic_session_setup(setup, db)
    commits = 0
    original_commit = db.commit

    def counted_commit():
        nonlocal commits
        commits += 1
        return original_commit()

    monkeypatch.setattr(db, "commit", counted_commit)
    if enrichment:
        batch = ConversationalDiagnosticProductionSupportsBatch(
            diagnostic_session_id="session-one",
            associations=[association],
        )
        save_conversational_diagnostic_production_supports(batch, db)
    else:
        save_conversational_diagnostic_session_setup(
            setup.model_copy(update={"production_supports": [association]}),
            db,
        )

    assert commits == 1


@pytest.mark.parametrize("failing_flush_call", [1, 2])
def test_enrichment_flush_failures_leave_no_residual_evidence(
    db,
    monkeypatch,
    failing_flush_call,
):
    production = add_production(db)
    save_conversational_diagnostic_session_setup(build_setup(), db)
    batch = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id="session-one",
        associations=[build_association(production.id)],
    )
    original_flush = db.flush
    calls = 0

    def failing_flush(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == failing_flush_call:
            raise SQLAlchemyError("injected association flush failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db, "flush", failing_flush)

    with pytest.raises(ConversationalDiagnosticPersistenceError):
        save_conversational_diagnostic_production_supports(batch, db)

    assert db.query(ActivityProductionModel).count() == 0
    assert db.query(SupportUsageModel).count() == 0


def test_enrichment_does_not_change_learner_production(db):
    production = add_production(db)
    original = (
        production.id,
        production.submission_id,
        production.prompt_id,
        production.turn_id,
        production.modality,
        production.response_text,
        production.audio_reference,
    )
    save_conversational_diagnostic_session_setup(build_setup(), db)
    batch = ConversationalDiagnosticProductionSupportsBatch(
        diagnostic_session_id="session-one",
        associations=[build_association(production.id)],
    )

    save_conversational_diagnostic_production_supports(batch, db)
    persisted = db.query(LearnerProductionModel).one()

    assert db.query(LearnerProductionModel).count() == 1
    assert (
        persisted.id,
        persisted.submission_id,
        persisted.prompt_id,
        persisted.turn_id,
        persisted.modality,
        persisted.response_text,
        persisted.audio_reference,
    ) == original


def test_get_enriched_setup_never_commits(db, monkeypatch):
    production = add_production(db)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    commits = 0

    def counted_commit():
        nonlocal commits
        commits += 1

    monkeypatch.setattr(db, "commit", counted_commit)

    assert get_conversational_diagnostic_session_setup(
        "session-one", db
    ) == setup
    assert commits == 0
