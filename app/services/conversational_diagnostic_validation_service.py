from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationResultRecord

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
    DiagnosticSessionStatus,
    InitialConversationalProfile,
    InitialConversationalProfileEvidence,
)


_DIAGNOSTIC_SESSION_TRANSITIONS = {
    ("in_progress", "provisional"),
    ("in_progress", "completed"),
    ("in_progress", "cancelled"),
    ("provisional", "completed"),
    ("provisional", "cancelled"),
}


def validate_diagnostic_session_status_transition(
    expected_current_status: DiagnosticSessionStatus,
    target_status: DiagnosticSessionStatus,
) -> None:
    """Validate the closed diagnostic session state machine.

    Valida la máquina cerrada de estados de la sesión diagnóstica.
    """
    if (expected_current_status, target_status) not in (
        _DIAGNOSTIC_SESSION_TRANSITIONS
    ):
        raise ValueError("Diagnostic session status transition is not allowed")


def validate_completed_diagnostic_evidence(
    activities: list[ConversationalDiagnosticActivity],
    observations: list[ConversationalDiagnosticObservation],
    requirement_label: str = "Completed diagnostic session",
) -> None:
    """Require observations for every diagnostic evidence type.

    Exige observaciones para cada tipo de evidencia diagnóstica.
    """
    activity_by_id = {
        activity.activity_id: activity for activity in activities
    }
    if len(activity_by_id) != len(activities):
        raise ValueError(
            "Diagnostic activities must have unique identifiers"
        )
    if any(
        observation.activity_id not in activity_by_id
        for observation in observations
    ):
        raise ValueError(
            "Diagnostic observation references an unknown activity"
        )
    required_evidence_types = {
        "comprehension",
        "spontaneous_production",
        "supported_production",
        "connected_exchange",
        "transfer",
        "motivating_context",
    }
    observed_evidence_types = {
        activity_by_id[observation.activity_id].expected_evidence_type
        for observation in observations
        if observation.activity_id in activity_by_id
    }
    missing_evidence_types = sorted(
        required_evidence_types - observed_evidence_types
    )
    if missing_evidence_types:
        raise ValueError(
            requirement_label + " requires complete diagnostic evidence: "
            + ", ".join(missing_evidence_types)
        )


def validate_diagnostic_session_context(
    session: ConversationalDiagnosticSession,
    context: ConversationalDiagnosticContext,
) -> None:
    """Validate that context belongs to the diagnostic session.

    Valida que el contexto pertenezca a la sesión diagnóstica.
    """
    if context.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic context must belong to the diagnostic session"
        )


def validate_diagnostic_activity_context(
    session: ConversationalDiagnosticSession,
    context: ConversationalDiagnosticContext,
    activity: ConversationalDiagnosticActivity,
) -> None:
    """Validate activity ownership and contextual traceability.

    Valida la pertenencia y trazabilidad contextual de la actividad.
    """
    validate_diagnostic_session_context(session, context)

    if activity.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic activity must belong to the diagnostic session"
        )

    if activity.context_id != context.context_id:
        raise ValueError(
            "Diagnostic activity must use the diagnostic context"
        )

    if activity.modality == "voice" and not context.audio_authorized:
        raise ValueError(
            "Voice diagnostic activity requires audio authorization"
        )


def validate_diagnostic_support_usage(
    session: ConversationalDiagnosticSession,
    activity: ConversationalDiagnosticActivity,
    usage: DiagnosticSupportUsage,
) -> None:
    """Validate support ownership and activity availability.

    Valida la pertenencia del apoyo y su disponibilidad en la actividad.
    """
    if usage.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic support must belong to the diagnostic session"
        )

    if usage.activity_id != activity.activity_id:
        raise ValueError(
            "Diagnostic support must belong to the diagnostic activity"
        )

    if activity.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic activity must belong to the diagnostic session"
        )

    if (
        usage.support_type != "none"
        and usage.support_type not in activity.available_supports
    ):
        raise ValueError(
            "Used diagnostic support must be available in the activity"
        )


