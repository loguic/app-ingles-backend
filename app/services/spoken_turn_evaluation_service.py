"""Ollama-backed, non-authoritative coaching for one A1 spoken turn."""

import json
import os
from dataclasses import dataclass
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.spoken_turn import (
    AdaptiveNextTurnDecision,
    CrossTurnImprovementEvidence,
    SpokenSemanticEvaluation,
    SpokenTurnEvaluationProvenance,
    SpokenTurnEvaluationRequest,
    SpokenTurnEvaluationResponse,
)


class OllamaSpokenTurnRuntimeError(RuntimeError):
    """The required local model runtime did not produce a usable response."""


@dataclass(frozen=True)
class OllamaSpokenTurnConfig:
    base_url: str
    model: str
    timeout_seconds: float

    @classmethod
    def from_environment(cls) -> "OllamaSpokenTurnConfig":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
        model = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct").strip()
        try:
            timeout_seconds = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
        except ValueError as error:
            raise OllamaSpokenTurnRuntimeError(
                "OLLAMA_TIMEOUT_SECONDS must be a positive number"
            ) from error
        if not base_url or not model or timeout_seconds <= 0:
            raise OllamaSpokenTurnRuntimeError(
                "Ollama base URL, model, and timeout must be configured"
            )
        return cls(
            base_url=base_url.rstrip("/"),
            model=model,
            timeout_seconds=timeout_seconds,
        )


class _ModelSemanticEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["adequate", "needs_repair"]
    context_relevant: bool
    rationale: str = Field(min_length=1, max_length=500)


class _ModelNextTurnDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: Literal["continue", "retry_with_support", "reduce_support"]
    support_level: Literal["model", "anchors", "initial_word", "none"]
    reason: str = Field(min_length=1, max_length=500)


class _ModelCrossTurnImprovement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparison_available: bool
    trend: Literal["improved", "maintained", "needs_more_evidence"]
    evidence: str = Field(min_length=1, max_length=500)


class _ModelSpokenTurnOutput(BaseModel):
    """The only model output accepted by the endpoint."""

    model_config = ConfigDict(extra="forbid")

    semantic_evaluation: _ModelSemanticEvaluation
    conversational_feedback: str = Field(min_length=1, max_length=500)
    next_turn: _ModelNextTurnDecision
    cross_turn_improvement: _ModelCrossTurnImprovement


def _prompt(
    request: SpokenTurnEvaluationRequest,
    *,
    correction: str | None = None,
) -> str:
    evidence = request.model_dump(
        mode="json",
        exclude={"experience_attempt_id", "audio_reference"},
    )
    return (
        "You are an A1 English speaking coach. Evaluate communicative meaning, "
        "not exact phrase overlap. Use the learner transcript, stated target intent, "
        "context, visible support, and prior-turn evidence. Decide whether the learner "
        "communicatively achieved the target. Produce concise learner feedback and one "
        "adaptive next-turn decision. Reduce support only when the evidence supports it. "
        "Never award mastery, completion, grades, or progress. Return only JSON matching "
        "the supplied schema.\n\nTURN EVIDENCE:\n"
        + json.dumps(evidence, ensure_ascii=False)
        + (
            "\n\nCORRECTION REQUIRED:\n" + correction
            if correction is not None
            else ""
        )
    )


def _normalize_cross_turn_improvement(
    request: SpokenTurnEvaluationRequest,
    output: _ModelSpokenTurnOutput,
) -> _ModelSpokenTurnOutput:
    """Derive comparison metadata from model-decided semantic statuses."""
    prior = request.prior_turn_evidence[-1] if request.prior_turn_evidence else None
    current_status = output.semantic_evaluation.status

    if prior is None:
        comparison_available = False
        trend = "needs_more_evidence"
        evidence = "This is the first turn, so there is nothing to compare yet."
    elif prior.semantic_status == "needs_repair" and current_status == "adequate":
        comparison_available = True
        trend = "improved"
        evidence = "This turn communicates the target more successfully than the previous turn."
    elif prior.semantic_status == current_status:
        comparison_available = True
        trend = "maintained"
        evidence = "This turn is at the same communication level as the previous turn."
    else:
        comparison_available = True
        trend = "needs_more_evidence"
        evidence = "This turn does not show a clear improvement over the previous turn."

    comparison = output.cross_turn_improvement.model_copy(
        update={
            "comparison_available": comparison_available,
            "trend": trend,
            "evidence": evidence,
        }
    )
    return output.model_copy(update={"cross_turn_improvement": comparison})


