"""Security boundary and persistence for isolated A1 v4 demo practice."""

import hashlib
import json
import secrets
from collections import defaultdict
from contextlib import nullcontext
from datetime import datetime, timezone
from threading import Lock
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import A1V4PracticeAudio, A1V4PracticeProduction, A1V4PracticeSession
from app.schemas.a1_v4_practice_session import (
    ACTIVITY_IDS,
    A1V4PracticeSessionCreate,
    A1V4PracticeSessionRecord,
    A1V4PracticeSessionSave,
    A1V4PracticeProductionRecord,
)
from app.services.production_audio_storage_service import store_production_audio


class A1V4PracticeAuthorizationError(PermissionError):
    pass


class A1V4PracticeConflictError(ValueError):
    pass


_sqlite_save_locks_guard = Lock()
_sqlite_save_locks: defaultdict[str, Lock] = defaultdict(Lock)


def _as_utc(value: datetime | None) -> datetime | None:
    """SQLite drops timezone metadata for ``DateTime(timezone=True)`` values."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(request: A1V4PracticeSessionCreate, db: Session) -> tuple[A1V4PracticeSession, str]:
    token = secrets.token_urlsafe(32)
    session = A1V4PracticeSession(
        session_id=str(uuid4()),
        declared_user_id=request.user_id.strip(),
        token_hash=_token_hash(token),
        created_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session, token


def require_session(session_id: UUID, token: str | None, db: Session) -> A1V4PracticeSession:
    if not token:
        raise A1V4PracticeAuthorizationError("Practice session token is required")
    session = db.get(A1V4PracticeSession, str(session_id))
    if session is None:
        raise A1V4PracticeAuthorizationError("Practice session credentials are invalid")
    if not secrets.compare_digest(session.token_hash, _token_hash(token)):
        raise A1V4PracticeAuthorizationError("Practice session credentials are invalid")
    return session


def upload_audio(session: A1V4PracticeSession, payload: bytes, db: Session):
    upload = store_production_audio(payload)
    db.add(A1V4PracticeAudio(session_id=session.session_id, audio_reference=upload.audio_reference))
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return upload


def _canonical_content(save: A1V4PracticeSessionSave) -> str:
    payload = [item.model_dump(mode="json") for item in save.productions]
    return json.dumps(sorted(payload, key=lambda item: item["activity_id"]), sort_keys=True, separators=(",", ":"))


def _record(session: A1V4PracticeSession, db: Session) -> A1V4PracticeSessionRecord:
    productions = db.query(A1V4PracticeProduction).filter_by(session_id=session.session_id).all()
    by_id = {item.activity_id: item for item in productions}
    return A1V4PracticeSessionRecord(
        session_id=UUID(session.session_id),
        declared_user_id=session.declared_user_id,
        practice_completed=set(by_id) == set(ACTIVITY_IDS)
        and all(
            isinstance(by_id[activity_id].client_evaluation, dict)
            and by_id[activity_id].client_evaluation.get("semantic_status") == "adequate"
            for activity_id in ACTIVITY_IDS
        ),
        saved=session.saved_at is not None,
        created_at=_as_utc(session.created_at),
        saved_at=_as_utc(session.saved_at),
        productions=[
            A1V4PracticeProductionRecord(
                activity_id=activity_id,
                audio_reference=by_id[activity_id].audio_reference,
                transcript=by_id[activity_id].transcript,
                client_evaluation=by_id[activity_id].client_evaluation,
                backend_verified_evidence={"audio_linked_to_session": True},
            )
            for activity_id in ACTIVITY_IDS
            if activity_id in by_id
        ],
    )


def save_session(session: A1V4PracticeSession, save: A1V4PracticeSessionSave, db: Session) -> A1V4PracticeSessionRecord:
    canonical = _canonical_content(save)
    content_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    dialect = db.get_bind().dialect.name
    if dialect == "sqlite":
        with _sqlite_save_locks_guard:
            sqlite_lock = _sqlite_save_locks[session.session_id]
        transaction_lock = sqlite_lock
    else:
        transaction_lock = nullcontext()

    with transaction_lock:
        locked_session = (
            db.query(A1V4PracticeSession)
            .filter_by(session_id=session.session_id)
            .with_for_update()
            .populate_existing()
            .one()
        )
        if locked_session.content_hash is not None:
            if secrets.compare_digest(locked_session.content_hash, content_hash):
                return _record(locked_session, db)
            raise A1V4PracticeConflictError(
                "Practice session has already been saved with different content"
            )

        linked_references = {
            value[0]
            for value in db.query(A1V4PracticeAudio.audio_reference)
            .filter_by(session_id=locked_session.session_id)
            .all()
        }
        if any(item.audio_reference not in linked_references for item in save.productions):
            raise ValueError("Audio reference is not linked to this practice session")

        try:
            for item in save.productions:
                db.add(A1V4PracticeProduction(
                    session_id=locked_session.session_id,
                    activity_id=item.activity_id,
                    audio_reference=item.audio_reference,
                    transcript=item.transcript,
                    client_evaluation=item.client_evaluation,
                ))
            locked_session.content_hash = content_hash
            locked_session.saved_at = datetime.now(timezone.utc)
            db.flush()
            result = _record(locked_session, db)
            db.commit()
            return result
        except IntegrityError:
            db.rollback()
            persisted = (
                db.query(A1V4PracticeSession)
                .filter_by(session_id=session.session_id)
                .populate_existing()
                .one()
            )
            if persisted.content_hash is not None:
                if secrets.compare_digest(persisted.content_hash, content_hash):
                    return _record(persisted, db)
                raise A1V4PracticeConflictError(
                    "Practice session has already been saved with different content"
                )
            raise
        except Exception:
            db.rollback()
            raise


def read_session(session: A1V4PracticeSession, db: Session) -> A1V4PracticeSessionRecord:
    return _record(session, db)
