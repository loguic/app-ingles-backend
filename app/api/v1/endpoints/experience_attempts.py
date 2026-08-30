from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.experience_attempt import (
    ExperienceAttemptRecord,
    ExperienceAttemptStart,
    ExperienceComprehensionResponseCreate,
    ExperienceComprehensionResponseRecord,
)
from app.services.content_service import (
    get_level_by_code,
    get_lesson_by_id,
    get_unit_by_id,
)
from app.services.experience_attempt_service import (
    get_experience_attempt_state,
    save_experience_comprehension_response,
    start_or_resume_experience_attempt,
)


router = APIRouter()


@router.post(
    "/experience-attempts/{attempt_id}/comprehension-responses/"
    "{comprehension_exercise_id}",
    response_model=ExperienceComprehensionResponseRecord,
)
def create_experience_comprehension_response(
    attempt_id: str,
    comprehension_exercise_id: str,
    command: ExperienceComprehensionResponseCreate,
    db: Session = Depends(get_db),
) -> ExperienceComprehensionResponseRecord:
    """Persist one backend-graded comprehension source."""
    try:
        return save_experience_comprehension_response(
            attempt_id,
            comprehension_exercise_id,
            command.selected_index,
            db,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _require_start_resources(command: ExperienceAttemptStart) -> None:
    """Preserve resource and hierarchy HTTP conventions for start/resume.

    Conserva las convenciones HTTP de recursos y jerarquía al iniciar/reanudar.
    """
    level = get_level_by_code(command.level_id)
    if level is None:
        raise HTTPException(
            status_code=404,
            detail=f"Level '{command.level_id}' not found",
        )

    unit = get_unit_by_id(command.unit_id)
    if unit is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unit '{command.unit_id}' not found",
        )

    lesson = get_lesson_by_id(command.lesson_id)
    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail=f"Lesson '{command.lesson_id}' not found",
        )

    if not any(item.id == unit.id for item in level.units) or not any(
        item.id == lesson.id for item in unit.lessons
    ):
        raise HTTPException(
            status_code=400,
            detail="Experience hierarchy does not match the content tree",
        )

    if lesson.experience is None:
        raise HTTPException(
            status_code=400,
            detail=f"Lesson '{command.lesson_id}' has no experience",
        )


@router.post(
    "/experience-attempts",
    response_model=ExperienceAttemptRecord,
)
def start_or_resume_attempt(
    command: ExperienceAttemptStart,
    db: Session = Depends(get_db),
) -> ExperienceAttemptRecord:
    """Start or resume one authoritative lesson experience attempt.

    Inicia o reanuda un intento autoritativo de experiencia de lección.
    """
    _require_start_resources(command)
    try:
        return start_or_resume_experience_attempt(command, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/experience-attempts/{attempt_id}",
    response_model=ExperienceAttemptRecord,
)
def read_experience_attempt(
    attempt_id: str,
    db: Session = Depends(get_db),
) -> ExperienceAttemptRecord:
    """Read authoritative lifecycle state for one experience attempt.

    Lee el estado autoritativo de ciclo de vida de un intento.
    """
    try:
        record = get_experience_attempt_state(attempt_id, db)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Experience attempt '{attempt_id}' not found",
        )

    return record
