import os
import subprocess
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission,
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticActivityProduction,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticObservationEvaluation,
    ConversationalDiagnosticSession,
    ConversationalDiagnosticSupportUsage,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
    LearnerProduction,
    ProductionEvaluationResult,
)


@pytest.fixture()
def db():
    """Create an isolated store with relational checks enabled.

    Crea un almacén aislado con comprobaciones relacionales activas.
    """
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


def add_session_tree(db, suffix: str):
    now = datetime.now(UTC)
    session = ConversationalDiagnosticSession(
        diagnostic_session_id=f"session-{suffix}",
        user_id=f"user-{suffix}",
        age_profile="adult",
        status="in_progress",
        started_at=now,
    )
    context = ConversationalDiagnosticContext(
        context_id=f"context-{suffix}",
        diagnostic_session_id=session.diagnostic_session_id,
        usual_languages=["Spanish"],
        previous_english_contact="School",
        general_interests=["travel"],
        learning_goals=["conversation"],
        autonomy_level="independent",
        responsible_adult_present=None,
        audio_authorized=True,
    )
    activity = ConversationalDiagnosticActivity(
        activity_id=f"activity-{suffix}",
        diagnostic_session_id=session.diagnostic_session_id,
        context_id=context.context_id,
        prompt_id=f"prompt-{suffix}",
        stage="initial_response",
        communicative_intention="Introduce yourself",
        modality="text",
        expected_evidence_type="spontaneous_production",
        available_supports=["visual"],
        sequence_order=1,
    )
    db.add(session)
    db.flush()
    db.add(context)
    db.flush()
    db.add(activity)
    db.commit()
    return session, context, activity


def add_production(db, prompt_id: str):
    submission = ConversationProductionSubmission(
        user_id="learner",
        level_id="diagnostic",
        unit_id="diagnostic",
        lesson_id="diagnostic",
        conversation_id="diagnostic",
    )
    db.add(submission)
    db.flush()
    production = LearnerProduction(
        submission_id=submission.id,
        prompt_id=prompt_id,
        turn_id="diagnostic-turn",
        modality="text",
        response_text="My name is Ana.",
    )
    db.add(production)
    db.commit()
    return production


def own_production(db, session, activity, production):
    ownership = ConversationalDiagnosticActivityProduction(
        production_id=production.id,
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        prompt_id=activity.prompt_id,
    )
    db.add(ownership)
    db.commit()
    return ownership


def add_evaluation(db, production):
    evaluation = ProductionEvaluationResult(
        production_id=production.id,
        criterion_id="diagnostic-continuity",
        status="passed",
        score=None,
        evaluator_id="technical-evaluator",
        evaluator_version="1.0",
        evaluated_at=datetime.now(UTC),
    )
    db.add(evaluation)
    db.commit()
    return evaluation


def add_observation(db, session, activity, production, suffix="linked"):
    observation = ConversationalDiagnosticObservation(
        observation_id=f"observation-{suffix}",
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        production_id=production.id,
        dimension="response_initiation",
        evidence_role="strength",
        description="The learner initiated a direct response.",
        support_level="minimal",
        observer_id="observer",
        observer_version="1.0",
        observed_at=datetime.now(UTC),
    )
    db.add(observation)
    db.commit()
    return observation


def test_models_keep_diagnostic_layers_separate():
    """Protect the boundary between evidence and pedagogical decisions.

    Protege la frontera entre evidencia y decisiones pedagógicas.
    """
    observation = ConversationalDiagnosticObservation.__table__
    profile = InitialConversationalProfile.__table__
    forbidden = {"progress", "mastery", "score", "correct", "feedback"}

    assert forbidden.isdisjoint(observation.columns)
    assert forbidden.isdisjoint(profile.columns)
    assert "evaluation_result_ids" not in observation.columns
    assert (
        ConversationalDiagnosticObservationEvaluation.__table__.name
        == "conversational_diagnostic_observation_evaluations"
    )
    assert "relevant_contexts" in profile.columns