def validate_diagnostic_observation(
    session: ConversationalDiagnosticSession,
    activity: ConversationalDiagnosticActivity,
    observation: ConversationalDiagnosticObservation,
) -> None:
    """Validate observation ownership and evidence traceability.

    Valida la pertenencia y trazabilidad de la observación.
    """
    if activity.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic activity must belong to the diagnostic session"
        )

    if observation.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Diagnostic observation must belong to the diagnostic session"
        )

    if observation.activity_id != activity.activity_id:
        raise ValueError(
            "Diagnostic observation must belong to the diagnostic activity"
        )

    if (
        observation.evaluation_result_ids
        and observation.production_id is None
    ):
        raise ValueError(
            "Diagnostic evaluations require an observed production"
        )

    production_required_dimensions = {
        "response_initiation",
        "direct_english_construction",
        "oral_production",
        "continuity",
        "linguistic_retrieval",
        "intelligibility",
        "support_need",
        "transfer",
    }

    if (
        observation.dimension in production_required_dimensions
        and observation.production_id is None
    ):
        raise ValueError(
            "Diagnostic observation dimension requires a production"
        )


def validate_initial_conversational_profile_session(
    session: ConversationalDiagnosticSession,
    profile: InitialConversationalProfile,
) -> None:
    """Validate profile ownership and diagnostic session state.

    Valida la pertenencia del perfil y el estado de la sesión diagnóstica.
    """
    if profile.diagnostic_session_id != session.diagnostic_session_id:
        raise ValueError(
            "Initial conversational profile must belong to "
            "the diagnostic session"
        )

    if session.status == "in_progress":
        raise ValueError(
            "In-progress diagnostic session cannot generate a profile"
        )

    if session.status == "cancelled":
        raise ValueError(
            "Cancelled diagnostic session cannot generate a profile"
        )

    if (
        profile.status == "confirmed"
        and session.status != "completed"
    ):
        raise ValueError(
            "Confirmed profile requires a completed diagnostic session"
        )

    if (
        profile.status == "provisional"
        and session.status != "provisional"
    ):
        raise ValueError(
            "Provisional profile requires a provisional diagnostic session"
        )


def validate_initial_profile_evidence(
    session: ConversationalDiagnosticSession,
    profile: InitialConversationalProfile,
    activities: list[ConversationalDiagnosticActivity],
    observations: list[ConversationalDiagnosticObservation],
    evidence_links: list[InitialConversationalProfileEvidence],
) -> None:
    """Validate profile evidence ownership and traceability.

    Valida la pertenencia y trazabilidad de las evidencias del perfil.
    """
    validate_initial_conversational_profile_session(session, profile)

    activity_ids = [
        activity.activity_id
        for activity in activities
    ]
    if len(activity_ids) != len(set(activity_ids)):
        raise ValueError(
            "Diagnostic activities must have unique identifiers"
        )

    for activity in activities:
        if activity.diagnostic_session_id != session.diagnostic_session_id:
            raise ValueError(
                "Profile activities must belong to the diagnostic session"
            )

    observation_ids = [
        observation.observation_id
        for observation in observations
    ]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError(
            "Diagnostic observations must have unique identifiers"
        )

    for observation in observations:
        if (
            observation.diagnostic_session_id
            != session.diagnostic_session_id
        ):
            raise ValueError(
                "Profile observations must belong to "
                "the diagnostic session"
            )

        if observation.activity_id not in activity_ids:
            raise ValueError(
                "Profile observation references an unknown activity"
            )

    linked_observation_ids: list[str] = []

    for link in evidence_links:
        if link.profile_id != profile.profile_id:
            raise ValueError(
                "Profile evidence must reference the initial profile"
            )

        if link.observation_id not in observation_ids:
            raise ValueError(
                "Profile evidence references an unknown observation"
            )

        linked_observation_ids.append(link.observation_id)

    if len(linked_observation_ids) != len(
        set(linked_observation_ids)
    ):
        raise ValueError(
            "Profile evidence cannot repeat observations"
        )

    if not linked_observation_ids:
        raise ValueError(
            "Initial conversational profile requires evidence"
        )

    if profile.status == "confirmed":
        observations_by_id = {
            observation.observation_id: observation
            for observation in observations
        }
        validate_completed_diagnostic_evidence(
            activities,
            [
                observations_by_id[observation_id]
                for observation_id in linked_observation_ids
            ],
            requirement_label="Confirmed profile",
        )


