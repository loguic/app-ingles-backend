import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_payload():
    return json.loads(CANDIDATE_PATH.read_text())


def test_real_candidate_feedback_integrity_is_valid():
    candidate = PedagogicalUnitCandidate.model_validate(
        load_payload()
    )

    assert len(candidate.feedback_plans) == 1
    assert len(candidate.feedback_plans[0].rules) == 3


def test_feedback_plan_requires_matching_evaluation_plan():
    payload = load_payload()
    payload["evaluation_plans"] = []

    with pytest.raises(
        ValidationError,
        match="requires evaluation plan for lesson",
    ):
        PedagogicalUnitCandidate.model_validate(payload)


def test_feedback_rule_rejects_unknown_evaluation_criterion():
    payload = load_payload()
    payload["feedback_plans"][0]["rules"][0][
        "criterion_id"
    ] = "unknown-criterion"

    with pytest.raises(
        ValidationError,
        match="unknown evaluation criteria",
    ):
        PedagogicalUnitCandidate.model_validate(payload)
