from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ConversationAttemptCreate(BaseModel):
    """Data required to save a completed conversation attempt.
    Datos necesarios para guardar un intento conversacional completado.
    """

    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    conversation_id: str
    mode: Literal["guided", "branching"]
    visited_turn_ids: list[str] = Field(min_length=1)
    selected_choice_ids: list[str] = Field(default_factory=list)


class ConversationAttemptRecord(ConversationAttemptCreate):
    """Saved conversation attempt returned by the API.
    Intento conversacional guardado que devuelve la API.
    """

    completed_at: datetime
