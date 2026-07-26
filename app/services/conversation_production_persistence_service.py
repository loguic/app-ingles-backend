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
from app.services.conversation_production_validation import (
    validate_conversation_production_submission,
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


def save_conversation_production_submission(
    record: ConversationProductionSubmission,
    conversation: Conversation,
    db: Session,
) -> ConversationProductionSubmissionRecord:
    """Validate and persist one complete submission atomically.

    Valida y persiste una entrega completa de forma atómica.
    """
    validate_conversation_production_submission(
        record,
        conversation,
    )

    submission = SubmissionModel(
        user_id=record.user_id,
        level_id=record.level_id,
        unit_id=record.unit_id,
        lesson_id=record.lesson_id,
        conversation_id=record.conversation_id,
    )
    productions: list[ProductionModel] = []

    try:
        db.add(submission)
        db.flush()

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
        db.refresh(submission)

        result = _build_submission_record(
            submission,
            productions,
        )
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return result


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
