from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

import app.services.direct_english_construction_review_persistence_service as service
from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission,
    DirectEnglishConstructionAttempt,
    DirectEnglishConstructionAttemptProduction,
    DirectEnglishConstructionProductionReview,
    ExperienceAttempt,
    ExperienceEvidenceState,
    LearnerProduction,
)
from app.schemas.content import ExternalReviewRequirement
from app.schemas.direct_english_construction_review import (
    DirectEnglishConstructionQualitativeReview,
    DirectEnglishConstructionQualitativeReviewBatch,
)
from app.services.content_service import get_lesson_by_id
from app.services.direct_english_construction_review_persistence_service import (
    DirectEnglishConstructionReviewInvariantError,
    DirectEnglishConstructionReviewReferenceError,
    save_direct_english_construction_qualitative_reviews,
)


NOW = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)
EVIDENCE_ID = "a1-u1-l1-ev-guided"


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def review_lesson(monkeypatch):
    lesson = get_lesson_by_id("a1-u1-l1").model_copy(deep=True)
    assert lesson.experience is not None
    lesson.experience.contract_version = "3.0"
    evidence = next(
        item
        for item in lesson.experience.evidence_definitions
        if item.id == EVIDENCE_ID
    )
    evidence.external_review_requirements = [
        ExternalReviewRequirement.model_validate(
            {
                "dimension": dimension,
                "production_function": function,
                "allowed_results": ["positive", "negative", "pending"],
                "question": "Is this production acceptable?",
            }
        )
        for function in ("guided", "expanded", "transfer")
        for dimension in ("relevance", "intelligibility")
    ]
    monkeypatch.setattr(
        service,
        "get_lesson_context_by_id",
        lambda lesson_id: ("A1", "a1-u1", lesson)
        if lesson_id == lesson.id
        else None,
    )
    return lesson


def add_bound_source(db, *, suffix="one", finalized=True):
    experience = ExperienceAttempt(
        attempt_id="experience-" + suffix,
        user_id="review-user-" + suffix,
        level_id="A1",
        unit_id="a1-u1",
        lesson_id="a1-u1-l1",
        experience_contract_version="3.0",
        status="in_progress",
        started_at=NOW,
        completed_at=None,
    )
    direct = DirectEnglishConstructionAttempt(
        attempt_id="direct-" + suffix,
        user_id=experience.user_id,
        level_id=experience.level_id,
        unit_id=experience.unit_id,
        lesson_id=experience.lesson_id,
        experience_attempt_id=experience.attempt_id,
        evidence_definition_id=EVIDENCE_ID,
        transfer_bank_id="bank-1",
        transfer_variant_id="variant-1",
        transfer_prompt_snapshot="Say something different.",
        selector_version="sha256-v1",
        status="finalized" if finalized else "started",
        started_at=NOW,
        finalized_at=NOW + timedelta(minutes=1) if finalized else None,
    )
    submission = ConversationProductionSubmission(
        user_id=experience.user_id,
        level_id=experience.level_id,
        unit_id=experience.unit_id,
        lesson_id=experience.lesson_id,
        conversation_id="a1-u1-l1-c-direct-guided",
        experience_attempt_id=experience.attempt_id,
    )
    db.add(experience)
    db.flush()
    db.add(direct)
    db.flush()
    db.add(submission)
    db.flush()
    links = {}
    for function in ("guided", "expanded", "transfer"):
        production = LearnerProduction(
            submission_id=submission.id,
            prompt_id="prompt-" + suffix + "-" + function,
            turn_id="turn-" + suffix + "-" + function,
            modality="voice",
            audio_reference="audio://" + function,
        )
        db.add(production)
        db.flush()
        link = DirectEnglishConstructionAttemptProduction(
            attempt_id=direct.attempt_id,
            learner_production_id=production.id,
            production_function=function,
            evidence_id=EVIDENCE_ID,
            configured_support_level={
                "guided": "anchors",
                "expanded": "initial_word",
                "transfer": "none",
            }[function],
            support_used={
                "guided": "anchors",
                "expanded": "initial_word",
                "transfer": "none",
            }[function],
        )
        db.add(link)
        db.flush()
        links[function] = link
    db.commit()
    return experience, direct, links


def batch(source, *, reviews, evidence_id=EVIDENCE_ID):
    experience, direct, _links = source
    return DirectEnglishConstructionQualitativeReviewBatch.model_validate(
        {
            "experience_attempt_id": experience.attempt_id,
            "direct_english_attempt_id": direct.attempt_id,
            "evidence_definition_id": evidence_id,
            "reviews": reviews,
        }
    )


def review(
    review_id,
    *,
    function="guided",
    dimension="relevance",
    result="positive",
    source_id="reviewer-1",
    source_type="human",
    source_version=None,
):
    return {
        "review_id": review_id,
        "production_function": function,
        "dimension": dimension,
        "result": result,
        "source_type": source_type,
        "source_id": source_id,
        "source_version": source_version,
        "reviewed_at": NOW,
    }


def test_persists_one_valid_batch_append_only(db, review_lesson):
    source = add_bound_source(db)
    records = save_direct_english_construction_qualitative_reviews(
        batch(
            source,
            reviews=[
                review("review-relevance"),
                review("review-intelligibility", dimension="intelligibility"),
            ],
        ),
        db,
    )

    assert [item.review_id for item in records] == [
        "review-relevance",
        "review-intelligibility",
    ]
    assert db.query(DirectEnglishConstructionProductionReview).count() == 2


