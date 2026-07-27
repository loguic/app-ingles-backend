from pydantic import BaseModel, Field


class ProductionAudioUploadRecord(BaseModel):
    """Represent one backend-managed learner audio asset.

    Representa un audio del estudiante administrado por backend.
    """

    audio_reference: str = Field(min_length=1)
    media_type: str = "audio/wav"
    size_bytes: int = Field(gt=0)
