"""Contracts for append-only Direct-English qualitative reviews.

Contratos para revisiones cualitativas append-only de inglés directo.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ReviewDimension = Literal["relevance", "intelligibility"]
ReviewResult = Literal["positive", "negative", "pending"]
ReviewSourceType = Literal["human", "external"]
ProductionFunction = Literal["guided", "expanded", "transfer"]


def _require_aware_timestamp(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("reviewed_at must be timezone-aware")


class DirectEnglishConstructionQualitativeReview(BaseModel):
    """Describe one immutable qualitative review command entry."""

    model_config = ConfigDict(extra="forbid")

    review_id: str
    production_function: ProductionFunction
    dimension: ReviewDimension
    result: ReviewResult
    source_type: ReviewSourceType
    source_id: str
    source_version: str | None = None
    reviewed_at: datetime

    @model_validator(mode="after")
    def validate_review(self) -> "DirectEnglishConstructionQualitativeReview":
        if not self.review_id.strip() or not self.source_id.strip():
            raise ValueError("review_id and source_id cannot be blank")
        if self.source_version is not None and not self.source_version.strip():
            raise ValueError("source_version cannot be blank")
        if self.source_type == "external" and self.source_version is None:
            raise ValueError("external review requires source_version")
        _require_aware_timestamp(self.reviewed_at)
        return self


class DirectEnglishConstructionQualitativeReviewBatch(BaseModel):
    """Group one atomic append-only review command for one bound source."""

    model_config = ConfigDict(extra="forbid")

    experience_attempt_id: str
    direct_english_attempt_id: str
    evidence_definition_id: str
    reviews: list[DirectEnglishConstructionQualitativeReview] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_batch(self) -> "DirectEnglishConstructionQualitativeReviewBatch":
        context_ids = (
            self.experience_attempt_id,
            self.direct_english_attempt_id,
            self.evidence_definition_id,
        )
        if any(not value.strip() for value in context_ids):
            raise ValueError("review batch context identifiers cannot be blank")
        review_ids = [review.review_id for review in self.reviews]
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("review IDs must be unique within one batch")
        pairs = [
            (review.production_function, review.dimension)
            for review in self.reviews
        ]
        if len(pairs) != len(set(pairs)):
            raise ValueError(
                "production function and dimension must be unique within one batch"
            )
        source_identity = {
            (
                review.source_type,
                review.source_id,
                review.source_version,
            )
            for review in self.reviews
        }
        if len(source_identity) != 1:
            raise ValueError("one review batch requires one source identity")
        return self


class DirectEnglishConstructionQualitativeReviewRecord(
    DirectEnglishConstructionQualitativeReview
):
    """Expose one immutable persisted qualitative review."""

    attempt_production_id: int = Field(gt=0)
