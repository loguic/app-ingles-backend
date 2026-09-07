"""Persist append-only qualitative reviews for bound Direct-English sources.

Persiste revisiones cualitativas append-only de fuentes Direct-English ligadas.
"""

from dataclasses import dataclass
from datetime import UTC

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    DirectEnglishConstructionAttempt as AttemptModel,
    DirectEnglishConstructionAttemptProduction as AttemptProductionModel,
    DirectEnglishConstructionProductionReview as ReviewModel,
    ExperienceAttempt,
)
from app.schemas.direct_english_construction_review import (
    DirectEnglishConstructionQualitativeReviewBatch,
    DirectEnglishConstructionQualitativeReviewRecord,
)
from app.schemas.content import EvidenceDefinition, Lesson
from app.services.content_service import get_lesson_context_by_id


class DirectEnglishConstructionReviewError(RuntimeError):
    """Base error for Direct-English qualitative review persistence."""


class DirectEnglishConstructionReviewReferenceError(
    DirectEnglishConstructionReviewError
):
    """Report a missing or cross-bound persisted source."""


class DirectEnglishConstructionReviewInvariantError(
    DirectEnglishConstructionReviewError
):
    """Report a conflict with the declared Direct-English review contract."""


class DirectEnglishConstructionReviewPersistenceError(
    DirectEnglishConstructionReviewError
):
    """Report storage failure without exposing database details."""


@dataclass(frozen=True)
class DirectEnglishConstructionReviewPersistenceStage:
    """Expose one flushed review batch to a transaction-owning orchestrator."""

    records: tuple[DirectEnglishConstructionQualitativeReviewRecord, ...]
    experience_attempt: ExperienceAttempt
    lesson: Lesson
    evidence: EvidenceDefinition
    direct_attempt: AttemptModel


def _record(
    review: ReviewModel,
    production_function: str,
) -> DirectEnglishConstructionQualitativeReviewRecord:
    reviewed_at = review.reviewed_at
    if reviewed_at.tzinfo is None:
        reviewed_at = reviewed_at.replace(tzinfo=UTC)
    return DirectEnglishConstructionQualitativeReviewRecord(
        review_id=review.review_id,
        production_function=production_function,
        dimension=review.dimension,
        result=review.result,
        source_type=review.source_type,
        source_id=review.source_id,
        source_version=review.source_version,
        reviewed_at=reviewed_at,
        attempt_production_id=review.attempt_production_id,
    )


def _resolve_bound_source(
    batch: DirectEnglishConstructionQualitativeReviewBatch,
    db: Session,
):
    experience_attempt = (
        db.query(ExperienceAttempt)
        .filter(ExperienceAttempt.attempt_id == batch.experience_attempt_id)
        .with_for_update()
        .one_or_none()
    )
    if experience_attempt is None:
        raise DirectEnglishConstructionReviewReferenceError(
            "Experience attempt does not exist"
        )

    direct_attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.attempt_id == batch.direct_english_attempt_id)
        .with_for_update()
        .one_or_none()
    )
    if direct_attempt is None:
        raise DirectEnglishConstructionReviewReferenceError(
            "Direct-English construction attempt does not exist"
        )
    if direct_attempt.experience_attempt_id != experience_attempt.attempt_id:
        raise DirectEnglishConstructionReviewReferenceError(
            "Direct-English construction attempt belongs to another experience attempt"
        )
    if direct_attempt.status != "finalized":
        raise DirectEnglishConstructionReviewInvariantError(
            "Direct-English construction attempt is not finalized"
        )
    if direct_attempt.evidence_definition_id != batch.evidence_definition_id:
        raise DirectEnglishConstructionReviewReferenceError(
            "Direct-English construction attempt belongs to another evidence definition"
        )
    if (
        direct_attempt.user_id != experience_attempt.user_id
        or direct_attempt.level_id != experience_attempt.level_id
        or direct_attempt.unit_id != experience_attempt.unit_id
        or direct_attempt.lesson_id != experience_attempt.lesson_id
    ):
        raise DirectEnglishConstructionReviewInvariantError(
            "Direct-English construction attempt contradicts the experience source"
        )

    context = get_lesson_context_by_id(experience_attempt.lesson_id)
    if context is None:
        raise DirectEnglishConstructionReviewInvariantError(
            "Experience hierarchy does not match the content tree"
        )
    level_id, unit_id, lesson = context
    experience = lesson.experience
    if (
        level_id != experience_attempt.level_id
        or unit_id != experience_attempt.unit_id
        or experience is None
        or experience.contract_version
        != experience_attempt.experience_contract_version
    ):
        raise DirectEnglishConstructionReviewInvariantError(
            "Experience hierarchy does not match the content tree"
        )
    evidence = next(
        (
            item
            for item in experience.evidence_definitions
            if item.id == batch.evidence_definition_id
        ),
        None,
    )
    if evidence is None:
        raise DirectEnglishConstructionReviewInvariantError(
            "Direct-English review evidence is unavailable"
        )
    if evidence.evidence_type not in {
        "guided_production",
        "contextual_response",
    }:
        raise DirectEnglishConstructionReviewInvariantError(
            "Direct-English qualitative review requires direct production evidence"
        )
    return experience_attempt, lesson, evidence, direct_attempt


