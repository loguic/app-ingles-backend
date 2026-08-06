from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    ConversationalDiagnosticActivity as ActivityModel,
    ConversationalDiagnosticActivityProduction as ActivityProductionModel,
    ConversationalDiagnosticContext as ContextModel,
    ConversationalDiagnosticObservation as ObservationModel,
    ConversationalDiagnosticObservationEvaluation as ObservationEvaluationModel,
    ConversationalDiagnosticSession as SessionModel,
    ConversationalDiagnosticSupportUsage as SupportUsageModel,
    LearnerProduction as LearnerProductionModel,
    ProductionEvaluationResult as EvaluationResultModel,
)
from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
)
from app.schemas.conversational_diagnostic_persistence import (
    ConversationalDiagnosticActivityProductionSetup,
    ConversationalDiagnosticObservationsBatch,
    ConversationalDiagnosticProductionSupportsBatch,
    ConversationalDiagnosticSessionTransition,
    ConversationalDiagnosticSessionSetup,
)
from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_activity_production,
    validate_diagnostic_activity_context,
    validate_diagnostic_activity_sequence,
    validate_diagnostic_context_references,
    validate_completed_diagnostic_evidence,
    validate_diagnostic_observation,
    validate_diagnostic_observation_evaluations,
    validate_diagnostic_observation_support,
    validate_diagnostic_session_context,
    validate_diagnostic_session_status_transition,
    validate_diagnostic_support_sequence,
)


class ConversationalDiagnosticPersistenceError(RuntimeError):
    """Base error for diagnostic persistence operations.

    Error base de las operaciones de persistencia diagnóstica.
    """


class DiagnosticSessionAlreadyExistsError(
    ConversationalDiagnosticPersistenceError
):
    """Report an existing diagnostic session identifier.

    Informa un identificador de sesión diagnóstica existente.
    """


class DiagnosticReferenceNotFoundError(
    ConversationalDiagnosticPersistenceError
):
    """Report a diagnostic aggregate that cannot be found.

    Informa un agregado diagnóstico que no puede encontrarse.
    """


class DiagnosticPersistenceInvariantError(
    ConversationalDiagnosticPersistenceError
):
    """Report an invalid or conflicting persistence invariant.

    Informa un invariante de persistencia inválido o conflictivo.
    """


def _validate_setup(setup: ConversationalDiagnosticSessionSetup) -> None:
    if (
        setup.session.status != "in_progress"
        or setup.session.completed_at is not None
    ):
        raise ValueError(
            "New diagnostic sessions must start in progress"
        )
    validate_diagnostic_session_context(setup.session, setup.context)
    validate_diagnostic_activity_sequence(setup.session, setup.activities)
    for activity in setup.activities:
        validate_diagnostic_activity_context(
            setup.session,
            setup.context,
            activity,
        )


def _session_contract(session: SessionModel) -> ConversationalDiagnosticSession:
    return ConversationalDiagnosticSession(
        diagnostic_session_id=session.diagnostic_session_id,
        user_id=session.user_id,
        age_profile=session.age_profile,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
    )


def _activity_contract(
    activity: ActivityModel,
) -> ConversationalDiagnosticActivity:
    return ConversationalDiagnosticActivity(
        activity_id=activity.activity_id,
        diagnostic_session_id=activity.diagnostic_session_id,
        context_id=activity.context_id,
        prompt_id=activity.prompt_id,
        stage=activity.stage,
        communicative_intention=activity.communicative_intention,
        modality=activity.modality,
        expected_evidence_type=activity.expected_evidence_type,
        available_supports=list(activity.available_supports),
        transfer_variant_id=activity.transfer_variant_id,
        sequence_order=activity.sequence_order,
    )


def _context_contract(context: ContextModel) -> ConversationalDiagnosticContext:
    return ConversationalDiagnosticContext(
        context_id=context.context_id,
        diagnostic_session_id=context.diagnostic_session_id,
        usual_languages=list(context.usual_languages),
        previous_english_contact=context.previous_english_contact,
        general_interests=list(context.general_interests),
        learning_goals=list(context.learning_goals),
        autonomy_level=context.autonomy_level,
        responsible_adult_present=context.responsible_adult_present,
        audio_authorized=context.audio_authorized,
    )


