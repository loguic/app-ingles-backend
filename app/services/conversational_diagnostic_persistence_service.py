from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

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
from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_activity_context,
    validate_diagnostic_activity_sequence,
    validate_diagnostic_session_context,
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
    validate_diagnostic_session_context(setup.session, setup.context)
    validate_diagnostic_activity_sequence(setup.session, setup.activities)
    for activity in setup.activities:
        validate_diagnostic_activity_context(
            setup.session,
            setup.context,
            activity,
        )


def _build_setup(
    session: SessionModel,
    context: ContextModel,
    activities: list[ActivityModel],
) -> ConversationalDiagnosticSessionSetup:
    """Reconstruct contracts without retaining ORM-backed state.

    Reconstruye contratos sin conservar estado dependiente del ORM.
    """
    return ConversationalDiagnosticSessionSetup(
        session=ConversationalDiagnosticSession(
            diagnostic_session_id=session.diagnostic_session_id,
            user_id=session.user_id,
            age_profile=session.age_profile,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
        ),
        context=ConversationalDiagnosticContext(
            context_id=context.context_id,
            diagnostic_session_id=context.diagnostic_session_id,
            usual_languages=list(context.usual_languages),
            previous_english_contact=context.previous_english_contact,
            general_interests=list(context.general_interests),
            learning_goals=list(context.learning_goals),
            autonomy_level=context.autonomy_level,
            responsible_adult_present=context.responsible_adult_present,
            audio_authorized=context.audio_authorized,
        ),
        activities=[
            ConversationalDiagnosticActivity(
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
            for activity in activities
        ],
    )


def _load_setup_models(
    diagnostic_session_id: str,
    db: Session,
) -> tuple[SessionModel, ContextModel, list[ActivityModel]]:
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
    return session, context, activities


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
        persisted = _build_setup(*_load_setup_models(
            setup.session.diagnostic_session_id,
            db,
        ))
        db.commit()
        return persisted
    except (
        DiagnosticSessionAlreadyExistsError,
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


def get_conversational_diagnostic_session_setup(
    diagnostic_session_id: str,
    db: Session,
) -> ConversationalDiagnosticSessionSetup:
    """Return one fully reconstructed diagnostic setup.

    Devuelve una configuración diagnóstica completamente reconstruida.
    """
    return _build_setup(*_load_setup_models(diagnostic_session_id, db))
