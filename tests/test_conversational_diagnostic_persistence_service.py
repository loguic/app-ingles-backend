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
    ConversationalDiagnosticObservation as ObservationModel,
    ConversationalDiagnosticObservationEvaluation as ObservationEvaluationModel,
    ConversationalDiagnosticSession as SessionModel,
    ConversationalDiagnosticSupportUsage as SupportUsageModel,
    LearnerProduction as LearnerProductionModel,
    ProductionEvaluationResult as EvaluationResultModel,
    InitialConversationalProfile as InitialProfileModel,
    InitialConversationalProfileEvidence as ProfileEvidenceModel,
)
from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
)
from app.schemas.conversational_diagnostic_persistence import (
    ConversationalDiagnosticActivityProductionSetup,
    ConversationalDiagnosticObservationsBatch,
    ConversationalDiagnosticProductionSupportsBatch,
    ConversationalDiagnosticProfilesBatch,
    ConversationalDiagnosticSessionTransition,
    ConversationalDiagnosticSessionSetup,
    InitialConversationalProfileSetup,
)
from app.services.conversational_diagnostic_persistence_service import (
    ConversationalDiagnosticPersistenceError,
    DiagnosticPersistenceInvariantError,
    DiagnosticReferenceNotFoundError,
    DiagnosticSessionAlreadyExistsError,
    get_conversational_diagnostic_session_setup,
    save_conversational_diagnostic_observations,
    save_conversational_diagnostic_production_supports,
    save_conversational_diagnostic_profiles,
    save_conversational_diagnostic_session_setup,
    transition_conversational_diagnostic_session,
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


def add_evaluation(db, production_id, *, suffix="one"):
    evaluation = EvaluationResultModel(
        production_id=production_id,
        criterion_id=f"criterion-{suffix}",
        status="passed",
        score=0.8,
        evaluator_id="technical-evaluator",
        evaluator_version="1.0",
        evaluated_at=STARTED_AT,
    )
    db.add(evaluation)
    db.commit()
    return evaluation


def build_observation(
    production_id=None,
    *,
    evaluation_result_ids=None,
    observation_id="observation-one",
    session_id="session-one",
    activity_id="activity-one-1",
    dimension=None,
    support_level=None,
    observed_at=STARTED_AT,
):
    if evaluation_result_ids is None:
        evaluation_result_ids = []
    if dimension is None:
        dimension = (
            "response_initiation"
            if production_id is not None
            else "listening_comprehension"
        )
    if support_level is None:
        support_level = "minimal" if production_id is not None else "none"
    return ConversationalDiagnosticObservation(
        observation_id=observation_id,
        diagnostic_session_id=session_id,
        activity_id=activity_id,
        production_id=production_id,
        evaluation_result_ids=evaluation_result_ids,
        dimension=dimension,
        evidence_role="strength",
        description="Observable diagnostic evidence",
        support_level=support_level,
        observer_id="diagnostic-observer",
        observer_version="1.0",
        observed_at=observed_at,
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


def test_previous_aggregates_remain_compatible_without_observations():
    setup = build_setup()
    association = build_association(1, supports=False)

    assert setup.observations == []
    assert setup.model_copy(
        update={"production_supports": [association]}
    ).observations == []


def test_initial_save_round_trips_observations_and_evaluations(db):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    observation = build_observation(
        production.id,
        evaluation_result_ids=[evaluation.id],
    )
    setup = build_setup().model_copy(
        update={
            "production_supports": [build_association(production.id)],
            "observations": [observation],
        }
    )

    saved = save_conversational_diagnostic_session_setup(setup, db)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)

    assert saved == setup
    assert loaded == setup
    assert db.query(ObservationModel).count() == 1
    assert db.query(ObservationEvaluationModel).count() == 1


def test_enriches_existing_session_with_observations(db):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    observation = build_observation(
        production.id,
        evaluation_result_ids=[evaluation.id],
    )
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="session-one",
        observations=[observation],
    )

    enriched = save_conversational_diagnostic_observations(batch, db)

    assert enriched.observations == [observation]
    assert db.query(ObservationEvaluationModel).count() == 1


