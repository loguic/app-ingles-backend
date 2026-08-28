from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import ExperienceAttempt
from app.schemas.experience_attempt import (
    ExperienceAttemptRecord,
    ExperienceAttemptStart,
    ExperienceEvidencePendingRecord,
)
from app.services.content_service import get_lesson_context_by_id


def _resolve_experience_context(
    level_id: str,
    unit_id: str,
    lesson_id: str,
):
    """Resolve one persisted hierarchy to a lesson experience.

    Resuelve una jerarquía persistida hacia una experiencia de lección.
    """
    context = get_lesson_context_by_id(lesson_id)
    if context is None:
        raise ValueError(
            "Experience hierarchy does not match the content tree"
        )

    resolved_level_id, resolved_unit_id, lesson = context
    if (
        resolved_level_id != level_id
        or resolved_unit_id != unit_id
        or lesson.id != lesson_id
    ):
        raise ValueError(
            "Experience hierarchy does not match the content tree"
        )

    if lesson.experience is None:
        raise ValueError(f"Lesson '{lesson_id}' has no experience")

    return lesson


def _pending_evidence_states(lesson) -> list[ExperienceEvidencePendingRecord]:
    """Derive B184.1 pending evidence in completion-policy order.

    Deriva las evidencias pendientes B184.1 en orden de completion policy.
    """
    experience = lesson.experience
    if experience is None:  # pragma: no cover - guarded by resolver.
        raise ValueError(f"Lesson '{lesson.id}' has no experience")

    definitions_by_id = {
        definition.id: definition
        for definition in experience.evidence_definitions
    }

    return [
        ExperienceEvidencePendingRecord(
            evidence_definition_id=evidence_id,
            evidence_type=definitions_by_id[evidence_id].evidence_type,
        )
        for evidence_id in experience.completion_policy.required_evidence_ids
    ]


def _record_from_model(
    attempt: ExperienceAttempt,
    lesson,
) -> ExperienceAttemptRecord:
    return ExperienceAttemptRecord(
        attempt_id=attempt.attempt_id,
        user_id=attempt.user_id,
        level_id=attempt.level_id,
        unit_id=attempt.unit_id,
        lesson_id=attempt.lesson_id,
        experience_contract_version=attempt.experience_contract_version,
        status=attempt.status,
        started_at=attempt.started_at,
        completed_at=attempt.completed_at,
        evidence_states=_pending_evidence_states(lesson),
    )


def _active_attempt_query(
    command: ExperienceAttemptStart,
    experience_contract_version: str,
    db: Session,
):
    return db.query(ExperienceAttempt).filter(
        ExperienceAttempt.user_id == command.user_id,
        ExperienceAttempt.level_id == command.level_id,
        ExperienceAttempt.unit_id == command.unit_id,
        ExperienceAttempt.lesson_id == command.lesson_id,
        ExperienceAttempt.experience_contract_version
        == experience_contract_version,
        ExperienceAttempt.status == "in_progress",
    )


def start_or_resume_experience_attempt(
    command: ExperienceAttemptStart,
    db: Session,
) -> ExperienceAttemptRecord:
    """Return the active attempt or atomically create one.

    Devuelve el intento activo o crea uno de forma atómica.
    """
    lesson = _resolve_experience_context(
        command.level_id,
        command.unit_id,
        command.lesson_id,
    )
    experience = lesson.experience
    if experience is None:  # pragma: no cover - guarded by resolver.
        raise ValueError(f"Lesson '{command.lesson_id}' has no experience")

    active_query = _active_attempt_query(
        command,
        experience.contract_version,
        db,
    )
    existing = active_query.one_or_none()
    if existing is not None:
        return _record_from_model(existing, lesson)

    attempt = ExperienceAttempt(
        attempt_id=uuid4().hex,
        user_id=command.user_id,
        level_id=command.level_id,
        unit_id=command.unit_id,
        lesson_id=command.lesson_id,
        experience_contract_version=experience.contract_version,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
        completed_at=None,
    )

    try:
        db.add(attempt)
        db.flush()
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = _active_attempt_query(
            command,
            experience.contract_version,
            db,
        ).one_or_none()
        if existing is not None:
            return _record_from_model(existing, lesson)
        raise
    except SQLAlchemyError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    db.refresh(attempt)
    return _record_from_model(attempt, lesson)


def get_experience_attempt_state(
    attempt_id: str,
    db: Session,
) -> ExperienceAttemptRecord | None:
    """Read one authoritative attempt without changing its lifecycle.

    Lee un intento autoritativo sin alterar su ciclo de vida.
    """
    attempt = db.get(ExperienceAttempt, attempt_id)
    if attempt is None:
        return None

    lesson = _resolve_experience_context(
        attempt.level_id,
        attempt.unit_id,
        attempt.lesson_id,
    )
    experience = lesson.experience
    if experience is None:  # pragma: no cover - guarded by resolver.
        raise ValueError(f"Lesson '{attempt.lesson_id}' has no experience")

    if experience.contract_version != attempt.experience_contract_version:
        raise ValueError(
            "Experience hierarchy does not match the content tree"
        )

    return _record_from_model(attempt, lesson)