def validate_diagnostic_activity_sequence(
    session: ConversationalDiagnosticSession,
    activities: list[ConversationalDiagnosticActivity],
) -> None:
    """Validate ownership and deterministic activity ordering.

    Valida la pertenencia y el orden determinista de las actividades.
    """
    activity_ids = [activity.activity_id for activity in activities]
    if len(activity_ids) != len(set(activity_ids)):
        raise ValueError(
            "Diagnostic activities must have unique identifiers"
        )

    sequence_orders = [
        activity.sequence_order
        for activity in activities
    ]
    if len(sequence_orders) != len(set(sequence_orders)):
        raise ValueError(
            "Diagnostic activities must have unique sequence orders"
        )

    for activity in activities:
        if activity.diagnostic_session_id != session.diagnostic_session_id:
            raise ValueError(
                "Diagnostic activities must belong to "
                "the diagnostic session"
            )

    if sequence_orders != sorted(sequence_orders):
        raise ValueError(
            "Diagnostic activities must follow sequence order"
        )


def validate_diagnostic_support_sequence(
    session: ConversationalDiagnosticSession,
    activity: ConversationalDiagnosticActivity,
    usages: list[DiagnosticSupportUsage],
) -> None:
    """Validate ordered support use and later support reduction.

    Valida el uso ordenado y la reducción posterior de apoyos.
    """
    for usage in usages:
        validate_diagnostic_support_usage(
            session,
            activity,
            usage,
        )

    sequence_orders = [
        usage.sequence_order
        for usage in usages
    ]
    if len(sequence_orders) != len(set(sequence_orders)):
        raise ValueError(
            "Diagnostic supports must have unique sequence orders"
        )

    if sequence_orders != sorted(sequence_orders):
        raise ValueError(
            "Diagnostic supports must follow sequence order"
        )

    usages_by_production: dict[int, list[DiagnosticSupportUsage]] = {}
    for usage in usages:
        usages_by_production.setdefault(
            usage.production_id,
            [],
        ).append(usage)

    for production_usages in usages_by_production.values():
        if (
            len(production_usages) > 1
            and any(
                usage.support_type == "none"
                for usage in production_usages
            )
        ):
            raise ValueError(
                "No-support usage cannot be combined with other supports"
            )

    support_level_rank = {
        "none": 0,
        "minimal": 1,
        "moderate": 2,
        "full": 3,
    }

    for index, usage in enumerate(usages):
        if not usage.withdrawn_afterward:
            continue

        later_usages = usages[index + 1 :]
        if not any(
            later.production_id != usage.production_id
            and support_level_rank[later.support_level]
            < support_level_rank[usage.support_level]
            for later in later_usages
        ):
            raise ValueError(
                "Withdrawn support requires a later production "
                "with lower support level"
            )


def validate_diagnostic_observation_support(
    session: ConversationalDiagnosticSession,
    activity: ConversationalDiagnosticActivity,
    observation: ConversationalDiagnosticObservation,
    usages: list[DiagnosticSupportUsage],
) -> None:
    """Validate observed support against support actually used.

    Valida el apoyo observado frente al apoyo realmente utilizado.
    """
    validate_diagnostic_observation(
        session,
        activity,
        observation,
    )

    if observation.production_id is None:
        if usages:
            raise ValueError(
                "Observation without production cannot reference supports"
            )

        if observation.support_level != "none":
            raise ValueError(
                "Observation without production requires none support level"
            )

        return

    matching_usages = [
        usage
        for usage in usages
        if (
            usage.diagnostic_session_id
            == session.diagnostic_session_id
            and usage.activity_id == activity.activity_id
            and usage.production_id == observation.production_id
        )
    ]

    if len(matching_usages) != len(usages):
        raise ValueError(
            "Observation supports must belong to its session, "
            "activity and production"
        )

    support_level_rank = {
        "none": 0,
        "minimal": 1,
        "moderate": 2,
        "full": 3,
    }
    expected_support_level = (
        "none"
        if not matching_usages
        else max(
            matching_usages,
            key=lambda usage: support_level_rank[usage.support_level],
        ).support_level
    )

    if observation.support_level != expected_support_level:
        raise ValueError(
            "Diagnostic observation support level must match "
            "the support actually used"
        )


