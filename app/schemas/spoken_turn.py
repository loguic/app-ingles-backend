"""Narrow runtime contract for an A1 spoken conversational turn.

This is deliberately an evaluation aid, not an assessment or mastery contract.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SpokenTurnTarget(BaseModel):
    """The communicative meaning expected for this one turn."""

    model_config = ConfigDict(extra="forbid")

    communicative_goal: str = Field(min_length=1)
    required_meaning_terms: list[str] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def validate_terms(self) -> "SpokenTurnTarget":
        normalized = [term.strip().casefold() for term in self.required_meaning_terms]
        if any(not term for term in normalized):
            raise ValueError("Target meaning terms cannot be blank")
        if len(normalized) != len(set(normalized)):
            raise ValueError("Target meaning terms must be unique")
        return self


class CurrentTurnSupportState(BaseModel):
    """Support actually available on the current turn, as observed by UI."""

    model_config = ConfigDict(extra="forbid")

    turn_id: str = Field(min_length=1)
    support_level: Literal["model", "anchors", "initial_word", "none"]
    visible_support: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_visible_support(self) -> "CurrentTurnSupportState":
        if any(not item.strip() for item in self.visible_support):
            raise ValueError("Visible support cannot be blank")
        if self.support_level == "none" and self.visible_support:
            raise ValueError("No-support turn cannot report visible support")
        return self


class PriorSpokenTurnEvidence(BaseModel):
    """A client-held earlier evaluation used only for this local comparison."""

    model_config = ConfigDict(extra="forbid")

    turn_id: str = Field(min_length=1)
    semantic_status: Literal["adequate", "needs_repair"]
    matched_meaning_terms: list[str] = Field(default_factory=list)
    missing_meaning_terms: list[str] = Field(default_factory=list)


class SpokenTurnEvaluationRequest(BaseModel):
    """Evidence and context for one real spoken turn.

    ``transcript`` is either learner-entered transcription or the STT result;
    audio stays an opaque reference managed by the existing audio endpoint.
    """

    model_config = ConfigDict(extra="forbid")

    experience_attempt_id: str | None = Field(default=None, min_length=1)
    transcript: str = Field(min_length=1, max_length=1000)
    transcript_source: Literal["learner", "stt"]
    audio_reference: str | None = None
    target: SpokenTurnTarget
    context: str = Field(min_length=1, max_length=1000)
    current_turn: CurrentTurnSupportState
    prior_turn_evidence: list[PriorSpokenTurnEvidence] = Field(
        default_factory=list,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_evidence(self) -> "SpokenTurnEvaluationRequest":
        if not self.transcript.strip():
            raise ValueError("Transcript cannot be blank")
        if not self.context.strip():
            raise ValueError("Context cannot be blank")
        if self.audio_reference is not None and not self.audio_reference.strip():
            raise ValueError("Audio reference cannot be blank")
        return self


class SpokenSemanticEvaluation(BaseModel):
    status: Literal["adequate", "needs_repair"]
    context_relevant: bool
    rationale: str = Field(min_length=1, max_length=500)


class AdaptiveNextTurnDecision(BaseModel):
    action: Literal["continue", "retry_with_support", "reduce_support"]
    support_level: Literal["model", "anchors", "initial_word", "none"]
    reason: str


class CrossTurnImprovementEvidence(BaseModel):
    comparison_available: bool
    trend: Literal["improved", "maintained", "needs_more_evidence"]
    evidence: str


class SpokenTurnEvaluationProvenance(BaseModel):
    """Identify the local model that generated this non-authoritative advice."""

    provider: Literal["ollama"]
    model: str = Field(min_length=1)


class SpokenTurnEvaluationResponse(BaseModel):
    """Non-authoritative coaching result for the current spoken turn."""

    semantic_evaluation: SpokenSemanticEvaluation
    conversational_feedback: str
    next_turn: AdaptiveNextTurnDecision
    cross_turn_improvement: CrossTurnImprovementEvidence
    provenance: SpokenTurnEvaluationProvenance
    mastery_awarded: Literal[False] = False