def test_get_orders_observations_and_evaluation_ids_stably(db):
    production = add_production(db)
    first_evaluation = add_evaluation(db, production.id, suffix="first")
    second_evaluation = add_evaluation(db, production.id, suffix="second")
    later = build_observation(
        production.id,
        evaluation_result_ids=[second_evaluation.id, first_evaluation.id],
        observation_id="observation-later",
        observed_at=STARTED_AT.replace(hour=11),
    )
    earlier = build_observation(
        production.id,
        observation_id="observation-earlier",
    )
    setup = build_setup().model_copy(
        update={
            "production_supports": [build_association(production.id)],
            "observations": [later, earlier],
        }
    )

    save_conversational_diagnostic_session_setup(setup, db)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)

    assert [item.observation_id for item in loaded.observations] == [
        "observation-earlier",
        "observation-later",
    ]
    assert loaded.observations[1].evaluation_result_ids == sorted(
        [first_evaluation.id, second_evaluation.id]
    )


def test_accepts_observation_without_evaluations(db):
    production = add_production(db)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)

    saved = save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[build_observation(production.id)],
        ),
        db,
    )

    assert saved.observations[0].evaluation_result_ids == []


def test_one_evaluation_can_support_multiple_compatible_observations(db):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    observations = [
        build_observation(
            production.id,
            evaluation_result_ids=[evaluation.id],
            observation_id=f"observation-{suffix}",
        )
        for suffix in ("first", "second")
    ]

    save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=observations,
        ),
        db,
    )

    assert db.query(ObservationEvaluationModel).count() == 2


def test_rejects_unknown_session_for_observation_batch(db):
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="unknown-session",
        observations=[
            build_observation(
                session_id="unknown-session",
                activity_id="unknown-activity",
            )
        ],
    )

    with pytest.raises(DiagnosticReferenceNotFoundError):
        save_conversational_diagnostic_observations(batch, db)


def test_rejects_unknown_observation_activity(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="session-one",
        observations=[build_observation(activity_id="unknown-activity")],
    )

    with pytest.raises(DiagnosticReferenceNotFoundError, match="activity"):
        save_conversational_diagnostic_observations(batch, db)


def test_rejects_unknown_observation_production(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="session-one",
        observations=[build_observation(999, support_level="none")],
    )

    with pytest.raises(DiagnosticReferenceNotFoundError, match="production"):
        save_conversational_diagnostic_observations(batch, db)


def test_rejects_unknown_evaluation(db):
    production = add_production(db)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)

    with pytest.raises(DiagnosticReferenceNotFoundError, match="evaluation"):
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[
                    build_observation(
                        production.id,
                        evaluation_result_ids=[999],
                    )
                ],
            ),
            db,
        )


def test_batch_rejects_duplicate_observation_identifier():
    observation = build_observation()

    with pytest.raises(ValidationError, match="unique identifiers"):
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[observation, observation],
        )


def test_batch_rejects_observation_from_another_session():
    with pytest.raises(ValidationError, match="diagnostic session"):
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[
                build_observation(session_id="another-session")
            ],
        )


def test_rejects_existing_observation_identifier(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="session-one",
        observations=[build_observation()],
    )
    save_conversational_diagnostic_observations(batch, db)

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="already exists",
    ):
        save_conversational_diagnostic_observations(batch, db)


def test_observation_contract_rejects_duplicate_evaluation_identifier():
    with pytest.raises(ValidationError, match="unique values"):
        build_observation(evaluation_result_ids=[1, 1])


def test_rejects_production_owned_by_another_activity(db):
    production = add_production(db)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    observation = build_observation(
        production.id,
        activity_id="activity-one-2",
        support_level="none",
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[observation],
            ),
            db,
        )

    assert "another activity" in str(captured.value.__cause__)


def test_rejects_evaluation_of_another_production(db):
    production = add_production(db, suffix="first")
    other = add_production(db, suffix="second")
    evaluation = add_evaluation(db, other.id)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[
                    build_observation(
                        production.id,
                        evaluation_result_ids=[evaluation.id],
                    )
                ],
            ),
            db,
        )

    assert "observed production" in str(captured.value.__cause__)


