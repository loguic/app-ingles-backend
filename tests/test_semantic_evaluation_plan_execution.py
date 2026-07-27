import json
from pathlib import Path

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.semantic_evaluation_service import (
    evaluate_semantic_production_from_plan,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_plan():
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )
    return candidate.evaluation_plans[0]


def build_text_production(
    production_id: int,
    prompt_id: str,
    turn_id: str,
    text: str,
) -> LearnerProductionRecord:
    return LearnerProductionRecord.model_validate(
        {
            "production_id": production_id,
            "prompt_id": prompt_id,
            "turn_id": turn_id,
            "modality": "text",
            "response_text": text,
            "audio_reference": None,
        }
    )


def test_name_production_passes_from_real_plan():
    results = evaluate_semantic_production_from_plan(
        build_text_production(
            1,
            "a1-u1-l1-c3-p1",
            "a1-u1-l1-c3-t2",
            "My name is John.",
        ),
        load_plan(),
    )

    assert len(results) == 1
    assert results[0].status == "passed"


def test_origin_voice_transcript_passes_from_real_plan():
    production = LearnerProductionRecord.model_validate(
        {
            "production_id": 2,
            "prompt_id": "a1-u1-l1-c3-p2",
            "turn_id": "a1-u1-l1-c3-t4",
            "modality": "voice",
            "response_text": None,
            "audio_reference": "local://origin.wav",
        }
    )

    results = evaluate_semantic_production_from_plan(
        production,
        load_plan(),
        recognized_text="I am from Ecuador.",
    )

    assert results[0].status == "passed"


def test_polite_response_passes_from_real_plan():
    results = evaluate_semantic_production_from_plan(
        build_text_production(
            3,
            "a1-u1-l1-c3-p3",
            "a1-u1-l1-c3-t6",
            "Nice to meet you too.",
        ),
        load_plan(),
    )

    assert results[0].status == "passed"


def test_non_matching_production_fails_from_real_plan():
    results = evaluate_semantic_production_from_plan(
        build_text_production(
            4,
            "a1-u1-l1-c3-p2",
            "a1-u1-l1-c3-t4",
            "Good morning.",
        ),
        load_plan(),
    )

    assert results[0].status == "failed"


def test_unknown_prompt_cannot_be_evaluated():
    with pytest.raises(
        ValueError,
        match="No applicable semantic criterion",
    ):
        evaluate_semantic_production_from_plan(
            build_text_production(
                5,
                "a1-u1-l1-c3-p99",
                "a1-u1-l1-c3-t99",
                "Hello.",
            ),
            load_plan(),
        )
