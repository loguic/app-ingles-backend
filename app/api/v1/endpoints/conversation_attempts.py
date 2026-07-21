from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation_attempt import (
    ConversationAttemptCreate,
    ConversationAttemptRecord,
)
from app.services.conversation_attempt_service import (
    get_conversation_attempts_by_user,
    save_conversation_attempt,
)


router = APIRouter()


@router.post(
    "/conversation-attempts",
    response_model=ConversationAttemptRecord,
)
def create_conversation_attempt(
    record: ConversationAttemptCreate,
    db: Session = Depends(get_db),
) -> ConversationAttemptRecord:
    """Save one validated completed conversation attempt.
    Guarda un intento conversacional completado y validado.
    """
    try:
        return save_conversation_attempt(record, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/conversation-attempts/{user_id}",
    response_model=list[ConversationAttemptRecord],
)
def read_conversation_attempts(
    user_id: str,
    db: Session = Depends(get_db),
) -> list[ConversationAttemptRecord]:
    """Read all saved conversation attempts for one user.
    Lee todos los intentos conversacionales guardados de un usuario.
    """
    return get_conversation_attempts_by_user(user_id, db)
