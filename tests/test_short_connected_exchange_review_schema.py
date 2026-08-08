from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReview,
    ShortConnectedExchangeProductionReviewBatch,
)


NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


def review_payload(**updates):
    payload = {
        "review_id": "review-1",
        "production_id": 1,
        "dimension": "intention_understanding",
        "result": "positive",
        "source_type": "human",
        "source_id": "reviewer-1",
        "source_version": None,
        "reviewed_at": NOW,
    }
    payload.update(updates)
    return payload


@pytest.mark.parametrize(
    ("dimension", "result"),
    [
        ("intention_understanding", "positive"),
        ("contingent_response", "negative"),
        ("intention_understanding", "pending"),
    ],
)
def test_review_accepts_dimensions_and_normal_results(dimension, result):
    review = ShortConnectedExchangeProductionReview.model_validate(
        review_payload(dimension=dimension, result=result)
    )
    assert review.dimension == dimension
    assert review.result == result


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dimension", "semantic"),
        ("result", "passed"),
        ("source_type", "automatic"),
    ],
)
def test_review_rejects_unknown_literals(field, value):
    with pytest.raises(ValidationError):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(**{field: value})
        )


@pytest.mark.parametrize("field", ["review_id", "source_id"])
def test_review_rejects_blank_identifiers(field):
    with pytest.raises(ValidationError, match="cannot be blank"):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(**{field: "  "})
        )


def test_review_requires_timezone_aware_timestamp():
    with pytest.raises(ValidationError, match="timezone-aware"):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(reviewed_at=datetime(2026, 8, 8, 12, 0))
        )


def test_external_review_requires_non_blank_version():
    with pytest.raises(ValidationError, match="requires source_version"):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(source_type="external")
        )
    with pytest.raises(ValidationError, match="cannot be blank"):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(source_type="external", source_version=" ")
        )


def test_human_review_allows_absent_but_not_blank_version():
    review = ShortConnectedExchangeProductionReview.model_validate(
        review_payload(source_version=None)
    )
    assert review.source_version is None
    with pytest.raises(ValidationError, match="cannot be blank"):
        ShortConnectedExchangeProductionReview.model_validate(
            review_payload(source_version=" ")
        )


def test_review_batch_must_be_non_empty():
    with pytest.raises(ValidationError):
        ShortConnectedExchangeProductionReviewBatch(reviews=[])


def test_review_batch_rejects_duplicate_production_dimension_pair():
    with pytest.raises(ValidationError, match="production and dimension"):
        ShortConnectedExchangeProductionReviewBatch.model_validate(
            {
                "reviews": [
                    review_payload(review_id="review-1"),
                    review_payload(review_id="review-2", result="pending"),
                ]
            }
        )


def test_review_batch_rejects_duplicate_review_ids():
    with pytest.raises(ValidationError, match="review IDs"):
        ShortConnectedExchangeProductionReviewBatch.model_validate(
            {
                "reviews": [
                    review_payload(),
                    review_payload(
                        dimension="contingent_response",
                        result="pending",
                    ),
                ]
            }
        )
