from datetime import datetime, timezone

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationResultRecord

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
)
from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_activity_context,
    validate_diagnostic_context_references,
    validate_diagnostic_activity_production,
    validate_diagnostic_activity_sequence,
    validate_diagnostic_observation,
    validate_diagnostic_observation_evaluations,
    validate_diagnostic_production_activity_ownership,
    validate_diagnostic_observation_support,
    validate_diagnostic_session_context,
    validate_diagnostic_support_sequence,
    validate_diagnostic_support_usage,
    validate_initial_conversational_profile_session,
    validate_initial_profile_evidence,
)


STARTED_AT = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


def build_session() -> ConversationalDiagnosticSession:
    return ConversationalDiagnosticSession(
        diagnostic_session_id="diagnostic-001",
        user_id="user-001",
        age_profile="9-12",
        started_at=STARTED_AT,
    )


def build_context(
    diagnostic_session_id: str = "diagnostic-001",
    *,
    audio_authorized: bool = True,
) -> ConversationalDiagnosticContext:
    return ConversationalDiagnosticContext(
        context_id="context-001",
        diagnostic_session_id=diagnostic_session_id,
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=audio_authorized,
    )


def test_accept_context_from_same_diagnostic_session() -> None:
    validate_diagnostic_session_context(
        build_session(),
        build_context(),
    )


def test_reject_context_from_another_diagnostic_session() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic context must belong to "
            "the diagnostic session"
        ),
    ):
        validate_diagnostic_session_context(
            build_session(),
            build_context("diagnostic-002"),
        )


def build_activity(
    diagnostic_session_id: str = "diagnostic-001",
    context_id: str = "context-001",
) -> ConversationalDiagnosticActivity:
    return ConversationalDiagnosticActivity(
        activity_id="activity-001",
        diagnostic_session_id=diagnostic_session_id,
        context_id=context_id,
        prompt_id="diagnostic-prompt-001",
        stage="initial_response",
        communicative_intention="Describe a favorite animal",
        modality="voice",
        expected_evidence_type="spontaneous_production",
        available_supports=["visual"],
        sequence_order=1,
    )


def test_accept_activity_from_same_session_and_context() -> None:
    validate_diagnostic_activity_context(
        build_session(),
        build_context(),
        build_activity(),
    )


def test_reject_activity_from_another_diagnostic_session() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic activity must belong to "
            "the diagnostic session"
        ),
    ):
        validate_diagnostic_activity_context(
            build_session(),
            build_context(),
            build_activity(diagnostic_session_id="diagnostic-002"),
        )


def test_reject_activity_using_another_context() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic activity must use the diagnostic context",
    ):
        validate_diagnostic_activity_context(
            build_session(),
            build_context(),
            build_activity(context_id="context-002"),
        )


def test_reject_voice_activity_without_audio_authorization() -> None:
    with pytest.raises(
        ValueError,
        match="Voice diagnostic activity requires audio authorization",
    ):
        validate_diagnostic_activity_context(
            build_session(),
            build_context(audio_authorized=False),
            build_activity(),
        )


def test_accept_non_voice_activity_without_audio_authorization() -> None:
    activity = ConversationalDiagnosticActivity(
        activity_id="activity-002",
        diagnostic_session_id="diagnostic-001",
        context_id="context-001",
        prompt_id="diagnostic-prompt-001",
        stage="context_selection",
        communicative_intention="Select one motivating context",
        modality="selection",
        expected_evidence_type="motivating_context",
        sequence_order=2,
    )

    validate_diagnostic_activity_context(
        build_session(),
        build_context(audio_authorized=False),
        activity,
    )


def build_support_usage(
    diagnostic_session_id: str = "diagnostic-001",
    activity_id: str = "activity-001",
    support_type: str = "visual",
    support_level: str | None = None,
    production_id: int = 1,
    sequence_order: int = 1,
    withdrawn_afterward: bool = False,
) -> DiagnosticSupportUsage:
    resolved_support_level = support_level
    if resolved_support_level is None:
        resolved_support_level = (
            "none" if support_type == "none" else "minimal"
        )

    return DiagnosticSupportUsage(
        diagnostic_session_id=diagnostic_session_id,
        activity_id=activity_id,
        production_id=production_id,
        support_type=support_type,
        support_level=resolved_support_level,
        sequence_order=sequence_order,
        provided_at=STARTED_AT,
        withdrawn_afterward=withdrawn_afterward,
    )


