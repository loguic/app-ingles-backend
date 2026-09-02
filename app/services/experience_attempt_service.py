from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import ExperienceAttempt, ExperienceComprehensionResponse
from app.schemas.experience_attempt import (
    ExperienceAttemptRecord,
    ExperienceAttemptStart,
    ExperienceComprehensionResponseRecord,
)
from app.services.content_service import (
    get_lesson_context_by_id,
    get_lesson_context_by_id_and_contract_version,
)
from app.services.experience_evidence_service import (
    accredit_evidence_states,
    effective_evidence_records,
    required_evidence_definitions,
    resolve_experience_attempt,
)


def _resolve_experience_context(
    level_id: str,
    unit_id: str,
    lesson_id: str,
    experience_contract_version: str | None = None,
):
    """Resolve one persisted hierarchy to a lesson experience.

    Resuelve una jerarquía persistida hacia una experiencia de lección.
    """
    context = get_lesson_context_by_id(lesson_id)
    if (
        experience_contract_version is not None
        and (
            context is None
            or context[2].experience is None
            or context[2].experience.contract_version
            != experience_contract_version
        )
    ):
        context = get_lesson_context_by_id_and_contract_version(
            lesson_id,
            experience_contract_version,
        )
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

    if (
        experience_contract_version is not None
        and lesson.experience.contract_version != experience_contract_version
    ):
        raise ValueError(
            "Experience hierarchy does not match the content tree"
        )

    return lesson


def _record_from_model(
    attempt: ExperienceAttempt,
    lesson,
    db: Session,
) -> ExperienceAttemptRecord:
    submitted_exercise_ids = {
        exercise_id
        for (exercise_id,) in db.query(
            ExperienceComprehensionResponse.comprehension_exercise_id
        ).filter(
            ExperienceComprehensionResponse.experience_attempt_id
            == attempt.attempt_id
        )
    }
    content_order = [
        evidence.comprehension_exercise_id
        for evidence in required_evidence_definitions(lesson)
        if evidence.evidence_type == "comprehension_result"
        and evidence.comprehension_exercise_id in submitted_exercise_ids
    ]
    ordered_submitted_exercise_ids = content_order + sorted(
        submitted_exercise_ids - set(content_order)
    )
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
        evidence_states=effective_evidence_records(attempt, lesson, db),
        submitted_comprehension_exercise_ids=ordered_submitted_exercise_ids,
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
    ).with_for_update()


def _is_active_attempt_uniqueness_conflict(error: IntegrityError) -> bool:
    """Recognize only the B184.1 one-active-attempt invariant."""
    constraint_name = getattr(
        getattr(error.orig, "diag", None),
        "constraint_name",
        None,
    )
    if constraint_name == "uq_experience_attempt_active_context":
        return True
    message = str(error.orig)
    return (
        "UNIQUE constraint failed: experience_attempts.user_id, "
        "experience_attempts.level_id, experience_attempts.unit_id, "
        "experience_attempts.lesson_id, "
        "experience_attempts.experience_contract_version"
    ) in message


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

    for create_number in range(2):
        existing = _active_attempt_query(
            command,
            experience.contract_version,
            db,
        ).one_or_none()
        if existing is not None:
            record = _record_from_model(existing, lesson, db)
            db.commit()
            return record

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
        except IntegrityError as error:
            db.rollback()
            if not _is_active_attempt_uniqueness_conflict(error):
                raise
            existing = _active_attempt_query(
                command,
                experience.contract_version,
                db,
            ).one_or_none()
            if existing is not None:
                record = _record_from_model(existing, lesson, db)
                db.commit()
                return record
            if create_number == 0:
                continue
            raise
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

        db.refresh(attempt)
        return _record_from_model(attempt, lesson, db)

    raise RuntimeError("Experience attempt retry was exhausted")


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
        attempt.experience_contract_version,
    )
    experience = lesson.experience
    if experience is None:  # pragma: no cover - guarded by resolver.
        raise ValueError(f"Lesson '{attempt.lesson_id}' has no experience")

    if experience.contract_version != attempt.experience_contract_version:
        raise ValueError(
            "Experience hierarchy does not match the content tree"
        )

    return _record_from_model(attempt, lesson, db)


def save_experience_comprehension_response(
    attempt_id: str,
    comprehension_exercise_id: str,
    selected_index: int,
    db: Session,
) -> ExperienceComprehensionResponseRecord:
    """Persist, accredit and possibly complete one comprehension response."""
    try:
        attempt, lesson = resolve_experience_attempt(
            attempt_id,
            db,
            for_update=True,
            require_in_progress=True,
        )
        matches = [
            definition
            for definition in required_evidence_definitions(lesson)
            if definition.evidence_type == "comprehension_result"
            and definition.comprehension_exercise_id
            == comprehension_exercise_id
        ]
        if len(matches) != 1:
            raise ValueError(
                "Comprehension exercise does not map to exactly one required evidence"
            )
        definition = matches[0]
        exercise = next(
            (
                item
                for item in lesson.exercises
                if item.id == comprehension_exercise_id
            ),
            None,
        )
        if exercise is None:
            raise ValueError("Comprehension exercise does not exist")
        if selected_index < 0 or selected_index >= len(exercise.options):
            raise ValueError("Selected comprehension option is out of range")

        submitted_at = datetime.now(timezone.utc)
        response = ExperienceComprehensionResponse(
            response_id=uuid4().hex,
            experience_attempt_id=attempt.attempt_id,
            evidence_definition_id=definition.id,
            activity_id=definition.activity_id,
            comprehension_exercise_id=comprehension_exercise_id,
            selected_index=selected_index,
            is_correct=selected_index == exercise.answer_index,
            submitted_at=submitted_at,
        )
        db.add(response)
        db.flush()
        accredit_evidence_states(
            attempt,
            lesson,
            [
                (
                    definition,
                    "satisfied" if response.is_correct else "pending",
                    "comprehension_response",
                    response.response_id,
                )
            ],
            db,
            accredited_at=submitted_at,
        )
        record = ExperienceComprehensionResponseRecord(
            response_id=response.response_id,
            experience_attempt_id=response.experience_attempt_id,
            evidence_definition_id=response.evidence_definition_id,
            activity_id=response.activity_id,
            comprehension_exercise_id=response.comprehension_exercise_id,
            selected_index=response.selected_index,
            is_correct=response.is_correct,
            submitted_at=response.submitted_at,
        )
        db.commit()
        return record
    except Exception:
        db.rollback()
        raise