def test_batch_rejects_production_required_dimension_without_production():
    observation = build_observation().model_copy(
        update={"dimension": "response_initiation"}
    )

    with pytest.raises(ValidationError, match="requires a production"):
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[observation],
        )


def test_accepts_legitimate_observation_without_production(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)

    saved = save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[build_observation()],
        ),
        db,
    )

    assert saved.observations[0].production_id is None


def test_batch_rejects_evaluation_without_production():
    observation = build_observation().model_copy(
        update={"evaluation_result_ids": [1]}
    )

    with pytest.raises(ValidationError, match="observed production"):
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[observation],
        )


def test_rejects_observation_support_level_not_actually_used(db):
    production = add_production(db)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[
                    build_observation(production.id, support_level="full")
                ],
            ),
            db,
        )

    assert "support level" in str(captured.value.__cause__)


def test_rejects_unknown_motivating_context(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-context",
        diagnostic_session_id="session-one",
        activity_id="activity-one-1",
        dimension="motivating_context",
        evidence_role="context_relevance",
        context_reference="unknown interest",
        description="Context evidence",
        support_level="none",
        observer_id="observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[observation],
            ),
            db,
        )

    assert "authorized general interests" in str(captured.value.__cause__)


@pytest.mark.parametrize("enrichment", [False, True])
def test_observation_writes_commit_exactly_once(
    db,
    monkeypatch,
    enrichment,
):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    association = build_association(production.id)
    observation = build_observation(
        production.id,
        evaluation_result_ids=[evaluation.id],
    )
    setup = build_setup().model_copy(
        update={"production_supports": [association]}
    )
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
        save_conversational_diagnostic_observations(
            ConversationalDiagnosticObservationsBatch(
                diagnostic_session_id="session-one",
                observations=[observation],
            ),
            db,
        )
    else:
        save_conversational_diagnostic_session_setup(
            setup.model_copy(update={"observations": [observation]}),
            db,
        )

    assert commits == 1


@pytest.mark.parametrize("failing_flush_call", [1, 2])
def test_observation_flush_failure_rolls_back_all_evidence(
    db,
    monkeypatch,
    failing_flush_call,
):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    batch = ConversationalDiagnosticObservationsBatch(
        diagnostic_session_id="session-one",
        observations=[
            build_observation(
                production.id,
                evaluation_result_ids=[evaluation.id],
            )
        ],
    )
    original_flush = db.flush
    calls = 0

    def failing_flush(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == failing_flush_call:
            raise SQLAlchemyError("injected observation flush failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db, "flush", failing_flush)

    with pytest.raises(ConversationalDiagnosticPersistenceError):
        save_conversational_diagnostic_observations(batch, db)

    assert db.query(ObservationModel).count() == 0
    assert db.query(ObservationEvaluationModel).count() == 0


def test_get_observations_never_commits(db, monkeypatch):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[build_observation()],
        ),
        db,
    )
    commits = 0

    def counted_commit():
        nonlocal commits
        commits += 1

    monkeypatch.setattr(db, "commit", counted_commit)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)

    assert loaded.observations
    assert commits == 0


def test_observations_are_isolated_between_sessions(db):
    first = build_setup("first")
    second = build_setup("second")
    save_conversational_diagnostic_session_setup(first, db)
    save_conversational_diagnostic_session_setup(second, db)
    save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-first",
            observations=[
                build_observation(
                    observation_id="observation-first",
                    session_id="session-first",
                    activity_id="activity-first-1",
                )
            ],
        ),
        db,
    )

    assert get_conversational_diagnostic_session_setup(
        "session-second", db
    ).observations == []