def test_subsequent_batches_preserve_same_dimension_history(db, review_lesson):
    source = add_bound_source(db)
    save_direct_english_construction_qualitative_reviews(
        batch(source, reviews=[review("review-first")]), db
    )
    save_direct_english_construction_qualitative_reviews(
        batch(source, reviews=[review("review-later", result="pending")]), db
    )

    assert [
        item.review_id
        for item in db.query(DirectEnglishConstructionProductionReview)
        .order_by(DirectEnglishConstructionProductionReview.review_id)
        .all()
    ] == ["review-first", "review-later"]


def test_duplicate_review_id_rejects_the_whole_batch(db, review_lesson):
    source = add_bound_source(db)
    save_direct_english_construction_qualitative_reviews(
        batch(source, reviews=[review("review-existing")]), db
    )

    with pytest.raises(DirectEnglishConstructionReviewInvariantError, match="review_id"):
        save_direct_english_construction_qualitative_reviews(
            batch(
                source,
                reviews=[
                    review("review-existing"),
                    review("review-new", dimension="intelligibility"),
                ],
            ),
            db,
        )
    assert db.query(DirectEnglishConstructionProductionReview).count() == 1


def test_write_boundary_rejects_duplicate_pair_and_mixed_source_identity(
    db,
    review_lesson,
):
    source = add_bound_source(db)
    invalid_pair = DirectEnglishConstructionQualitativeReviewBatch.model_construct(
        experience_attempt_id=source[0].attempt_id,
        direct_english_attempt_id=source[1].attempt_id,
        evidence_definition_id=EVIDENCE_ID,
        reviews=[
            DirectEnglishConstructionQualitativeReview.model_validate(
                review("review-pair-one")
            ),
            DirectEnglishConstructionQualitativeReview.model_validate(
                review("review-pair-two")
            ),
        ],
    )
    with pytest.raises(DirectEnglishConstructionReviewInvariantError, match="Production function"):
        save_direct_english_construction_qualitative_reviews(invalid_pair, db)

    mixed_source = DirectEnglishConstructionQualitativeReviewBatch.model_construct(
        experience_attempt_id=source[0].attempt_id,
        direct_english_attempt_id=source[1].attempt_id,
        evidence_definition_id=EVIDENCE_ID,
        reviews=[
            DirectEnglishConstructionQualitativeReview.model_validate(
                review("review-source-one")
            ),
            DirectEnglishConstructionQualitativeReview.model_validate(
                review(
                    "review-source-two",
                    dimension="intelligibility",
                    source_id="reviewer-2",
                )
            ),
        ],
    )
    with pytest.raises(DirectEnglishConstructionReviewInvariantError, match="source identity"):
        save_direct_english_construction_qualitative_reviews(mixed_source, db)

    assert db.query(DirectEnglishConstructionProductionReview).count() == 0


def test_rejects_cross_attempt_and_cross_evidence(db, review_lesson):
    first = add_bound_source(db, suffix="first")
    second = add_bound_source(db, suffix="second")
    cross_attempt = batch(
        (second[0], first[1], first[2]),
        reviews=[review("review-cross-attempt")],
    )
    with pytest.raises(DirectEnglishConstructionReviewReferenceError, match="another experience"):
        save_direct_english_construction_qualitative_reviews(cross_attempt, db)

    with pytest.raises(DirectEnglishConstructionReviewReferenceError, match="another evidence"):
        save_direct_english_construction_qualitative_reviews(
            batch(first, evidence_id="other-evidence", reviews=[review("review-cross-evidence")]),
            db,
        )


def test_rejects_unfinalized_attempt_and_unknown_function(db, review_lesson):
    source = add_bound_source(db, finalized=False)
    with pytest.raises(DirectEnglishConstructionReviewInvariantError, match="not finalized"):
        save_direct_english_construction_qualitative_reviews(
            batch(source, reviews=[review("review-unfinalized")]), db
        )

    finalized_source = add_bound_source(db, suffix="finalized")
    db.delete(finalized_source[2]["transfer"])
    db.commit()
    with pytest.raises(DirectEnglishConstructionReviewReferenceError, match="production does not exist"):
        save_direct_english_construction_qualitative_reviews(
            batch(
                finalized_source,
                reviews=[review("review-unknown-function", function="transfer")],
            ),
            db,
        )


def test_rejects_undeclared_dimension_for_function(db, review_lesson):
    source = add_bound_source(db)
    evidence = next(
        item
        for item in review_lesson.experience.evidence_definitions
        if item.id == EVIDENCE_ID
    )
    evidence.external_review_requirements = [
        item
        for item in evidence.external_review_requirements
        if not (
            item.production_function == "guided"
            and item.dimension == "intelligibility"
        )
    ]
    with pytest.raises(DirectEnglishConstructionReviewInvariantError, match="not declared"):
        save_direct_english_construction_qualitative_reviews(
            batch(
                source,
                reviews=[review("review-undeclared", dimension="intelligibility")],
            ),
            db,
        )


def test_persistence_never_changes_evidence_or_completion(db, review_lesson):
    source = add_bound_source(db)
    experience = source[0]
    save_direct_english_construction_qualitative_reviews(
        batch(source, reviews=[review("review-neutral")]), db
    )

    assert db.query(ExperienceEvidenceState).count() == 0
    assert db.get(ExperienceAttempt, experience.attempt_id).status == "in_progress"
