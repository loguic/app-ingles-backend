"""Apply qualitative Direct-English reviews to authoritative evidence state."""

from collections import defaultdict

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    DirectEnglishConstructionAttemptProduction as AttemptProductionModel,
    DirectEnglishConstructionProductionReview as ReviewModel,
    ExperienceEvidenceState,
)
from app.schemas.direct_english_construction_review import (
    DirectEnglishConstructionQualitativeReviewBatch,
    DirectEnglishConstructionQualitativeReviewRecord,
)
from app.services.direct_english_construction_review_persistence_service import (
    DirectEnglishConstructionReviewError,
    DirectEnglishConstructionReviewInvariantError,
    DirectEnglishConstructionReviewPersistenceError,
    stage_direct_english_construction_qualitative_reviews,
)
from app.services.experience_evidence_service import accredit_evidence_states


def _required_positive_pairs(evidence) -> set[tuple[str, str]]:
    return {
        (requirement.production_function, requirement.dimension)
        for requirement in evidence.external_review_requirements
        if requirement.production_function is not None
        and requirement.positive_required_for_completion
    }


def _positive_coverage_by_source(
    direct_attempt_id: str,
    evidence_definition_id: str,
    db: Session,
) -> dict[tuple[str, str, str | None], set[tuple[str, str]]]:
    rows = (
        db.query(ReviewModel, AttemptProductionModel.production_function)
        .join(
            AttemptProductionModel,
            AttemptProductionModel.id == ReviewModel.attempt_production_id,
        )
        .filter(
            AttemptProductionModel.attempt_id == direct_attempt_id,
            AttemptProductionModel.evidence_id == evidence_definition_id,
            ReviewModel.result == "positive",
        )
        .all()
    )
    coverage = defaultdict(set)
    for review, production_function in rows:
        source = (
            review.source_type,
            review.source_id,
            review.source_version,
        )
        coverage[source].add((production_function, review.dimension))
    return dict(coverage)


def _promote_if_complete(stage, db: Session) -> None:
    state = (
        db.query(ExperienceEvidenceState)
        .filter(
            ExperienceEvidenceState.experience_attempt_id
            == stage.experience_attempt.attempt_id,
            ExperienceEvidenceState.evidence_definition_id
            == stage.evidence.id,
        )
        .with_for_update()
        .one_or_none()
    )
    if (
        state is None
        or state.status != "needs_review"
        or state.source_type != "direct_english_construction_attempt"
        or state.direct_english_construction_attempt_id
        != stage.direct_attempt.attempt_id
    ):
        return

    required_pairs = _required_positive_pairs(stage.evidence)
    if not required_pairs:
        return
    coverage_by_source = _positive_coverage_by_source(
        stage.direct_attempt.attempt_id,
        stage.evidence.id,
        db,
    )
    if not any(
        required_pairs <= covered_pairs
        for covered_pairs in coverage_by_source.values()
    ):
        return

    try:
        accredit_evidence_states(
            stage.experience_attempt,
            stage.lesson,
            [
                (
                    stage.evidence,
                    "satisfied",
                    "direct_english_construction_attempt",
                    stage.direct_attempt.attempt_id,
                )
            ],
            db,
        )
    except ValueError as exc:
        raise DirectEnglishConstructionReviewInvariantError(str(exc)) from exc


def save_and_accredit_direct_english_construction_qualitative_reviews(
    batch: DirectEnglishConstructionQualitativeReviewBatch,
    db: Session,
) -> list[DirectEnglishConstructionQualitativeReviewRecord]:
    """Append reviews and promote their effective evidence in one transaction."""
    try:
        stage = stage_direct_english_construction_qualitative_reviews(batch, db)
        _promote_if_complete(stage, db)
        db.commit()
        return list(stage.records)
    except DirectEnglishConstructionReviewError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise DirectEnglishConstructionReviewInvariantError(
            "Could not apply Direct-English qualitative reviews"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DirectEnglishConstructionReviewPersistenceError(
            "Could not apply Direct-English qualitative reviews"
        ) from exc
    except Exception:
        db.rollback()
        raise
