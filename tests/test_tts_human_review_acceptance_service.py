"""Functional, non-concurrent coverage for durable TTS review acceptance."""

from datetime import UTC, datetime
import hashlib
import os
from pathlib import Path
import tempfile

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.db.models import TtsHumanReviewAcceptance
from app.schemas.tts_engine_benchmark import (
    HumanReviewRecord,
    LockClaim,
    TTS_PUBLIC_REVIEW_SLOT_VERSION,
)
from app.services import tts_human_review_acceptance_service as acceptance_service
from app.services.tts_human_review_acceptance_service import (
    InvalidLockedHandoff,
    LockedReviewHandoffAcceptanceRequest,
    ReviewAcceptancePersistenceError,
    ReviewSlotConflict,
    StoredReviewIntegrityError,
    accept_locked_review_handoff,
)
from app.services.tts_public_reviewer_workflow import (
    lock_public_review,
    serialize_locked_review_handoff,
)
from scripts.engineering.postgresql_devsecops_adapter import (
    AdapterConfig,
    AdapterError,
    CommandRunner,
    PostgreSQLCluster,
    cleanup_workspace,
    create_database,
    create_workspace,
    discover_binaries,
    run_alembic,
    validate_config,
)
from tests.test_tts_engine_benchmark_schema import (
    PRIVATE_COMMITMENT_KEY as REAL_PRIVATE_COMMITMENT_KEY,
    _complete_public_review,
)


ROOT = Path(__file__).resolve().parents[1]
BASE_REVISION = "d1842b7f3a91"
ACCEPTANCE_REVISION = "e6c42a9b1d70"
PRIVATE_KEY = b"test-private-review-commitment-key"
PACKAGE = object()
PRIVATE_MANIFEST = object()


@pytest.fixture(scope="module")
def acceptance_session_factory():
    authorized_parent = Path(tempfile.gettempdir())
    port = 58000 + (os.getpid() % 7000)
    config = AdapterConfig(
        environment="test",
        port=port,
        repository_root=ROOT,
        authorized_temp_parent=authorized_parent,
        initial_revision=BASE_REVISION,
        target_revision=ACCEPTANCE_REVISION,
    )
    validate_config(config)
    workspace = create_workspace(authorized_parent)
    cluster = PostgreSQLCluster(
        workspace,
        discover_binaries(repository_root=ROOT),
        CommandRunner(config.timeout_seconds),
        port,
    )
    engine = None
    database = "tts_human_review_acceptance_service"
    try:
        cluster.initialize()
        cluster.start()
        create_database(cluster, database)
        run_alembic(cluster, database, "upgrade", ACCEPTANCE_REVISION, ROOT)
        engine = create_engine(
            f"postgresql+psycopg://postgres@/{database}",
            connect_args={"host": str(workspace.socket), "port": port},
        )
        yield sessionmaker(bind=engine, expire_on_commit=False)
    except AdapterError as error:
        pytest.fail(
            f"isolated PostgreSQL setup failed: {error}",
            pytrace=False,
        )
    finally:
        if engine is not None:
            engine.dispose()
        try:
            cluster.stop()
        finally:
            cleanup_workspace(workspace)


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _claim(
    handoff_token: str,
    slot_token: str,
    *,
    naturalness: str = "meets",
) -> LockClaim:
    package_id = "review_package_" + _digest(f"package:{slot_token}")
    blind_review_id = "br_" + _digest(f"blind:{slot_token}")[:32]
    review = HumanReviewRecord.model_validate(
        {
            "blind_review_id": blind_review_id,
            "reviewer_id": "reviewer_a",
            "locked_at": datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
            "perceived_transcription": "I need water.",
            "first_listen_without_transcript": True,
            "reference_text_revealed_after_first_listen": True,
            "ipa_revealed_after_first_listen": True,
            "target_locale_revealed_after_first_listen": True,
            "intelligibility": "meets",
            "pronunciation_correctness": "meets",
            "locale_accent_conformance": "meets",
            "naturalness": naturalness,
            "prosody_rhythm": "meets",
            "a1_pedagogical_suitability": "meets",
        }
    )
    slot_payload = (
        '{"blind_review_id":"'
        + blind_review_id
        + '","domain":"'
        + TTS_PUBLIC_REVIEW_SLOT_VERSION
        + '","package_id":"'
        + package_id
        + '","reviewer_id":"reviewer_a"}'
    )
    return LockClaim.model_validate(
        {
            "review_slot_version": TTS_PUBLIC_REVIEW_SLOT_VERSION,
            "review_slot_id": "review_slot_"
            + hashlib.sha256(slot_payload.encode("utf-8")).hexdigest(),
            "package_id": package_id,
            "lock_transition_id": "review_lock_"
            + _digest(f"lock:{handoff_token}"),
            "handoff_id": "review_handoff_" + _digest(f"handoff:{handoff_token}"),
            "review": review,
        }
    )


