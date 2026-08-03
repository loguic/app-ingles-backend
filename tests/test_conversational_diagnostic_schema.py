from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
)


STARTED_AT = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)
COMPLETED_AT = STARTED_AT + timedelta(minutes=15)


def test_create_in_progress_diagnostic_session() -> None:
    session = ConversationalDiagnosticSession(
        diagnostic_session_id="diagnostic-001",
        user_id="user-001",
        age_profile="9-12",
        started_at=STARTED_AT,
    )

    assert session.status == "in_progress"
    assert session.completed_at is None


@pytest.mark.parametrize(
    "status",
    ["provisional", "completed", "cancelled"],
)
def test_create_finished_diagnostic_session(status: str) -> None:
    session = ConversationalDiagnosticSession(
        diagnostic_session_id="diagnostic-001",
        user_id="user-001",
        age_profile="9-12",
        status=status,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
    )

    assert session.status == status
    assert session.completed_at == COMPLETED_AT


def test_reject_completed_at_for_in_progress_session() -> None:
    with pytest.raises(
        ValidationError,
        match="In-progress diagnostic session cannot define completed_at",
    ):
        ConversationalDiagnosticSession(
            diagnostic_session_id="diagnostic-001",
            user_id="user-001",
            age_profile="9-12",
            started_at=STARTED_AT,
            completed_at=COMPLETED_AT,
        )


@pytest.mark.parametrize(
    "status",
    ["provisional", "completed", "cancelled"],
)
def test_reject_missing_completed_at_for_finished_session(
    status: str,
) -> None:
    with pytest.raises(
        ValidationError,
        match="Finished diagnostic session requires completed_at",
    ):
        ConversationalDiagnosticSession(
            diagnostic_session_id="diagnostic-001",
            user_id="user-001",
            age_profile="9-12",
            status=status,
            started_at=STARTED_AT,
        )


def test_reject_completion_before_session_start() -> None:
    with pytest.raises(
        ValidationError,
        match="Diagnostic session completed_at cannot precede started_at",
    ):
        ConversationalDiagnosticSession(
            diagnostic_session_id="diagnostic-001",
            user_id="user-001",
            age_profile="9-12",
            status="completed",
            started_at=STARTED_AT,
            completed_at=STARTED_AT - timedelta(seconds=1),
        )


def test_reject_unknown_age_profile() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticSession(
            diagnostic_session_id="diagnostic-001",
            user_id="user-001",
            age_profile="unknown",
            started_at=STARTED_AT,
        )

def test_create_diagnostic_context() -> None:
    context = ConversationalDiagnosticContext(
        context_id="context-001",
        diagnostic_session_id="diagnostic-001",
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals", "science"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=True,
    )

    assert context.usual_languages == ["Spanish"]
    assert context.general_interests == ["animals", "science"]
    assert context.audio_authorized is True


@pytest.mark.parametrize(
    ("field_name", "values", "message"),
    [
        (
            "usual_languages",
            ["Spanish", "Spanish"],
            "usual_languages must contain unique values",
        ),
        (
            "general_interests",
            ["science", "science"],
            "general_interests must contain unique values",
        ),
        (
            "learning_goals",
            ["speak", "speak"],
            "learning_goals must contain unique values",
        ),
    ],
)
def test_reject_duplicate_diagnostic_context_values(
    field_name: str,
    values: list[str],
    message: str,
) -> None:
    data = {
        "context_id": "context-001",
        "diagnostic_session_id": "diagnostic-001",
        "usual_languages": ["Spanish"],
        "previous_english_contact": "School classes",
        "general_interests": [],
        "learning_goals": [],
        "autonomy_level": "developing",
    }
    data[field_name] = values

    with pytest.raises(ValidationError, match=message):
        ConversationalDiagnosticContext(**data)


@pytest.mark.parametrize(
    ("field_name", "values", "message"),
    [
        (
            "usual_languages",
            [" "],
            "usual_languages cannot contain blank values",
        ),
        (
            "general_interests",
            ["animals", " "],
            "general_interests cannot contain blank values",
        ),
        (
            "learning_goals",
            [" "],
            "learning_goals cannot contain blank values",
        ),
    ],
)
def test_reject_blank_diagnostic_context_values(
    field_name: str,
    values: list[str],
    message: str,
) -> None:
    data = {
        "context_id": "context-001",
        "diagnostic_session_id": "diagnostic-001",
        "usual_languages": ["Spanish"],
        "previous_english_contact": "School classes",
        "general_interests": [],
        "learning_goals": [],
        "autonomy_level": "developing",
    }
    data[field_name] = values

    with pytest.raises(ValidationError, match=message):
        ConversationalDiagnosticContext(**data)