def _validate_batch_invariants(
    batch: DirectEnglishConstructionQualitativeReviewBatch,
) -> None:
    """Reassert write-boundary invariants for one immutable review batch."""
    review_ids = [review.review_id for review in batch.reviews]
    if len(review_ids) != len(set(review_ids)):
        raise DirectEnglishConstructionReviewInvariantError(
            "Review IDs must be unique within one batch"
        )
    pairs = [
        (review.production_function, review.dimension)
        for review in batch.reviews
    ]
    if len(pairs) != len(set(pairs)):
        raise DirectEnglishConstructionReviewInvariantError(
            "Production function and dimension must be unique within one batch"
        )
    source_identity = {
        (
            review.source_type,
            review.source_id,
            review.source_version,
        )
        for review in batch.reviews
    }
    if len(source_identity) != 1:
        raise DirectEnglishConstructionReviewInvariantError(
            "One review batch requires one source identity"
        )


def stage_direct_english_construction_qualitative_reviews(
    batch: DirectEnglishConstructionQualitativeReviewBatch,
    db: Session,
) -> DirectEnglishConstructionReviewPersistenceStage:
    """Validate and flush one neutral review batch without owning commit."""
    _validate_batch_invariants(batch)
    experience_attempt, lesson, evidence, direct_attempt = _resolve_bound_source(
        batch,
        db,
    )
    links = (
        db.query(AttemptProductionModel)
        .filter(AttemptProductionModel.attempt_id == direct_attempt.attempt_id)
        .with_for_update()
        .all()
    )
    links_by_function = {link.production_function: link for link in links}
    requirements_by_key = {
        (requirement.production_function, requirement.dimension): requirement
        for requirement in evidence.external_review_requirements
    }
    for review in batch.reviews:
        link = links_by_function.get(review.production_function)
        if link is None:
            raise DirectEnglishConstructionReviewReferenceError(
                "Direct-English attempt production does not exist"
            )
        if link.evidence_id != batch.evidence_definition_id:
            raise DirectEnglishConstructionReviewReferenceError(
                "Direct-English attempt production belongs to another evidence definition"
            )
        requirement = requirements_by_key.get(
            (review.production_function, review.dimension)
        )
        if requirement is None:
            raise DirectEnglishConstructionReviewInvariantError(
                "Qualitative review dimension is not declared for this production function"
            )
        if review.result not in requirement.allowed_results:
            raise DirectEnglishConstructionReviewInvariantError(
                "Qualitative review result is not permitted by active content"
            )

    review_ids = [review.review_id for review in batch.reviews]
    existing_review_id = (
        db.query(ReviewModel.review_id)
        .filter(ReviewModel.review_id.in_(review_ids))
        .first()
    )
    if existing_review_id is not None:
        raise DirectEnglishConstructionReviewInvariantError(
            "Qualitative review_id already exists"
        )

    persisted = [
        ReviewModel(
            review_id=review.review_id,
            attempt_production_id=links_by_function[
                review.production_function
            ].id,
            dimension=review.dimension,
            result=review.result,
            source_type=review.source_type,
            source_id=review.source_id,
            source_version=review.source_version,
            reviewed_at=review.reviewed_at,
        )
        for review in batch.reviews
    ]
    db.add_all(persisted)
    db.flush()
    records = tuple(
        _record(review, command.production_function)
        for review, command in zip(persisted, batch.reviews, strict=True)
    )
    return DirectEnglishConstructionReviewPersistenceStage(
        records=records,
        experience_attempt=experience_attempt,
        lesson=lesson,
        evidence=evidence,
        direct_attempt=direct_attempt,
    )


def save_direct_english_construction_qualitative_reviews(
    batch: DirectEnglishConstructionQualitativeReviewBatch,
    db: Session,
) -> list[DirectEnglishConstructionQualitativeReviewRecord]:
    """Validate and append one Direct-English review batch atomically.

    This persistence boundary records review facts only. It never updates
    evidence states, completion, progress, mastery, or retention.
    """
    try:
        stage = stage_direct_english_construction_qualitative_reviews(batch, db)
        db.commit()
        return list(stage.records)
    except DirectEnglishConstructionReviewError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise DirectEnglishConstructionReviewInvariantError(
            "Could not append Direct-English qualitative reviews"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DirectEnglishConstructionReviewPersistenceError(
            "Could not persist Direct-English qualitative reviews"
        ) from exc
    except Exception:
        db.rollback()
        raise
