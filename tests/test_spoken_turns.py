from app.main import app


def _payload(**updates):
    payload = {
        "transcript": "Hello, I am Ana.",
        "transcript_source": "stt",
        "target": {
            "communicative_goal": "Introduce yourself",
            "required_meaning_terms": ["hello", "I am"],
        },
        "context": "Meet a new classmate.",
        "current_turn": {
            "turn_id": "a1-turn-1",
            "support_level": "anchors",
            "visible_support": ["Hello", "I am"],
        },
    }
    payload.update(updates)
    return payload


def test_spoken_turn_endpoint_is_registered():
    assert any(
        route.path == "/api/v1/spoken-turn-evaluations"
        and "POST" in route.methods
        for route in app.routes
    )