def test_reject_blank_previous_english_contact() -> None:
    with pytest.raises(
        ValidationError,
        match="previous_english_contact cannot be blank",
    ):
        ConversationalDiagnosticContext(
            context_id="context-001",
            diagnostic_session_id="diagnostic-001",
            usual_languages=["Spanish"],
            previous_english_contact=" ",
            autonomy_level="supported",
        )


def test_reject_empty_usual_languages() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticContext(
            context_id="context-001",
            diagnostic_session_id="diagnostic-001",
            usual_languages=[],
            previous_english_contact="No previous contact",
            autonomy_level="supported",
        )


def test_reject_unknown_autonomy_level() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticContext(
            context_id="context-001",
            diagnostic_session_id="diagnostic-001",
            usual_languages=["Spanish"],
            previous_english_contact="School classes",
            autonomy_level="unknown",
        )

def test_create_diagnostic_activity() -> None:
    activity = ConversationalDiagnosticActivity(
        activity_id="activity-001",
        diagnostic_session_id="diagnostic-001",
        context_id="context-001",
        prompt_id="diagnostic-prompt-001",
        stage="initial_response",
        communicative_intention="Describe a favorite animal",
        modality="voice",
        expected_evidence_type="spontaneous_production",
        available_supports=["visual", "keyword"],
        sequence_order=1,
    )

    assert activity.stage == "initial_response"
    assert activity.available_supports == ["visual", "keyword"]
    assert activity.transfer_variant_id is None


def test_create_transfer_activity() -> None:
    activity = ConversationalDiagnosticActivity(
        activity_id="activity-002",
        diagnostic_session_id="diagnostic-001",
        context_id="context-001",
        prompt_id="diagnostic-prompt-001",
        stage="transfer",
        communicative_intention="Describe a different animal",
        modality="voice",
        expected_evidence_type="transfer",
        available_supports=["visual"],
        transfer_variant_id="variant-001",
        sequence_order=2,
    )

    assert activity.stage == "transfer"
    assert activity.transfer_variant_id == "variant-001"


def test_reject_blank_communicative_intention() -> None:
    with pytest.raises(
        ValidationError,
        match="communicative_intention cannot be blank",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="initial_response",
            communicative_intention=" ",
            modality="voice",
            expected_evidence_type="spontaneous_production",
            sequence_order=1,
        )


def test_reject_duplicate_available_supports() -> None:
    with pytest.raises(
        ValidationError,
        match="available_supports must contain unique values",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="guided_construction",
            communicative_intention="Build one supported sentence",
            modality="voice",
            expected_evidence_type="supported_production",
            available_supports=["pattern", "pattern"],
            sequence_order=1,
        )


def test_reject_transfer_activity_without_variant() -> None:
    with pytest.raises(
        ValidationError,
        match="Transfer activity requires transfer_variant_id",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="transfer",
            communicative_intention="Respond to a changed situation",
            modality="voice",
            expected_evidence_type="transfer",
            sequence_order=1,
        )


def test_reject_transfer_variant_outside_transfer_activity() -> None:
    with pytest.raises(
        ValidationError,
        match="Only transfer activity can define transfer_variant_id",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="initial_response",
            communicative_intention="Give an initial response",
            modality="voice",
            expected_evidence_type="spontaneous_production",
            transfer_variant_id="variant-001",
            sequence_order=1,
        )


def test_reject_transfer_evidence_outside_transfer_activity() -> None:
    with pytest.raises(
        ValidationError,
        match="Transfer evidence requires transfer activity",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="connected_exchange",
            communicative_intention="Continue the conversation",
            modality="voice",
            expected_evidence_type="transfer",
            sequence_order=1,
        )


def test_reject_non_positive_activity_sequence_order() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="adaptation",
            communicative_intention="Become familiar with the activity",
            modality="selection",
            expected_evidence_type="motivating_context",
            sequence_order=0,
        )