def validate_diagnostic_activity_production(
    activity: ConversationalDiagnosticActivity,
    production: LearnerProductionRecord,
    observation: ConversationalDiagnosticObservation | None = None,
) -> None:
    """Validate production origin and optional observation traceability.

    Valida el origen de la producción y la trazabilidad de la observación.
    """
    if production.prompt_id != activity.prompt_id:
        raise ValueError(
            "Diagnostic production must match the activity prompt"
        )

    if activity.modality not in {"text", "voice"}:
        raise ValueError(
            "Diagnostic activity modality does not capture "
            "a learner production"
        )

    if production.modality != activity.modality:
        raise ValueError(
            "Diagnostic production modality must match "
            "the diagnostic activity"
        )

    if (
        observation is not None
        and observation.production_id != production.production_id
    ):
        raise ValueError(
            "Diagnostic observation must reference the learner production"
        )


def validate_diagnostic_observation_evaluations(
    observation: ConversationalDiagnosticObservation,
    evaluations: list[ProductionEvaluationResultRecord],
) -> None:
    """Validate technical evaluations referenced by an observation.

    Valida las evaluaciones técnicas referenciadas por una observación.
    """
    evaluation_ids = [
        evaluation.evaluation_result_id
        for evaluation in evaluations
    ]
    if len(evaluation_ids) != len(set(evaluation_ids)):
        raise ValueError(
            "Diagnostic evaluations must have unique identifiers"
        )

    if set(evaluation_ids) != set(
        observation.evaluation_result_ids
    ):
        raise ValueError(
            "Diagnostic observation evaluations must match "
            "the referenced evaluation identifiers"
        )

    if evaluations and observation.production_id is None:
        raise ValueError(
            "Diagnostic evaluations require an observed production"
        )

    for evaluation in evaluations:
        if evaluation.production_id != observation.production_id:
            raise ValueError(
                "Diagnostic evaluation must belong to "
                "the observed production"
            )


def validate_diagnostic_production_activity_ownership(
    observations: list[ConversationalDiagnosticObservation],
) -> None:
    """Ensure each production belongs to only one diagnostic activity.

    Garantiza que cada producción pertenezca a una sola actividad diagnóstica.
    """
    activity_by_production: dict[int, str] = {}

    for observation in observations:
        if observation.production_id is None:
            continue

        previous_activity_id = activity_by_production.setdefault(
            observation.production_id,
            observation.activity_id,
        )
        if previous_activity_id != observation.activity_id:
            raise ValueError(
                "Diagnostic production cannot be reused "
                "across different activities"
            )


def validate_diagnostic_context_references(
    context: ConversationalDiagnosticContext,
    observations: list[ConversationalDiagnosticObservation],
) -> None:
    """Validate motivating-context references against authorized context.

    Valida las referencias motivadoras contra el contexto autorizado.
    """
    available_contexts = {
        value.strip()
        for value in context.general_interests
    }

    for observation in observations:
        if observation.evidence_role != "context_relevance":
            continue

        if (
            observation.diagnostic_session_id
            != context.diagnostic_session_id
        ):
            raise ValueError(
                "Context observation must belong to "
                "the diagnostic context session"
            )

        assert observation.context_reference is not None
        if observation.context_reference.strip() not in available_contexts:
            raise ValueError(
                "Diagnostic context reference must exist "
                "in authorized general interests"
            )
