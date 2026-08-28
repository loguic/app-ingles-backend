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


class ExperienceEvidencePendingRecord(BaseModel):
    """Represent one required B184.1 evidence as derived pending state.

    Representa una evidencia requerida B184.1 como estado pendiente derivado.
    """

    evidence_definition_id: str
    evidence_type: str
    status: Literal["pending"] = "pending"


class ExperienceAttemptRecord(BaseModel):
    """Expose authoritative lifecycle state without evidence accreditation.

    Expone estado autoritativo de ciclo de vida sin acreditar evidencias.
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
    evidence_states: list[ExperienceEvidencePendingRecord]