def _support_contract(usage: SupportUsageModel) -> DiagnosticSupportUsage:
    return DiagnosticSupportUsage(
        diagnostic_session_id=usage.diagnostic_session_id,
        activity_id=usage.activity_id,
        production_id=usage.production_id,
        support_type=usage.support_type,
        support_level=usage.support_level,
        sequence_order=usage.sequence_order,
        provided_at=usage.provided_at,
        withdrawn_afterward=usage.withdrawn_afterward,
    )


def _build_setup(
    session: SessionModel,
    context: ContextModel,
    activities: list[ActivityModel],
    associations: list[ActivityProductionModel],
    usages: list[SupportUsageModel],
    observations: list[ObservationModel],
    observation_evaluations: list[ObservationEvaluationModel],
) -> ConversationalDiagnosticSessionSetup:
    """Reconstruct contracts without retaining ORM-backed state.

    Reconstruye contratos sin conservar estado dependiente del ORM.
    """
    return ConversationalDiagnosticSessionSetup(
        session=_session_contract(session),
        context=_context_contract(context),
        activities=[_activity_contract(activity) for activity in activities],
        production_supports=[
            ConversationalDiagnosticActivityProductionSetup(
                diagnostic_session_id=association.diagnostic_session_id,
                activity_id=association.activity_id,
                production_id=association.production_id,
                support_usages=[
                    _support_contract(usage)
                    for usage in usages
                    if usage.activity_id == association.activity_id
                    and usage.production_id == association.production_id
                ],
            )
            for association in associations
        ],
        observations=[
            ConversationalDiagnosticObservation(
                observation_id=observation.observation_id,
                diagnostic_session_id=observation.diagnostic_session_id,
                activity_id=observation.activity_id,
                production_id=observation.production_id,
                evaluation_result_ids=sorted(
                    link.evaluation_result_id
                    for link in observation_evaluations
                    if link.observation_id == observation.observation_id
                ),
                dimension=observation.dimension,
                evidence_role=observation.evidence_role,
                context_reference=observation.context_reference,
                description=observation.description,
                support_level=observation.support_level,
                observer_id=observation.observer_id,
                observer_version=observation.observer_version,
                observed_at=observation.observed_at,
            )
            for observation in observations
        ],
    )


def _load_setup_models(
    diagnostic_session_id: str,
    db: Session,
) -> tuple[
    SessionModel,
    ContextModel,
    list[ActivityModel],
    list[ActivityProductionModel],
    list[SupportUsageModel],
    list[ObservationModel],
    list[ObservationEvaluationModel],
]:
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.diagnostic_session_id == diagnostic_session_id
        )
        .one_or_none()
    )
    if session is None:
        raise DiagnosticReferenceNotFoundError(
            "Diagnostic session does not exist"
        )

    context = (
        db.query(ContextModel)
        .filter(
            ContextModel.diagnostic_session_id == diagnostic_session_id
        )
        .one_or_none()
    )
    if context is None:
        raise DiagnosticReferenceNotFoundError(
            "Diagnostic session context does not exist"
        )

    activities = (
        db.query(ActivityModel)
        .filter(
            ActivityModel.diagnostic_session_id == diagnostic_session_id
        )
        .order_by(
            ActivityModel.sequence_order.asc(),
            ActivityModel.activity_id.asc(),
        )
        .all()
    )
    if not activities:
        raise DiagnosticReferenceNotFoundError(
            "Diagnostic session activities do not exist"
        )
    associations = (
        db.query(ActivityProductionModel)
        .join(
            ActivityModel,
            (
                ActivityModel.diagnostic_session_id
                == ActivityProductionModel.diagnostic_session_id
            )
            & (ActivityModel.activity_id == ActivityProductionModel.activity_id),
        )
        .filter(
            ActivityProductionModel.diagnostic_session_id
            == diagnostic_session_id
        )
        .order_by(
            ActivityModel.sequence_order.asc(),
            ActivityProductionModel.activity_id.asc(),
            ActivityProductionModel.production_id.asc(),
        )
        .all()
    )
    usages = (
        db.query(SupportUsageModel)
        .join(
            ActivityModel,
            (
                ActivityModel.diagnostic_session_id
                == SupportUsageModel.diagnostic_session_id
            )
            & (ActivityModel.activity_id == SupportUsageModel.activity_id),
        )
        .filter(
            SupportUsageModel.diagnostic_session_id
            == diagnostic_session_id
        )
        .order_by(
            ActivityModel.sequence_order.asc(),
            SupportUsageModel.activity_id.asc(),
            SupportUsageModel.production_id.asc(),
            SupportUsageModel.sequence_order.asc(),
            SupportUsageModel.provided_at.asc(),
            SupportUsageModel.id.asc(),
        )
        .all()
    )
    observations = (
        db.query(ObservationModel)
        .join(
            ActivityModel,
            (
                ActivityModel.diagnostic_session_id
                == ObservationModel.diagnostic_session_id
            )
            & (ActivityModel.activity_id == ObservationModel.activity_id),
        )
        .filter(
            ObservationModel.diagnostic_session_id == diagnostic_session_id
        )
        .order_by(
            ActivityModel.sequence_order.asc(),
            ObservationModel.activity_id.asc(),
            ObservationModel.observed_at.asc(),
            ObservationModel.observation_id.asc(),
        )
        .all()
    )
    observation_evaluations = (
        db.query(ObservationEvaluationModel)
        .filter(
            ObservationEvaluationModel.diagnostic_session_id
            == diagnostic_session_id
        )
        .order_by(
            ObservationEvaluationModel.observation_id.asc(),
            ObservationEvaluationModel.evaluation_result_id.asc(),
        )
        .all()
    )
    return (
        session,
        context,
        activities,
        associations,
        usages,
        observations,
        observation_evaluations,
    )


