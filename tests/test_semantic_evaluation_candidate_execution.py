import json
from pathlib import Path

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.semantic_evaluation_service import (
    evaluate_candidate_semantic_production,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def test_candidate_evaluates_real_name_production():
    production = LearnerProductionRecord.model_validate(
        {
            "production_id": 1,
            "prompt_id": "a1-u1-l1-c3-p1",
            "turn_id": "a1-u1-l1-c3-t2",
            "modality": "text",
            "response_text": "My name is John.",
            "audio_reference": None,
        }
    )

    results = evaluate_candidate_semantic_production(
        load_candidate(),
        "a1-u1-l1",
        production,
    )

    assert len(results) == 1
    assert results[0].status == "passed"


def test_candidate_rejects_lesson_without_evaluation_plan():
    production = LearnerProductionRecord.model_validate(
        {
            "production_id": 2,
            "prompt_id": "a1-u1-l1-c3-p1",
            "turn_id": "a1-u1-l1-c3-t2",
            "modality": "text",
            "response_text": "My name is John.",
            "audio_reference": None,
        }
    )

    with pytest.raises(
        ValueError,
        match="No evaluation plan for lesson",
    ):
        evaluate_candidate_semantic_production(
            load_candidate(),
            "a1-u1-l9",
            production,
        )
