import json
from pathlib import Path
from app.schemas.content import ContentTreeResponse, Lesson
from app.services.pedagogical_authoritative_curriculum_hierarchy import (
    AuthoritativeCurriculumHierarchy,
    _issue_authoritative_curriculum_hierarchy,
)

CONTENT_TREE_PATH = Path(__file__).resolve().parents[2] / "content" / "content_tree.json"
HISTORICAL_A1_U1_L1_V2_PATH = (
    Path(__file__).resolve().parents[2]
    / "content"
    / "history"
    / "a1-u1-l1-2.0.json"
)
HISTORICAL_A1_U1_L1_V2_KEY = ("a1-u1-l1", "2.0")

def build_content_tree() -> ContentTreeResponse:
    data = json.loads(CONTENT_TREE_PATH.read_text(encoding="utf-8"))
    return ContentTreeResponse.model_validate(data)


def load_authoritative_curriculum_hierarchy(
) -> AuthoritativeCurriculumHierarchy:
    """Load the complete hierarchy through the authoritative provider.

    Carga la jerarquía completa mediante el proveedor autoritativo.
    """
    hierarchy = build_content_tree()
    return _issue_authoritative_curriculum_hierarchy(hierarchy)

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


def get_lesson_context_by_id(lesson_id: str):
    """Return the hierarchy and lesson associated with one stable ID.

    Devuelve la jerarquía y la lección asociadas a un identificador estable.
    """
    tree = build_content_tree()

    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                if lesson.id == lesson_id:
                    return level.code, unit.id, lesson

    return None


def _historical_a1_u1_l1_v2_context():
    """Load the single immutable B184.4 compatibility snapshot."""
    try:
        data = json.loads(
            HISTORICAL_A1_U1_L1_V2_PATH.read_text(encoding="utf-8")
        )
        level_id = data["level_id"]
        unit_id = data["unit_id"]
        lesson = Lesson.model_validate(data["lesson"])
    except (FileNotFoundError, KeyError, TypeError, ValueError) as error:
        raise ValueError("Historical experience snapshot is invalid") from error

    lesson_id, contract_version = HISTORICAL_A1_U1_L1_V2_KEY
    if (
        level_id != "A1"
        or unit_id != "a1-u1"
        or lesson.id != lesson_id
        or lesson.experience is None
        or lesson.experience.contract_version != contract_version
    ):
        raise ValueError("Historical experience snapshot is contradictory")
    return level_id, unit_id, lesson


def get_lesson_context_by_id_and_contract_version(
    lesson_id: str,
    contract_version: str,
):
    """Resolve one active or explicitly archived LessonExperience version."""
    active_context = get_lesson_context_by_id(lesson_id)
    if active_context is not None:
        _level_id, _unit_id, active_lesson = active_context
        active_experience = active_lesson.experience
        if (
            active_experience is not None
            and active_experience.contract_version == contract_version
        ):
            if (lesson_id, contract_version) == HISTORICAL_A1_U1_L1_V2_KEY:
                historical_context = _historical_a1_u1_l1_v2_context()
                if (
                    historical_context[0] != active_context[0]
                    or historical_context[1] != active_context[1]
                    or historical_context[2].model_dump(mode="json")
                    != active_lesson.model_dump(mode="json")
                ):
                    raise ValueError(
                        "Historical experience snapshot contradicts active content"
                    )
            return active_context

    if (lesson_id, contract_version) == HISTORICAL_A1_U1_L1_V2_KEY:
        return _historical_a1_u1_l1_v2_context()
    return None

def get_conversation_context_by_id(conversation_id: str):
    """Return the hierarchy and conversation associated with one stable ID.
    Devuelve la jerarquía y conversación asociadas a un identificador estable.
    """
    tree = build_content_tree()

    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                for conversation in lesson.conversations:
                    if conversation.id == conversation_id:
                        return level.code, unit.id, lesson.id, conversation

    return None


def get_conversation_by_id(conversation_id: str):
    """Return a conversation by its stable ID.
    Devuelve una conversación mediante su identificador estable.
    """
    context = get_conversation_context_by_id(conversation_id)
    return context[3] if context is not None else None


def evaluate_exercise(exercise_id: str, selected_index: int):
    tree = build_content_tree()
    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                for exercise in lesson.exercises:
                    if exercise.id == exercise_id:
                        return selected_index == exercise.answer_index
    return None


def get_skill_ids_by_exercise_id(exercise_id: str) -> list[str]:
    """Return the skill IDs associated with an exercise."""
    tree = build_content_tree()

    for level in tree.levels:
        for unit in level.units:
            for lesson in unit.lessons:
                for exercise in lesson.exercises:
                    if exercise.id == exercise_id:
                        return exercise.skill_ids

    return []