def _reject_existing_identifiers(
    setup: ConversationalDiagnosticSessionSetup,
    db: Session,
) -> None:
    if (
        db.query(SessionModel.diagnostic_session_id)
        .filter(
            SessionModel.diagnostic_session_id
            == setup.session.diagnostic_session_id
        )
        .first()
        is not None
    ):
        raise DiagnosticSessionAlreadyExistsError(
            "Diagnostic session identifier already exists"
        )

    if (
        db.query(ContextModel.context_id)
        .filter(ContextModel.context_id == setup.context.context_id)
        .first()
        is not None
    ):
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic context identifier already exists"
        )

    activity_ids = [item.activity_id for item in setup.activities]
    existing_activity = (
        db.query(ActivityModel.activity_id)
        .filter(ActivityModel.activity_id.in_(activity_ids))
        .first()
    )
    if existing_activity is not None:
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic activity identifier already exists"
        )


def _prepare_production_supports(
    session: ConversationalDiagnosticSession,
    activities: list[ConversationalDiagnosticActivity],
    associations: list[ConversationalDiagnosticActivityProductionSetup],
    db: Session,
) -> list[ConversationalDiagnosticActivityProductionSetup]:
    """Resolve persisted productions and validate the complete support history.

    Resuelve producciones persistidas y valida el historial completo de apoyos.
    """
    if not associations:
        return []

    activity_by_id = {activity.activity_id: activity for activity in activities}
    for association in associations:
        if association.diagnostic_session_id != session.diagnostic_session_id:
            raise ValueError(
                "Diagnostic production must belong to the diagnostic session"
            )
        if association.activity_id not in activity_by_id:
            raise DiagnosticReferenceNotFoundError(
                "Diagnostic activity does not exist in the session"
            )

    production_ids = [association.production_id for association in associations]
    if len(production_ids) != len(set(production_ids)):
        raise ValueError("Diagnostic production identifiers must be unique")

    productions = (
        db.query(LearnerProductionModel)
        .filter(LearnerProductionModel.id.in_(production_ids))
        .all()
    )
    production_by_id = {production.id: production for production in productions}
    missing_ids = sorted(set(production_ids) - set(production_by_id))
    if missing_ids:
        raise DiagnosticReferenceNotFoundError(
            "Referenced learner production does not exist"
        )

    existing_owner = (
        db.query(ActivityProductionModel.production_id)
        .filter(ActivityProductionModel.production_id.in_(production_ids))
        .first()
    )
    if existing_owner is not None:
        raise DiagnosticPersistenceInvariantError(
            "Learner production is already associated"
        )

    for association in associations:
        activity = activity_by_id[association.activity_id]
        production = production_by_id[association.production_id]
        validate_diagnostic_activity_production(
            activity,
            LearnerProductionRecord(
                production_id=production.id,
                prompt_id=production.prompt_id,
                turn_id=production.turn_id,
                modality=production.modality,
                response_text=production.response_text,
                audio_reference=production.audio_reference,
            ),
        )
        for usage in association.support_usages:
            if (
                usage.diagnostic_session_id != session.diagnostic_session_id
                or usage.activity_id != association.activity_id
                or usage.production_id != association.production_id
            ):
                raise ValueError(
                    "Diagnostic support identifiers must match its association"
                )

    existing_usages = (
        db.query(SupportUsageModel)
        .filter(
            SupportUsageModel.diagnostic_session_id
            == session.diagnostic_session_id
        )
        .all()
    )
    for activity_id, activity in activity_by_id.items():
        combined = [
            _support_contract(usage)
            for usage in existing_usages
            if usage.activity_id == activity_id
        ]
        combined.extend(
            usage
            for association in associations
            if association.activity_id == activity_id
            for usage in association.support_usages
        )
        combined.sort(
            key=lambda usage: (
                usage.sequence_order,
                usage.provided_at.isoformat(),
                usage.production_id,
            )
        )
        validate_diagnostic_support_sequence(session, activity, combined)

    activity_order = {
        activity.activity_id: activity.sequence_order for activity in activities
    }
    return sorted(
        associations,
        key=lambda association: (
            activity_order[association.activity_id],
            association.activity_id,
            association.production_id,
        ),
    )


