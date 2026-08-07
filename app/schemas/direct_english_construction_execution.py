"""Contracts for internal direct-English execution.

Contratos para la ejecución interna de construcción directa en inglés.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.conversation_production import (
    ConversationProductionSubmission,
)


ProductionFunction = Literal["guided", "expanded", "transfer"]
SupportLevel = Literal["model", "anchors", "initial_word", "none"]


def _require_aware_timestamp(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(field_name + " must include timezone information")


class DirectEnglishConstructionAttemptStart(BaseModel):
    """Start one stable direct-English attempt.

    Inicia un intento estable de construcción directa.
    """

    attempt_id: str
    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    started_at: datetime

    @model_validator(mode="after")
    def validate_start(self) -> "DirectEnglishConstructionAttemptStart":
        values = (
            self.attempt_id,
            self.user_id,
            self.level_id,
            self.unit_id,
            self.lesson_id,
        )
        if any(not value.strip() for value in values):
            raise ValueError("Direct-English attempt identifiers cannot be blank")
        _require_aware_timestamp(self.started_at, "started_at")
        return self


class DirectEnglishConstructionProductionCapture(BaseModel):
    """Capture one production and the support that actually occurred.

    Captura una producción y el apoyo que realmente se utilizó.
    """

    production_function: ProductionFunction
    submission: ConversationProductionSubmission
    support_used: SupportLevel
    transfer_variant_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_transfer_reference(
        self,
    ) -> "DirectEnglishConstructionProductionCapture":
        if self.production_function == "transfer":
            if (
                self.transfer_variant_id is None
                or not self.transfer_variant_id.strip()
            ):
                raise ValueError(
                    "Transfer capture requires transfer_variant_id"
                )
        elif self.transfer_variant_id is not None:
            raise ValueError(
                "Only transfer capture can define transfer_variant_id"
            )
        return self


class DirectEnglishConstructionAttemptFinalize(BaseModel):
    """Finalize one attempt with exactly three production functions.

    Finaliza un intento con exactamente tres funciones de producción.
    """

    attempt_id: str
    captures: list[DirectEnglishConstructionProductionCapture] = Field(
        min_length=3,
        max_length=3,
    )
    finalized_at: datetime

    @model_validator(mode="after")
    def validate_finalize(self) -> "DirectEnglishConstructionAttemptFinalize":
        if not self.attempt_id.strip():
            raise ValueError("attempt_id cannot be blank")
        _require_aware_timestamp(self.finalized_at, "finalized_at")
        functions = [item.production_function for item in self.captures]
        if len(functions) != len(set(functions)):
            raise ValueError("Production functions must be unique")
        if set(functions) != {"guided", "expanded", "transfer"}:
            raise ValueError(
                "Finalize requires guided, expanded and transfer captures"
            )
        return self


class DirectEnglishConstructionAttemptProductionRecord(BaseModel):
    """Expose one persisted production without interpreting its meaning.

    Expone una producción persistida sin interpretar su significado.
    """

    production_function: ProductionFunction
    evidence_id: str
    production_id: int
    prompt_id: str
    modality_used: Literal["text", "voice"]
    configured_support_level: SupportLevel
    support_used: SupportLevel


class DirectEnglishConstructionAttemptRecord(BaseModel):
    """Reconstruct one complete or started direct-English attempt.

    Reconstruye un intento iniciado o finalizado de inglés directo.
    """

    attempt_id: str
    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    status: Literal["started", "finalized"]
    transfer_bank_id: str
    transfer_variant_id: str
    transfer_prompt_snapshot: str
    selector_version: str
    started_at: datetime
    finalized_at: Optional[datetime] = None
    productions: list[DirectEnglishConstructionAttemptProductionRecord]
    completion_requirements_met: bool