def test_accept_available_diagnostic_support() -> None:
    validate_diagnostic_support_usage(
        build_session(),
        build_activity(),
        build_support_usage(),
    )


def test_accept_no_support_usage() -> None:
    validate_diagnostic_support_usage(
        build_session(),
        build_activity(),
        build_support_usage(support_type="none"),
    )


def test_reject_support_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic support must belong to the diagnostic session",
    ):
        validate_diagnostic_support_usage(
            build_session(),
            build_activity(),
            build_support_usage(diagnostic_session_id="diagnostic-002"),
        )


def test_reject_support_from_another_activity() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic support must belong to the diagnostic activity",
    ):
        validate_diagnostic_support_usage(
            build_session(),
            build_activity(),
            build_support_usage(activity_id="activity-002"),
        )


def test_reject_support_unavailable_in_activity() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Used diagnostic support must be available "
            "in the activity"
        ),
    ):
        validate_diagnostic_support_usage(
            build_session(),
            build_activity(),
            build_support_usage(support_type="pattern"),
        )


def build_observation(
    diagnostic_session_id: str = "diagnostic-001",
    activity_id: str = "activity-001",
    production_id: int | None = 1,
    evaluation_result_ids: list[int] | None = None,
    support_level: str = "minimal",
    evidence_role: str = "development_need",
) -> ConversationalDiagnosticObservation:
    return ConversationalDiagnosticObservation(
        observation_id="observation-001",
        diagnostic_session_id=diagnostic_session_id,
        activity_id=activity_id,
        production_id=production_id,
        evaluation_result_ids=(
            [2] if evaluation_result_ids is None
            else evaluation_result_ids
        ),
        dimension="oral_production",
        evidence_role=evidence_role,
        description="Produced one understandable sentence.",
        support_level=support_level,
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )


def test_accept_diagnostic_observation() -> None:
    validate_diagnostic_observation(
        build_session(),
        build_activity(),
        build_observation(),
    )


def test_accept_observation_without_production_or_evaluation() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    validate_diagnostic_observation(
        build_session(),
        build_activity(),
        observation,
    )


def test_reject_observation_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic observation must belong to the diagnostic session",
    ):
        validate_diagnostic_observation(
            build_session(),
            build_activity(),
            build_observation(diagnostic_session_id="diagnostic-002"),
        )


def test_reject_observation_from_another_activity() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic observation must belong to the diagnostic activity",
    ):
        validate_diagnostic_observation(
            build_session(),
            build_activity(),
            build_observation(activity_id="activity-002"),
        )


def test_reject_evaluations_without_observed_production() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic evaluations require an observed production",
    ):
        validate_diagnostic_observation(
            build_session(),
            build_activity(),
            build_observation(
                production_id=None,
                evaluation_result_ids=[2],
            ),
        )


def build_finished_session(
    status: str = "completed",
) -> ConversationalDiagnosticSession:
    return ConversationalDiagnosticSession(
        diagnostic_session_id="diagnostic-001",
        user_id="user-001",
        age_profile="9-12",
        status=status,
        started_at=STARTED_AT,
        completed_at=STARTED_AT,
    )


def build_initial_profile(
    status: str = "confirmed",
    diagnostic_session_id: str = "diagnostic-001",
) -> InitialConversationalProfile:
    return InitialConversationalProfile(
        profile_id="profile-001",
        diagnostic_session_id=diagnostic_session_id,
        status=status,
        priority_blockage="Needs support to expand oral responses.",
        target_capacity="Build and extend one connected response.",
        recommended_support_level="minimal",
        relevant_contexts=["animals"],
        recommended_method="direct-english-construction",
        first_lesson_id="lesson-animals-001",
        review_criterion="Respond to a new variation with less support.",
        evidence_summary="Evidence from several diagnostic observations.",
        generated_at=STARTED_AT,
        generator_id="deterministic-profile-generator",
        generator_version="1.0",
    )


