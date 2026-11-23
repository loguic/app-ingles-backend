"""Private persistence contract for the isolated A1 v4 practice demo."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


ACTIVITY_IDS = (
    "own-production",
    "lower-support-own-production",
    "nearby-transfer-food",
)


class A1V4PracticeSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(min_length=1, max_length=200)


class A1V4PracticeSessionCreated(BaseModel):
    session_id: UUID
    token: str = Field(min_length=32)
    practice_session: Literal[True] = True
    curricular_accreditation: Literal[False] = False


class A1V4PracticeProduction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_id: Literal[
        "own-production",
        "lower-support-own-production",
        "nearby-transfer-food",
    ]
    audio_reference: str = Field(min_length=1)
    transcript: str = Field(min_length=1, max_length=1000)
    client_evaluation: dict[str, Any] | None = None


class A1V4PracticeSessionSave(BaseModel):
    model_config = ConfigDict(extra="forbid")

    productions: list[A1V4PracticeProduction] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def require_exact_activity_set(self) -> "A1V4PracticeSessionSave":
        activity_ids = [item.activity_id for item in self.productions]
        if set(activity_ids) != set(ACTIVITY_IDS) or len(set(activity_ids)) != 3:
            raise ValueError("Practice session requires exactly the three A1 v4 activities")
        return self


class A1V4PracticeProductionRecord(A1V4PracticeProduction):
    backend_verified_evidence: dict[str, bool]


class A1V4PracticeSessionRecord(BaseModel):
    session_id: UUID
    declared_user_id: str
    practice_session: Literal[True] = True
    curricular_accreditation: Literal[False] = False
    practice_completed: bool
    saved: bool
    created_at: datetime
    saved_at: datetime | None
    productions: list[A1V4PracticeProductionRecord] = Field(default_factory=list)
