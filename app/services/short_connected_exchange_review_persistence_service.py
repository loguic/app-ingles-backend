from collections import defaultdict
from datetime import UTC

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
    ShortConnectedExchangeProductionReview as ReviewModel,
)
from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReviewBatch,
    ShortConnectedExchangeProductionReviewHistory,
    ShortConnectedExchangeProductionReviewRecord,
    ShortConnectedExchangeSubmissionReviewHistory,
)
from app.services.content_service import (
    get_conversation_context_by_id,
    get_lesson_by_id,
)


B181_LESSON_ID = "a1-u1-l2"
B181_CONVERSATION_ID = "a1-u1-l2-c1"


class ShortConnectedExchangeReviewError(RuntimeError):
    """Base error for independent B181 production reviews."""


class ShortConnectedExchangeReviewReferenceError(
    ShortConnectedExchangeReviewError
):
    """Report a missing or out-of-scope persisted reference."""


class ShortConnectedExchangeReviewInvariantError(
    ShortConnectedExchangeReviewError
):
    """Report a mismatch with the active B181 review rubric."""


class ShortConnectedExchangeReviewPersistenceError(
    ShortConnectedExchangeReviewError
):
    """Report a storage failure without exposing database details."""


def _record(review: ReviewModel) -> ShortConnectedExchangeProductionReviewRecord:
    reviewed_at = review.reviewed_at
    if reviewed_at.tzinfo is None:
        reviewed_at = reviewed_at.replace(tzinfo=UTC)
    return ShortConnectedExchangeProductionReviewRecord(
        review_id=review.review_id,
        production_id=review.production_id,
        dimension=review.dimension,
        result=review.result,
        source_type=review.source_type,
        source_id=review.source_id,
        source_version=review.source_version,
        reviewed_at=reviewed_at,
    )


def _b181_context():
    context = get_conversation_context_by_id(B181_CONVERSATION_ID)
    if context is None:
        raise ShortConnectedExchangeReviewInvariantError(
            "Active B181 conversation does not exist"
        )
    level_id, unit_id, lesson_id, conversation = context
    if lesson_id != B181_LESSON_ID or conversation.id != B181_CONVERSATION_ID:
        raise ShortConnectedExchangeReviewInvariantError(
            "Active B181 conversation hierarchy is invalid"
        )
    return level_id, unit_id, lesson_id, conversation


def _requirements_by_prompt(conversation):
    prompt_turns = {
        turn.production_prompt.id: turn.id
        for turn in conversation.turns
        if turn.production_prompt is not None
    }
    context = get_conversation_context_by_id(conversation.id)
    assert context is not None
    lesson_id = context[2]
    lesson = get_lesson_by_id(lesson_id)
    experience = lesson.experience if lesson is not None else None
    if experience is None:
        raise ShortConnectedExchangeReviewInvariantError(
            "Active B181 review rubric does not exist"
        )
    evidence_by_prompt = defaultdict(list)
    for evidence in experience.evidence_definitions:
        if evidence.production_prompt_id is not None:
            evidence_by_prompt[evidence.production_prompt_id].append(evidence)
    requirements = {}
    for prompt_id, turn_id in prompt_turns.items():
        evidence = evidence_by_prompt[prompt_id]
        if len(evidence) != 1:
            raise ShortConnectedExchangeReviewInvariantError(
                "B181 prompt must map to exactly one evidence definition"
            )
        requirements[prompt_id] = (
            turn_id,
            {
                item.dimension: set(item.allowed_results)
                for item in evidence[0].external_review_requirements
            },
        )
    return requirements


def _submission_productions(
    submission: SubmissionModel,
    requirements,
    db: Session,
):
    productions = (
        db.query(ProductionModel)
        .filter(ProductionModel.submission_id == submission.id)
        .order_by(ProductionModel.id.asc())
        .all()
    )
    if len(productions) != 3:
        raise ShortConnectedExchangeReviewInvariantError(
            "B181 submission must contain three real productions"
        )
    if {production.prompt_id for production in productions} != set(
        requirements
    ):
        raise ShortConnectedExchangeReviewInvariantError(
            "B181 submission prompts do not match active content"
        )
    for production in productions:
        expected_turn_id = requirements[production.prompt_id][0]
        if production.turn_id != expected_turn_id:
            raise ShortConnectedExchangeReviewInvariantError(
                "B181 production turn does not match its prompt"
            )
    return productions


