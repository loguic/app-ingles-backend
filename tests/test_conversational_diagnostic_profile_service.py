from datetime import datetime, timezone

import pytest

from app.schemas.content import Lesson

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    InitialConversationalProfilePlan,
)
from app.services.conversational_diagnostic_profile_service import (
    build_initial_profile_evidence_links,
    generate_initial_conversational_profile,
    resolve_initial_profile_status,
    validate_initial_profile_plan_lesson,
    resolve_priority_blockage_observation,
    resolve_relevant_contexts,
)


STARTED_AT = datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc)


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


def test_resolve_confirmed_profile_status() -> None:
    assert (
        resolve_initial_profile_status(
            build_finished_session("completed")
        )
        == "confirmed"
    )


def test_resolve_provisional_profile_status() -> None:
    assert (
        resolve_initial_profile_status(
            build_finished_session("provisional")
        )
        == "provisional"
    )


@pytest.mark.parametrize("status", ["in_progress", "cancelled"])
def test_reject_session_status_without_profile(
    status: str,
) -> None:
    session = build_finished_session().model_copy(
        update={"status": status}
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic session status cannot generate "
            "an initial conversational profile"
        ),
    ):
        resolve_initial_profile_status(session)


def build_profile_observation(
    observation_id: str = "observation-priority",
    evidence_role: str = "priority_blockage",
) -> ConversationalDiagnosticObservation:
    return ConversationalDiagnosticObservation(
        observation_id=observation_id,
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-supported",
        production_id=1,
        dimension="support_need",
        evidence_role=evidence_role,
        description="Needs support to expand oral responses.",
        support_level="minimal",
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )


def test_resolve_single_priority_blockage_observation() -> None:
    observation = build_profile_observation()

    assert (
        resolve_priority_blockage_observation([observation])
        == observation
    )


def test_reject_missing_priority_blockage_observation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial profile requires one "
            "priority blockage observation"
        ),
    ):
        resolve_priority_blockage_observation(
            [
                build_profile_observation(
                    evidence_role="development_need"
                )
            ]
        )


def test_reject_multiple_priority_blockage_observations() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial profile cannot have multiple "
            "priority blockage observations"
        ),
    ):
        resolve_priority_blockage_observation(
            [
                build_profile_observation(),
                build_profile_observation(
                    observation_id="observation-priority-002"
                ),
            ]
        )


def build_relevant_context_observation(
    observation_id: str = "observation-context-001",
    context_reference: str = "animals",
) -> ConversationalDiagnosticObservation:
    return ConversationalDiagnosticObservation(
        observation_id=observation_id,
        diagnostic_session_id="diagnostic-001",
        activity_id="activity-context",
        dimension="motivating_context",
        evidence_role="context_relevance",
        context_reference=context_reference,
        description="Selected one motivating context.",
        support_level="none",
        observer_id="deterministic-diagnostic-observer",
        observer_version="1.0",
        observed_at=STARTED_AT,
    )


def test_resolve_unique_relevant_contexts_in_order() -> None:
    observations = [
        build_profile_observation(
            evidence_role="development_need"
        ),
        build_relevant_context_observation(
            context_reference="animals"
        ),
        build_relevant_context_observation(
            observation_id="observation-context-002",
            context_reference="space",
        ),
        build_relevant_context_observation(
            observation_id="observation-context-003",
            context_reference="animals",
        ),
    ]

    assert resolve_relevant_contexts(observations) == [
        "animals",
        "space",
    ]


def test_reject_missing_relevant_context_observation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial profile requires one "
            "relevant context observation"
        ),
    ):
        resolve_relevant_contexts(
            [
                build_profile_observation(
                    evidence_role="development_need"
                )
            ]
        )