def test_observation_enrichment_does_not_mutate_sources(db):
    production = add_production(db)
    evaluation = add_evaluation(db, production.id)
    production_snapshot = (
        production.prompt_id,
        production.modality,
        production.response_text,
    )
    evaluation_snapshot = (
        evaluation.production_id,
        evaluation.criterion_id,
        evaluation.status,
        evaluation.score,
    )
    setup = build_setup().model_copy(
        update={"production_supports": [build_association(production.id)]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=[
                build_observation(
                    production.id,
                    evaluation_result_ids=[evaluation.id],
                )
            ],
        ),
        db,
    )

    persisted_production = db.query(LearnerProductionModel).one()
    persisted_evaluation = db.query(EvaluationResultModel).one()
    assert db.query(LearnerProductionModel).count() == 1
    assert db.query(EvaluationResultModel).count() == 1
    assert (
        persisted_production.prompt_id,
        persisted_production.modality,
        persisted_production.response_text,
    ) == production_snapshot
    assert (
        persisted_evaluation.production_id,
        persisted_evaluation.criterion_id,
        persisted_evaluation.status,
        persisted_evaluation.score,
    ) == evaluation_snapshot
    assert not hasattr(persisted_evaluation, "mastery")
    assert not hasattr(persisted_evaluation, "consensus")


def build_transition(
    target_status,
    *,
    expected_current_status="in_progress",
    transitioned_at=STARTED_AT,
):
    return ConversationalDiagnosticSessionTransition(
        diagnostic_session_id="session-one",
        expected_current_status=expected_current_status,
        target_status=target_status,
        transitioned_at=transitioned_at,
    )


def build_completed_transition_setup():
    setup = build_setup(activity_count=6)
    evidence_types = [
        "comprehension",
        "spontaneous_production",
        "supported_production",
        "connected_exchange",
        "transfer",
        "motivating_context",
    ]
    activities = []
    observations = []
    for activity, evidence_type in zip(
        setup.activities,
        evidence_types,
        strict=True,
    ):
        updates = {"expected_evidence_type": evidence_type}
        if evidence_type == "transfer":
            updates.update(
                {"stage": "transfer", "transfer_variant_id": "variant-1"}
            )
        activity = activity.model_copy(update=updates)
        activities.append(activity)
        if evidence_type == "motivating_context":
            observations.append(
                ConversationalDiagnosticObservation(
                    observation_id="observation-motivating-context",
                    diagnostic_session_id="session-one",
                    activity_id=activity.activity_id,
                    dimension="motivating_context",
                    evidence_role="context_relevance",
                    context_reference="travel",
                    description="Motivating context evidence",
                    support_level="none",
                    observer_id="diagnostic-observer",
                    observer_version="1.0",
                    observed_at=STARTED_AT,
                )
            )
        else:
            observations.append(
                build_observation(
                    observation_id=f"observation-{evidence_type}",
                    activity_id=activity.activity_id,
                )
            )
    return ConversationalDiagnosticSessionSetup(
        session=setup.session,
        context=setup.context,
        activities=activities,
        observations=observations,
    )


@pytest.mark.parametrize("target_status", ["provisional", "cancelled"])
def test_transitions_in_progress_session_without_complete_coverage(
    db,
    target_status,
):
    save_conversational_diagnostic_session_setup(build_setup(), db)

    transitioned = transition_conversational_diagnostic_session(
        build_transition(target_status),
        db,
    )

    assert transitioned.status == target_status
    assert transitioned.completed_at == STARTED_AT


def test_transitions_in_progress_session_to_completed_with_coverage(db):
    setup = build_completed_transition_setup()
    save_conversational_diagnostic_session_setup(setup, db)

    transitioned = transition_conversational_diagnostic_session(
        build_transition("completed"),
        db,
    )

    assert transitioned.status == "completed"


def test_transitions_provisional_session_to_completed(db):
    setup = build_completed_transition_setup()
    observations = setup.observations
    save_conversational_diagnostic_session_setup(
        setup.model_copy(update={"observations": []}),
        db,
    )
    transition_conversational_diagnostic_session(
        build_transition("provisional"),
        db,
    )
    save_conversational_diagnostic_observations(
        ConversationalDiagnosticObservationsBatch(
            diagnostic_session_id="session-one",
            observations=observations,
        ),
        db,
    )

    transitioned = transition_conversational_diagnostic_session(
        build_transition(
            "completed",
            expected_current_status="provisional",
            transitioned_at=STARTED_AT.replace(hour=11),
        ),
        db,
    )

    assert transitioned.status == "completed"
    assert transitioned.completed_at == STARTED_AT.replace(hour=11)


