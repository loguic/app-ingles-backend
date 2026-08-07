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
OrientationPriority = Literal[
    "relevance",
    "direct_english_construction",
    "intelligibility",
    "secondary_accuracy",
]
OrientationSourceType = Literal["human", "external"]


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


class DirectEnglishConstructionOrientationCreate(BaseModel):
    """Register one already selected orientation for one production.

    Registra una orientación ya seleccionada para una producción.
    """

    orientation_id: str
    attempt_id: str
    production_function: ProductionFunction
    priority: OrientationPriority
    guidance_text: str = Field(max_length=2000)
    source_type: OrientationSourceType
    source_id: str
    source_version: Optional[str] = None
    created_at: datetime

    @model_validator(mode="after")
    def validate_orientation(
        self,
    ) -> "DirectEnglishConstructionOrientationCreate":
        required = (
            self.orientation_id,
            self.attempt_id,
            self.guidance_text,
            self.source_id,
        )
        if any(not value.strip() for value in required):
            raise ValueError("Orientation values cannot be blank")
        if self.source_version is not None and not self.source_version.strip():
            raise ValueError("source_version cannot be blank")
        if self.source_type == "external" and self.source_version is None:
            raise ValueError("External orientation requires source_version")
        _require_aware_timestamp(self.created_at, "created_at")
        return self


class DirectEnglishConstructionOrientationRecord(BaseModel):
    """Expose one immutable registered orientation.

    Expone una orientación registrada e inmutable.
    """

    orientation_id: str
    priority: OrientationPriority
    guidance_text: str
    source_type: OrientationSourceType
    source_id: str
    source_version: Optional[str] = None
    created_at: datetime


class DirectEnglishConstructionRetryPreparationRequest(BaseModel):
    """Request preparation for one focused function of a new attempt.

    Solicita preparar una función focal de un nuevo intento.
    """

    previous_attempt_id: str
    production_function: ProductionFunction

    @model_validator(mode="after")
    def validate_request(
        self,
    ) -> "DirectEnglishConstructionRetryPreparationRequest":
        if not self.previous_attempt_id.strip():
            raise ValueError("previous_attempt_id cannot be blank")
        return self


class DirectEnglishConstructionRetryPreparation(BaseModel):
    """Describe a read-only guided retry without claiming improvement.

    Describe un reintento guiado de solo lectura sin afirmar mejora.
    """

    previous_attempt_id: str
    production_function: ProductionFunction
    orientation: DirectEnglishConstructionOrientationRecord
    conversation_id: str
    prompt_id: str
    previous_configured_support_level: SupportLevel
    previous_support_used: SupportLevel
    next_support_level: SupportLevel
    transfer_bank_id: Optional[str] = None
    previous_transfer_variant_id: Optional[str] = None
    previous_transfer_prompt_snapshot: Optional[str] = None
    transfer_selection_policy: Optional[
        Literal["new_attempt_selector"]
    ] = None
    requires_new_attempt_id: bool = True

    @model_validator(mode="after")
    def validate_transfer_metadata(
        self,
    ) -> "DirectEnglishConstructionRetryPreparation":
        transfer_values = (
            self.transfer_bank_id,
            self.previous_transfer_variant_id,
            self.previous_transfer_prompt_snapshot,
            self.transfer_selection_policy,
        )
        if self.production_function == "transfer":
            if any(value is None or not value.strip() for value in transfer_values):
                raise ValueError("Transfer retry requires complete metadata")
            if self.next_support_level != "none":
                raise ValueError("Transfer retry requires no support")
        elif any(value is not None for value in transfer_values):
            raise ValueError("Only transfer retry can include transfer metadata")
        if self.requires_new_attempt_id is not True:
            raise ValueError("Retry preparation requires a new attempt_id")
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
    orientation: Optional[DirectEnglishConstructionOrientationRecord] = None


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
