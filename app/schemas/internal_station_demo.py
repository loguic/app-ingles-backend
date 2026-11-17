from typing import Literal

from pydantic import BaseModel, Field


class InternalStationSituation(BaseModel):
    """Content-only definition for an internal Flutter station situation."""

    id: str = Field(pattern=r"^station-[a-z]+$")
    title: str = Field(min_length=1, max_length=120)
    scenario: str = Field(min_length=1, max_length=500)
    reference_audio_provisional: Literal[True]
    initial_prompt: str = Field(min_length=1, max_length=300)
    retry_orientation: str = Field(min_length=1, max_length=500)


class InternalStationDemoContent(BaseModel):
    scope: Literal["internal_demo"]
    active_curriculum: Literal[False]
    situations: list[InternalStationSituation] = Field(min_length=2, max_length=2)
