import json

import httpx
import pytest

from app.schemas.spoken_turn import SpokenTurnEvaluationRequest
from app.services.spoken_turn_evaluation_service import (
    OllamaSpokenTurnConfig,
    OllamaSpokenTurnEvaluator,
    OllamaSpokenTurnRuntimeError,
    evaluate_spoken_turn,
)


def _request(**updates) -> SpokenTurnEvaluationRequest:
    payload = {
        "transcript": "Water please.",
        "transcript_source": "stt",
        "target": {
            "communicative_goal": "requesting water",
            "required_meaning_terms": ["water"],
        },
        "context": "You are thirsty after exercise.",
        "current_turn": {
            "turn_id": "a1-water-1",
            "support_level": "anchors",
            "visible_support": ["water", "please"],
        },
    }
    payload.update(updates)
    return SpokenTurnEvaluationRequest.model_validate(payload)


def _model_output(status="adequate") -> dict:
    return {
        "semantic_evaluation": {
            "status": status,
            "context_relevant": status == "adequate",
            "rationale": "The learner requests water politely.",
        },
        "conversational_feedback": "Good. Your request is clear.",
        "next_turn": {
            "action": "continue",
            "support_level": "anchors",
            "reason": "The request is communicatively clear.",
        },
        "cross_turn_improvement": {
            "comparison_available": False,
            "trend": "needs_more_evidence",
            "evidence": "Collect another turn to compare.",
        },
    }


def _evaluator(handler) -> OllamaSpokenTurnEvaluator:
    client = httpx.Client(
        base_url="http://ollama.test",
        transport=httpx.MockTransport(handler),
    )
    return OllamaSpokenTurnEvaluator(
        OllamaSpokenTurnConfig(
            base_url="http://ollama.test",
            model="qwen3:4b-instruct",
            timeout_seconds=5,
        ),
        client=client,
    )


def test_calls_ollama_with_structured_schema_and_deterministic_options():
    observed = {}

    def handler(request):
        observed.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={"response": json.dumps(_model_output())},
        )

    result = evaluate_spoken_turn(_request(), evaluator=_evaluator(handler))

    assert observed["model"] == "qwen3:4b-instruct"
    assert observed["stream"] is False
    assert observed["options"] == {"temperature": 0, "seed": 42}
    assert observed["format"]["additionalProperties"] is False
    assert result.semantic_evaluation.status == "adequate"
    assert result.provenance.provider == "ollama"
    assert result.provenance.model == "qwen3:4b-instruct"
    assert result.mastery_awarded is False


def test_rejects_invalid_model_json_without_rules_fallback():
    def handler(_request):
        return httpx.Response(200, json={"response": '{"semantic_evaluation": {}}'})

    with pytest.raises(OllamaSpokenTurnRuntimeError, match="Ollama spoken-turn"):
        evaluate_spoken_turn(_request(), evaluator=_evaluator(handler))


def test_rejects_provider_failure_without_rules_fallback():
    def handler(_request):
        return httpx.Response(503, json={"error": "model unavailable"})

    with pytest.raises(OllamaSpokenTurnRuntimeError, match="503"):
        evaluate_spoken_turn(_request(), evaluator=_evaluator(handler))


def test_normalizes_cross_turn_metadata_without_re_evaluating_model_output():
    calls = []
    inconsistent = _model_output("needs_repair")
    inconsistent["cross_turn_improvement"] = {
        "comparison_available": False,
        "trend": "improved",
        "evidence": "The learner improved.",
    }

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200, json={"response": json.dumps(inconsistent)})

    result = evaluate_spoken_turn(
        _request(
            transcript="I need some help.",
            target={
                "communicative_goal": "requesting help",
                "required_meaning_terms": ["help"],
            },
            prior_turn_evidence=[
                {
                    "turn_id": "a1-help-0",
                    "semantic_status": "needs_repair",
                    "missing_meaning_terms": ["help"],
                }
            ],
        ),
        evaluator=_evaluator(handler),
    )

    assert len(calls) == 1
    assert result.semantic_evaluation.status == "needs_repair"
    assert result.cross_turn_improvement.comparison_available is True
    assert result.cross_turn_improvement.trend == "maintained"
    assert (
        result.cross_turn_improvement.evidence
        == "This turn is at the same communication level as the previous turn."
    )