def test_transitions_provisional_session_to_cancelled(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    transition_conversational_diagnostic_session(
        build_transition("provisional"),
        db,
    )

    transitioned = transition_conversational_diagnostic_session(
        build_transition(
            "cancelled",
            expected_current_status="provisional",
            transitioned_at=STARTED_AT.replace(hour=11),
        ),
        db,
    )

    assert transitioned.status == "cancelled"


def test_rejects_completed_transition_without_complete_coverage(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        transition_conversational_diagnostic_session(
            build_transition("completed"),
            db,
        )

    assert "complete diagnostic evidence" in str(captured.value.__cause__)
    assert db.query(SessionModel).one().status == "in_progress"


def test_rejects_unknown_transition_session(db):
    command = build_transition("cancelled").model_copy(
        update={"diagnostic_session_id": "unknown"}
    )

    with pytest.raises(DiagnosticReferenceNotFoundError):
        transition_conversational_diagnostic_session(command, db)


def test_rejects_transition_when_expected_status_is_stale(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    transition_conversational_diagnostic_session(
        build_transition("provisional"),
        db,
    )

    with pytest.raises(
        DiagnosticPersistenceInvariantError,
        match="expected state",
    ):
        transition_conversational_diagnostic_session(
            build_transition("cancelled"),
            db,
        )


def test_transition_contract_rejects_repeated_or_reopened_status():
    with pytest.raises(ValidationError, match="not allowed"):
        build_transition(
            "provisional",
            expected_current_status="provisional",
        )
    with pytest.raises(ValidationError, match="not allowed"):
        build_transition(
            "in_progress",
            expected_current_status="completed",
        )


def test_rejects_transition_timestamp_before_session_start(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        transition_conversational_diagnostic_session(
            build_transition(
                "cancelled",
                transitioned_at=STARTED_AT.replace(hour=9),
            ),
            db,
        )

    assert "started_at" in str(captured.value.__cause__)


def test_rejects_transition_timestamp_before_provisional_close(db):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    transition_conversational_diagnostic_session(
        build_transition(
            "provisional",
            transitioned_at=STARTED_AT.replace(hour=11),
        ),
        db,
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        transition_conversational_diagnostic_session(
            build_transition(
                "cancelled",
                expected_current_status="provisional",
                transitioned_at=STARTED_AT,
            ),
            db,
        )

    assert "prior close" in str(captured.value.__cause__)


@pytest.mark.parametrize("status", ["provisional", "completed", "cancelled"])
def test_rejects_new_session_not_in_progress(db, status):
    setup = build_setup()
    invalid = setup.model_copy(
        update={
            "session": setup.session.model_copy(
                update={"status": status, "completed_at": STARTED_AT}
            )
        }
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(invalid, db)

    assert "start in progress" in str(captured.value.__cause__)
    assert db.query(SessionModel).count() == 0


def test_transition_commits_exactly_once_and_creates_no_profile(
    db,
    monkeypatch,
):
    save_conversational_diagnostic_session_setup(build_setup(), db)
    commits = 0
    original_commit = db.commit

    def counted_commit():
        nonlocal commits
        commits += 1
        return original_commit()

    monkeypatch.setattr(db, "commit", counted_commit)

    transition_conversational_diagnostic_session(
        build_transition("provisional"),
        db,
    )

    assert commits == 1
    assert db.query(InitialProfileModel).count() == 0


def test_transition_commit_failure_rolls_back_state(db, monkeypatch):
    save_conversational_diagnostic_session_setup(build_setup(), db)

    def failing_commit():
        raise SQLAlchemyError("injected transition commit failure")

    monkeypatch.setattr(db, "commit", failing_commit)

    with pytest.raises(ConversationalDiagnosticPersistenceError) as captured:
        transition_conversational_diagnostic_session(
            build_transition("provisional"),
            db,
        )

    assert isinstance(captured.value.__cause__, SQLAlchemyError)
    persisted = db.query(SessionModel).one()
    assert persisted.status == "in_progress"
    assert persisted.completed_at is None


def build_initial_profile(
    *,
    profile_id="profile-one",
    session_id="session-one",
    status="provisional",
    generated_at=STARTED_AT,
    first_lesson_id="lesson-generated-one",
):
    return InitialConversationalProfile(
        profile_id=profile_id,
        diagnostic_session_id=session_id,
        status=status,
        priority_blockage="Needs support to initiate responses",
        target_capacity="Initiate short conversational responses",
        recommended_support_level="minimal",
        relevant_contexts=["travel"],
        recommended_method="direct-english-construction",
        first_lesson_id=first_lesson_id,
        review_criterion="Review after three independent responses",
        evidence_summary="Diagnostic evidence supports this initial plan",
        generated_at=generated_at,
        generator_id="initial-profile-generator",
        generator_version="1.0",
    )


def build_profile_setup(profile, observation_ids):
    return InitialConversationalProfileSetup(
        profile=profile,
        evidences=[
            InitialConversationalProfileEvidence(
                profile_id=profile.profile_id,
                observation_id=observation_id,
            )
            for observation_id in observation_ids
        ],
    )


def persist_provisional_profile_session(db):
    setup = build_setup().model_copy(
        update={"observations": [build_observation()]}
    )
    save_conversational_diagnostic_session_setup(setup, db)
    transition_conversational_diagnostic_session(
        build_transition("provisional"),
        db,
    )
    return setup


def persist_completed_profile_session(db):
    setup = build_completed_transition_setup()
    save_conversational_diagnostic_session_setup(setup, db)
    transition_conversational_diagnostic_session(
        build_transition("completed"),
        db,
    )
    return setup


def test_profile_contracts_preserve_previous_aggregate_compatibility():
    setup = build_setup()

    assert setup.profiles == []


def test_initial_session_creation_rejects_profiles(db):
    setup = build_setup().model_copy(
        update={
            "profiles": [
                build_profile_setup(
                    build_initial_profile(),
                    ["observation-one"],
                )
            ]
        }
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_session_setup(setup, db)

    assert "transitioned" in str(captured.value.__cause__)
    assert db.query(SessionModel).count() == 0


def test_appends_provisional_profile_and_round_trips_exactly(db):
    persist_provisional_profile_session(db)
    profile = build_initial_profile(first_lesson_id="catalog-not-consulted")
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[build_profile_setup(profile, ["observation-one"])],
    )

    saved = save_conversational_diagnostic_profiles(batch, db)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)

    assert saved.profiles == batch.profiles
    assert loaded.profiles == batch.profiles
    assert loaded.profiles[0].profile == profile
    assert loaded.profiles[0].profile.first_lesson_id == "catalog-not-consulted"
    assert db.query(ObservationModel).count() == 1
    assert db.query(SessionModel).one().status == "provisional"


def test_profile_enrichment_rejects_missing_session(db):
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(),
                ["observation-one"],
            )
        ],
    )

    with pytest.raises(DiagnosticReferenceNotFoundError):
        save_conversational_diagnostic_profiles(batch, db)

    assert db.query(InitialProfileModel).count() == 0


def test_appends_confirmed_profile_with_complete_evidence(db):
    setup = persist_completed_profile_session(db)
    profile = build_initial_profile(status="confirmed")
    observation_ids = [
        observation.observation_id
        for observation in reversed(setup.observations)
    ]
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[build_profile_setup(profile, observation_ids)],
    )

    saved = save_conversational_diagnostic_profiles(batch, db)

    expected_order = [
        observation.observation_id for observation in setup.observations
    ]
    assert [
        evidence.observation_id for evidence in saved.profiles[0].evidences
    ] == expected_order
    assert saved.profiles[0].profile == profile


@pytest.mark.parametrize(
    ("session_status", "profile_status"),
    [
        ("in_progress", "provisional"),
        ("cancelled", "provisional"),
        ("provisional", "confirmed"),
        ("completed", "provisional"),
    ],
)
def test_rejects_profile_incompatible_with_persisted_session_status(
    db,
    session_status,
    profile_status,
):
    if session_status == "completed":
        setup = persist_completed_profile_session(db)
    else:
        setup = build_setup().model_copy(
            update={"observations": [build_observation()]}
        )
        save_conversational_diagnostic_session_setup(setup, db)
        if session_status != "in_progress":
            transition_conversational_diagnostic_session(
                build_transition(session_status),
                db,
            )
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(status=profile_status),
                [setup.observations[0].observation_id],
            )
        ],
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_profiles(batch, db)

    assert captured.value.__cause__ is not None
    assert db.query(InitialProfileModel).count() == 0