def test_build_ordered_initial_profile_evidence_links() -> None:
    observations = [
        build_profile_observation(
            observation_id="observation-001"
        ),
        build_profile_observation(
            observation_id="observation-002",
            evidence_role="development_need",
        ),
    ]

    links = build_initial_profile_evidence_links(
        "profile-001",
        observations,
    )

    assert [
        link.observation_id
        for link in links
    ] == [
        "observation-001",
        "observation-002",
    ]
    assert all(
        link.profile_id == "profile-001"
        for link in links
    )


def test_reject_empty_initial_profile_evidence_links() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial profile evidence links "
            "require observations"
        ),
    ):
        build_initial_profile_evidence_links(
            "profile-001",
            [],
        )


def test_reject_duplicate_initial_profile_observation_ids() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Initial profile evidence links require "
            "unique observation identifiers"
        ),
    ):
        build_initial_profile_evidence_links(
            "profile-001",
            [
                build_profile_observation(),
                build_profile_observation(),
            ],
        )


def test_generate_traceable_initial_conversational_profile() -> None:
    context = ConversationalDiagnosticContext(
        context_id="context-001",
        diagnostic_session_id="diagnostic-001",
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=True,
    )
    specifications = [
        (
            "activity-comprehension",
            "listening_comprehension",
            "comprehension",
            "listening_comprehension",
        ),
        (
            "activity-spontaneous",
            "initial_response",
            "spontaneous_production",
            "oral_production",
        ),
        (
            "activity-supported",
            "guided_construction",
            "supported_production",
            "support_need",
        ),
        (
            "activity-exchange",
            "connected_exchange",
            "connected_exchange",
            "continuity",
        ),
        (
            "activity-transfer",
            "transfer",
            "transfer",
            "transfer",
        ),
        (
            "activity-context",
            "context_selection",
            "motivating_context",
            "motivating_context",
        ),
    ]
    activities = []
    observations = []

    for sequence_order, (
        activity_id,
        stage,
        evidence_type,
        dimension,
    ) in enumerate(specifications, start=1):
        activities.append(
            ConversationalDiagnosticActivity(
                activity_id=activity_id,
                diagnostic_session_id="diagnostic-001",
                context_id="context-001",
                prompt_id="prompt-" + str(sequence_order),
                stage=stage,
                communicative_intention="Collect diagnostic evidence.",
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
                observation_id="observation-" + str(sequence_order),
                diagnostic_session_id="diagnostic-001",
                activity_id=activity_id,
                production_id=(
                    None
                    if dimension == "motivating_context"
                    else sequence_order
                ),
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
                description=(
                    "Needs support to expand oral responses."
                    if dimension == "support_need"
                    else "Observed diagnostic evidence."
                ),
                support_level=(
                    "none"
                    if dimension == "motivating_context"
                    else "minimal"
                ),
                observer_id="deterministic-diagnostic-observer",
                observer_version="1.0",
                observed_at=STARTED_AT,
            )
        )

    plan = InitialConversationalProfilePlan(
        target_capacity="Build and extend one connected response.",
        recommended_support_level="minimal",
        recommended_method="direct-english-construction",
        first_lesson_id="lesson-animals-001",
        review_criterion="Respond to a new variation with less support.",
    )

    profile, links = generate_initial_conversational_profile(
        profile_id="profile-001",
        session=build_finished_session("completed"),
        context=context,
        activities=activities,
        observations=observations,
        plan=plan,
        lessons=[build_recommended_lesson()],
        generated_at=STARTED_AT,
        generator_id="deterministic-profile-generator",
        generator_version="1.0",
    )

    assert profile.status == "confirmed"
    assert profile.priority_blockage == (
        "Needs support to expand oral responses."
    )
    assert profile.relevant_contexts == ["animals"]
    assert profile.recommended_method == (
        "direct-english-construction"
    )
    assert profile.first_lesson_id == "lesson-animals-001"
    assert profile.evidence_summary == (
        "6 diagnostic observations linked."
    )
    assert len(links) == 6
    assert all(link.profile_id == "profile-001" for link in links)


