import json
from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_validation_service import (
    validate_production_evaluation_criteria,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def test_pilot_candidate_declares_traceable_semantic_evaluation_plan():
    """Protect the pilot evaluation plan. / Protege el plan evaluativo piloto."""
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )

    assert len(candidate.evaluation_plans) == 1

    plan = candidate.evaluation_plans[0]
    assert plan.lesson_id == "a1-u1-l1"

    criteria_by_prompt = {
        criterion.prompt_id: criterion
        for criterion in plan.criteria
    }

    assert set(criteria_by_prompt) == {
        "a1-u1-l1-c3-p1",
        "a1-u1-l1-c3-p2",
        "a1-u1-l1-c3-p3",
    }

    expected_descriptions = {
        "a1-u1-l1-c3-p1": "The learner states a name.",
        "a1-u1-l1-c3-p2": "The learner states an origin.",
        "a1-u1-l1-c3-p3": "The learner responds politely.",
    }

    for prompt_id, criterion in criteria_by_prompt.items():
        assert criterion.evidence_definition_id == "a1-u1-l1-ev3"
        assert criterion.conversation_id == "a1-u1-l1-c3"
        assert criterion.dimension == "semantic"
        assert criterion.measurement_mode == "binary"
        assert criterion.success_threshold is None
        assert criterion.applicable_modalities == ["text", "voice"]
        assert criterion.description == expected_descriptions[prompt_id]

    lesson = candidate.candidate_unit.lessons[0]
    validate_production_evaluation_criteria(
        lesson,
        plan.criteria,
    )