def test_reject_unknown_diagnostic_activity_stage() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="diagnostic-prompt-001",
            stage="unknown",
            communicative_intention="Complete one activity",
            modality="voice",
            expected_evidence_type="spontaneous_production",
            sequence_order=1,
        )

def test_create_no_support_usage() -> None:
    usage = DiagnosticSupportUsage(
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-001",
        production_id=1,
        support_type="none",
        support_level="none",
        sequence_order=1,
        provided_at=STARTED_AT,
    )

    assert usage.support_type == "none"
    assert usage.support_level == "none"
    assert usage.withdrawn_afterward is False


def test_create_used_support() -> None:
    usage = DiagnosticSupportUsage(
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-001",
        production_id=1,
        support_type="visual",
        support_level="minimal",
        sequence_order=1,
        provided_at=STARTED_AT,
        withdrawn_afterward=True,
    )

    assert usage.support_type == "visual"
    assert usage.support_level == "minimal"
    assert usage.withdrawn_afterward is True


def test_reject_no_support_with_non_none_level() -> None:
    with pytest.raises(
        ValidationError,
        match="No-support usage requires none support_level",
    ):
        DiagnosticSupportUsage(
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=1,
            support_type="none",
            support_level="minimal",
            sequence_order=1,
            provided_at=STARTED_AT,
        )


def test_reject_used_support_with_none_level() -> None:
    with pytest.raises(
        ValidationError,
        match="Used support requires a non-none support_level",
    ):
        DiagnosticSupportUsage(
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=1,
            support_type="keyword",
            support_level="none",
            sequence_order=1,
            provided_at=STARTED_AT,
        )


def test_reject_no_support_marked_as_withdrawn() -> None:
    with pytest.raises(
        ValidationError,
        match="No-support usage cannot be marked as withdrawn",
    ):
        DiagnosticSupportUsage(
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=1,
            support_type="none",
            support_level="none",
            sequence_order=1,
            provided_at=STARTED_AT,
            withdrawn_afterward=True,
        )


def test_reject_non_positive_support_production_id() -> None:
    with pytest.raises(ValidationError):
        DiagnosticSupportUsage(
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=0,
            support_type="visual",
            support_level="minimal",
            sequence_order=1,
            provided_at=STARTED_AT,
        )


def test_reject_non_positive_support_sequence_order() -> None:
    with pytest.raises(ValidationError):
        DiagnosticSupportUsage(
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=1,
            support_type="visual",
            support_level="minimal",
            sequence_order=0,
            provided_at=STARTED_AT,
        )

def test_create_diagnostic_observation() -> None:
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-001",
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-001",
        production_id=1,
        evaluation_result_ids=[2, 3],
        dimension="direct_english_construction",
        description=(
            "Built the initial sentence without translation support."
        ),
        support_level="minimal",
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )

    assert observation.production_id == 1
    assert observation.evaluation_result_ids == [2, 3]
    assert observation.dimension == "direct_english_construction"


def test_create_observation_without_production() -> None:
    observation = ConversationalDiagnosticObservation(
        observation_id="observation-001",
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-001",
        dimension="listening_comprehension",
        description="Followed the spoken instruction with visual support.",
        support_level="minimal",
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )

    assert observation.production_id is None
    assert observation.evaluation_result_ids == []


@pytest.mark.parametrize(
    "field_name",
    [
        "observation_id",
        "diagnostic_session_id",
        "activity_id",
        "description",
        "observer_id",
        "observer_version",
    ],
)
def test_reject_blank_diagnostic_observation_text_field(
    field_name: str,
) -> None:
    data = {
        "observation_id": "observation-001",
        "diagnostic_session_id": "diagnostic-001",
        "activity_id": "activity-001",
        "dimension": "oral_production",
        "description": "Produced one understandable sentence.",
        "support_level": "none",
        "observer_id": "deterministic-diagnostic-observer",
        "observer_version": "1.0",
        "observed_at": STARTED_AT,
    }
    data[field_name] = " "

    with pytest.raises(
        ValidationError,
        match=field_name + " cannot be blank",
    ):
        ConversationalDiagnosticObservation(**data)