def build_recommended_lesson(
    lesson_id: str = "lesson-animals-001",
) -> Lesson:
    return Lesson.model_validate(
        {
            "id": lesson_id,
            "title": "Talk about animals",
            "experience": {
                "contract_version": "2.0",
                "mission": {
                    "id": lesson_id + "-mission",
                    "title": "Talk about animals",
                    "situation": "Share one animal preference.",
                    "observable_outcome": (
                        "Produce one connected response."
                    ),
                    "success_criteria": [
                        "The learner produces one response."
                    ],
                },
                "skill_ids": ["a1_talk_about_animals"],
                "stages": [
                    {
                        "id": lesson_id + "-stage",
                        "type": "evidence",
                        "instruction": "Provide one response.",
                        "activity_ids": [lesson_id + "-conversation"],
                        "mode": "required",
                        "completion_condition": "evidence_recorded",
                    }
                ],
                "language_support": [],
                "evidence_definitions": [
                    {
                        "id": lesson_id + "-evidence",
                        "skill_ids": ["a1_talk_about_animals"],
                        "stage_id": lesson_id + "-stage",
                        "activity_id": lesson_id + "-conversation",
                        "evidence_type": "contextual_response",
                        "measurement_mode": "completion",
                        "required": True,
                    }
                ],
                "completion_policy": {
                    "practiced_stage_ids": [lesson_id + "-stage"],
                    "required_evidence_ids": [
                        lesson_id + "-evidence"
                    ],
                    "reinforcement_on_failure": True,
                    "allow_retry": True,
                },
            },
            "conversations": [
                {
                    "id": lesson_id + "-conversation",
                    "title": "Animal conversation",
                    "mode": "free",
                    "start_turn_id": lesson_id + "-turn",
                    "turns": [
                        {
                            "id": lesson_id + "-turn",
                            "speaker": "learner",
                            "en": "Talk about an animal you like.",
                            "next_turn_id": None,
                            "choices": [],
                            "production_prompt": {
                                "id": lesson_id + "-prompt",
                                "accepted_modalities": [
                                    "text",
                                    "voice",
                                ],
                                "required": True,
                            },
                        }
                    ],
                }
            ],
        }
    )


def build_initial_profile_plan() -> InitialConversationalProfilePlan:
    return InitialConversationalProfilePlan(
        target_capacity="Build and extend one connected response.",
        recommended_support_level="minimal",
        recommended_method="direct-english-construction",
        first_lesson_id="lesson-animals-001",
        review_criterion="Respond to a new variation with less support.",
    )


def test_accept_existing_initial_profile_lesson() -> None:
    validate_initial_profile_plan_lesson(
        build_initial_profile_plan(),
        [build_recommended_lesson()],
    )


def test_reject_duplicate_initial_profile_lesson_ids() -> None:
    with pytest.raises(
        ValueError,
        match="Initial profile lessons must have unique identifiers",
    ):
        validate_initial_profile_plan_lesson(
            build_initial_profile_plan(),
            [
                build_recommended_lesson(),
                build_recommended_lesson(),
            ],
        )


def test_reject_missing_initial_profile_lesson() -> None:
    with pytest.raises(
        ValueError,
        match="Initial profile first lesson must exist",
    ):
        validate_initial_profile_plan_lesson(
            build_initial_profile_plan(),
            [
                build_recommended_lesson(
                    lesson_id="lesson-space-001"
                )
            ],
        )


def test_reject_initial_profile_lesson_without_experience() -> None:
    lesson = Lesson(
        id="lesson-animals-001",
        title="Talk about animals",
    )

    with pytest.raises(
        ValueError,
        match=(
            "Initial profile first lesson requires "
            "LessonExperience"
        ),
    ):
        validate_initial_profile_plan_lesson(
            build_initial_profile_plan(),
            [lesson],
        )