def _add_production_supports(
    associations: list[ConversationalDiagnosticActivityProductionSetup],
    activities: dict[str, ConversationalDiagnosticActivity],
    db: Session,
) -> None:
    for association in associations:
        db.add(
            ActivityProductionModel(
                diagnostic_session_id=association.diagnostic_session_id,
                activity_id=association.activity_id,
                production_id=association.production_id,
                prompt_id=activities[association.activity_id].prompt_id,
            )
        )
    if associations:
        db.flush()

    usages = [
        usage
        for association in associations
        for usage in association.support_usages
    ]
    for usage in sorted(
        usages,
        key=lambda item: (
            item.sequence_order,
            item.provided_at.isoformat(),
            item.activity_id,
            item.production_id,
        ),
    ):
        db.add(
            SupportUsageModel(
                diagnostic_session_id=usage.diagnostic_session_id,
                activity_id=usage.activity_id,
                production_id=usage.production_id,
                support_type=usage.support_type,
                support_level=usage.support_level,
                sequence_order=usage.sequence_order,
                provided_at=usage.provided_at,
                withdrawn_afterward=usage.withdrawn_afterward,
            )
        )
    if associations:
        db.flush()


def _association_contracts(
    associations: list[ActivityProductionModel],
    usages: list[SupportUsageModel],
) -> list[ConversationalDiagnosticActivityProductionSetup]:
    return [
        ConversationalDiagnosticActivityProductionSetup(
            diagnostic_session_id=association.diagnostic_session_id,
            activity_id=association.activity_id,
            production_id=association.production_id,
            support_usages=[
                _support_contract(usage)
                for usage in usages
                if usage.activity_id == association.activity_id
                and usage.production_id == association.production_id
            ],
        )
        for association in associations
    ]


def _evaluation_contract(
    evaluation: EvaluationResultModel,
) -> ProductionEvaluationResultRecord:
    return ProductionEvaluationResultRecord(
        evaluation_result_id=evaluation.id,
        production_id=evaluation.production_id,
        criterion_id=evaluation.criterion_id,
        status=evaluation.status,
        score=evaluation.score,
        evaluator_id=evaluation.evaluator_id,
        evaluator_version=evaluation.evaluator_version,
        evaluated_at=evaluation.evaluated_at,
    )


