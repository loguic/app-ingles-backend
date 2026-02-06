from fastapi import APIRouter
from app.schemas.levels import LevelsResponse

router = APIRouter()

@router.get("/levels", response_model=LevelsResponse)
def list_levels() -> LevelsResponse:
    return LevelsResponse(levels=["A1", "A2", "B1", "B2", "C1", "C2"])
