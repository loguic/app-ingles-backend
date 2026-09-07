from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.direct_english_construction_review import (
    DirectEnglishConstructionQualitativeReview,
    DirectEnglishConstructionQualitativeReviewBatch,
)


NOW = datetime(2026, 9, 7, 12, 0, tzinfo=UTC)


def review_payload(**updates):
    payload = {
        "review_id": "review-1",
        "production_function": "guided",
        "dimension": "relevance",
        "result": "positive",
        "source_type": "human",
        "source_id": "reviewer-1",
        "source_version": None,
        "reviewed_at": NOW,
    }
    payload.update(updates)
    return payload


def batch_payload(**updates):
    payload = {
        "experience_attempt_id": "experience-1",
        "direct_english_attempt_id": "direct-1",
        "evidence_definition_id": "evidence-1",
        "reviews": [review_payload()],
    }
    payload.update(updates)
    return payload


def test_accepts_valid_human_review():
    review = DirectEnglishConstructionQualitativeReview.model_validate(
        review_payload()
    )

    assert review.source_version is None


def test_accepts_valid_external_review_with_version():
    review = DirectEnglishConstructionQualitativeReview.model_validate(
        review_payload(source_type="external", source_version="v1")
    )

    assert review.source_version == "v1"


def test_external_review_requires_version():
    with pytest.raises(ValidationError, match="requires source_version"):
        DirectEnglishConstructionQualitativeReview.model_validate(
            review_payload(source_type="external")
        )


@pytest.mark.parametrize("field", ["review_id", "source_id"])
def test_rejects_blank_identifiers(field):
    with pytest.raises(ValidationError, match="cannot be blank"):
        DirectEnglishConstructionQualitativeReview.model_validate(
            review_payload(**{field: "  "})
        )


def test_rejects_naive_timestamp():
    with pytest.raises(ValidationError, match="timezone-aware"):
        DirectEnglishConstructionQualitativeReview.model_validate(
            review_payload(reviewed_at=datetime(2026, 9, 7, 12, 0))
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dimension", "semantic"),
        ("result", "passed"),
        ("production_function", "free"),
    ],
)
def test_rejects_unknown_contract_literals(field, value):
    with pytest.raises(ValidationError):
        DirectEnglishConstructionQualitativeReview.model_validate(
            review_payload(**{field: value})
        )


def test_batch_rejects_duplicate_function_dimension_pair():
    with pytest.raises(ValidationError, match="production function and dimension"):
        DirectEnglishConstructionQualitativeReviewBatch.model_validate(
            batch_payload(
                reviews=[
                    review_payload(review_id="review-1"),
                    review_payload(review_id="review-2", result="pending"),
                ]
            )
        )


def test_batch_rejects_mixed_source_identity():
    with pytest.raises(ValidationError, match="one source identity"):
        DirectEnglishConstructionQualitativeReviewBatch.model_validate(
            batch_payload(
                reviews=[
                    review_payload(review_id="review-1"),
                    review_payload(
                        review_id="review-2",
                        dimension="intelligibility",
                        source_id="reviewer-2",
                    ),
                ]
            )
        )