def test_accept_confirmed_profile_for_completed_session() -> None:
    validate_initial_conversational_profile_session(
        build_finished_session("completed"),
        build_initial_profile("confirmed"),
    )


def test_accept_provisional_profile_for_provisional_session() -> None:
    validate_initial_conversational_profile_session(
        build_finished_session("provisional"),
        build_initial_profile("provisional"),
    )


def test_reject_profile_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial conversational profile must belong to "
            "the diagnostic session"
        ),
    ):
        validate_initial_conversational_profile_session(
            build_finished_session(),
            build_initial_profile(
                diagnostic_session_id="diagnostic-002"
            ),
        )


def test_reject_profile_for_in_progress_session() -> None:
    with pytest.raises(
        ValueError,
        match="In-progress diagnostic session cannot generate a profile",
    ):
        validate_initial_conversational_profile_session(
            build_session(),
            build_initial_profile(),
        )


def test_reject_profile_for_cancelled_session() -> None:
    with pytest.raises(
        ValueError,
        match="Cancelled diagnostic session cannot generate a profile",
    ):
        validate_initial_conversational_profile_session(
            build_finished_session("cancelled"),
            build_initial_profile(),
        )


def test_reject_confirmed_profile_for_provisional_session() -> None:
    with pytest.raises(
        ValueError,
        match="Confirmed profile requires a completed diagnostic session",
    ):
        validate_initial_conversational_profile_session(
            build_finished_session("provisional"),
            build_initial_profile("confirmed"),
        )


def test_reject_provisional_profile_for_completed_session() -> None:
    with pytest.raises(
        ValueError,
        match="Provisional profile requires a provisional diagnostic session",
    ):
        validate_initial_conversational_profile_session(
            build_finished_session("completed"),
            build_initial_profile("provisional"),
        )


def build_profile_evidence_link(
    profile_id: str = "profile-001",
    observation_id: str = "observation-001",
) -> InitialConversationalProfileEvidence:
    return InitialConversationalProfileEvidence(
        profile_id=profile_id,
        observation_id=observation_id,
    )


def test_accept_provisional_initial_profile_evidence() -> None:
    validate_initial_profile_evidence(
        build_finished_session("provisional"),
        build_initial_profile("provisional"),
        [build_activity()],
        [build_observation()],
        [build_profile_evidence_link()],
    )


def test_reject_profile_observation_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match="Profile observations must belong to the diagnostic session",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [
                build_observation(
                    diagnostic_session_id="diagnostic-002"
                )
            ],
            [build_profile_evidence_link()],
        )


def test_reject_evidence_link_to_another_profile() -> None:
    with pytest.raises(
        ValueError,
        match="Profile evidence must reference the initial profile",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation()],
            [
                build_profile_evidence_link(
                    profile_id="profile-002"
                )
            ],
        )


def test_reject_evidence_link_to_unknown_observation() -> None:
    with pytest.raises(
        ValueError,
        match="Profile evidence references an unknown observation",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation()],
            [
                build_profile_evidence_link(
                    observation_id="observation-999"
                )
            ],
        )


def test_reject_duplicate_observation_identifiers() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic observations must have unique identifiers",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation(), build_observation()],
            [build_profile_evidence_link()],
        )


def test_reject_repeated_profile_evidence_observation() -> None:
    with pytest.raises(
        ValueError,
        match="Profile evidence cannot repeat observations",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation()],
            [
                build_profile_evidence_link(),
                build_profile_evidence_link(),
            ],
        )


def test_reject_initial_profile_without_evidence() -> None:
    with pytest.raises(
        ValueError,
        match="Initial conversational profile requires evidence",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation()],
            [],
        )


def test_reject_duplicate_profile_activity_identifiers() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic activities must have unique identifiers",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity(), build_activity()],
            [build_observation()],
            [build_profile_evidence_link()],
        )


def test_reject_profile_activity_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match="Profile activities must belong to the diagnostic session",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [
                build_activity(
                    diagnostic_session_id="diagnostic-002"
                )
            ],
            [build_observation()],
            [build_profile_evidence_link()],
        )


