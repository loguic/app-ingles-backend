"""Protected, non-curricular persistence for the A1 v4 practice demo."""

from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.session import get_db
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def practice_database(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'a1-v4-practice.sqlite'}",
        connect_args={"check_same_thread": False},
    )
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    yield factory
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _wav() -> bytes:
    return b"RIFF" + (40).to_bytes(4, "little") + b"WAVE" + b"practice"


def _create_session() -> tuple[str, str]:
    response = client.post(
        "/api/v1/a1-v4-practice-sessions",
        json={"user_id": "declared-demo-user"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["practice_session"] is True
    assert payload["curricular_accreditation"] is False
    assert payload["session_id"]
    assert payload["token"]
    return payload["session_id"], payload["token"]


def _headers(token: str) -> dict[str, str]:
    return {"X-A1-V4-Practice-Token": token}


def _upload(session_id: str, token: str) -> str:
    response = client.post(
        f"/api/v1/a1-v4-practice-sessions/{session_id}/audio",
        headers=_headers(token),
        files={"audio": ("answer.wav", _wav(), "audio/wav")},
    )
    assert response.status_code == 200
    return response.json()["audio_reference"]


def _save_payload(audio_references: list[str]) -> dict:
    activities = [
        "own-production",
        "lower-support-own-production",
        "nearby-transfer-food",
    ]
    return {
        "productions": [
            {
                "activity_id": activity,
                "audio_reference": audio_reference,
                "transcript": "I need water." if activity != activities[-1] else "I need food.",
                "client_evaluation": {"semantic_status": "adequate"},
            }
            for activity, audio_reference in zip(activities, audio_references)
        ]
    }


def test_practice_session_protects_audio_save_and_read(monkeypatch, tmp_path):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    session_id, token = _create_session()

    assert client.get(f"/api/v1/a1-v4-practice-sessions/{session_id}").status_code == 401
    assert client.get(
        f"/api/v1/a1-v4-practice-sessions/{session_id}",
        headers=_headers("wrong-token"),
    ).status_code == 403

    audio_references = [_upload(session_id, token) for _ in range(3)]
    payload = _save_payload(audio_references)
    saved = client.post(
        f"/api/v1/a1-v4-practice-sessions/{session_id}/save",
        headers=_headers(token),
        json=payload,
    )
    assert saved.status_code == 200
    assert saved.json()["saved"] is True
    assert saved.json()["practice_completed"] is True
    assert saved.json()["curricular_accreditation"] is False

    repeated = client.post(
        f"/api/v1/a1-v4-practice-sessions/{session_id}/save",
        headers=_headers(token),
        json=payload,
    )
    assert repeated.status_code == 200
    assert repeated.json() == saved.json()

    changed = _save_payload(audio_references)
    changed["productions"][0]["transcript"] = "I need tea."
    conflict = client.post(
        f"/api/v1/a1-v4-practice-sessions/{session_id}/save",
        headers=_headers(token),
        json=changed,
    )
    assert conflict.status_code == 409

    stored = client.get(
        f"/api/v1/a1-v4-practice-sessions/{session_id}",
        headers=_headers(token),
    )
    assert stored.status_code == 200
    assert [item["activity_id"] for item in stored.json()["productions"]] == [
        "own-production",
        "lower-support-own-production",
        "nearby-transfer-food",
    ]


def test_practice_session_rejects_audio_owned_by_another_session(monkeypatch, tmp_path):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    first_id, first_token = _create_session()
    second_id, second_token = _create_session()
    foreign_audio = _upload(first_id, first_token)
    own_audio = [_upload(second_id, second_token) for _ in range(2)]

    response = client.post(
        f"/api/v1/a1-v4-practice-sessions/{second_id}/save",
        headers=_headers(second_token),
        json=_save_payload([foreign_audio, *own_audio]),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Audio reference is not linked to this practice session"


@pytest.mark.parametrize(
    ("change_second_payload", "expected_statuses"),
    [
        (False, [200, 200]),
        (True, [200, 409]),
    ],
)
def test_concurrent_saves_are_idempotent_or_conflict(
    monkeypatch,
    tmp_path,
    practice_database,
    change_second_payload,
    expected_statuses,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    session_id, token = _create_session()
    audio_references = [_upload(session_id, token) for _ in range(3)]
    first_payload = _save_payload(audio_references)
    second_payload = _save_payload(audio_references)
    if change_second_payload:
        second_payload["productions"][0]["transcript"] = "I need tea."

    barrier = Barrier(2)
    from app.services import a1_v4_practice_session_service as service

    original_canonical_content = service._canonical_content

    def synchronized_canonical_content(save):
        result = original_canonical_content(save)
        barrier.wait(timeout=5)
        return result

    monkeypatch.setattr(service, "_canonical_content", synchronized_canonical_content)

    from app.schemas.a1_v4_practice_session import A1V4PracticeSessionSave

    def save(payload):
        db = practice_database()
        try:
            session = service.require_session(session_id, token, db)
            result = service.save_session(
                session,
                A1V4PracticeSessionSave.model_validate(payload),
                db,
            )
            return 200, result.model_dump(mode="json")
        except service.A1V4PracticeConflictError:
            return 409, None
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(save, [first_payload, second_payload]))

    assert sorted(status for status, _ in responses) == expected_statuses
    successful = [body for status, body in responses if status == 200]
    assert all(result["saved"] is True for result in successful)
    if not change_second_payload:
        assert successful[0] == successful[1]


@pytest.mark.parametrize("evaluation", [None, {"semantic_status": "needs_repair"}])
def test_saved_productions_do_not_complete_practice_without_three_adequate_evaluations(
    monkeypatch,
    tmp_path,
    evaluation,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    session_id, token = _create_session()
    audio_references = [_upload(session_id, token) for _ in range(3)]
    payload = _save_payload(audio_references)
    payload["productions"][1]["client_evaluation"] = evaluation

    response = client.post(
        f"/api/v1/a1-v4-practice-sessions/{session_id}/save",
        headers=_headers(token),
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["saved"] is True
    assert response.json()["practice_completed"] is False
    assert response.json()["curricular_accreditation"] is False
