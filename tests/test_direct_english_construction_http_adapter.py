from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.services.direct_english_construction_execution_service as execution_service
from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission,
    DirectEnglishConstructionAttempt,
    DirectEnglishConstructionAttemptProduction,
    ExperienceAttempt,
    ExperienceEvidenceState,
    LearnerProduction,
)
from app.db.session import get_db
from app.main import app
from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptStart,
)
from app.services.direct_english_construction_execution_service import (
    start_direct_english_construction_attempt,
)
from app.services.production_audio_storage_service import store_production_audio


PUBLIC_SOURCE_FIELDS = {
    "direct_english_attempt_id",
    "experience_attempt_id",
    "status",
    "transfer_variant_id",
    "transfer_prompt",
}


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    testing_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(engine)
    try:
        yield testing_session
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _start_experience(
    client: TestClient,
    *,
    user_id: str,
    lesson_id: str = "a1-u1-l1",
) -> dict:
    response = client.post(
        "/api/v1/experience-attempts",
        json={
            "user_id": user_id,
            "level_id": "A1",
            "unit_id": "a1-u1",
            "lesson_id": lesson_id,
        },
    )
    assert response.status_code == 200
    return response.json()


def _start_route(experience_attempt_id: str) -> str:
    return (
        "/api/v1/experience-attempts/"
        + experience_attempt_id
        + "/direct-english-construction-attempts"
    )


def _finalize_route(
    experience_attempt_id: str,
    direct_english_attempt_id: str,
) -> str:
    return (
        _start_route(experience_attempt_id)
        + "/"
        + direct_english_attempt_id
        + "/finalize"
    )


def _public_start(
    client: TestClient,
    experience_attempt_id: str,
    direct_english_attempt_id: str,
):
    return client.post(
        _start_route(experience_attempt_id),
        json={"attempt_id": direct_english_attempt_id},
    )


def _audio_references(tmp_path, count: int) -> list[str]:
    return [
        store_production_audio(
            b"RIFF\x04\x00\x00\x00WAVE",
            storage_dir=tmp_path,
        ).audio_reference
        for _ in range(count)
    ]


def _captures(
    audio_references: list[str],
    *,
    text_function: str | None = None,
) -> list[dict]:
    references = iter(audio_references)
    captures = []
    for function in ("guided", "expanded", "transfer"):
        if function == text_function:
            captures.append(
                {
                    "production_function": function,
                    "modality": "text",
                    "response_text": "I introduce myself in my own words.",
                }
            )
        else:
            captures.append(
                {
                    "production_function": function,
                    "modality": "voice",
                    "audio_reference": next(references),
                }
            )
    return captures


def test_public_start_derives_bound_context_and_returns_narrow_source(
    client,
    session_factory,
):
    experience = _start_experience(client, user_id="http-start-user")
    before = datetime.now(UTC)

    response = _public_start(client, experience["attempt_id"], "http-source-1")

    assert response.status_code == 200
    assert set(response.json()) == PUBLIC_SOURCE_FIELDS
    assert response.json() == {
        "direct_english_attempt_id": "http-source-1",
        "experience_attempt_id": experience["attempt_id"],
        "status": "started",
        "transfer_variant_id": response.json()["transfer_variant_id"],
        "transfer_prompt": response.json()["transfer_prompt"],
    }
    with session_factory() as db:
        source = db.get(DirectEnglishConstructionAttempt, "http-source-1")
        assert source is not None
        assert source.user_id == "http-start-user"
        assert source.level_id == "A1"
        assert source.unit_id == "a1-u1"
        assert source.lesson_id == "a1-u1-l1"
        assert source.experience_attempt_id == experience["attempt_id"]
        started_at = source.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=UTC)
        assert started_at >= before


def test_equivalent_public_start_retry_returns_the_same_started_source(
    client,
    session_factory,
):
    experience = _start_experience(client, user_id="http-retry-user")

    first = _public_start(client, experience["attempt_id"], "stable-source")
    second = _public_start(client, experience["attempt_id"], "stable-source")

    assert first.status_code == second.status_code == 200
    assert second.json() == first.json()
    with session_factory() as db:
        assert db.query(DirectEnglishConstructionAttempt).count() == 1


def test_public_start_rejects_source_identity_bound_to_another_experience(
    client,
):
    first = _start_experience(client, user_id="http-collision-one")
    second = _start_experience(client, user_id="http-collision-two")
    assert _public_start(client, first["attempt_id"], "collision-source").status_code == 200

    rejected = _public_start(
        client,
        second["attempt_id"],
        "collision-source",
    )

    assert rejected.status_code == 400
    assert "already in use" in rejected.json()["detail"]