def _prepare_observations(
    session: ConversationalDiagnosticSession,
    context: ConversationalDiagnosticContext,
    activities: list[ConversationalDiagnosticActivity],
    associations: list[ConversationalDiagnosticActivityProductionSetup],
    observations: list[ConversationalDiagnosticObservation],
    db: Session,
) -> list[ConversationalDiagnosticObservation]:
    """Resolve and validate observation traceability before any write.

    Resuelve y valida la trazabilidad de observaciones antes de escribir.
    """
    if not observations:
        return []

    observation_ids = [item.observation_id for item in observations]
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("Diagnostic observation identifiers must be unique")
    for observation in observations:
        if len(observation.evaluation_result_ids) != len(
            set(observation.evaluation_result_ids)
        ):
            raise ValueError(
                "Diagnostic evaluation identifiers must be unique"
            )

    existing_observation = (
        db.query(ObservationModel.observation_id)
        .filter(ObservationModel.observation_id.in_(observation_ids))
        .first()
    )
    if existing_observation is not None:
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic observation identifier already exists"
        )

    activity_by_id = {activity.activity_id: activity for activity in activities}
    owner_by_production = {
        association.production_id: association for association in associations
    }
    production_ids = {
        observation.production_id
        for observation in observations
        if observation.production_id is not None
    }
    productions = (
        db.query(LearnerProductionModel)
        .filter(LearnerProductionModel.id.in_(production_ids))
        .all()
        if production_ids
        else []
    )
    production_by_id = {production.id: production for production in productions}
    if production_ids - set(production_by_id):
        raise DiagnosticReferenceNotFoundError(
            "Referenced learner production does not exist"
        )

    evaluation_ids = {
        evaluation_id
        for observation in observations
        for evaluation_id in observation.evaluation_result_ids
    }
    evaluations = (
        db.query(EvaluationResultModel)
        .filter(EvaluationResultModel.id.in_(evaluation_ids))
        .all()
        if evaluation_ids
        else []
    )
    evaluation_by_id = {
        evaluation.id: evaluation for evaluation in evaluations
    }
    if evaluation_ids - set(evaluation_by_id):
        raise DiagnosticReferenceNotFoundError(
            "Referenced production evaluation does not exist"
        )

    validate_diagnostic_context_references(context, observations)
    for observation in observations:
        activity = activity_by_id.get(observation.activity_id)
        if activity is None:
            raise DiagnosticReferenceNotFoundError(
                "Diagnostic observation activity does not exist"
            )
        validate_diagnostic_observation(session, activity, observation)

        matching_usages: list[DiagnosticSupportUsage] = []
        if observation.production_id is not None:
            owner = owner_by_production.get(observation.production_id)
            if owner is None:
                raise DiagnosticReferenceNotFoundError(
                    "Diagnostic activity-production association does not exist"
                )
            if owner.activity_id != observation.activity_id:
                raise ValueError(
                    "Diagnostic observation production belongs to another activity"
                )
            production = production_by_id[observation.production_id]
            validate_diagnostic_activity_production(
                activity,
                LearnerProductionRecord(
                    production_id=production.id,
                    prompt_id=production.prompt_id,
                    turn_id=production.turn_id,
                    modality=production.modality,
                    response_text=production.response_text,
                    audio_reference=production.audio_reference,
                ),
                observation,
            )
            matching_usages = list(owner.support_usages)

        validate_diagnostic_observation_support(
            session,
            activity,
            observation,
            matching_usages,
        )
        validate_diagnostic_observation_evaluations(
            observation,
            [
                _evaluation_contract(evaluation_by_id[evaluation_id])
                for evaluation_id in observation.evaluation_result_ids
            ],
        )

    activity_order = {
        activity.activity_id: activity.sequence_order for activity in activities
    }
    return sorted(
        observations,
        key=lambda observation: (
            activity_order[observation.activity_id],
            observation.activity_id,
            observation.observed_at.isoformat(),
            observation.observation_id,
        ),
    )


def _add_observations(
    observations: list[ConversationalDiagnosticObservation],
    db: Session,
) -> None:
    for observation in observations:
        db.add(
            ObservationModel(
                observation_id=observation.observation_id,
                diagnostic_session_id=observation.diagnostic_session_id,
                activity_id=observation.activity_id,
                production_id=observation.production_id,
                dimension=observation.dimension,
                evidence_role=observation.evidence_role,
                context_reference=observation.context_reference,
                description=observation.description,
                support_level=observation.support_level,
                observer_id=observation.observer_id,
                observer_version=observation.observer_version,
                observed_at=observation.observed_at,
            )
        )
    if observations:
        db.flush()

    for observation in sorted(
        observations,
        key=lambda item: item.observation_id,
    ):
        for evaluation_result_id in sorted(observation.evaluation_result_ids):
            assert observation.production_id is not None
            db.add(
                ObservationEvaluationModel(
                    diagnostic_session_id=observation.diagnostic_session_id,
                    observation_id=observation.observation_id,
                    evaluation_result_id=evaluation_result_id,
                    production_id=observation.production_id,
                )
            )
    if observations:
        db.flush()


