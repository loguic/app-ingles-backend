import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import ExperienceAttempt, ExperienceComprehensionResponse
from app.api.v1.endpoints.content import get_content_tree
from app.schemas.content import Lesson, Level, Unit
from app.schemas.experience_attempt import ExperienceAttemptStart
from app.services import content_service
from app.services import experience_attempt_service
from app.services import experience_evidence_service


def _historical_payload() -> dict:
    return json.loads(
        content_service.HISTORICAL_A1_U1_L1_V2_PATH.read_text(
            encoding="utf-8"
        )
    )


def _active_v3_context():
    historical = _historical_a1_u1_l1_context()
    payload = historical[2].model_dump(mode="json")
    payload["experience"]["contract_version"] = "3.0"
    lesson = Lesson.model_validate(payload)
    return "A1", "a1-u1", lesson


def _historical_a1_u1_l1_context():
    return content_service._historical_a1_u1_l1_v2_context()


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _attempt(
    *,
    attempt_id: str,
    contract_version: str,
    user_id: str = "versioning-user",
) -> ExperienceAttempt:
    now = datetime.now(timezone.utc)
    return ExperienceAttempt(
        attempt_id=attempt_id,
        user_id=user_id,
        level_id="A1",
        unit_id="a1-u1",
        lesson_id="a1-u1-l1",
        experience_contract_version=contract_version,
        status="in_progress",
        started_at=now,
        completed_at=None,
    )


@pytest.mark.parametrize("contract_version", ["2.0", "3.0"])
def test_schema_accepts_declared_contract_versions(contract_version):
    payload = _historical_payload()["lesson"]
    payload["experience"]["contract_version"] = contract_version

    lesson = Lesson.model_validate(payload)

    assert lesson.experience is not None
    assert lesson.experience.contract_version == contract_version


def test_schema_rejects_undeclared_contract_version():
    payload = _historical_payload()["lesson"]
    payload["experience"]["contract_version"] = "2.1"

    with pytest.raises(ValidationError):
        Lesson.model_validate(payload)


def test_historical_snapshot_is_exact_current_a1_u1_l1_payload():
    snapshot = _historical_payload()
    active = json.loads(
        content_service.CONTENT_TREE_PATH.read_text(encoding="utf-8")
    )
    lesson = active["levels"][0]["units"][0]["lessons"][0]

    assert snapshot["level_id"] == "A1"
    assert snapshot["unit_id"] == "a1-u1"
    assert snapshot["lesson"] == lesson


def test_historical_snapshot_context_validates_hierarchy_and_version():
    level_id, unit_id, lesson = _historical_a1_u1_l1_context()

    assert (level_id, unit_id, lesson.id) == ("A1", "a1-u1", "a1-u1-l1")
    assert lesson.experience is not None
    assert lesson.experience.contract_version == "2.0"


def test_normal_active_lookup_does_not_expose_historical_snapshot():
    active_lesson = content_service.get_lesson_by_id("a1-u1-l1")

    assert active_lesson is not None
    assert active_lesson.experience is not None
    assert active_lesson.experience.contract_version == "2.0"
    assert content_service.get_lesson_by_id("a1-u1-l1-2.0") is None


def test_exact_resolver_returns_matching_active_version(monkeypatch):
    active_context = _active_v3_context()
    monkeypatch.setattr(
        content_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )

    assert (
        content_service.get_lesson_context_by_id_and_contract_version(
            "a1-u1-l1", "3.0"
        )
        == active_context
    )


def test_exact_resolver_returns_archived_historical_version(monkeypatch):
    active_context = _active_v3_context()
    monkeypatch.setattr(
        content_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )

    level_id, unit_id, lesson = (
        content_service.get_lesson_context_by_id_and_contract_version(
            "a1-u1-l1", "2.0"
        )
    )

    assert (level_id, unit_id, lesson.id) == ("A1", "a1-u1", "a1-u1-l1")
    assert lesson.experience is not None
    assert lesson.experience.contract_version == "2.0"


def test_exact_resolver_fails_closed_for_unknown_pair():
    assert (
        content_service.get_lesson_context_by_id_and_contract_version(
            "a1-u1-l1", "9.9"
        )
        is None
    )
    assert (
        content_service.get_lesson_context_by_id_and_contract_version(
            "unknown-lesson", "2.0"
        )
        is None
    )


def test_malformed_archive_fails_closed(monkeypatch, tmp_path):
    malformed_archive = tmp_path / "a1-u1-l1-2.0.json"
    malformed_archive.write_text(
        json.dumps({"level_id": "A2", "unit_id": "a1-u1", "lesson": {}}),
        encoding="utf-8",
    )
    active_context = _active_v3_context()
    monkeypatch.setattr(
        content_service,
        "HISTORICAL_A1_U1_L1_V2_PATH",
        malformed_archive,
    )
    monkeypatch.setattr(
        content_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )

    with pytest.raises(ValueError, match="Historical experience snapshot"):
        content_service.get_lesson_context_by_id_and_contract_version(
            "a1-u1-l1", "2.0"
        )


def test_historical_attempt_get_uses_archived_evidence_order(monkeypatch, db):
    active_context = _active_v3_context()
    monkeypatch.setattr(
        content_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )
    monkeypatch.setattr(
        experience_attempt_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )
    db.add(_attempt(attempt_id="historical-attempt", contract_version="2.0"))
    db.commit()

    record = experience_attempt_service.get_experience_attempt_state(
        "historical-attempt", db
    )

    assert record is not None
    assert record.experience_contract_version == "2.0"
    assert [item.evidence_definition_id for item in record.evidence_states] == [
        "a1-u1-l1-ev-guided",
        "a1-u1-l1-ev-expanded",
        "a1-u1-l1-ev-transfer",
    ]


def test_active_v3_start_does_not_resume_historical_v2_attempt(monkeypatch, db):
    active_context = _active_v3_context()
    monkeypatch.setattr(
        experience_attempt_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )
    db.add(_attempt(attempt_id="historical-active", contract_version="2.0"))
    db.commit()

    record = experience_attempt_service.start_or_resume_experience_attempt(
        ExperienceAttemptStart(
            user_id="versioning-user",
            level_id="A1",
            unit_id="a1-u1",
            lesson_id="a1-u1-l1",
        ),
        db,
    )

    assert record.attempt_id != "historical-active"
    assert record.experience_contract_version == "3.0"


def test_active_attempt_uniqueness_remains_version_scoped(db):
    db.add(_attempt(attempt_id="historical-active", contract_version="2.0"))
    db.add(_attempt(attempt_id="canonical-active", contract_version="3.0"))
    db.commit()

    assert db.query(ExperienceAttempt).count() == 2


def test_historical_source_mutation_does_not_fall_through_to_active_v3(
    monkeypatch, db
):
    active_context = _active_v3_context()
    monkeypatch.setattr(
        experience_evidence_service,
        "get_lesson_context_by_id",
        lambda lesson_id: active_context if lesson_id == "a1-u1-l1" else None,
    )
    db.add(_attempt(attempt_id="historical-source", contract_version="2.0"))
    db.commit()

    with pytest.raises(ValueError, match="hierarchy does not match"):
        experience_attempt_service.save_experience_comprehension_response(
            "historical-source",
            "a1-u1-l1-q1",
            0,
            db,
        )

    assert db.query(ExperienceComprehensionResponse).count() == 0


def test_active_content_api_does_not_expose_history():
    response = get_content_tree().model_dump(mode="json")

    assert "history" not in response
    lessons = response["levels"][0]["units"][0]["lessons"]
    assert [lesson["id"] for lesson in lessons].count("a1-u1-l1") == 1