def _payload(token: str) -> bytes:
    return f'{{"canonical":"{token}"}}'.encode("utf-8")


def _request(payload: bytes) -> LockedReviewHandoffAcceptanceRequest:
    return LockedReviewHandoffAcceptanceRequest(
        canonical_handoff=payload,
        package=PACKAGE,  # type: ignore[arg-type]
        private_manifest=PRIVATE_MANIFEST,  # type: ignore[arg-type]
        private_commitment_key=PRIVATE_KEY,
    )


def _patch_validation(monkeypatch, claims_by_payload):
    calls = []

    def fake_validate(package, manifest, payload, *, private_commitment_key):
        assert package is PACKAGE
        assert manifest is PRIVATE_MANIFEST
        assert private_commitment_key == PRIVATE_KEY
        calls.append(payload)
        outcome = claims_by_payload[payload]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(
        acceptance_service,
        "validate_locked_review_handoff",
        fake_validate,
    )
    return calls


def _rows(session_factory):
    with session_factory() as db:
        return list(
            db.execute(
                select(TtsHumanReviewAcceptance).order_by(
                    TtsHumanReviewAcceptance.review_slot_id
                )
            ).scalars()
        )


def _seed(
    session_factory,
    *,
    claim: LockClaim,
    canonical_handoff: bytes,
    review_slot_id: str | None = None,
    handoff_id: str | None = None,
):
    with session_factory() as db:
        db.execute(
            postgresql_insert(TtsHumanReviewAcceptance).values(
                review_slot_id=review_slot_id or claim.review_slot_id,
                review_slot_version=claim.review_slot_version,
                package_id=claim.package_id,
                handoff_id=handoff_id or claim.handoff_id,
                lock_transition_id=claim.lock_transition_id,
                review_id=claim.review.review_id,
                canonical_handoff=canonical_handoff,
            )
        )
        db.commit()


def test_invalid_handoff_does_not_open_a_session_or_write(monkeypatch):
    payload = _payload("invalid")
    _patch_validation(monkeypatch, {payload: ValueError("invalid handoff")})
    opened = 0

    def session_factory():
        nonlocal opened
        opened += 1
        raise AssertionError("invalid handoff must not open a session")

    with pytest.raises(InvalidLockedHandoff):
        accept_locked_review_handoff(_request(payload), session_factory=session_factory)
    assert opened == 0


def test_authentic_a_handoff_crosses_into_b_for_accept_retry_and_conflict(
    acceptance_session_factory,
):
    private_manifest, package, complete = _complete_public_review(
        naturalness="meets",
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )
    first_handoff = lock_public_review(
        complete,
        package,
        private_manifest,
        locked_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )
    first_payload = serialize_locked_review_handoff(
        first_handoff,
        package,
        private_manifest,
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )

    _, divergent_package, divergent_complete = _complete_public_review(
        naturalness="minor_issue",
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )
    divergent_handoff = lock_public_review(
        divergent_complete,
        divergent_package,
        private_manifest,
        locked_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )
    divergent_payload = serialize_locked_review_handoff(
        divergent_handoff,
        divergent_package,
        private_manifest,
        private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
    )

    first = accept_locked_review_handoff(
        LockedReviewHandoffAcceptanceRequest(
            canonical_handoff=first_payload,
            package=package,
            private_manifest=private_manifest,
            private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
        ),
        session_factory=acceptance_session_factory,
    )
    retry = accept_locked_review_handoff(
        LockedReviewHandoffAcceptanceRequest(
            canonical_handoff=first_payload,
            package=package,
            private_manifest=private_manifest,
            private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
        ),
        session_factory=acceptance_session_factory,
    )
    with pytest.raises(ReviewSlotConflict):
        accept_locked_review_handoff(
            LockedReviewHandoffAcceptanceRequest(
                canonical_handoff=divergent_payload,
                package=divergent_package,
                private_manifest=private_manifest,
                private_commitment_key=REAL_PRIVATE_COMMITMENT_KEY,
            ),
            session_factory=acceptance_session_factory,
        )

    assert first.status == "accepted"
    assert retry.status == "already_accepted"
    assert retry.accepted_at == first.accepted_at
    assert retry.claim == first.claim
    rows = [
        row
        for row in _rows(acceptance_session_factory)
        if row.review_slot_id == first.claim.review_slot_id
    ]
    assert len(rows) == 1
    assert rows[0].handoff_id == first.claim.handoff_id
    assert rows[0].canonical_handoff == first_payload
    assert rows[0].accepted_at == first.accepted_at


