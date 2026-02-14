from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.content import ContentTreeResponse, Level, Unit, Lesson
from app.services.content_service import (
    build_content_tree,
    get_level_by_code,
    get_unit_by_id,
    get_lesson_by_id,
)

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

@router.get("/content/levels/{level_code}/units", response_model=List[Unit])
def list_units_by_level(level_code: str) -> List[Unit]:
    level = get_level(level_code)
    return level.units

@router.get("/content/units/{unit_id}", response_model=Unit)
def get_unit(unit_id: str) -> Unit:
    unit = get_unit_by_id(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit '{unit_id}' not found")
    return unit

@router.get("/content/units/{unit_id}/lessons", response_model=List[Lesson])
def list_lessons_by_unit(unit_id: str) -> List[Lesson]:
    unit = get_unit(unit_id)
    return unit.lessons

@router.get("/content/lessons/{lesson_id}", response_model=Lesson)
def get_lesson(lesson_id: str) -> Lesson:
    lesson = get_lesson_by_id(lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")
    return lesson
