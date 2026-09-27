from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.content import ContentTreeResponse, Level, Unit, Lesson
from app.services.content_service import (
    CONTENT_TREE_PATH,
    build_content_tree,
    select_active_runtime_content_tree,
)

router = APIRouter()


def _select_content_tree() -> ContentTreeResponse:
    """Select one verified runtime tree, or the legacy tree when absent."""

    repository_root = CONTENT_TREE_PATH.parent.parent
    runtime_tree = select_active_runtime_content_tree(repository_root)
    return build_content_tree() if runtime_tree is None else runtime_tree


def _get_level_from_tree(
    tree: ContentTreeResponse,
    level_code: str,
) -> Level | None:
    return next(
        (level for level in tree.levels if level.code.upper() == level_code.upper()),
        None,
    )


def _get_unit_from_tree(tree: ContentTreeResponse, unit_id: str) -> Unit | None:
    return next(
        (
            unit
            for level in tree.levels
            for unit in level.units
            if unit.id == unit_id
        ),
        None,
    )


def _get_lesson_from_tree(
    tree: ContentTreeResponse,
    lesson_id: str,
) -> Lesson | None:
    return next(
        (
            lesson
            for level in tree.levels
            for unit in level.units
            for lesson in unit.lessons
            if lesson.id == lesson_id
        ),
        None,
    )


@router.get("/content/tree", response_model=ContentTreeResponse)
def get_content_tree() -> ContentTreeResponse:
    return _select_content_tree()

@router.get("/content/levels/{level_code}", response_model=Level)
def get_level(level_code: str) -> Level:
    level = _get_level_from_tree(_select_content_tree(), level_code)
    if level is None:
        raise HTTPException(status_code=404, detail=f"Level '{level_code}' not found")
    return level

@router.get("/content/levels/{level_code}/units", response_model=List[Unit])
def list_units_by_level(level_code: str) -> List[Unit]:
    level = _get_level_from_tree(_select_content_tree(), level_code)
    if level is None:
        raise HTTPException(status_code=404, detail=f"Level '{level_code}' not found")
    return level.units

@router.get("/content/units/{unit_id}", response_model=Unit)
def get_unit(unit_id: str) -> Unit:
    unit = _get_unit_from_tree(_select_content_tree(), unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit '{unit_id}' not found")
    return unit

@router.get("/content/units/{unit_id}/lessons", response_model=List[Lesson])
def list_lessons_by_unit(unit_id: str) -> List[Lesson]:
    unit = _get_unit_from_tree(_select_content_tree(), unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail=f"Unit '{unit_id}' not found")
    return unit.lessons

@router.get("/content/lessons/{lesson_id}", response_model=Lesson)
def get_lesson(lesson_id: str) -> Lesson:
    lesson = _get_lesson_from_tree(_select_content_tree(), lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail=f"Lesson '{lesson_id}' not found")
    return lesson
