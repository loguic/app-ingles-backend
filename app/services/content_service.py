from app.schemas.content import ContentTreeResponse, Level, Unit, Lesson

def build_content_tree() -> ContentTreeResponse:
    return ContentTreeResponse(
        levels=[
            Level(
                code="A1",
                units=[
                    Unit(
                        id="a1-u1",
                        title="Basics: Greetings & Introductions",
                        lessons=[
                            Lesson(id="a1-u1-l1", title="Hello / Goodbye"),
                            Lesson(id="a1-u1-l2", title="Introducing yourself"),
                        ],
                    )
                ],
            ),
            Level(code="A2", units=[]),
        ]
    )

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
