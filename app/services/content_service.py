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