def test_profiles_are_append_only_and_can_share_observation(db):
    persist_provisional_profile_session(db)
    first = build_profile_setup(
        build_initial_profile(profile_id="profile-b"),
        ["observation-one"],
    )
    second = build_profile_setup(
        build_initial_profile(
            profile_id="profile-a",
            generated_at=STARTED_AT.replace(hour=11),
        ),
        ["observation-one"],
    )

    save_conversational_diagnostic_profiles(
        ConversationalDiagnosticProfilesBatch(
            diagnostic_session_id="session-one",
            profiles=[first],
        ),
        db,
    )
    saved = save_conversational_diagnostic_profiles(
        ConversationalDiagnosticProfilesBatch(
            diagnostic_session_id="session-one",
            profiles=[second],
        ),
        db,
    )

    assert [item.profile.profile_id for item in saved.profiles] == [
        "profile-b",
        "profile-a",
    ]
    assert db.query(InitialProfileModel).count() == 2
    assert db.query(ProfileEvidenceModel).count() == 2

    with pytest.raises(DiagnosticPersistenceInvariantError):
        save_conversational_diagnostic_profiles(
            ConversationalDiagnosticProfilesBatch(
                diagnostic_session_id="session-one",
                profiles=[first],
            ),
            db,
        )
    assert db.query(InitialProfileModel).count() == 2


