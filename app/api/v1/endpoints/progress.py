from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.progress import ProgressRecommendation, ProgressRecord, ProgressStats, SkillMastery
from app.services.progress_service import (
    get_progress_by_user,
    get_progress_recommendation,
    get_progress_stats,
    get_skill_mastery,
    save_progress,
)

router = APIRouter()


@router.post("/progress", response_model=ProgressRecord)
def create_progress(
    record: ProgressRecord,
    db: Session = Depends(get_db),
) -> ProgressRecord:
    """Save a user progress record in PostgreSQL."""
    return save_progress(record, db)


@router.get("/progress/{user_id}", response_model=List[ProgressRecord])
def read_progress(
    user_id: str,
    db: Session = Depends(get_db),
) -> List[ProgressRecord]:
    """Read all progress records for a user from PostgreSQL."""
    return get_progress_by_user(user_id, db)


@router.get("/progress/{user_id}/stats", response_model=ProgressStats)
def read_progress_stats(
    user_id: str,
    db: Session = Depends(get_db),
) -> ProgressStats:
    """Calculate user progress statistics from PostgreSQL records."""
    return get_progress_stats(user_id, db)



@router.get("/progress/{user_id}/recommendation", response_model=ProgressRecommendation)
def read_progress_recommendation(
    user_id: str,
    db: Session = Depends(get_db),
) -> ProgressRecommendation:
    """Return a basic learning recommendation for a user."""
    return get_progress_recommendation(user_id, db)



@router.get("/progress/{user_id}/skills/{skill_id}/mastery", response_model=SkillMastery)
def read_skill_mastery(
    user_id: str,
    skill_id: str,
    db: Session = Depends(get_db),
) -> SkillMastery:
    """Return the user's mastery score for a specific skill."""
    return get_skill_mastery(user_id, skill_id, db)