def _cross_field_error(
    request: SpokenTurnEvaluationRequest,
    output: _ModelSpokenTurnOutput,
) -> str | None:
    """Reject contradictory model claims without deciding meaning locally."""
    prior = request.prior_turn_evidence[-1] if request.prior_turn_evidence else None
    comparison = output.cross_turn_improvement
    current_status = output.semantic_evaluation.status

    if prior is None:
        if comparison.comparison_available:
            return "comparison_available requires prior_turn_evidence"
        if comparison.trend != "needs_more_evidence":
            return "a first turn cannot claim an improvement trend"
    else:
        if not comparison.comparison_available:
            return "prior_turn_evidence requires comparison_available=true"
        if (
            comparison.trend == "improved"
            and (
                prior.semantic_status != "needs_repair"
                or current_status != "adequate"
            )
        ):
            return "improved requires prior needs_repair and current adequate"
        if (
            comparison.trend == "maintained"
            and current_status != prior.semantic_status
        ):
            return "maintained requires the same prior and current semantic status"

    return None


def _apply_pedagogical_transition_guard(
    output: _ModelSpokenTurnOutput,
) -> _ModelSpokenTurnOutput:
    """Prevent unsafe support reduction without altering model semantics."""
    if (
        output.semantic_evaluation.status != "adequate"
        and output.next_turn.action == "reduce_support"
    ):
        return output.model_copy(
            update={
                "next_turn": _ModelNextTurnDecision(
                    action="retry_with_support",
                    support_level=output.next_turn.support_level,
                    reason=(
                        "Current semantic evaluation needs repair; retry with "
                        "the available support."
                    ),
                )
            }
        )
    return output


class OllamaSpokenTurnEvaluator:
    """Call Ollama's local HTTP API with deterministic generation settings."""

    def __init__(
        self,
        config: OllamaSpokenTurnConfig | None = None,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self._config = config or OllamaSpokenTurnConfig.from_environment()
        self._client = client

    @property
    def config(self) -> OllamaSpokenTurnConfig:
        return self._config

    def evaluate(
        self,
        request: SpokenTurnEvaluationRequest,
        *,
        correction: str | None = None,
    ) -> _ModelSpokenTurnOutput:
        payload = {
            "model": self._config.model,
            "prompt": _prompt(request, correction=correction),
            "format": _ModelSpokenTurnOutput.model_json_schema(),
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "seed": 42},
        }
        try:
            if self._client is not None:
                response = self._client.post("/api/generate", json=payload)
            else:
                with httpx.Client(
                    base_url=self._config.base_url,
                    timeout=self._config.timeout_seconds,
                ) as client:
                    response = client.post("/api/generate", json=payload)
            response.raise_for_status()
            body = response.json()
            generated = body["response"]
            if not isinstance(generated, str):
                raise TypeError("Ollama response field must be a JSON string")
            return _ModelSpokenTurnOutput.model_validate_json(generated)
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise OllamaSpokenTurnRuntimeError(
                "Ollama spoken-turn evaluation failed: " + str(error)
            ) from error


def evaluate_spoken_turn(
    request: SpokenTurnEvaluationRequest,
    *,
    evaluator: OllamaSpokenTurnEvaluator | None = None,
) -> SpokenTurnEvaluationResponse:
    """Use the configured local model; never substitute deterministic semantics."""
    runtime = evaluator or OllamaSpokenTurnEvaluator()
    output = runtime.evaluate(request)
    output = _normalize_cross_turn_improvement(request, output)
    error = _cross_field_error(request, output)
    if error is not None:
        output = runtime.evaluate(
            request,
            correction=(
                "Your prior JSON was logically inconsistent: "
                + error
                + ". Re-evaluate the transcript and return a coherent JSON result. "
                "Do not copy the prior semantic decision blindly."
            ),
        )
        error = _cross_field_error(request, output)
        if error is not None:
            raise OllamaSpokenTurnRuntimeError(
                "Ollama spoken-turn evaluation remained logically inconsistent: "
                + error
            )
    output = _apply_pedagogical_transition_guard(output)
    return SpokenTurnEvaluationResponse(
        semantic_evaluation=SpokenSemanticEvaluation(
            **output.semantic_evaluation.model_dump()
        ),
        conversational_feedback=output.conversational_feedback,
        next_turn=AdaptiveNextTurnDecision(**output.next_turn.model_dump()),
        cross_turn_improvement=CrossTurnImprovementEvidence(
            **output.cross_turn_improvement.model_dump()
        ),
        provenance=SpokenTurnEvaluationProvenance(
            provider="ollama",
            model=runtime.config.model,
        ),
    )
