from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ReviewDimension = Literal[
    "intention_understanding",
    "contingent_response",
]
ReviewResult = Literal["positive", "negative", "pending"]
ReviewSourceType = Literal["human", "external"]


def _require_aware_timestamp(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("reviewed_at must be timezone-aware")


class ShortConnectedExchangeProductionReview(BaseModel):
    """Describe one independent review without pedagogical aggregation."""

    review_id: str
    production_id: int = Field(gt=0)
    dimension: ReviewDimension
    result: ReviewResult
    source_type: ReviewSourceType
    source_id: str
    source_version: str | None = None
    reviewed_at: datetime

    @model_validator(mode="after")
    def validate_review(self) -> "ShortConnectedExchangeProductionReview":
        if not self.review_id.strip() or not self.source_id.strip():
            raise ValueError("review_id and source_id cannot be blank")
        if self.source_version is not None and not self.source_version.strip():
            raise ValueError("source_version cannot be blank")
        if self.source_type == "external" and self.source_version is None:
            raise ValueError("external review requires source_version")
        _require_aware_timestamp(self.reviewed_at)
        return self


class ShortConnectedExchangeProductionReviewBatch(BaseModel):
    """Group one atomic append-only review command."""

    reviews: list[ShortConnectedExchangeProductionReview] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_unique_batch_pairs(
        self,
    ) -> "ShortConnectedExchangeProductionReviewBatch":
        review_ids = [review.review_id for review in self.reviews]
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("review IDs must be unique within one batch")
        pairs = [
            (review.production_id, review.dimension)
            for review in self.reviews
        ]
        if len(pairs) != len(set(pairs)):
            raise ValueError(
                "production and dimension must be unique within one batch"
            )
        return self


class ShortConnectedExchangeProductionReviewRecord(
    ShortConnectedExchangeProductionReview
):
    """Expose one immutable persisted review."""


class ShortConnectedExchangeProductionReviewHistory(BaseModel):
    """Expose review history for one real learner production."""

    production_id: int = Field(gt=0)
    prompt_id: str
    turn_id: str
    reviews: list[ShortConnectedExchangeProductionReviewRecord] = Field(
        default_factory=list
    )


class ShortConnectedExchangeSubmissionReviewHistory(BaseModel):
    """Expose all production-review histories from one B181 submission."""

    submission_id: int = Field(gt=0)
    productions: list[ShortConnectedExchangeProductionReviewHistory]
