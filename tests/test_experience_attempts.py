from datetime import datetime, timedelta, timezone
import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import experience_attempts as endpoint_module
from app.db.database import Base
from app.db.models import ExperienceAttempt, UserProgress
from app.db.session import get_db
from app.main import app
from app.schemas.content import Lesson, Level, Unit
from app.schemas.experience_attempt import ExperienceAttemptStart
from app.services import experience_attempt_service as service_module


def _lesson_with_b184_experience() -> Lesson:
    return Lesson.model_validate(
        {
            "id": "b184-a1-u1-l1",
            "title": "First English encounter",
            "conversations": [
                {
                    "id": "b184-a1-u1-l1-c-context",
                    "title": "Context response",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "context-partner",
                            "speaker": "partner",
                            "en": "Hi.",
                        },
                        {
                            "id": "context-learner",
                            "speaker": "learner",
                            "en": "Respond.",
                            "production_prompt": {
                                "id": "context-prompt",
                                "accepted_modalities": ["voice"],
                                "required": True,
                            },
                        },
                    ],
                },
                {
                    "id": "b184-a1-u1-l1-c-final",
                    "title": "Final exchange",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "final-partner",
                            "speaker": "partner",
                            "en": "What is your name?",
                        }
                    ],
                },
            ],
            "exercises": [
                {
                    "id": "b184-a1-u1-l1-q-comprehension",
                    "type": "mcq",
                    "prompt": "What greeting did you hear?",
                    "options": ["Hi.", "Goodbye."],
                    "answer_index": 0,
                    "skill_ids": ["a1_first_encounter"],
                }
            ],
            "experience": {
                "contract_version": "2.0",
                "mission": {
                    "id": "b184-a1-u1-l1-mission",
                    "title": "Meet someone",
                    "situation": "Meet a new person.",
                    "observable_outcome": "Complete a brief encounter.",
                    "success_criteria": ["Participate in the exchange."],
                },
                "skill_ids": ["a1_first_encounter"],
                "stages": [
                    {
                        "id": "b184-s-context",
                        "type": "comprehension",
                        "instruction": "Understand the greeting.",
                        "activity_ids": ["b184-a1-u1-l1-c-context"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "b184-s-response",
                        "type": "assisted_response",
                        "instruction": "Respond in context.",
                        "activity_ids": ["b184-a1-u1-l1-c-context"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "b184-s-production",
                        "type": "guided_production",
                        "instruction": "Produce a name response.",
                        "activity_ids": ["b184-a1-u1-l1-c-context"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "b184-s-final",
                        "type": "applied_conversation",
                        "instruction": "Complete the final exchange.",
                        "activity_ids": ["b184-a1-u1-l1-c-final"],
                        "completion_condition": "evidence_recorded",
                    },
                ],
                "evidence_definitions": [
                    {
                        "id": "b184-ev-comprehension",
                        "skill_ids": ["a1_first_encounter"],
                        "stage_id": "b184-s-context",
                        "activity_id": "b184-a1-u1-l1-c-context",
                        "comprehension_exercise_id": (
                            "b184-a1-u1-l1-q-comprehension"
                        ),
                        "evidence_type": "comprehension_result",
                        "measurement_mode": "binary",
                    },
                    {
                        "id": "b184-ev-contextual",
                        "skill_ids": ["a1_first_encounter"],
                        "stage_id": "b184-s-response",
                        "activity_id": "b184-a1-u1-l1-c-context",
                        "evidence_type": "contextual_response",
                        "measurement_mode": "completion",
                        "production_prompt_id": "context-prompt",
                    },
                    {
                        "id": "b184-ev-production",
                        "skill_ids": ["a1_first_encounter"],
                        "stage_id": "b184-s-production",
                        "activity_id": "b184-a1-u1-l1-c-context",
                        "evidence_type": "guided_production",
                        "measurement_mode": "completion",
                        "production_prompt_id": "context-prompt",
                    },
                    {
                        "id": "b184-ev-conversation",
                        "skill_ids": ["a1_first_encounter"],
                        "stage_id": "b184-s-final",
                        "activity_id": "b184-a1-u1-l1-c-final",
                        "evidence_type": "conversation_completion",
                        "measurement_mode": "completion",
                    },
                ],
                "completion_policy": {
                    "practiced_stage_ids": [
                        "b184-s-context",
                        "b184-s-response",
                        "b184-s-production",
                        "b184-s-final",
                    ],
                    "required_evidence_ids": [
                        "b184-ev-conversation",
                        "b184-ev-production",
                        "b184-ev-contextual",
                        "b184-ev-comprehension",
                    ],
                },
            },
        }
    )


@pytest.fixture()
def isolated_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    try:
        yield testing_session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(isolated_db):
    def override_get_db():
        db = isolated_db()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def experience_context(monkeypatch):
    lesson = _lesson_with_b184_experience()
    unit = Unit(id="b184-a1-u1", title="First unit", lessons=[lesson])
    level = Level(code="A1", units=[unit])

    monkeypatch.setattr(
        endpoint_module,
        "get_level_by_code",
        lambda level_id: level if level_id.upper() == "A1" else None,
    )
    monkeypatch.setattr(
        endpoint_module,
        "get_unit_by_id",
        lambda unit_id: unit if unit_id == unit.id else None,
    )
    monkeypatch.setattr(
        endpoint_module,
        "get_lesson_by_id",
        lambda lesson_id: lesson if lesson_id == lesson.id else None,
    )
    monkeypatch.setattr(
        service_module,
        "get_lesson_context_by_id",
        lambda lesson_id: (level.code, unit.id, lesson)
        if lesson_id == lesson.id
        else None,
    )
    monkeypatch.setattr(
        "app.services.experience_evidence_service.get_lesson_context_by_id",
        lambda lesson_id: (level.code, unit.id, lesson)
        if lesson_id == lesson.id
        else None,
    )
    return level, unit, lesson


def _payload(*, user_id: str = "test-user-b1841") -> dict[str, str]:
    return {
        "user_id": user_id,
        "level_id": "A1",
        "unit_id": "b184-a1-u1",
        "lesson_id": "b184-a1-u1-l1",
    }


def test_start_creates_authoritative_in_progress_attempt(
    client,
    experience_context,
):
    response = client.post("/api/v1/experience-attempts", json=_payload())

    assert response.status_code == 200
    record = response.json()
    assert record["attempt_id"]
    assert record["status"] == "in_progress"
    assert record["completed_at"] is None
    assert record["experience_contract_version"] == "2.0"
    assert record["started_at"]


def test_repeated_start_resumes_same_attempt_without_changing_started_at(
    client,
    experience_context,
):
    first = client.post("/api/v1/experience-attempts", json=_payload()).json()
    second_response = client.post("/api/v1/experience-attempts", json=_payload())

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["attempt_id"] == first["attempt_id"]
    assert second["started_at"] == first["started_at"]
    assert second["completed_at"] is None


def test_completed_history_is_not_reused_and_new_active_attempt_follows(
    client,
    isolated_db,
    experience_context,
):
    _, _, lesson = experience_context
    db = isolated_db()
    completed_at = datetime.now(timezone.utc)
    db.add(
        ExperienceAttempt(
            attempt_id="completed-b1841",
            user_id="test-user-b1841-completed",
            level_id="A1",
            unit_id="b184-a1-u1",
            lesson_id=lesson.id,
            experience_contract_version="2.0",
            status="completed",
            started_at=completed_at - timedelta(minutes=1),
            completed_at=completed_at,
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/api/v1/experience-attempts",
        json=_payload(user_id="test-user-b1841-completed"),
    )

    assert response.status_code == 200
    record = response.json()
    assert record["attempt_id"] != "completed-b1841"
    assert record["status"] == "in_progress"


def test_database_rejects_duplicate_matching_active_attempts(
    isolated_db,
):
    db = isolated_db()
    now = datetime.now(timezone.utc)
    identity = {
        "user_id": "test-user-b1841-unique",
        "level_id": "A1",
        "unit_id": "b184-a1-u1",
        "lesson_id": "b184-a1-u1-l1",
        "experience_contract_version": "2.0",
        "status": "in_progress",
        "started_at": now,
        "completed_at": None,
    }
    db.add(ExperienceAttempt(attempt_id="active-one", **identity))
    db.commit()
    db.add(ExperienceAttempt(attempt_id="active-two", **identity))

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
    db.close()


def test_concurrent_equivalent_creation_recovers_existing_active_attempt(
    isolated_db,
    experience_context,
    monkeypatch,
):
    command = ExperienceAttemptStart(**_payload(user_id="test-user-b1841-race"))
    db = isolated_db()
    original_flush = db.flush

    def race_flush(*args, **kwargs):
        other = isolated_db()
        try:
            other.add(
                ExperienceAttempt(
                    attempt_id="race-winner",
                    user_id=command.user_id,
                    level_id=command.level_id,
                    unit_id=command.unit_id,
                    lesson_id=command.lesson_id,
                    experience_contract_version="2.0",
                    status="in_progress",
                    started_at=datetime.now(timezone.utc),
                    completed_at=None,
                )
            )
            other.commit()
        finally:
            other.close()
        raise IntegrityError(
            "simulated concurrent unique conflict",
            {},
            sqlite3.IntegrityError(
                "UNIQUE constraint failed: experience_attempts.user_id, "
                "experience_attempts.level_id, experience_attempts.unit_id, "
                "experience_attempts.lesson_id, "
                "experience_attempts.experience_contract_version"
            ),
        )

    monkeypatch.setattr(db, "flush", race_flush)
    try:
        record = service_module.start_or_resume_experience_attempt(command, db)
    finally:
        monkeypatch.setattr(db, "flush", original_flush)
        db.close()

    assert record.attempt_id == "race-winner"
    assert record.status == "in_progress"


def test_start_does_not_swallow_unrelated_integrity_error(
    isolated_db,
    experience_context,
    monkeypatch,
):
    command = ExperienceAttemptStart(
        **_payload(user_id="test-user-b1841-unrelated-integrity")
    )
    db = isolated_db()
    monkeypatch.setattr(
        db,
        "flush",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            IntegrityError(
                "unrelated integrity failure",
                {},
                sqlite3.IntegrityError("CHECK constraint failed: unrelated"),
            )
        ),
    )
    try:
        with pytest.raises(IntegrityError, match="unrelated integrity"):
            service_module.start_or_resume_experience_attempt(command, db)
    finally:
        db.close()


def test_get_returns_existing_attempt_and_pending_evidence_in_policy_order(
    client,
    experience_context,
):
    created = client.post("/api/v1/experience-attempts", json=_payload()).json()

    response = client.get(
        "/api/v1/experience-attempts/" + created["attempt_id"]
    )

    assert response.status_code == 200
    record = response.json()
    assert record["attempt_id"] == created["attempt_id"]
    assert [
        state["evidence_definition_id"]
        for state in record["evidence_states"]
    ] == [
        "b184-ev-conversation",
        "b184-ev-production",
        "b184-ev-contextual",
        "b184-ev-comprehension",
    ]
    assert [state["status"] for state in record["evidence_states"]] == [
        "pending",
        "pending",
        "pending",
        "pending",
    ]


def test_post_and_get_cannot_complete_attempt_or_write_user_progress(
    client,
    isolated_db,
    experience_context,
):
    rejected = client.post(
        "/api/v1/experience-attempts",
        json={**_payload(), "status": "completed"},
    )
    assert rejected.status_code == 422

    created = client.post("/api/v1/experience-attempts", json=_payload()).json()
    read = client.get("/api/v1/experience-attempts/" + created["attempt_id"])

    assert read.status_code == 200
    assert read.json()["status"] == "in_progress"
    assert read.json()["completed_at"] is None
    db = isolated_db()
    try:
        assert db.query(UserProgress).count() == 0
    finally:
        db.close()


def test_comprehension_endpoint_accepts_only_selection_and_derives_truth(
    client,
    experience_context,
):
    created = client.post("/api/v1/experience-attempts", json=_payload()).json()
    route = (
        "/api/v1/experience-attempts/"
        + created["attempt_id"]
        + "/comprehension-responses/b184-a1-u1-l1-q-comprehension"
    )
    rejected = client.post(
        route,
        json={"selected_index": 1, "is_correct": True, "status": "satisfied"},
    )
    assert rejected.status_code == 422

    response = client.post(route, json={"selected_index": 0})
    assert response.status_code == 200
    source = response.json()
    assert source["evidence_definition_id"] == "b184-ev-comprehension"
    assert source["activity_id"] == "b184-a1-u1-l1-c-context"
    assert source["is_correct"] is True

    authoritative = client.get(
        "/api/v1/experience-attempts/" + created["attempt_id"]
    ).json()
    statuses = {
        item["evidence_definition_id"]: item["status"]
        for item in authoritative["evidence_states"]
    }
    assert statuses["b184-ev-comprehension"] == "satisfied"
    assert authoritative["status"] == "in_progress"


@pytest.mark.parametrize(
    ("patch_name", "value", "payload", "status_code", "detail"),
    [
        (
            "get_level_by_code",
            lambda _: None,
            _payload(),
            404,
            "Level 'A1' not found",
        ),
        (
            "get_unit_by_id",
            lambda _: None,
            _payload(),
            404,
            "Unit 'b184-a1-u1' not found",
        ),
        (
            "get_lesson_by_id",
            lambda _: None,
            _payload(),
            404,
            "Lesson 'b184-a1-u1-l1' not found",
        ),
    ],
)
def test_start_uses_existing_not_found_error_conventions(
    client,
    experience_context,
    monkeypatch,
    patch_name,
    value,
    payload,
    status_code,
    detail,
):
    monkeypatch.setattr(endpoint_module, patch_name, value)

    response = client.post("/api/v1/experience-attempts", json=payload)

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def test_start_rejects_lesson_without_experience(
    client,
    experience_context,
    monkeypatch,
):
    _, _, lesson = experience_context
    legacy_lesson = lesson.model_copy(update={"experience": None})
    monkeypatch.setattr(endpoint_module, "get_lesson_by_id", lambda _: legacy_lesson)

    response = client.post("/api/v1/experience-attempts", json=_payload())

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Lesson 'b184-a1-u1-l1' has no experience"
    }


def test_start_rejects_hierarchy_mismatch(
    client,
    experience_context,
    monkeypatch,
):
    level, _, _ = experience_context
    monkeypatch.setattr(
        endpoint_module,
        "get_level_by_code",
        lambda _: level.model_copy(update={"units": []}),
    )

    response = client.post("/api/v1/experience-attempts", json=_payload())

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Experience hierarchy does not match the content tree"
    }


def test_get_rejects_unknown_attempt(client, experience_context):
    response = client.get("/api/v1/experience-attempts/missing-b1841")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Experience attempt 'missing-b1841' not found"
    }