def test_first_accept_uses_factory_session_and_preserves_exact_bytes(
    acceptance_session_factory,
    monkeypatch,
):
    claim = _claim("first", "first-slot")
    payload = _payload("first")
    _patch_validation(monkeypatch, {payload: claim})
    created = []

    def session_factory():
        session = acceptance_session_factory()
        created.append(session)
        return session

    outside = acceptance_session_factory()
    outside.execute(select(func.count()).select_from(TtsHumanReviewAcceptance))
    try:
        result = accept_locked_review_handoff(
            _request(payload),
            session_factory=session_factory,
        )
        assert result.status == "accepted"
        assert result.claim == claim
        assert result.accepted_at.tzinfo is not None
        assert len(created) == 1
        assert outside.in_transaction()
        rows = [row for row in _rows(acceptance_session_factory) if row.handoff_id == claim.handoff_id]
        assert len(rows) == 1
        assert rows[0].canonical_handoff == payload
        assert rows[0].accepted_at == result.accepted_at
    finally:
        outside.rollback()
        outside.close()


def test_identical_retry_returns_original_acceptance_without_new_row(
    acceptance_session_factory,
    monkeypatch,
):
    claim = _claim("retry", "retry-slot")
    payload = _payload("retry")
    calls = _patch_validation(monkeypatch, {payload: claim})
    first = accept_locked_review_handoff(
        _request(payload),
        session_factory=acceptance_session_factory,
    )
    retry = accept_locked_review_handoff(
        _request(payload),
        session_factory=acceptance_session_factory,
    )
    assert first.status == "accepted"
    assert retry.status == "already_accepted"
    assert retry.claim == claim
    assert retry.accepted_at == first.accepted_at
    assert calls == [payload, payload, payload]
    assert len([row for row in _rows(acceptance_session_factory) if row.handoff_id == claim.handoff_id]) == 1


def test_divergent_valid_handoff_for_slot_is_conflict(
    acceptance_session_factory,
    monkeypatch,
):
    first_claim = _claim("conflict-first", "conflict-slot")
    other_claim = _claim(
        "conflict-other",
        "conflict-slot",
        naturalness="minor_issue",
    )
    first_payload = _payload("conflict-first")
    other_payload = _payload("conflict-other")
    _patch_validation(
        monkeypatch,
        {first_payload: first_claim, other_payload: other_claim},
    )
    accepted = accept_locked_review_handoff(
        _request(first_payload),
        session_factory=acceptance_session_factory,
    )
    with pytest.raises(ReviewSlotConflict):
        accept_locked_review_handoff(
            _request(other_payload),
            session_factory=acceptance_session_factory,
        )
    rows = [
        row
        for row in _rows(acceptance_session_factory)
        if row.review_slot_id == first_claim.review_slot_id
    ]
    assert len(rows) == 1
    assert rows[0].handoff_id == first_claim.handoff_id
    assert rows[0].canonical_handoff == first_payload
    assert rows[0].accepted_at == accepted.accepted_at