def test_reject_profile_observation_with_unknown_activity() -> None:
    with pytest.raises(
        ValueError,
        match="Profile observation references an unknown activity",
    ):
        validate_initial_profile_evidence(
            build_finished_session(),
            build_initial_profile(),
            [build_activity()],
            [build_observation(activity_id="activity-999")],
            [build_profile_evidence_link()],
        )

def build_complete_profile_evidence() -> tuple[
    list[ConversationalDiagnosticActivity],
    list[ConversationalDiagnosticObservation],
    list[InitialConversationalProfileEvidence],
]:
    specifications = [
        (
            "activity-comprehension",
            "listening_comprehension",
            "comprehension",
            "observation-comprehension",
            "listening_comprehension",
        ),
        (
            "activity-spontaneous",
            "initial_response",
            "spontaneous_production",
            "observation-spontaneous",
            "oral_production",
        ),
        (
            "activity-supported",
            "guided_construction",
            "supported_production",
            "observation-supported",
            "support_need",
        ),
        (
            "activity-exchange",
            "connected_exchange",
            "connected_exchange",
            "observation-exchange",
            "continuity",
        ),
        (
            "activity-transfer",
            "transfer",
            "transfer",
            "observation-transfer",
            "transfer",
        ),
        (
            "activity-context",
            "context_selection",
            "motivating_context",
            "observation-context",
            "motivating_context",
        ),
    ]

    activities: list[ConversationalDiagnosticActivity] = []
    observations: list[ConversationalDiagnosticObservation] = []
    links: list[InitialConversationalProfileEvidence] = []

    for sequence_order, specification in enumerate(
        specifications,
        start=1,
    ):
        (
            activity_id,
            stage,
            evidence_type,
            observation_id,
            dimension,
        ) = specification

        activities.append(
            ConversationalDiagnosticActivity(
                activity_id=activity_id,
                diagnostic_session_id="diagnostic-001",
                context_id="context-001",
                prompt_id="diagnostic-prompt-001",
                stage=stage,
                communicative_intention="Complete diagnostic evidence.",
                modality=(
                    "selection"
                    if stage == "context_selection"
                    else "voice"
                ),
                expected_evidence_type=evidence_type,
                available_supports=["visual"],
                transfer_variant_id=(
                    "variant-001"
                    if stage == "transfer"
                    else None
                ),
                sequence_order=sequence_order,
            )
        )
        observations.append(
            ConversationalDiagnosticObservation(
                observation_id=observation_id,
                diagnostic_session_id="diagnostic-001",
                activity_id=activity_id,
                production_id=sequence_order,
                dimension=dimension,
                evidence_role=(
                    "context_relevance"
                    if dimension == "motivating_context"
                    else (
                        "priority_blockage"
                        if dimension == "support_need"
                        else "development_need"
                    )
                ),
                context_reference=(
                    "animals"
                    if dimension == "motivating_context"
                    else None
                ),
                description="Observed diagnostic evidence.",
                support_level="minimal",
                observer_id="deterministic-diagnostic-observer",
                observer_version="1.0",
                observed_at=STARTED_AT,
            )
        )
        links.append(
            InitialConversationalProfileEvidence(
                profile_id="profile-001",
                observation_id=observation_id,
            )
        )

    return activities, observations, links


def test_accept_confirmed_profile_with_complete_evidence() -> None:
    activities, observations, links = (
        build_complete_profile_evidence()
    )

    validate_initial_profile_evidence(
        build_finished_session("completed"),
        build_initial_profile("confirmed"),
        activities,
        observations,
        links,
    )


def test_reject_confirmed_profile_with_incomplete_evidence() -> None:
    activities, observations, links = (
        build_complete_profile_evidence()
    )

    with pytest.raises(
        ValueError,
        match=(
            "Confirmed profile requires complete diagnostic evidence: "
            "motivating_context"
        ),
    ):
        validate_initial_profile_evidence(
            build_finished_session("completed"),
            build_initial_profile("confirmed"),
            activities,
            observations,
            links[:-1],
        )


def test_accept_diagnostic_activity_sequence() -> None:
    first = build_activity()
    second = first.model_copy(
        update={
            "activity_id": "activity-002",
            "sequence_order": 2,
        }
    )

    validate_diagnostic_activity_sequence(
        build_session(),
        [first, second],
    )