def _validated_productions(batch, db: Session):
    review_ids = [review.review_id for review in batch.reviews]
    if len(review_ids) != len(set(review_ids)):
        raise ShortConnectedExchangeReviewInvariantError(
            "Review IDs must be unique within one batch"
        )
    pairs = [
        (review.production_id, review.dimension)
        for review in batch.reviews
    ]
    if len(pairs) != len(set(pairs)):
        raise ShortConnectedExchangeReviewInvariantError(
            "Production and dimension must be unique within one batch"
        )
    production_ids = {review.production_id for review in batch.reviews}
    rows = (
        db.query(ProductionModel, SubmissionModel)
        .join(
            SubmissionModel,
            SubmissionModel.id == ProductionModel.submission_id,
        )
        .filter(ProductionModel.id.in_(production_ids))
        .all()
    )
    by_id = {
        production.id: (production, submission)
        for production, submission in rows
    }
    missing = sorted(production_ids - set(by_id))
    if missing:
        raise ShortConnectedExchangeReviewReferenceError(
            "Reviews reference unknown productions: "
            + ", ".join(str(item) for item in missing)
        )
    submission_ids = {submission.id for _, submission in by_id.values()}
    if len(submission_ids) != 1:
        raise ShortConnectedExchangeReviewInvariantError(
            "One review batch must belong to one submission"
        )
    level_id, unit_id, lesson_id, conversation = _b181_context()
    requirements = _requirements_by_prompt(conversation)
    submission = next(iter(by_id.values()))[1]
    _submission_productions(submission, requirements, db)
    for review in batch.reviews:
        production, submission = by_id[review.production_id]
        if (
            submission.level_id != level_id
            or submission.unit_id != unit_id
            or submission.lesson_id != lesson_id
            or submission.conversation_id != conversation.id
        ):
            raise ShortConnectedExchangeReviewReferenceError(
                "Review production does not belong to active B181 content"
            )
        prompt_requirement = requirements.get(production.prompt_id)
        if prompt_requirement is None:
            raise ShortConnectedExchangeReviewInvariantError(
                "Review production prompt is not declared by B181"
            )
        expected_turn_id, dimensions = prompt_requirement
        if production.turn_id != expected_turn_id:
            raise ShortConnectedExchangeReviewInvariantError(
                "Review production turn does not match its B181 prompt"
            )
        allowed_results = dimensions.get(review.dimension)
        if allowed_results is None:
            raise ShortConnectedExchangeReviewInvariantError(
                "Review dimension is not declared by B181 evidence"
            )
        if review.result not in allowed_results:
            raise ShortConnectedExchangeReviewInvariantError(
                "Review result is not allowed by B181 evidence"
            )
    return by_id


def save_short_connected_exchange_production_reviews(
    batch: ShortConnectedExchangeProductionReviewBatch,
    db: Session,
) -> list[ShortConnectedExchangeProductionReviewRecord]:
    """Validate and append one B181 review batch atomically."""
    try:
        _validated_productions(batch, db)
        review_ids = [review.review_id for review in batch.reviews]
        if (
            db.query(ReviewModel.review_id)
            .filter(ReviewModel.review_id.in_(review_ids))
            .first()
            is not None
        ):
            raise ShortConnectedExchangeReviewInvariantError(
                "Review ID already exists"
            )
        models = [
            ReviewModel(
                review_id=review.review_id,
                production_id=review.production_id,
                dimension=review.dimension,
                result=review.result,
                source_type=review.source_type,
                source_id=review.source_id,
                source_version=review.source_version,
                reviewed_at=review.reviewed_at,
            )
            for review in batch.reviews
        ]
        db.add_all(models)
        db.flush()
        records = [_record(model) for model in models]
        db.commit()
        return records
    except ShortConnectedExchangeReviewError:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        raise ShortConnectedExchangeReviewInvariantError(
            "Review batch conflicts with persisted data"
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        raise ShortConnectedExchangeReviewPersistenceError(
            "Could not persist B181 production reviews"
        ) from error
    except Exception:
        db.rollback()
        raise


def get_short_connected_exchange_reviews_by_submission(
    submission_id: int,
    db: Session,
) -> ShortConnectedExchangeSubmissionReviewHistory:
    """Return every independent review for one complete B181 submission."""
    submission = db.get(SubmissionModel, submission_id)
    if submission is None:
        raise ShortConnectedExchangeReviewReferenceError(
            "Conversation production submission does not exist"
        )
    level_id, unit_id, lesson_id, conversation = _b181_context()
    if (
        submission.level_id != level_id
        or submission.unit_id != unit_id
        or submission.lesson_id != lesson_id
        or submission.conversation_id != conversation.id
    ):
        raise ShortConnectedExchangeReviewReferenceError(
            "Submission does not belong to active B181 content"
        )
    requirements = _requirements_by_prompt(conversation)
    productions = _submission_productions(submission, requirements, db)
    production_ids = [production.id for production in productions]
    reviews = (
        db.query(ReviewModel)
        .filter(ReviewModel.production_id.in_(production_ids))
        .order_by(
            ReviewModel.reviewed_at.asc(),
            ReviewModel.review_id.asc(),
        )
        .all()
    )
    reviews_by_production = defaultdict(list)
    for review in reviews:
        reviews_by_production[review.production_id].append(_record(review))
    return ShortConnectedExchangeSubmissionReviewHistory(
        submission_id=submission.id,
        productions=[
            ShortConnectedExchangeProductionReviewHistory(
                production_id=production.id,
                prompt_id=production.prompt_id,
                turn_id=production.turn_id,
                reviews=reviews_by_production[production.id],
            )
            for production in productions
        ],
    )