def test_divergent_stored_evidence_is_rejected(
    acceptance_session_factory,
    monkeypatch,
):
    incoming_claim = _claim("stored-incoming", "stored-slot")
    stored_claim = _claim("stored-other", "stored-slot", naturalness="minor_issue")
    incoming_payload = _payload("stored-incoming")
    stored_payload = _payload("stored-other")
    _patch_validation(
        monkeypatch,
        {incoming_payload: incoming_claim, stored_payload: stored_claim},
    )
    _seed(
        acceptance_session_factory,
        claim=incoming_claim,
        canonical_handoff=stored_payload,
    )
    with pytest.raises(StoredReviewIntegrityError):
        accept_locked_review_handoff(
            _request(incoming_payload),
            session_factory=acceptance_session_factory,
        )


def test_handoff_reused_in_another_slot_is_persistence_error(
    acceptance_session_factory,
    monkeypatch,
):
    claim = _claim("duplicate-handoff", "duplicate-slot")
    payload = _payload("duplicate-handoff")
    _patch_validation(monkeypatch, {payload: claim})
    _seed(
        acceptance_session_factory,
        claim=claim,
        canonical_handoff=payload,
        review_slot_id="review_slot_seeded_elsewhere",
    )
    with pytest.raises(ReviewAcceptancePersistenceError):
        accept_locked_review_handoff(
            _request(payload),
            session_factory=acceptance_session_factory,
        )
    assert len([row for row in _rows(acceptance_session_factory) if row.handoff_id == claim.handoff_id]) == 1


@pytest.mark.parametrize("operation", ("insert", "select"))
def test_insert_or_select_failure_rolls_back(
    acceptance_session_factory,
    monkeypatch,
    operation,
):
    claim = _claim(f"failure-{operation}", f"failure-{operation}-slot")
    payload = _payload(f"failure-{operation}")
    _patch_validation(monkeypatch, {payload: claim})
    db = acceptance_session_factory()
    rollbacks = 0
    original_rollback = db.rollback

    def counted_rollback():
        nonlocal rollbacks
        rollbacks += 1
        return original_rollback()

    monkeypatch.setattr(db, "rollback", counted_rollback)
    if operation == "insert":
        monkeypatch.setattr(
            acceptance_service,
            "_insert_acceptance_do_nothing",
            lambda *_args: (_ for _ in ()).throw(SQLAlchemyError("insert failed")),
        )
    else:
        monkeypatch.setattr(
            acceptance_service,
            "_insert_acceptance_do_nothing",
            lambda *_args: None,
        )
        monkeypatch.setattr(
            acceptance_service,
            "_load_acceptance_by_slot",
            lambda *_args: (_ for _ in ()).throw(SQLAlchemyError("select failed")),
        )

    with pytest.raises(ReviewAcceptancePersistenceError):
        accept_locked_review_handoff(_request(payload), session_factory=lambda: db)
    assert rollbacks == 1


def test_failed_commit_never_returns_accepted(
    acceptance_session_factory,
    monkeypatch,
):
    claim = _claim("commit-failure", "commit-failure-slot")
    payload = _payload("commit-failure")
    _patch_validation(monkeypatch, {payload: claim})
    db = acceptance_session_factory()
    monkeypatch.setattr(
        db,
        "commit",
        lambda: (_ for _ in ()).throw(SQLAlchemyError("commit failed")),
    )
    with pytest.raises(ReviewAcceptancePersistenceError):
        accept_locked_review_handoff(_request(payload), session_factory=lambda: db)
    assert not [row for row in _rows(acceptance_session_factory) if row.handoff_id == claim.handoff_id]


def test_uncertain_commit_is_not_accepted_and_retry_reads_durable_row(
    acceptance_session_factory,
    monkeypatch,
):
    claim = _claim("commit-uncertain", "commit-uncertain-slot")
    payload = _payload("commit-uncertain")
    _patch_validation(monkeypatch, {payload: claim})
    db = acceptance_session_factory()
    original_commit = db.commit

    def commit_then_fail():
        original_commit()
        raise SQLAlchemyError("commit acknowledgement lost")

    monkeypatch.setattr(db, "commit", commit_then_fail)
    with pytest.raises(ReviewAcceptancePersistenceError):
        accept_locked_review_handoff(_request(payload), session_factory=lambda: db)
    retry = accept_locked_review_handoff(
        _request(payload),
        session_factory=acceptance_session_factory,
    )
    assert retry.status == "already_accepted"
    assert retry.claim == claim
