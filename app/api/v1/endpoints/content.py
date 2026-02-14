from fastapi import APIRouter, HTTPException
from app.schemas.content import ContentTreeResponse, Level, Unit
from app.services.content_service import build_content_tree, get_level_by_code, get_unit_by_id

router = APIRouter()

@router.get("/content/tree", response_model=ContentTreeResponse)
def get_content_tree() -> ContentTreeResponse:
    return build_content_tree()

@router.get("/content/levels/{level_code}", response_model=Level)
def get_level(level_code: str) -> Level:
    level = get_level_by_code(level_code)
    if level is None:
        raise HTTPException(status_code=404, detail=f"Level '{level_code}' not found")
    return level

@router.get("/content/units/{unit_id}", response_model=Unit)
def get_unit(unit_id: str) -> Unit:
    unit = get_unit_by_id(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit '{unit_id}' not found")
    return unit
