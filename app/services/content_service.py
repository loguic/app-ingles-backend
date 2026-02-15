import json
from pathlib import Path
from app.schemas.content import ContentTreeResponse

CONTENT_TREE_PATH = Path(__file__).resolve().parents[2] / "content" / "content_tree.json"

def build_content_tree() -> ContentTreeResponse:
    data = json.loads(CONTENT_TREE_PATH.read_text(encoding="utf-8"))
    return ContentTreeResponse.model_validate(data)

def get_level_by_code(level_code: str):
    tree = build_content_tree()
    for level in tree.levels:
        if level.code.upper() == level_code.upper():
            return level
    return None

def get_unit_by_id(unit_id: str):
    tree = build_content_tree()
    for level in tree.levels:
        for unit in level.units:
            if unit.id == unit_id:
                return unit
    return None

def get_lesson_by_id(lesson_id: str):
    tree = build_content_tree()
    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                if lesson.id == lesson_id:
                    return lesson
    return None

def evaluate_exercise(exercise_id: str, selected_index: int):
    tree = build_content_tree()
    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                for exercise in lesson.exercises:
                    if exercise.id == exercise_id:
                        return selected_index == exercise.answer_index
    return None