def test_normalizes_cross_turn_metadata_before_consistency_validation():
    calls = []
    output = _model_output("needs_repair")
    output["cross_turn_improvement"] = {
        "comparison_available": False,
        "trend": "improved",
        "evidence": "The learner improved.",
    }

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200, json={"response": json.dumps(output)})

    result = evaluate_spoken_turn(
        _request(
            prior_turn_evidence=[
                {
                    "turn_id": "a1-water-0",
                    "semantic_status": "needs_repair",
                }
            ]
        ),
        evaluator=_evaluator(handler),
    )

    assert len(calls) == 1
    assert result.semantic_evaluation.status == "needs_repair"
    assert result.cross_turn_improvement.comparison_available is True
    assert result.cross_turn_improvement.trend == "maintained"
    assert (
        result.cross_turn_improvement.evidence
        == "This turn is at the same communication level as the previous turn."
    )


def test_needs_repair_cannot_reduce_support_without_rewriting_semantics():
    output = _model_output("needs_repair")
    output["semantic_evaluation"]["rationale"] = "The learner asks for food, not water."
    output["next_turn"] = {
        "action": "reduce_support",
        "support_level": "initial_word",
        "reason": "Try with less support.",
    }

    def handler(_request):
        return httpx.Response(200, json={"response": json.dumps(output)})

    result = evaluate_spoken_turn(
        _request(transcript="I'm hungry."),
        evaluator=_evaluator(handler),
    )

    assert result.semantic_evaluation.status == "needs_repair"
    assert result.semantic_evaluation.rationale == (
        "The learner asks for food, not water."
    )
    assert result.next_turn.action == "retry_with_support"
    assert result.next_turn.support_level == "initial_word"
    assert result.conversational_feedback == "Good. Your request is clear."


@pytest.mark.skipif(
    __import__("os").getenv("RUN_OLLAMA_SPOKEN_TURN_TEST") != "1",
    reason="set RUN_OLLAMA_SPOKEN_TURN_TEST=1 to invoke local Ollama",
)
@pytest.mark.parametrize(
    ("transcript", "expected_status"),
    [
        ("I need water.", "adequate"),
        ("Can I have some water, please?", "adequate"),
        ("Water please.", "adequate"),
        ("I'm hungry.", "needs_repair"),
    ],
)
def test_real_ollama_requesting_water_semantic_cases(transcript, expected_status):
    result = evaluate_spoken_turn(_request(transcript=transcript))

    assert result.semantic_evaluation.status == expected_status
    assert result.provenance.provider == "ollama"


@pytest.mark.skipif(
    __import__("os").getenv("RUN_OLLAMA_SPOKEN_TURN_TEST") != "1",
    reason="set RUN_OLLAMA_SPOKEN_TURN_TEST=1 to invoke local Ollama",
)
def test_real_ollama_returns_cross_turn_evidence_for_improvement():
    result = evaluate_spoken_turn(
        _request(
            transcript="I need some help.",
            target={
                "communicative_goal": "requesting help",
                "required_meaning_terms": ["help"],
            },
            prior_turn_evidence=[
                {
                    "turn_id": "a1-help-0",
                    "semantic_status": "needs_repair",
                    "missing_meaning_terms": ["help"],
                }
            ],
        )
    )

    assert result.cross_turn_improvement.comparison_available is True
    assert result.cross_turn_improvement.evidence
    assert result.semantic_evaluation.status == "adequate"
    assert result.cross_turn_improvement.trend == "improved"