def test_reject_duplicate_activity_sequence_orders() -> None:
    first = build_activity()
    second = first.model_copy(
        update={"activity_id": "activity-002"}
    )

    with pytest.raises(
        ValueError,
        match="Diagnostic activities must have unique sequence orders",
    ):
        validate_diagnostic_activity_sequence(
            build_session(),
            [first, second],
        )


def test_reject_activity_sequence_from_another_session() -> None:
    activity = build_activity(
        diagnostic_session_id="diagnostic-002"
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic activities must belong to "
            "the diagnostic session"
        ),
    ):
        validate_diagnostic_activity_sequence(
            build_session(),
            [activity],
        )


def test_reject_activities_outside_sequence_order() -> None:
    first = build_activity()
    second = first.model_copy(
        update={
            "activity_id": "activity-002",
            "sequence_order": 2,
        }
    )

    with pytest.raises(
        ValueError,
        match="Diagnostic activities must follow sequence order",
    ):
        validate_diagnostic_activity_sequence(
            build_session(),
            [second, first],
        )


def test_reject_production_required_dimension_without_production() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic observation dimension requires a production"
        ),
    ):
        validate_diagnostic_observation(
            build_session(),
            build_activity(),
            observation,
        )


def test_accept_diagnostic_support_sequence() -> None:
    usages = [
        build_support_usage(
            support_level="moderate",
            production_id=1,
            sequence_order=1,
            withdrawn_afterward=True,
        ),
        build_support_usage(
            support_level="minimal",
            production_id=2,
            sequence_order=2,
        ),
    ]

    validate_diagnostic_support_sequence(
        build_session(),
        build_activity(),
        usages,
    )


def test_reject_duplicate_support_sequence_orders() -> None:
    usages = [
        build_support_usage(
            production_id=1,
            sequence_order=1,
        ),
        build_support_usage(
            production_id=2,
            sequence_order=1,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Diagnostic supports must have unique sequence orders",
    ):
        validate_diagnostic_support_sequence(
            build_session(),
            build_activity(),
            usages,
        )


def test_reject_supports_outside_sequence_order() -> None:
    usages = [
        build_support_usage(
            production_id=2,
            sequence_order=2,
        ),
        build_support_usage(
            production_id=1,
            sequence_order=1,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Diagnostic supports must follow sequence order",
    ):
        validate_diagnostic_support_sequence(
            build_session(),
            build_activity(),
            usages,
        )


def test_reject_no_support_combined_with_other_support() -> None:
    usages = [
        build_support_usage(
            support_type="none",
            production_id=1,
            sequence_order=1,
        ),
        build_support_usage(
            support_type="visual",
            production_id=1,
            sequence_order=2,
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "No-support usage cannot be combined "
            "with other supports"
        ),
    ):
        validate_diagnostic_support_sequence(
            build_session(),
            build_activity(),
            usages,
        )


def test_reject_withdrawn_support_reduced_in_same_production() -> None:
    usages = [
        build_support_usage(
            support_level="moderate",
            production_id=1,
            sequence_order=1,
            withdrawn_afterward=True,
        ),
        build_support_usage(
            support_level="minimal",
            production_id=1,
            sequence_order=2,
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "Withdrawn support requires a later production "
            "with lower support level"
        ),
    ):
        validate_diagnostic_support_sequence(
            build_session(),
            build_activity(),
            usages,
        )


@pytest.mark.parametrize(
    "later_support_level",
    ["moderate", "full"],
)
def test_reject_withdrawn_support_without_later_reduction(
    later_support_level: str,
) -> None:
    usages = [
        build_support_usage(
            support_level="moderate",
            production_id=1,
            sequence_order=1,
            withdrawn_afterward=True,
        ),
        build_support_usage(
            support_level=later_support_level,
            production_id=2,
            sequence_order=2,
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "Withdrawn support requires a later production "
            "with lower support level"
        ),
    ):
        validate_diagnostic_support_sequence(
            build_session(),
            build_activity(),
            usages,
        )


def test_accept_observation_matching_used_support() -> None:
    usages = [
        build_support_usage(
            support_type="visual",
            support_level="minimal",
            sequence_order=1,
        ),
        build_support_usage(
            support_type="keyword",
            support_level="moderate",
            sequence_order=2,
        ),
    ]

    validate_diagnostic_observation_support(
        build_session(),
        build_activity(),
        build_observation(support_level="moderate"),
        usages,
    )


def test_accept_observation_without_used_support() -> None:
    validate_diagnostic_observation_support(
        build_session(),
        build_activity(),
        build_observation(support_level="none"),
        [],
    )


def test_reject_observation_with_incorrect_support_level() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic observation support level must match "
            "the support actually used"
        ),
    ):
        validate_diagnostic_observation_support(
            build_session(),
            build_activity(),
            build_observation(support_level="minimal"),
            [
                build_support_usage(
                    support_level="moderate",
                )
            ],
        )


