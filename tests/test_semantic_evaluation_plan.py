import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.evaluation import LessonProductionEvaluationPlan
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def test_pilot_plan_declares_one_rule_per_semantic_criterion():
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )
    plan = candidate.evaluation_plans[0]

    assert len(plan.criteria) == 3
    assert len(plan.semantic_rules) == 3
    assert {rule.criterion_id for rule in plan.semantic_rules} == {
        criterion.id for criterion in plan.criteria
    }


def test_plan_rejects_duplicate_semantic_rule_for_criterion():
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )
    payload = candidate.evaluation_plans[0].model_dump()
    payload["semantic_rules"].append(payload["semantic_rules"][0])

    with pytest.raises(
        ValidationError,
        match="rule IDs must be unique",
    ):
        LessonProductionEvaluationPlan.model_validate(payload)


def test_plan_rejects_rule_for_unknown_semantic_criterion():
    candidate = PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )
    payload = candidate.evaluation_plans[0].model_dump()
    payload["semantic_rules"][0]["criterion_id"] = "unknown-criterion"

    with pytest.raises(
        ValidationError,
        match="unknown semantic criteria",
    ):
        LessonProductionEvaluationPlan.model_validate(payload)