def test_public_start_rejects_missing_completed_and_incompatible_experience(
    client,
    session_factory,
):
    missing = _public_start(client, "missing-experience", "missing-source")
    assert missing.status_code == 404

    completed = _start_experience(client, user_id="http-completed-user")
    with session_factory() as db:
        attempt = db.get(ExperienceAttempt, completed["attempt_id"])
        attempt.status = "completed"
        attempt.completed_at = datetime.now(UTC)
        db.commit()
    completed_response = _public_start(
        client,
        completed["attempt_id"],
        "completed-source",
    )
    assert completed_response.status_code == 400

    incompatible = _start_experience(
        client,
        user_id="http-incompatible-user",
        lesson_id="a1-u1-l2",
    )
    incompatible_response = _public_start(
        client,
        incompatible["attempt_id"],
        "incompatible-source",
    )
    assert incompatible_response.status_code == 400


@pytest.mark.parametrize(
    "extra_field",
    [
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "started_at",
        "experience_attempt_id",
        "evidence_definition_id",
        "evidence_type",
        "status",
        "completed",
        "mastery",
        "score",
        "transfer_variant_id",
        "support_used",
    ],
)
def test_public_start_rejects_every_unapproved_field(client, extra_field):
    experience = _start_experience(
        client,
        user_id="http-extra-start-" + extra_field,
    )
    payload = {"attempt_id": "extra-start-" + extra_field, extra_field: "forged"}

    response = client.post(_start_route(experience["attempt_id"]), json=payload)

    assert response.status_code == 422


def test_finalize_requires_the_persisted_experience_binding(
    client,
    session_factory,
):
    first = _start_experience(client, user_id="http-binding-one")
    second = _start_experience(client, user_id="http-binding-two")
    assert _public_start(client, first["attempt_id"], "binding-source").status_code == 200

    response = client.post(
        _finalize_route(second["attempt_id"], "binding-source"),
        json={"captures": _captures(["unused-1", "unused-2", "unused-3"])},
    )

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"]
    with session_factory() as db:
        source = db.get(DirectEnglishConstructionAttempt, "binding-source")
        assert source.status == "started"
        assert db.query(ConversationProductionSubmission).count() == 0


def test_finalize_missing_direct_english_source_returns_404(client):
    experience = _start_experience(client, user_id="http-missing-direct")

    response = client.post(
        _finalize_route(experience["attempt_id"], "missing-direct-source"),
        json={"captures": _captures(["unused-1", "unused-2", "unused-3"])},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "captures",
    [
        [
            {"production_function": "guided", "modality": "text", "response_text": "one"},
            {"production_function": "expanded", "modality": "text", "response_text": "two"},
        ],
        [
            {"production_function": "guided", "modality": "text", "response_text": "one"},
            {"production_function": "guided", "modality": "text", "response_text": "two"},
            {"production_function": "transfer", "modality": "text", "response_text": "three"},
        ],
    ],
)
def test_finalize_requires_each_production_function_exactly_once(client, captures):
    experience = _start_experience(client, user_id="http-functions-user")
    assert _public_start(client, experience["attempt_id"], "functions-source").status_code == 200

    response = client.post(
        _finalize_route(experience["attempt_id"], "functions-source"),
        json={"captures": captures},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "extra_field",
    [
        "user_id",
        "level_id",
        "unit_id",
        "lesson_id",
        "experience_attempt_id",
        "conversation_id",
        "prompt_id",
        "turn_id",
        "evidence_definition_id",
        "support_used",
        "transfer_variant_id",
        "finalized_at",
        "status",
        "completed",
        "mastery",
        "score",
    ],
)
def test_finalize_rejects_unapproved_capture_fields(client, extra_field):
    experience = _start_experience(
        client,
        user_id="http-extra-finalize-" + extra_field,
    )
    source_id = "extra-finalize-" + extra_field
    assert _public_start(client, experience["attempt_id"], source_id).status_code == 200
    captures = _captures(["unused-1", "unused-2", "unused-3"])
    captures[0][extra_field] = "forged"

    response = client.post(
        _finalize_route(experience["attempt_id"], source_id),
        json={"captures": captures},
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "capture",
    [
        {"production_function": "guided", "modality": "voice"},
        {
            "production_function": "guided",
            "modality": "voice",
            "audio_reference": "production-audio://one",
            "response_text": "forged text",
        },
        {"production_function": "guided", "modality": "text"},
        {
            "production_function": "guided",
            "modality": "text",
            "response_text": "valid text",
            "audio_reference": "production-audio://one",
        },
    ],
)
def test_finalize_rejects_invalid_modality_specific_fields(client, capture):
    experience = _start_experience(client, user_id="http-modality-user")
    assert _public_start(client, experience["attempt_id"], "modality-source").status_code == 200
    captures = _captures(["unused-1", "unused-2", "unused-3"])
    captures[0] = capture

    response = client.post(
        _finalize_route(experience["attempt_id"], "modality-source"),
        json={"captures": captures},
    )

    assert response.status_code == 422