def test_profiles_with_same_timestamp_are_recovered_by_profile_id(db):
    persist_provisional_profile_session(db)
    profile_b = build_profile_setup(
        build_initial_profile(profile_id="profile-b"),
        ["observation-one"],
    )
    profile_a = build_profile_setup(
        build_initial_profile(profile_id="profile-a"),
        ["observation-one"],
    )

    saved = save_conversational_diagnostic_profiles(
        ConversationalDiagnosticProfilesBatch(
            diagnostic_session_id="session-one",
            profiles=[profile_b, profile_a],
        ),
        db,
    )

    assert [item.profile.profile_id for item in saved.profiles] == [
        "profile-a",
        "profile-b",
    ]


def test_profile_batch_rejects_duplicate_profile_and_evidence_ids():
    profile = build_initial_profile()
    item = build_profile_setup(profile, ["observation-one"])

    with pytest.raises(ValidationError):
        ConversationalDiagnosticProfilesBatch(
            diagnostic_session_id="session-one",
            profiles=[item, item],
        )
    with pytest.raises(ValidationError):
        InitialConversationalProfileSetup(
            profile=profile,
            evidences=[
                InitialConversationalProfileEvidence(
                    profile_id=profile.profile_id,
                    observation_id="observation-one",
                ),
                InitialConversationalProfileEvidence(
                    profile_id=profile.profile_id,
                    observation_id="observation-one",
                ),
            ],
        )


def test_profile_contract_rejects_empty_or_crossed_evidence():
    profile = build_initial_profile()

    with pytest.raises(ValidationError):
        InitialConversationalProfileSetup(profile=profile, evidences=[])
    with pytest.raises(ValidationError):
        InitialConversationalProfileSetup(
            profile=profile,
            evidences=[
                InitialConversationalProfileEvidence(
                    profile_id="profile-other",
                    observation_id="observation-one",
                )
            ],
        )


