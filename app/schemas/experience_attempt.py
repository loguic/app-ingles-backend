from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExperienceAttemptStart(BaseModel):
    """Request the authoritative start or resume of one lesson experience.

    Solicita el inicio o la reanudación autoritativa de una experiencia.
    """

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1)
    level_id: str = Field(min_length=1)
    unit_id: str = Field(min_length=1)
    lesson_id: str = Field(min_length=1)


class ExperienceEvidenceStateRecord(BaseModel):
    """Represent one required evidence in its effective authoritative state.

    Representa el estado autoritativo efectivo de una evidencia requerida.
    """

    evidence_definition_id: str
    evidence_type: str
    status: Literal["pending", "needs_review", "satisfied"] = "pending"


class ExperienceComprehensionResponseCreate(BaseModel):
    """Submit only the learner-selected option for authoritative grading."""

    model_config = ConfigDict(extra="forbid")

    selected_index: int = Field(ge=0)


class ExperienceComprehensionResponseRecord(BaseModel):
    """Expose source facts derived and persisted by the backend."""

    response_id: str
    experience_attempt_id: str
    evidence_definition_id: str
    activity_id: str
    comprehension_exercise_id: str
    selected_index: int
    is_correct: bool
    submitted_at: datetime


class ExperienceAttemptRecord(BaseModel):
    """Expose authoritative lifecycle and effective required evidence state.

    Expone el ciclo de vida y el estado efectivo de evidencia requerida.
    """

    attempt_id: str
    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    experience_contract_version: str
    status: Literal["in_progress", "completed"]
    started_at: datetime
    completed_at: datetime | None
    evidence_states: list[ExperienceEvidenceStateRecord]
    submitted_comprehension_exercise_ids: list[str] = Field(
        default_factory=list
    )