def test_reject_observation_support_from_another_production() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Observation supports must belong to its session, "
            "activity and production"
        ),
    ):
        validate_diagnostic_observation_support(
            build_session(),
            build_activity(),
            build_observation(
                production_id=1,
                support_level="minimal",
            ),
            [
                build_support_usage(
                    production_id=2,
                    support_level="minimal",
                )
            ],
        )


def build_learner_production(
    production_id: int = 1,
    prompt_id: str = "diagnostic-prompt-001",
) -> LearnerProductionRecord:
    return LearnerProductionRecord(
        production_id=production_id,
        prompt_id=prompt_id,
        turn_id="diagnostic-turn-001",
        modality="text",
        response_text="I like animals.",
    )


def test_accept_diagnostic_activity_production() -> None:
    validate_diagnostic_activity_production(
        build_activity().model_copy(
            update={"modality": "text"}
        ),
        build_learner_production(),
    )


def test_accept_observation_linked_to_activity_production() -> None:
    validate_diagnostic_activity_production(
        build_activity().model_copy(
            update={"modality": "text"}
        ),
        build_learner_production(),
        build_observation(production_id=1),
    )


def test_reject_production_from_another_activity_prompt() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic production must match the activity prompt",
    ):
        validate_diagnostic_activity_production(
            build_activity(),
            build_learner_production(
                prompt_id="diagnostic-prompt-999"
            ),
        )


def test_reject_observation_linked_to_another_production() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic observation must reference "
            "the learner production"
        ),
    ):
        validate_diagnostic_activity_production(
            build_activity().model_copy(
                update={"modality": "text"}
            ),
            build_learner_production(production_id=1),
            build_observation(production_id=2),
        )


def build_evaluation_result(
    evaluation_result_id: int = 2,
    production_id: int = 1,
) -> ProductionEvaluationResultRecord:
    return ProductionEvaluationResultRecord(
        evaluation_result_id=evaluation_result_id,
        production_id=production_id,
        criterion_id="criterion-001",
        status="passed",
        score=None,
        evaluator_id="deterministic-semantic-evaluator",
        evaluator_version="1.0",
        evaluated_at=STARTED_AT,
    )


def test_accept_diagnostic_observation_evaluations() -> None:
    validate_diagnostic_observation_evaluations(
        build_observation(
            production_id=1,
            evaluation_result_ids=[2],
        ),
        [build_evaluation_result()],
    )


def test_reject_duplicate_diagnostic_evaluation_ids() -> None:
    with pytest.raises(
        ValueError,
        match="Diagnostic evaluations must have unique identifiers",
    ):
        validate_diagnostic_observation_evaluations(
            build_observation(
                production_id=1,
                evaluation_result_ids=[2],
            ),
            [
                build_evaluation_result(),
                build_evaluation_result(),
            ],
        )


def test_reject_mismatched_observation_evaluation_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic observation evaluations must match "
            "the referenced evaluation identifiers"
        ),
    ):
        validate_diagnostic_observation_evaluations(
            build_observation(
                production_id=1,
                evaluation_result_ids=[2],
            ),
            [
                build_evaluation_result(
                    evaluation_result_id=3
                )
            ],
        )


def test_reject_evaluation_from_another_production() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic evaluation must belong to "
            "the observed production"
        ),
    ):
        validate_diagnostic_observation_evaluations(
            build_observation(
                production_id=1,
                evaluation_result_ids=[2],
            ),
            [
                build_evaluation_result(
                    production_id=2
                )
            ],
        )