def test_finalize_rejects_unmanaged_voice_audio_without_persistence(
    client,
    session_factory,
):
    experience = _start_experience(client, user_id="http-audio-user")
    assert _public_start(client, experience["attempt_id"], "audio-source").status_code == 200

    response = client.post(
        _finalize_route(experience["attempt_id"], "audio-source"),
        json={"captures": _captures(["audio/a.wav", "audio/b.wav", "audio/c.wav"])},
    )

    assert response.status_code == 400
    with session_factory() as db:
        assert db.get(DirectEnglishConstructionAttempt, "audio-source").status == "started"
        assert db.query(ConversationProductionSubmission).count() == 0
        assert db.query(ExperienceEvidenceState).count() == 0


def test_sufficient_finalize_accredits_and_get_exposes_authoritative_completion(
    client,
    session_factory,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    experience = _start_experience(client, user_id="http-completion-user")
    source_id = "completion-source"
    assert _public_start(client, experience["attempt_id"], source_id).status_code == 200

    response = client.post(
        _finalize_route(experience["attempt_id"], source_id),
        json={"captures": _captures(_audio_references(tmp_path, 3))},
    )

    assert response.status_code == 200
    assert set(response.json()) == PUBLIC_SOURCE_FIELDS
    assert response.json()["status"] == "finalized"
    assert {
        "evidence_definition_ids",
        "evidence_states",
        "completion_requirements_met",
        "completed",
        "mastery",
        "score",
        "selector_version",
        "productions",
    }.isdisjoint(response.json())
    authoritative = client.get(
        "/api/v1/experience-attempts/" + experience["attempt_id"]
    )
    assert authoritative.status_code == 200
    assert authoritative.json()["status"] == "completed"
    assert authoritative.json()["completed_at"] is not None
    assert {item["status"] for item in authoritative.json()["evidence_states"]} == {
        "satisfied"
    }
    with session_factory() as db:
        assert db.query(DirectEnglishConstructionAttemptProduction).count() == 3
        assert db.query(ConversationProductionSubmission).count() == 3
        assert db.query(LearnerProduction).count() == 3


def test_text_capture_remains_pending_and_does_not_complete(
    client,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    experience = _start_experience(client, user_id="http-text-user")
    source_id = "text-source"
    assert _public_start(client, experience["attempt_id"], source_id).status_code == 200

    response = client.post(
        _finalize_route(experience["attempt_id"], source_id),
        json={
            "captures": _captures(
                _audio_references(tmp_path, 2),
                text_function="expanded",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "finalized"
    authoritative = client.get(
        "/api/v1/experience-attempts/" + experience["attempt_id"]
    ).json()
    assert authoritative["status"] == "in_progress"
    assert [item["status"] for item in authoritative["evidence_states"]].count(
        "pending"
    ) == 1
    assert [item["status"] for item in authoritative["evidence_states"]].count(
        "satisfied"
    ) == 2


def test_forced_finalize_failure_rolls_back_source_evidence_and_completion(
    client,
    session_factory,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    experience = _start_experience(client, user_id="http-rollback-user")
    source_id = "rollback-source"
    assert _public_start(client, experience["attempt_id"], source_id).status_code == 200

    def fail_accreditation(*_args, **_kwargs):
        raise RuntimeError("forced accreditation failure")

    monkeypatch.setattr(
        execution_service,
        "accredit_evidence_states",
        fail_accreditation,
    )
    with pytest.raises(RuntimeError, match="forced accreditation failure"):
        client.post(
            _finalize_route(experience["attempt_id"], source_id),
            json={"captures": _captures(_audio_references(tmp_path, 3))},
        )

    with session_factory() as db:
        assert db.get(DirectEnglishConstructionAttempt, source_id).status == "started"
        assert db.get(ExperienceAttempt, experience["attempt_id"]).status == "in_progress"
        assert db.query(ConversationProductionSubmission).count() == 0
        assert db.query(LearnerProduction).count() == 0
        assert db.query(DirectEnglishConstructionAttemptProduction).count() == 0
        assert db.query(ExperienceEvidenceState).count() == 0


def test_existing_internal_unbound_start_remains_valid(session_factory):
    with session_factory() as db:
        record = start_direct_english_construction_attempt(
            DirectEnglishConstructionAttemptStart(
                attempt_id="legacy-unbound-source",
                user_id="legacy-user",
                level_id="A1",
                unit_id="a1-u1",
                lesson_id="a1-u1-l1",
                started_at=datetime.now(UTC),
            ),
            db,
        )

    assert record.status == "started"
    assert record.experience_attempt_id is None
