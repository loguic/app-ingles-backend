from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.progress import ProgressRecord, ProgressStats
from app.services.progress_service import (
    get_progress_by_user,
    get_progress_stats,
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