def test_reject_non_positive_evaluation_result_id() -> None:
    with pytest.raises(
        ValidationError,
        match="evaluation_result_ids must contain positive values",
    ):
        ConversationalDiagnosticObservation(
            observation_id="observation-001",
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            evaluation_result_ids=[0],
            dimension="intelligibility",
            description="The spoken message was understandable.",
            support_level="none",
            observer_id="deterministic-diagnostic-observer",
            observer_version="1.0",
            observed_at=STARTED_AT,
        )


def test_reject_duplicate_evaluation_result_ids() -> None:
    with pytest.raises(
        ValidationError,
        match="evaluation_result_ids must contain unique values",
    ):
        ConversationalDiagnosticObservation(
            observation_id="observation-001",
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            evaluation_result_ids=[2, 2],
            dimension="intelligibility",
            description="The spoken message was understandable.",
            support_level="none",
            observer_id="deterministic-diagnostic-observer",
            observer_version="1.0",
            observed_at=STARTED_AT,
        )


def test_reject_non_positive_observation_production_id() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticObservation(
            observation_id="observation-001",
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            production_id=0,
            dimension="oral_production",
            description="Produced one sentence.",
            support_level="none",
            observer_id="deterministic-diagnostic-observer",
            observer_version="1.0",
            observed_at=STARTED_AT,
        )


def test_reject_unknown_diagnostic_dimension() -> None:
    with pytest.raises(ValidationError):
        ConversationalDiagnosticObservation(
            observation_id="observation-001",
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-001",
            dimension="unknown",
            description="Observed one response.",
            support_level="none",
            observer_id="deterministic-diagnostic-observer",
            observer_version="1.0",
            observed_at=STARTED_AT,
        )

def test_create_initial_conversational_profile() -> None:
    profile = InitialConversationalProfile(
        profile_id="profile-001",
        diagnostic_session_id="diagnostic-001",
        status="confirmed",
        priority_blockage="Needs support to expand oral responses.",
        target_capacity="Build and extend one connected response.",
        recommended_support_level="minimal",
        relevant_contexts=["animals", "science"],
        recommended_method="direct-english-construction",
        first_experience_id="experience-animals-001",
        review_criterion=(
            "Respond to one new variation with less support."
        ),
        evidence_summary=(
            "Produced connected responses with minimal visual support."
        ),
        generated_at=COMPLETED_AT,
        generator_id="deterministic-profile-generator",
        generator_version="1.0",
    )

    assert profile.status == "confirmed"
    assert profile.relevant_contexts == ["animals", "science"]
    assert profile.recommended_support_level == "minimal"


def test_create_provisional_initial_profile() -> None:
    profile = InitialConversationalProfile(
        profile_id="profile-001",
        diagnostic_session_id="diagnostic-001",
        status="provisional",
        priority_blockage="Transfer evidence is still missing.",
        target_capacity="Reuse one pattern in a changed situation.",
        recommended_support_level="moderate",
        relevant_contexts=["adventures"],
        recommended_method="direct-english-construction",
        first_experience_id="experience-adventure-001",
        review_criterion="Complete one transfer activity.",
        evidence_summary="Available evidence is incomplete.",
        generated_at=COMPLETED_AT,
        generator_id="deterministic-profile-generator",
        generator_version="1.0",
    )

    assert profile.status == "provisional"


@pytest.mark.parametrize(
    "field_name",
    [
        "profile_id",
        "diagnostic_session_id",
        "priority_blockage",
        "target_capacity",
        "recommended_method",
        "first_experience_id",
        "review_criterion",
        "evidence_summary",
        "generator_id",
        "generator_version",
    ],
)
def test_reject_blank_initial_profile_text_field(
    field_name: str,
) -> None:
    data = {
        "profile_id": "profile-001",
        "diagnostic_session_id": "diagnostic-001",
        "status": "confirmed",
        "priority_blockage": "Needs support to expand responses.",
        "target_capacity": "Build one connected response.",
        "recommended_support_level": "minimal",
        "relevant_contexts": ["animals"],
        "recommended_method": "direct-english-construction",
        "first_experience_id": "experience-animals-001",
        "review_criterion": "Respond with less support.",
        "evidence_summary": "Evidence from several observations.",
        "generated_at": COMPLETED_AT,
        "generator_id": "deterministic-profile-generator",
        "generator_version": "1.0",
    }
    data[field_name] = " "

    with pytest.raises(
        ValidationError,
        match=field_name + " cannot be blank",
    ):
        InitialConversationalProfile(**data)