def test_accept_matching_voice_production_modality() -> None:
    activity = build_activity().model_copy(
        update={"modality": "voice"}
    )
    production = build_learner_production().model_copy(
        update={"modality": "voice"}
    )

    validate_diagnostic_activity_production(
        activity,
        production,
    )


def test_reject_mismatched_diagnostic_production_modality() -> None:
    activity = build_activity().model_copy(
        update={"modality": "voice"}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic production modality must match "
            "the diagnostic activity"
        ),
    ):
        validate_diagnostic_activity_production(
            activity,
            build_learner_production(),
        )


@pytest.mark.parametrize("modality", ["listening", "selection"])
def test_reject_non_production_activity_modality(
    modality: str,
) -> None:
    activity = build_activity().model_copy(
        update={"modality": modality}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic activity modality does not capture "
            "a learner production"
        ),
    ):
        validate_diagnostic_activity_production(
            activity,
            build_learner_production(),
        )


def test_accept_same_production_for_same_activity_observations() -> None:
    observations = [
        build_observation(production_id=1),
        build_observation(production_id=1).model_copy(
            update={
                "observation_id": "observation-002",
                "dimension": "continuity",
            }
        ),
    ]

    validate_diagnostic_production_activity_ownership(
        observations
    )


def test_ignore_observations_without_production_ownership() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
        support_level="none",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    validate_diagnostic_production_activity_ownership(
        [observation]
    )


def test_reject_production_reused_across_activities() -> None:
    observations = [
        build_observation(production_id=1),
        build_observation(
            activity_id="activity-002",
            production_id=1,
        ).model_copy(
            update={"observation_id": "observation-002"}
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic production cannot be reused "
            "across different activities"
        ),
    ):
        validate_diagnostic_production_activity_ownership(
            observations
        )


def test_accept_observation_without_production_or_support() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
        support_level="none",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    validate_diagnostic_observation_support(
        build_session(),
        build_activity(),
        observation,
        [],
    )


def test_reject_support_for_observation_without_production() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
        support_level="none",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Observation without production cannot "
            "reference supports"
        ),
    ):
        validate_diagnostic_observation_support(
            build_session(),
            build_activity(),
            observation,
            [build_support_usage(production_id=1)],
        )


def test_reject_support_level_for_observation_without_production() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
        support_level="minimal",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Observation without production requires "
            "none support level"
        ),
    ):
        validate_diagnostic_observation_support(
            build_session(),
            build_activity(),
            observation,
            [],
        )


def test_accept_observation_without_production_or_evaluations() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[],
        support_level="none",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    validate_diagnostic_observation_evaluations(
        observation,
        [],
    )


def test_reject_evaluations_without_observed_production() -> None:
    observation = build_observation(
        production_id=None,
        evaluation_result_ids=[2],
        support_level="none",
    ).model_copy(
        update={"dimension": "listening_comprehension"}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic evaluations require "
            "an observed production"
        ),
    ):
        validate_diagnostic_observation_evaluations(
            observation,
            [build_evaluation_result(production_id=1)],
        )


def build_context_observation(
    diagnostic_session_id: str = "diagnostic-001",
    context_reference: str = "animals",
) -> ConversationalDiagnosticObservation:
    return ConversationalDiagnosticObservation(
        observation_id="observation-context",
        diagnostic_session_id=diagnostic_session_id,
        activity_id="activity-context",
        dimension="motivating_context",
        evidence_role="context_relevance",
        context_reference=context_reference,
        description="The learner selected a motivating context.",
        support_level="none",
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )


def test_accept_authorized_diagnostic_context_reference() -> None:
    validate_diagnostic_context_references(
        build_context(),
        [build_context_observation()],
    )


def test_reject_unauthorized_diagnostic_context_reference() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic context reference must exist "
            "in authorized general interests"
        ),
    ):
        validate_diagnostic_context_references(
            build_context(),
            [
                build_context_observation(
                    context_reference="video games"
                )
            ],
        )


def test_reject_context_observation_from_another_session() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Context observation must belong to "
            "the diagnostic context session"
        ),
    ):
        validate_diagnostic_context_references(
            build_context(),
            [
                build_context_observation(
                    diagnostic_session_id="diagnostic-999"
                )
            ],
        )