def test_cross_session_activity_context_is_rejected(db):
    _, first_context, _ = add_session_tree(db, "one")
    second_session, _, _ = add_session_tree(db, "two")
    db.add(
        ConversationalDiagnosticActivity(
            activity_id="cross-session",
            diagnostic_session_id=second_session.diagnostic_session_id,
            context_id=first_context.context_id,
            prompt_id="cross-prompt",
            stage="initial_response",
            communicative_intention="Cross session",
            modality="text",
            expected_evidence_type="spontaneous_production",
            available_supports=[],
            sequence_order=2,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_support_and_observation_remain_separate_and_traceable(db):
    session, _, activity = add_session_tree(db, "trace")
    production = add_production(db, activity.prompt_id)
    own_production(db, session, activity, production)
    support = ConversationalDiagnosticSupportUsage(
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        production_id=production.id,
        support_type="visual",
        support_level="minimal",
        sequence_order=1,
        provided_at=datetime.now(UTC),
        withdrawn_afterward=True,
    )
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-trace",
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        production_id=production.id,
        dimension="response_initiation",
        evidence_role="strength",
        description="The learner initiated a direct response.",
        support_level="minimal",
        observer_id="observer",
        observer_version="1.0",
        observed_at=datetime.now(UTC),
    )
    db.add_all([support, observation])
    db.commit()

    assert support.id > 0
    assert observation.production_id == production.id


def test_profile_history_is_accumulative(db):
    session, _, activity = add_session_tree(db, "history")
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-history",
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        dimension="listening_comprehension",
        evidence_role="development_need",
        description="The exchange stopped after one turn.",
        support_level="moderate",
        observer_id="observer",
        observer_version="1.0",
        observed_at=datetime.now(UTC),
    )
    db.add(observation)
    db.flush()

    profiles = []
    for version, status in (("1.0", "provisional"), ("1.1", "confirmed")):
        profile = InitialConversationalProfile(
            profile_id=f"profile-{version}",
            diagnostic_session_id=session.diagnostic_session_id,
            status=status,
            priority_blockage="Conversational continuity",
            target_capacity="Sustain a short exchange",
            recommended_support_level="moderate",
            relevant_contexts=["travel"],
            recommended_method="direct-english-construction",
            first_lesson_id="lesson-1",
            review_criterion="Completes three connected turns",
            evidence_summary="One observed continuity interruption",
            generated_at=datetime.now(UTC),
            generator_id="profile-generator",
            generator_version=version,
        )
        profiles.append(profile)
        db.add(profile)
        db.flush()
        db.add(
            InitialConversationalProfileEvidence(
                diagnostic_session_id=session.diagnostic_session_id,
                profile_id=profile.profile_id,
                observation_id=observation.observation_id,
            )
        )
    db.commit()

    assert db.query(InitialConversationalProfile).count() == 2
    assert [item.generator_version for item in profiles] == ["1.0", "1.1"]
    assert db.query(InitialConversationalProfileEvidence).count() == 2


