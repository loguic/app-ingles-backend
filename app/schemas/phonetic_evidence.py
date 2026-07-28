from datetime import datetime

from pydantic import BaseModel, Field


class PhoneticEvaluationEvidence(BaseModel):
    """Represent normalized acoustic evidence without deciding success.

    Representa evidencia acústica normalizada sin decidir el éxito.
    """

    production_id: int = Field(gt=0)
    criterion_id: str = Field(min_length=1)
    audio_reference: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    analyzed_at: datetime

class AcousticPhoneticMeasurement(BaseModel):
    """Represent one technical acoustic score before domain traceability.

    Representa una medición acústica técnica antes de añadir trazabilidad.
    """

    score: float = Field(ge=0.0, le=1.0)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    analyzed_at: datetime