def test_reject_blank_relevant_context() -> None:
    with pytest.raises(
        ValidationError,
        match="relevant_contexts cannot contain blank values",
    ):
        InitialConversationalProfile(
            profile_id="profile-001",
            diagnostic_session_id="diagnostic-001",
            status="provisional",
            priority_blockage="More evidence is required.",
            target_capacity="Produce one supported response.",
            recommended_support_level="moderate",
            relevant_contexts=["animals", " "],
            recommended_method="direct-english-construction",
            first_experience_id="experience-animals-001",
            review_criterion="Complete one additional activity.",
            evidence_summary="Evidence remains incomplete.",
            generated_at=COMPLETED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )


def test_reject_duplicate_relevant_contexts() -> None:
    with pytest.raises(
        ValidationError,
        match="relevant_contexts must contain unique values",
    ):
        InitialConversationalProfile(
            profile_id="profile-001",
            diagnostic_session_id="diagnostic-001",
            status="confirmed",
            priority_blockage="Needs support to expand responses.",
            target_capacity="Build one connected response.",
            recommended_support_level="minimal",
            relevant_contexts=["animals", "animals"],
            recommended_method="direct-english-construction",
            first_experience_id="experience-animals-001",
            review_criterion="Respond with less support.",
            evidence_summary="Evidence from several observations.",
            generated_at=COMPLETED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )


def test_reject_empty_relevant_contexts() -> None:
    with pytest.raises(ValidationError):
        InitialConversationalProfile(
            profile_id="profile-001",
            diagnostic_session_id="diagnostic-001",
            status="provisional",
            priority_blockage="More evidence is required.",
            target_capacity="Produce one supported response.",
            recommended_support_level="moderate",
            relevant_contexts=[],
            recommended_method="direct-english-construction",
            first_experience_id="experience-animals-001",
            review_criterion="Complete one additional activity.",
            evidence_summary="Evidence remains incomplete.",
            generated_at=COMPLETED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )


def test_reject_unknown_initial_profile_status() -> None:
    with pytest.raises(ValidationError):
        InitialConversationalProfile(
            profile_id="profile-001",
            diagnostic_session_id="diagnostic-001",
            status="unknown",
            priority_blockage="More evidence is required.",
            target_capacity="Produce one supported response.",
            recommended_support_level="moderate",
            relevant_contexts=["animals"],
            recommended_method="direct-english-construction",
            first_experience_id="experience-animals-001",
            review_criterion="Complete one additional activity.",
            evidence_summary="Evidence remains incomplete.",
            generated_at=COMPLETED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )


def test_create_initial_profile_evidence_link() -> None:
    link = InitialConversationalProfileEvidence(
        profile_id="profile-001",
        observation_id="observation-001",
    )

    assert link.profile_id == "profile-001"
    assert link.observation_id == "observation-001"


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        ("profile_id", "profile_id cannot be blank"),
        ("observation_id", "observation_id cannot be blank"),
    ],
)
def test_reject_blank_initial_profile_evidence_identifier(
    field_name: str,
    message: str,
) -> None:
    data = {
        "profile_id": "profile-001",
        "observation_id": "observation-001",
    }
    data[field_name] = " "

    with pytest.raises(ValidationError, match=message):
        InitialConversationalProfileEvidence(**data)


def test_reject_blank_context_id() -> None:
    with pytest.raises(
        ValidationError,
        match="context_id cannot be blank",
    ):
        ConversationalDiagnosticContext(
            context_id=" ",
            diagnostic_session_id="diagnostic-001",
            usual_languages=["Spanish"],
            previous_english_contact="School classes",
            autonomy_level="developing",
        )


def test_reject_blank_activity_prompt_id() -> None:
    with pytest.raises(
        ValidationError,
        match="prompt_id cannot be blank",
    ):
        ConversationalDiagnosticActivity(
            activity_id="activity-001",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id=" ",
            stage="initial_response",
            communicative_intention="Give an initial response",
            modality="voice",
            expected_evidence_type="spontaneous_production",
            sequence_order=1,
        )