def test_profile_evidence_rejects_cross_session_observation(db):
    first_session, _, first_activity = add_session_tree(db, "evidence-one")
    second_session, _, _ = add_session_tree(db, "evidence-two")
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-one",
        diagnostic_session_id=first_session.diagnostic_session_id,
        activity_id=first_activity.activity_id,
        dimension="listening_comprehension",
        evidence_role="strength",
        description="Connected response.",
        support_level="none",
        observer_id="observer",
        observer_version="1.0",
        observed_at=datetime.now(UTC),
    )
    profile = InitialConversationalProfile(
        profile_id="profile-two",
        diagnostic_session_id=second_session.diagnostic_session_id,
        status="provisional",
        priority_blockage="Response initiation",
        target_capacity="Initiate a response",
        recommended_support_level="minimal",
        relevant_contexts=["travel"],
        recommended_method="direct-english-construction",
        first_lesson_id="lesson-1",
        review_criterion="Initiates independently",
        evidence_summary="Provisional evidence",
        generated_at=datetime.now(UTC),
        generator_id="profile-generator",
        generator_version="1.0",
    )
    db.add_all([observation, profile])
    db.commit()
    db.add(
        InitialConversationalProfileEvidence(
            diagnostic_session_id=second_session.diagnostic_session_id,
            profile_id=profile.profile_id,
            observation_id=observation.observation_id,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_production_ownership_rejects_incompatible_activity(db):
    session, _, activity = add_session_tree(db, "wrong-prompt")
    production = add_production(db, "another-prompt")
    db.add(
        ConversationalDiagnosticActivityProduction(
            production_id=production.id,
            diagnostic_session_id=session.diagnostic_session_id,
            activity_id=activity.activity_id,
            prompt_id=activity.prompt_id,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_production_cannot_be_reused_by_two_activities(db):
    session, context, first_activity = add_session_tree(db, "exclusive")
    second_activity = ConversationalDiagnosticActivity(
        activity_id="activity-exclusive-two",
        diagnostic_session_id=session.diagnostic_session_id,
        context_id=context.context_id,
        prompt_id=first_activity.prompt_id,
        stage="initial_response",
        communicative_intention="Repeat introduction",
        modality="text",
        expected_evidence_type="spontaneous_production",
        available_supports=[],
        sequence_order=2,
    )
    db.add(second_activity)
    db.commit()
    production = add_production(db, first_activity.prompt_id)
    own_production(db, session, first_activity, production)
    db.add(
        ConversationalDiagnosticActivityProduction(
            production_id=production.id,
            diagnostic_session_id=session.diagnostic_session_id,
            activity_id=second_activity.activity_id,
            prompt_id=second_activity.prompt_id,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_observation_evaluation_rejects_unknown_evaluation(db):
    session, _, activity = add_session_tree(db, "unknown-evaluation")
    production = add_production(db, activity.prompt_id)
    own_production(db, session, activity, production)
    observation = add_observation(db, session, activity, production, "unknown")
    db.add(
        ConversationalDiagnosticObservationEvaluation(
            diagnostic_session_id=session.diagnostic_session_id,
            observation_id=observation.observation_id,
            evaluation_result_id=999999,
            production_id=production.id,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_observation_evaluation_rejects_another_production(db):
    session, _, activity = add_session_tree(db, "wrong-evaluation")
    production = add_production(db, activity.prompt_id)
    another_production = add_production(db, "unrelated-prompt")
    evaluation = add_evaluation(db, another_production)
    own_production(db, session, activity, production)
    observation = add_observation(db, session, activity, production, "wrong")
    db.add(
        ConversationalDiagnosticObservationEvaluation(
            diagnostic_session_id=session.diagnostic_session_id,
            observation_id=observation.observation_id,
            evaluation_result_id=evaluation.id,
            production_id=production.id,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_observation_evaluation_rejects_duplicate(db):
    session, _, activity = add_session_tree(db, "duplicate-evaluation")
    production = add_production(db, activity.prompt_id)
    evaluation = add_evaluation(db, production)
    own_production(db, session, activity, production)
    observation = add_observation(db, session, activity, production, "duplicate")
    links = [
        ConversationalDiagnosticObservationEvaluation(
            diagnostic_session_id=session.diagnostic_session_id,
            observation_id=observation.observation_id,
            evaluation_result_id=evaluation.id,
            production_id=production.id,
        )
        for _ in range(2)
    ]
    db.add_all(links)

    with pytest.raises(IntegrityError):
        db.commit()


def test_production_dependent_observation_requires_production(db):
    session, _, activity = add_session_tree(db, "required-production")
    db.add(
        ConversationalDiagnosticObservation(
            observation_id="observation-required-production",
            diagnostic_session_id=session.diagnostic_session_id,
            activity_id=activity.activity_id,
            production_id=None,
            dimension="continuity",
            evidence_role="development_need",
            description="Continuity evidence requires a production.",
            support_level="none",
            observer_id="observer",
            observer_version="1.0",
            observed_at=datetime.now(UTC),
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()


def test_non_production_observation_is_accepted(db):
    session, _, activity = add_session_tree(db, "no-production")
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-no-production",
        diagnostic_session_id=session.diagnostic_session_id,
        activity_id=activity.activity_id,
        production_id=None,
        dimension="listening_comprehension",
        evidence_role="strength",
        description="The learner selected the matching meaning.",
        support_level="none",
        observer_id="observer",
        observer_version="1.0",
        observed_at=datetime.now(UTC),
    )
    db.add(observation)
    db.commit()

    assert observation.production_id is None


def test_production_dependent_observation_accepts_valid_ownership(db):
    session, _, activity = add_session_tree(db, "valid-production")
    production = add_production(db, activity.prompt_id)
    own_production(db, session, activity, production)

    observation = add_observation(
        db,
        session,
        activity,
        production,
        "valid-production",
    )

    assert observation.dimension == "response_initiation"
    assert observation.production_id == production.id


def test_alembic_upgrade_and_downgrade_in_isolated_database(tmp_path):
    """Exercise both migration directions outside the real database.

    Ejercita ambas direcciones fuera de la base de datos real.
    """
    database_path = tmp_path / "diagnostic-migration.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"

    upgrade = subprocess.run(
        [".venv/bin/alembic", "upgrade", "head"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert upgrade.returncode == 0, upgrade.stderr

    downgrade = subprocess.run(
        [".venv/bin/alembic", "downgrade", "f81a78f8c1c4"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert downgrade.returncode == 0, downgrade.stderr
