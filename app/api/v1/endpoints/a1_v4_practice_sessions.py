from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.a1_v4_practice_session import A1V4PracticeSessionCreate, A1V4PracticeSessionCreated, A1V4PracticeSessionRecord, A1V4PracticeSessionSave
from app.services.a1_v4_practice_session_service import A1V4PracticeAuthorizationError, A1V4PracticeConflictError, create_session, read_session, require_session, save_session, upload_audio
from app.services.production_audio_storage_service import MAX_PRODUCTION_AUDIO_BYTES


router = APIRouter()


def _authorized(session_id: UUID, token: str | None, db: Session):
    try:
        return require_session(session_id, token, db)
    except A1V4PracticeAuthorizationError as error:
        raise HTTPException(status_code=401 if token is None else 403, detail=str(error)) from error


@router.post("/a1-v4-practice-sessions", response_model=A1V4PracticeSessionCreated)
def create_a1_v4_practice_session(request: A1V4PracticeSessionCreate, db: Session = Depends(get_db)):
    session, token = create_session(request, db)
    return A1V4PracticeSessionCreated(session_id=UUID(session.session_id), token=token)


@router.post("/a1-v4-practice-sessions/{session_id}/audio")
async def upload_a1_v4_practice_audio(session_id: UUID, audio: UploadFile = File(...), x_a1_v4_practice_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    session = _authorized(session_id, x_a1_v4_practice_token, db)
    try:
        return upload_audio(session, await audio.read(MAX_PRODUCTION_AUDIO_BYTES + 1), db)
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        await audio.close()


@router.post("/a1-v4-practice-sessions/{session_id}/save", response_model=A1V4PracticeSessionRecord)
def save_a1_v4_practice_session(session_id: UUID, request: A1V4PracticeSessionSave, x_a1_v4_practice_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    session = _authorized(session_id, x_a1_v4_practice_token, db)
    try:
        return save_session(session, request, db)
    except A1V4PracticeConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/a1-v4-practice-sessions/{session_id}", response_model=A1V4PracticeSessionRecord)
def get_a1_v4_practice_session(session_id: UUID, x_a1_v4_practice_token: str | None = Header(default=None), db: Session = Depends(get_db)):
    return read_session(_authorized(session_id, x_a1_v4_practice_token, db), db)