def save_conversational_diagnostic_session_setup(
    setup: ConversationalDiagnosticSessionSetup,
    db: Session,
) -> ConversationalDiagnosticSessionSetup:
    """Validate and persist one diagnostic setup atomically.

    Valida y persiste una configuración diagnóstica de forma atómica.
    """
    try:
        _validate_setup(setup)
        with db.no_autoflush:
            _reject_existing_identifiers(setup, db)
            prepared_associations = _prepare_production_supports(
                setup.session,
                setup.activities,
                setup.production_supports,
                db,
            )
            prepared_observations = _prepare_observations(
                setup.session,
                setup.context,
                setup.activities,
                prepared_associations,
                setup.observations,
                db,
            )

        session = SessionModel(
            diagnostic_session_id=setup.session.diagnostic_session_id,
            user_id=setup.session.user_id,
            age_profile=setup.session.age_profile,
            status=setup.session.status,
            started_at=setup.session.started_at,
            completed_at=setup.session.completed_at,
        )
        db.add(session)
        db.flush()

        context = ContextModel(
            context_id=setup.context.context_id,
            diagnostic_session_id=setup.context.diagnostic_session_id,
            usual_languages=list(setup.context.usual_languages),
            previous_english_contact=setup.context.previous_english_contact,
            general_interests=list(setup.context.general_interests),
            learning_goals=list(setup.context.learning_goals),
            autonomy_level=setup.context.autonomy_level,
            responsible_adult_present=setup.context.responsible_adult_present,
            audio_authorized=setup.context.audio_authorized,
        )
        db.add(context)
        db.flush()

        for item in sorted(
            setup.activities,
            key=lambda activity: (
                activity.sequence_order,
                activity.activity_id,
            ),
        ):
            db.add(
                ActivityModel(
                    activity_id=item.activity_id,
                    diagnostic_session_id=item.diagnostic_session_id,
                    context_id=item.context_id,
                    prompt_id=item.prompt_id,
                    stage=item.stage,
                    communicative_intention=item.communicative_intention,
                    modality=item.modality,
                    expected_evidence_type=item.expected_evidence_type,
                    available_supports=list(item.available_supports),
                    transfer_variant_id=item.transfer_variant_id,
                    sequence_order=item.sequence_order,
                )
            )
        db.flush()
        _add_production_supports(
            prepared_associations,
            {activity.activity_id: activity for activity in setup.activities},
            db,
        )
        _add_observations(prepared_observations, db)
        persisted = _build_setup(*_load_setup_models(
            setup.session.diagnostic_session_id,
            db,
        ))
        db.commit()
        return persisted
    except (
        DiagnosticSessionAlreadyExistsError,
        DiagnosticReferenceNotFoundError,
        DiagnosticPersistenceInvariantError,
    ):
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic setup violates a persistence invariant"
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic setup conflicts with persisted data"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise ConversationalDiagnosticPersistenceError(
            "Diagnostic setup could not be persisted"
        ) from exc
    except Exception:
        db.rollback()
        raise


def save_conversational_diagnostic_production_supports(
    batch: ConversationalDiagnosticProductionSupportsBatch,
    db: Session,
) -> ConversationalDiagnosticSessionSetup:
    """Enrich an existing session with production ownership atomically.

    Enriquece atómicamente una sesión existente con propiedad de producciones.
    """
    try:
        (
            session_model,
            _context,
            activity_models,
            _associations,
            _usages,
            _observations,
            _observation_evaluations,
        ) = _load_setup_models(batch.diagnostic_session_id, db)
        session = _session_contract(session_model)
        activities = [
            _activity_contract(activity) for activity in activity_models
        ]
        with db.no_autoflush:
            prepared_associations = _prepare_production_supports(
                session,
                activities,
                batch.associations,
                db,
            )
        _add_production_supports(
            prepared_associations,
            {activity.activity_id: activity for activity in activities},
            db,
        )
        persisted = _build_setup(
            *_load_setup_models(batch.diagnostic_session_id, db)
        )
        db.commit()
        return persisted
    except (
        DiagnosticReferenceNotFoundError,
        DiagnosticPersistenceInvariantError,
    ):
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic production support batch violates an invariant"
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic production support batch conflicts with persisted data"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise ConversationalDiagnosticPersistenceError(
            "Diagnostic production support batch could not be persisted"
        ) from exc
    except Exception:
        db.rollback()
        raise


