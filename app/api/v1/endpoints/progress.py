from fastapi import APIRouter
from typing import List
from app.schemas.progress import ProgressRecord
from app.services.progress_service import save_progress, get_progress_by_user

router = APIRouter()

@router.post("/progress", response_model=ProgressRecord)
def create_progress(record: ProgressRecord) -> ProgressRecord:
    return save_progress(record)

@router.get("/progress/{user_id}", response_model=List[ProgressRecord])
def read_progress(user_id: str) -> List[ProgressRecord]:
    return get_progress_by_user(user_id)