def test_profile_rejects_missing_and_cross_session_observations(db):
    persist_provisional_profile_session(db)
    missing_batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(),
                ["observation-missing"],
            )
        ],
    )
    with pytest.raises(DiagnosticReferenceNotFoundError):
        save_conversational_diagnostic_profiles(missing_batch, db)

    other = build_setup("two").model_copy(
        update={
            "observations": [
                build_observation(
                    observation_id="observation-two",
                    session_id="session-two",
                    activity_id="activity-two-1",
                )
            ]
        }
    )
    save_conversational_diagnostic_session_setup(other, db)
    crossed_batch = missing_batch.model_copy(
        update={
            "profiles": [
                build_profile_setup(
                    build_initial_profile(profile_id="profile-crossed"),
                    ["observation-two"],
                )
            ]
        }
    )
    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_profiles(crossed_batch, db)

    assert captured.value.__cause__ is not None
    assert db.query(InitialProfileModel).count() == 0


def test_confirmed_profile_rejects_incomplete_evidence(db):
    setup = persist_completed_profile_session(db)
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(status="confirmed"),
                [setup.observations[0].observation_id],
            )
        ],
    )

    with pytest.raises(DiagnosticPersistenceInvariantError) as captured:
        save_conversational_diagnostic_profiles(batch, db)

    assert "Confirmed profile" in str(captured.value.__cause__)
    assert db.query(InitialProfileModel).count() == 0


def test_profile_write_commits_exactly_once(db, monkeypatch):
    persist_provisional_profile_session(db)
    commits = 0
    original_commit = db.commit

    def counted_commit():
        nonlocal commits
        commits += 1
        return original_commit()

    monkeypatch.setattr(db, "commit", counted_commit)
    save_conversational_diagnostic_profiles(
        ConversationalDiagnosticProfilesBatch(
            diagnostic_session_id="session-one",
            profiles=[
                build_profile_setup(
                    build_initial_profile(),
                    ["observation-one"],
                )
            ],
        ),
        db,
    )

    assert commits == 1


@pytest.mark.parametrize("failing_flush_call", [1, 2])
def test_profile_flush_failure_rolls_back_profiles_and_evidence(
    db,
    monkeypatch,
    failing_flush_call,
):
    persist_provisional_profile_session(db)
    calls = 0
    original_flush = db.flush

    def failing_flush(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == failing_flush_call:
            raise SQLAlchemyError("injected profile flush failure")
        return original_flush(*args, **kwargs)

    monkeypatch.setattr(db, "flush", failing_flush)
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(),
                ["observation-one"],
            )
        ],
    )

    with pytest.raises(ConversationalDiagnosticPersistenceError) as captured:
        save_conversational_diagnostic_profiles(batch, db)

    assert isinstance(captured.value.__cause__, SQLAlchemyError)
    assert db.query(InitialProfileModel).count() == 0
    assert db.query(ProfileEvidenceModel).count() == 0


def test_profile_commit_failure_rolls_back_without_mutating_history(
    db,
    monkeypatch,
):
    persist_provisional_profile_session(db)

    def failing_commit():
        raise SQLAlchemyError("injected profile commit failure")

    monkeypatch.setattr(db, "commit", failing_commit)
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(),
                ["observation-one"],
            )
        ],
    )

    with pytest.raises(ConversationalDiagnosticPersistenceError):
        save_conversational_diagnostic_profiles(batch, db)

    assert db.query(InitialProfileModel).count() == 0
    assert db.query(ProfileEvidenceModel).count() == 0
    assert db.query(ObservationModel).one().description == (
        "Observable diagnostic evidence"
    )
    assert db.query(SessionModel).one().status == "provisional"


def test_get_with_profiles_does_not_commit_or_use_lazy_loading(
    db,
    monkeypatch,
):
    persist_provisional_profile_session(db)
    batch = ConversationalDiagnosticProfilesBatch(
        diagnostic_session_id="session-one",
        profiles=[
            build_profile_setup(
                build_initial_profile(),
                ["observation-one"],
            )
        ],
    )
    save_conversational_diagnostic_profiles(batch, db)

    def forbidden_commit():
        raise AssertionError("get must not commit")

    monkeypatch.setattr(db, "commit", forbidden_commit)
    loaded = get_conversational_diagnostic_session_setup("session-one", db)
    db.expunge_all()

    assert loaded.profiles == batch.profiles
    assert not hasattr(loaded.profiles[0].profile, "progress")
    assert not hasattr(loaded.profiles[0].profile, "mastery")
