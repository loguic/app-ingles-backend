from datetime import datetime

from app.schemas.content import Lesson

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
    InitialConversationalProfilePlan,
    InitialConversationalProfileStatus,
)



from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_context_references,
    validate_diagnostic_session_context,
    validate_initial_profile_evidence,
)

def resolve_initial_profile_status(
    session: ConversationalDiagnosticSession,
) -> InitialConversationalProfileStatus:
    """Resolve the revisable profile status from the session.

    Resuelve el estado revisable del perfil desde la sesión.
    """
    if session.status == "completed":
        return "confirmed"

    if session.status == "provisional":
        return "provisional"

    raise ValueError(
        "Diagnostic session status cannot generate "
        "an initial conversational profile"
    )


def resolve_priority_blockage_observation(
    observations: list[ConversationalDiagnosticObservation],
) -> ConversationalDiagnosticObservation:
    """Return the single explicitly declared priority blockage.

    Devuelve el único bloqueo prioritario declarado explícitamente.
    """
    priority_observations = [
        observation
        for observation in observations
        if observation.evidence_role == "priority_blockage"
    ]

    if not priority_observations:
        raise ValueError(
            "Initial profile requires one priority blockage observation"
        )

    if len(priority_observations) > 1:
        raise ValueError(
            "Initial profile cannot have multiple "
            "priority blockage observations"
        )

    return priority_observations[0]


def resolve_relevant_contexts(
    observations: list[ConversationalDiagnosticObservation],
) -> list[str]:
    """Return unique explicitly referenced motivating contexts.

    Devuelve contextos motivadores únicos y referenciados explícitamente.
    """
    relevant_contexts: list[str] = []

    for observation in observations:
        if observation.evidence_role != "context_relevance":
            continue

        assert observation.context_reference is not None
        context_reference = observation.context_reference.strip()

        if context_reference not in relevant_contexts:
            relevant_contexts.append(context_reference)

    if not relevant_contexts:
        raise ValueError(
            "Initial profile requires one relevant context observation"
        )

    return relevant_contexts


def build_initial_profile_evidence_links(
    profile_id: str,
    observations: list[ConversationalDiagnosticObservation],
) -> list[InitialConversationalProfileEvidence]:
    """Build ordered traceability links for one initial profile.

    Construye enlaces ordenados de trazabilidad para un perfil inicial.
    """
    if not observations:
        raise ValueError(
            "Initial profile evidence links require observations"
        )

    observation_ids = [
        observation.observation_id
        for observation in observations
    ]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError(
            "Initial profile evidence links require "
            "unique observation identifiers"
        )

    return [
        InitialConversationalProfileEvidence(
            profile_id=profile_id,
            observation_id=observation_id,
        )
        for observation_id in observation_ids
    ]


def generate_initial_conversational_profile(
    profile_id: str,
    session: ConversationalDiagnosticSession,
    context: ConversationalDiagnosticContext,
    activities: list[ConversationalDiagnosticActivity],
    observations: list[ConversationalDiagnosticObservation],
    plan: InitialConversationalProfilePlan,
    lessons: list[Lesson],
    generated_at: datetime,
    generator_id: str,
    generator_version: str,
) -> tuple[
    InitialConversationalProfile,
    list[InitialConversationalProfileEvidence],
]:
    """Generate one traceable and revisable initial profile.

    Genera un perfil inicial trazable y revisable.
    """
    validate_diagnostic_session_context(
        session,
        context,
    )
    validate_diagnostic_context_references(
        context,
        observations,
    )
    validate_initial_profile_plan_lesson(
        plan,
        lessons,
    )

    priority_observation = (
        resolve_priority_blockage_observation(observations)
    )
    relevant_contexts = resolve_relevant_contexts(observations)
    status = resolve_initial_profile_status(session)

    profile = InitialConversationalProfile(
        profile_id=profile_id,
        diagnostic_session_id=session.diagnostic_session_id,
        status=status,
        priority_blockage=priority_observation.description,
        target_capacity=plan.target_capacity,
        recommended_support_level=(
            plan.recommended_support_level
        ),
        relevant_contexts=relevant_contexts,
        recommended_method=plan.recommended_method,
        first_lesson_id=plan.first_lesson_id,
        review_criterion=plan.review_criterion,
        evidence_summary=(
            str(len(observations))
            + " diagnostic observations linked."
        ),
        generated_at=generated_at,
        generator_id=generator_id,
        generator_version=generator_version,
    )

    evidence_links = build_initial_profile_evidence_links(
        profile_id,
        observations,
    )

    validate_initial_profile_evidence(
        session,
        profile,
        activities,
        observations,
        evidence_links,
    )

    return profile, evidence_links


def validate_initial_profile_plan_lesson(
    plan: InitialConversationalProfilePlan,
    lessons: list[Lesson],
) -> None:
    """Validate the first recommended lesson from explicit content.

    Valida la primera lección recomendada contra contenido explícito.
    """
    lesson_ids = [lesson.id for lesson in lessons]

    if len(lesson_ids) != len(set(lesson_ids)):
        raise ValueError(
            "Initial profile lessons must have unique identifiers"
        )

    lessons_by_id = {
        lesson.id: lesson
        for lesson in lessons
    }
    lesson = lessons_by_id.get(plan.first_lesson_id)

    if lesson is None:
        raise ValueError(
            "Initial profile first lesson must exist"
        )

    if lesson.experience is None:
        raise ValueError(
            "Initial profile first lesson requires LessonExperience"
        )
