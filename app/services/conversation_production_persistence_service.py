from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
)
from app.schemas.content import Conversation
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
    ConversationProductionSubmissionRecord,
    LearnerProductionRecord,
)
from app.services.content_service import (
    get_conversation_context_by_id,
)
from app.services.conversation_production_validation import (
    validate_conversation_production_submission,
)
from app.services.experience_evidence_service import (
    accredit_evidence_states,
    required_evidence_definitions,
    resolve_experience_attempt,
    validate_attempt_source_context,
)
from app.services.production_audio_storage_service import (
    resolve_production_audio_path,
)


def _build_submission_record(
    submission: SubmissionModel,
    productions: list[ProductionModel],
) -> ConversationProductionSubmissionRecord:
    """Reconstruct one persisted submission without evaluating it.

    Reconstruye una entrega persistida sin evaluarla.
    """
    return ConversationProductionSubmissionRecord(
        submission_id=submission.id,
        user_id=submission.user_id,
        level_id=submission.level_id,
        unit_id=submission.unit_id,
        lesson_id=submission.lesson_id,
        conversation_id=submission.conversation_id,
        experience_attempt_id=submission.experience_attempt_id,
        submitted_at=submission.submitted_at,
        productions=[
            LearnerProductionRecord(
                production_id=item.id,
                prompt_id=item.prompt_id,
                turn_id=item.turn_id,
                modality=item.modality,
                response_text=item.response_text,
                audio_reference=item.audio_reference,
            )
            for item in productions
        ],
    )


def _add_validated_conversation_production_submission(
    record: ConversationProductionSubmission,
    conversation: Conversation,
    db: Session,
    *,
    experience_attempt_id: str | None = None,
) -> tuple[SubmissionModel, list[ProductionModel]]:
    """Add one validated submission without owning the transaction.

    Añade una entrega validada sin apropiarse de la transacción.
    """
    submission = SubmissionModel(
        user_id=record.user_id,
        level_id=record.level_id,
        unit_id=record.unit_id,
        lesson_id=record.lesson_id,
        conversation_id=record.conversation_id,
        experience_attempt_id=(
            experience_attempt_id
            if experience_attempt_id is not None
            else record.experience_attempt_id
        ),
    )
    db.add(submission)
    db.flush()

    productions: list[ProductionModel] = []
    for captured in record.productions:
        production = ProductionModel(
            submission_id=submission.id,
            prompt_id=captured.prompt_id,
            turn_id=captured.turn_id,
            modality=captured.modality,
            response_text=captured.response_text,
            audio_reference=captured.audio_reference,
        )
        db.add(production)
        productions.append(production)

    db.flush()
    return submission, productions


def save_active_conversation_production_submission(
    record: ConversationProductionSubmission,
    db: Session,
) -> ConversationProductionSubmissionRecord:
    """Resolve active content and persist one validated submission.

    Resuelve contenido activo y persiste una entrega validada.
    """
    context = get_conversation_context_by_id(
        record.conversation_id
    )
    if context is None:
        raise ValueError("Conversation does not exist")

    level_id, unit_id, lesson_id, conversation = context
    if (
        record.level_id != level_id
        or record.unit_id != unit_id
        or record.lesson_id != lesson_id
    ):
        raise ValueError(
            "Conversation hierarchy does not match the content tree"
        )

    return save_conversation_production_submission(
        record,
        conversation,
        db,
    )

def save_conversation_production_submission(
    record: ConversationProductionSubmission,
    conversation: Conversation,
    db: Session,
) -> ConversationProductionSubmissionRecord:
    """Validate and persist one complete submission atomically.

    Valida y persiste una entrega completa de forma atómica.
    """
    validate_conversation_production_submission(record, conversation)

    try:
        attempt = None
        lesson = None
        evidence_by_prompt = {}
        if record.experience_attempt_id is not None:
            attempt, lesson = resolve_experience_attempt(
                record.experience_attempt_id,
                db,
                for_update=True,
                require_in_progress=True,
            )
            validate_attempt_source_context(
                attempt,
                user_id=record.user_id,
                level_id=record.level_id,
                unit_id=record.unit_id,
                lesson_id=record.lesson_id,
            )
            if not any(
                item.id == record.conversation_id
                for item in lesson.conversations
            ):
                raise ValueError(
                    "Production conversation does not belong to experience"
                )
            definitions = [
                definition
                for definition in required_evidence_definitions(lesson)
                if definition.evidence_type == "contextual_response"
                and definition.activity_id == record.conversation_id
                and definition.production_prompt_id is not None
            ]
            for captured in record.productions:
                matches = [
                    definition
                    for definition in definitions
                    if definition.production_prompt_id == captured.prompt_id
                ]
                if len(matches) != 1:
                    raise ValueError(
                        "Production prompt does not map to exactly one required evidence"
                    )
                definition = matches[0]
                if not definition.external_review_requirements:
                    raise ValueError(
                        "Bound production submission requires review-backed evidence"
                    )
                if captured.modality != "voice" or not captured.audio_reference:
                    raise ValueError(
                        "Review-backed production requires managed voice audio"
                    )
                try:
                    resolve_production_audio_path(captured.audio_reference)
                except (RuntimeError, ValueError, FileNotFoundError) as error:
                    raise ValueError(str(error)) from error
                evidence_by_prompt[captured.prompt_id] = definition

        submission, productions = (
            _add_validated_conversation_production_submission(
                record,
                conversation,
                db,
            )
        )
        if attempt is not None and lesson is not None:
            accredit_evidence_states(
                attempt,
                lesson,
                [
                    (
                        evidence_by_prompt[production.prompt_id],
                        "needs_review",
                        "conversation_production_submission",
                        submission.id,
                    )
                    for production in productions
                ],
                db,
            )
        db.refresh(submission)

        result = _build_submission_record(
            submission,
            productions,
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    return result


def get_active_conversation_production_submissions_by_user(
    user_id: str,
    db: Session,
) -> list[ConversationProductionSubmissionRecord]:
    """Return only submissions belonging to active content.

    Devuelve solo entregas pertenecientes al contenido activo.
    """
    records = get_conversation_production_submissions_by_user(
        user_id,
        db,
    )
    active_records: list[
        ConversationProductionSubmissionRecord
    ] = []

    for record in records:
        context = get_conversation_context_by_id(
            record.conversation_id
        )
        if context is None:
            continue

        level_id, unit_id, lesson_id, _ = context
        if (
            record.level_id == level_id
            and record.unit_id == unit_id
            and record.lesson_id == lesson_id
        ):
            active_records.append(record)

    return active_records

def get_conversation_production_submissions_by_user(
    user_id: str,
    db: Session,
) -> list[ConversationProductionSubmissionRecord]:
    """Return persisted submissions in chronological order.

    Devuelve entregas persistidas en orden cronológico.
    """
    submissions = (
        db.query(SubmissionModel)
        .filter(SubmissionModel.user_id == user_id)
        .order_by(
            SubmissionModel.submitted_at.asc(),
            SubmissionModel.id.asc(),
        )
        .all()
    )

    records: list[ConversationProductionSubmissionRecord] = []

    for submission in submissions:
        productions = (
            db.query(ProductionModel)
            .filter(
                ProductionModel.submission_id == submission.id
            )
            .order_by(ProductionModel.id.asc())
            .all()
        )
        records.append(
            _build_submission_record(submission, productions)
        )

    return records
