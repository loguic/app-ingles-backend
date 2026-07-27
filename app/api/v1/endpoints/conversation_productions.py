from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation_production import (
    ConversationProductionSubmission,
    ConversationProductionSubmissionRecord,
)
from app.schemas.production_audio import ProductionAudioUploadRecord
from app.services.conversation_production_persistence_service import (
    get_active_conversation_production_submissions_by_user,
    save_active_conversation_production_submission,
)
from app.services.production_audio_storage_service import (
    MAX_PRODUCTION_AUDIO_BYTES,
    store_production_audio,
)


router = APIRouter()


@router.post(
    "/conversation-production-audio",
    response_model=ProductionAudioUploadRecord,
)
async def create_conversation_production_audio(
    audio: UploadFile = File(...),
) -> ProductionAudioUploadRecord:
    """Store one learner WAV before production submission.

    Almacena un WAV del estudiante antes de enviar la producción.
    """
    try:
        payload = await audio.read(
            MAX_PRODUCTION_AUDIO_BYTES + 1
        )
        return store_production_audio(payload)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    finally:
        await audio.close()


@router.post(
    "/conversation-productions",
    response_model=ConversationProductionSubmissionRecord,
)
def create_conversation_production(
    record: ConversationProductionSubmission,
    db: Session = Depends(get_db),
) -> ConversationProductionSubmissionRecord:
    """Save one production belonging to active content.

    Guarda una producción perteneciente al contenido activo.
    """
    try:
        return save_active_conversation_production_submission(
            record,
            db,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get(
    "/conversation-productions/{user_id}",
    response_model=list[ConversationProductionSubmissionRecord],
)
def read_conversation_productions(
    user_id: str,
    db: Session = Depends(get_db),
) -> list[ConversationProductionSubmissionRecord]:
    """Read productions that still belong to active content.

    Lee producciones que todavía pertenecen al contenido activo.
    """
    return get_active_conversation_production_submissions_by_user(
        user_id,
        db,
    )
