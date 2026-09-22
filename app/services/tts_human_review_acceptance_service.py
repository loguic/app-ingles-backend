"""Durably accept one privately validated TTS human-review handoff."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Literal

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.orm import Session

from app.db.models import TtsHumanReviewAcceptance
from app.schemas.tts_engine_benchmark import (
    BlindReviewManifest,
    LockClaim,
    PublicReviewerPackage,
)
from app.services.tts_public_reviewer_workflow import (
    validate_locked_review_handoff,
)


class InvalidLockedHandoff(RuntimeError):
    """The private A boundary rejected the supplied handoff."""


class ReviewSlotConflict(RuntimeError):
    """Another valid handoff was already accepted for the review slot."""


class StoredReviewIntegrityError(RuntimeError):
    """Stored acceptance evidence cannot support its claimed provenance."""


class ReviewAcceptancePersistenceError(RuntimeError):
    """Persistence did not establish a reliable durable acceptance result."""


@dataclass(frozen=True)
class LockedReviewHandoffAcceptanceRequest:
    """A canonical handoff and the private context needed to validate it."""

    canonical_handoff: bytes
    package: PublicReviewerPackage
    private_manifest: BlindReviewManifest
    private_commitment_key: bytes = field(repr=False)


@dataclass(frozen=True)
class LockedReviewAcceptanceResult:
    """One durable acceptance outcome after A validation and B persistence."""

    status: Literal["accepted", "already_accepted"]
    claim: LockClaim
    accepted_at: datetime


@dataclass(frozen=True)
class _StoredAcceptance:
    review_slot_id: str
    review_slot_version: str
    package_id: str
    handoff_id: str
    lock_transition_id: str
    review_id: str
    canonical_handoff: bytes
    accepted_at: datetime


def _stored_acceptance_from_mapping(mapping) -> _StoredAcceptance | None:
    if mapping is None:
        return None
    return _StoredAcceptance(
        review_slot_id=mapping["review_slot_id"],
        review_slot_version=mapping["review_slot_version"],
        package_id=mapping["package_id"],
        handoff_id=mapping["handoff_id"],
        lock_transition_id=mapping["lock_transition_id"],
        review_id=mapping["review_id"],
        canonical_handoff=bytes(mapping["canonical_handoff"]),
        accepted_at=mapping["accepted_at"],
    )


def _acceptance_columns():
    return (
        TtsHumanReviewAcceptance.review_slot_id,
        TtsHumanReviewAcceptance.review_slot_version,
        TtsHumanReviewAcceptance.package_id,
        TtsHumanReviewAcceptance.handoff_id,
        TtsHumanReviewAcceptance.lock_transition_id,
        TtsHumanReviewAcceptance.review_id,
        TtsHumanReviewAcceptance.canonical_handoff,
        TtsHumanReviewAcceptance.accepted_at,
    )


def _insert_acceptance_do_nothing(
    db: Session,
    claim: LockClaim,
    canonical_handoff: bytes,
) -> _StoredAcceptance | None:
    statement = (
        postgresql_insert(TtsHumanReviewAcceptance)
        .values(
            review_slot_id=claim.review_slot_id,
            review_slot_version=claim.review_slot_version,
            package_id=claim.package_id,
            handoff_id=claim.handoff_id,
            lock_transition_id=claim.lock_transition_id,
            review_id=claim.review.review_id,
            canonical_handoff=canonical_handoff,
        )
        .on_conflict_do_nothing(
            index_elements=(TtsHumanReviewAcceptance.review_slot_id,)
        )
        .returning(*_acceptance_columns())
    )
    return _stored_acceptance_from_mapping(
        db.execute(statement).mappings().one_or_none()
    )


def _load_acceptance_by_slot(
    db: Session,
    review_slot_id: str,
) -> _StoredAcceptance | None:
    statement = select(*_acceptance_columns()).where(
        TtsHumanReviewAcceptance.review_slot_id == review_slot_id
    )
    return _stored_acceptance_from_mapping(
        db.execute(statement).mappings().one_or_none()
    )


def _stored_projections_match_claim(
    stored: _StoredAcceptance,
    claim: LockClaim,
    canonical_handoff: bytes,
) -> bool:
    return (
        stored.review_slot_id == claim.review_slot_id
        and stored.review_slot_version == claim.review_slot_version
        and stored.package_id == claim.package_id
        and stored.handoff_id == claim.handoff_id
        and stored.lock_transition_id == claim.lock_transition_id
        and stored.review_id == claim.review.review_id
        and stored.canonical_handoff == canonical_handoff
    )


def _reconstruct_and_verify_stored_acceptance(
    stored: _StoredAcceptance,
    request: LockedReviewHandoffAcceptanceRequest,
) -> LockClaim:
    try:
        claim = validate_locked_review_handoff(
            request.package,
            request.private_manifest,
            stored.canonical_handoff,
            private_commitment_key=request.private_commitment_key,
        )
    except Exception as error:
        raise StoredReviewIntegrityError(
            "Stored review acceptance cannot be validated by A"
        ) from error
    if not _stored_projections_match_claim(
        stored,
        claim,
        stored.canonical_handoff,
    ):
        raise StoredReviewIntegrityError(
            "Stored review acceptance projections diverge from its handoff"
        )
    return claim


def _rollback_defensively(db: Session) -> None:
    try:
        db.rollback()
    except Exception:
        pass


def accept_locked_review_handoff(
    request: LockedReviewHandoffAcceptanceRequest,
    *,
    session_factory: Callable[[], Session],
) -> LockedReviewAcceptanceResult:
    """Accept one canonical handoff only after A and the database both agree.

    The function owns the session it receives from ``session_factory``.  It
    never accepts an externally supplied ``LockClaim`` and never persists the
    private validation context.
    """

    try:
        claim = validate_locked_review_handoff(
            request.package,
            request.private_manifest,
            request.canonical_handoff,
            private_commitment_key=request.private_commitment_key,
        )
    except Exception as error:
        raise InvalidLockedHandoff("Locked review handoff is invalid") from error

    try:
        db = session_factory()
    except Exception as error:
        raise ReviewAcceptancePersistenceError(
            "Could not open an acceptance session"
        ) from error

    owns_session = False
    try:
        if db.in_transaction() or db.new or db.dirty or db.deleted:
            raise ReviewAcceptancePersistenceError(
                "Acceptance session factory must provide an unused session"
            )
        owns_session = True

        try:
            inserted = _insert_acceptance_do_nothing(
                db,
                claim,
                request.canonical_handoff,
            )
        except Exception as error:
            _rollback_defensively(db)
            raise ReviewAcceptancePersistenceError(
                "Could not insert review acceptance"
            ) from error

        if inserted is not None:
            try:
                db.commit()
            except Exception as error:
                _rollback_defensively(db)
                raise ReviewAcceptancePersistenceError(
                    "Review acceptance commit was not confirmed"
                ) from error
            return LockedReviewAcceptanceResult(
                status="accepted",
                claim=claim,
                accepted_at=inserted.accepted_at,
            )

        try:
            stored = _load_acceptance_by_slot(db, claim.review_slot_id)
        except Exception as error:
            _rollback_defensively(db)
            raise ReviewAcceptancePersistenceError(
                "Could not load existing review acceptance"
            ) from error
        if stored is None:
            _rollback_defensively(db)
            raise ReviewAcceptancePersistenceError(
                "Slot conflict did not yield a durable review acceptance"
            )

        try:
            stored_claim = _reconstruct_and_verify_stored_acceptance(
                stored,
                request,
            )
        except StoredReviewIntegrityError:
            _rollback_defensively(db)
            raise

        if stored.handoff_id != claim.handoff_id:
            _rollback_defensively(db)
            raise ReviewSlotConflict(
                "A different handoff is already accepted for this review slot"
            )
        if not _stored_projections_match_claim(
            stored,
            claim,
            request.canonical_handoff,
        ):
            _rollback_defensively(db)
            raise StoredReviewIntegrityError(
                "Stored review acceptance diverges from the supplied handoff"
            )

        _rollback_defensively(db)
        return LockedReviewAcceptanceResult(
            status="already_accepted",
            claim=stored_claim,
            accepted_at=stored.accepted_at,
        )
    finally:
        if owns_session:
            db.close()