def test_generate_provisional_initial_conversational_profile() -> None:
    context = ConversationalDiagnosticContext(
        context_id="context-001",
        diagnostic_session_id="diagnostic-001",
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=True,
    )
    activities = [
        ConversationalDiagnosticActivity(
            activity_id="activity-supported",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="prompt-supported",
            stage="guided_construction",
            communicative_intention="Produce one supported response.",
            modality="voice",
            expected_evidence_type="supported_production",
            available_supports=["visual"],
            sequence_order=1,
        ),
        ConversationalDiagnosticActivity(
            activity_id="activity-context",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="prompt-context",
            stage="context_selection",
            communicative_intention="Select one motivating context.",
            modality="selection",
            expected_evidence_type="motivating_context",
            available_supports=[],
            sequence_order=2,
        ),
    ]
    observations = [
        ConversationalDiagnosticObservation(
            observation_id="observation-priority",
            diagnostic_session_id="diagnostic-001",
            activity_id="activity-supported",
            production_id=1,
            dimension="support_need",
            evidence_role="priority_blockage",
            description="Needs support to expand oral responses.",
            support_level="minimal",
            observer_id="deterministic-diagnostic-observer",
            observer_version="1.0",
            observed_at=STARTED_AT,
        ),
        build_relevant_context_observation(),
    ]

    profile, links = generate_initial_conversational_profile(
        profile_id="profile-provisional-001",
        session=build_finished_session("provisional"),
        context=context,
        activities=activities,
        observations=observations,
        plan=build_initial_profile_plan(),
        lessons=[build_recommended_lesson()],
        generated_at=STARTED_AT,
        generator_id="deterministic-profile-generator",
        generator_version="1.0",
    )

    assert profile.status == "provisional"
    assert profile.priority_blockage == (
        "Needs support to expand oral responses."
    )
    assert profile.relevant_contexts == ["animals"]
    assert profile.evidence_summary == (
        "2 diagnostic observations linked."
    )
    assert len(links) == 2


def test_reject_confirmed_profile_with_incomplete_evidence() -> None:
    context = ConversationalDiagnosticContext(
        context_id="context-001",
        diagnostic_session_id="diagnostic-001",
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=True,
    )
    activities = [
        ConversationalDiagnosticActivity(
            activity_id="activity-supported",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="prompt-supported",
            stage="guided_construction",
            communicative_intention="Produce one supported response.",
            modality="voice",
            expected_evidence_type="supported_production",
            available_supports=["visual"],
            sequence_order=1,
        ),
        ConversationalDiagnosticActivity(
            activity_id="activity-context",
            diagnostic_session_id="diagnostic-001",
            context_id="context-001",
            prompt_id="prompt-context",
            stage="context_selection",
            communicative_intention="Select one motivating context.",
            modality="selection",
            expected_evidence_type="motivating_context",
            sequence_order=2,
        ),
    ]
    observations = [
        build_profile_observation(),
        build_relevant_context_observation(),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "Confirmed profile requires complete "
            "diagnostic evidence"
        ),
    ):
        generate_initial_conversational_profile(
            profile_id="profile-confirmed-001",
            session=build_finished_session("completed"),
            context=context,
            activities=activities,
            observations=observations,
            plan=build_initial_profile_plan(),
            lessons=[build_recommended_lesson()],
            generated_at=STARTED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )


def test_reject_profile_context_from_another_session() -> None:
    context = ConversationalDiagnosticContext(
        context_id="context-other-session",
        diagnostic_session_id="diagnostic-other",
        usual_languages=["Spanish"],
        previous_english_contact="School classes",
        general_interests=["animals"],
        learning_goals=["speak with confidence"],
        autonomy_level="developing",
        responsible_adult_present=True,
        audio_authorized=True,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Diagnostic context must belong to "
            "the diagnostic session"
        ),
    ):
        generate_initial_conversational_profile(
            profile_id="profile-invalid-context",
            session=build_finished_session("completed"),
            context=context,
            activities=[],
            observations=[],
            plan=build_initial_profile_plan(),
            lessons=[build_recommended_lesson()],
            generated_at=STARTED_AT,
            generator_id="deterministic-profile-generator",
            generator_version="1.0",
        )