def save_conversational_diagnostic_observations(
    batch: ConversationalDiagnosticObservationsBatch,
    db: Session,
) -> ConversationalDiagnosticSessionSetup:
    """Enrich an existing session with observations atomically.

    Enriquece atómicamente una sesión existente con observaciones.
    """
    try:
        (
            session_model,
            context_model,
            activity_models,
            association_models,
            usage_models,
            _observations,
            _observation_evaluations,
        ) = _load_setup_models(batch.diagnostic_session_id, db)
        session = _session_contract(session_model)
        context = _context_contract(context_model)
        activities = [
            _activity_contract(activity) for activity in activity_models
        ]
        associations = _association_contracts(
            association_models,
            usage_models,
        )
        with db.no_autoflush:
            prepared_observations = _prepare_observations(
                session,
                context,
                activities,
                associations,
                batch.observations,
                db,
            )
        _add_observations(prepared_observations, db)
        persisted = _build_setup(
            *_load_setup_models(batch.diagnostic_session_id, db)
        )
        db.commit()
        return persisted
    except (
        DiagnosticReferenceNotFoundError,
        DiagnosticPersistenceInvariantError,
    ):
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic observation batch violates an invariant"
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic observation batch conflicts with persisted data"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise ConversationalDiagnosticPersistenceError(
            "Diagnostic observation batch could not be persisted"
        ) from exc
    except Exception:
        db.rollback()
        raise


def transition_conversational_diagnostic_session(
    command: ConversationalDiagnosticSessionTransition,
    db: Session,
) -> ConversationalDiagnosticSession:
    """Apply one explicit state transition with optimistic concurrency.

    Aplica una transición explícita con concurrencia optimista.
    """
    try:
        session_model = (
            db.query(SessionModel)
            .filter(
                SessionModel.diagnostic_session_id
                == command.diagnostic_session_id
            )
            .one_or_none()
        )
        if session_model is None:
            raise DiagnosticReferenceNotFoundError(
                "Diagnostic session does not exist"
            )
        if session_model.status != command.expected_current_status:
            raise DiagnosticPersistenceInvariantError(
                "Diagnostic session status differs from the expected state"
            )

        validate_diagnostic_session_status_transition(
            command.expected_current_status,
            command.target_status,
        )
        if command.transitioned_at < session_model.started_at:
            raise ValueError(
                "Diagnostic session transition cannot precede started_at"
            )
        if (
            session_model.completed_at is not None
            and command.transitioned_at < session_model.completed_at
        ):
            raise ValueError(
                "Diagnostic session transition cannot precede its prior close"
            )

        if command.target_status == "completed":
            persisted = _build_setup(
                *_load_setup_models(command.diagnostic_session_id, db)
            )
            validate_completed_diagnostic_evidence(
                persisted.activities,
                persisted.observations,
            )

        rowcount = (
            db.query(SessionModel)
            .filter(
                SessionModel.diagnostic_session_id
                == command.diagnostic_session_id,
                SessionModel.status == command.expected_current_status,
            )
            .update(
                {
                    SessionModel.status: command.target_status,
                    SessionModel.completed_at: command.transitioned_at,
                },
                synchronize_session=False,
            )
        )
        if rowcount != 1:
            raise DiagnosticPersistenceInvariantError(
                "Diagnostic session transition lost its expected state"
            )

        transitioned_model = (
            db.query(SessionModel)
            .populate_existing()
            .filter(
                SessionModel.diagnostic_session_id
                == command.diagnostic_session_id
            )
            .one()
        )
        transitioned = _session_contract(transitioned_model)
        db.commit()
        return transitioned
    except (
        DiagnosticReferenceNotFoundError,
        DiagnosticPersistenceInvariantError,
    ):
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic session transition violates an invariant"
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise DiagnosticPersistenceInvariantError(
            "Diagnostic session transition conflicts with persisted data"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise ConversationalDiagnosticPersistenceError(
            "Diagnostic session transition could not be persisted"
        ) from exc
    except Exception:
        db.rollback()
        raise


def get_conversational_diagnostic_session_setup(
    diagnostic_session_id: str,
    db: Session,
) -> ConversationalDiagnosticSessionSetup:
    """Return one fully reconstructed diagnostic setup.

    Devuelve una configuración diagnóstica completamente reconstruida.
    """
    return _build_setup(*_load_setup_models(diagnostic_session_id, db))
