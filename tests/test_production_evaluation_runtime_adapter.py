import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.production_evaluation_runtime import (
    ProductionEvaluationRuntimeConfig,
)
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.production_evaluation_runtime_adapter import (
    build_runtime_evaluation_config_from_candidate,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_candidate():
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def test_candidate_adapts_to_neutral_runtime_config():
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )

    assert config.lesson_id == "a1-u1-l1"
    assert config.evaluation_plan.lesson_id == "a1-u1-l1"
    assert config.feedback_plan.lesson_id == "a1-u1-l1"
    assert len(config.evaluation_plan.criteria) == 3
    assert len(config.feedback_plan.rules) == 3


def test_adapter_rejects_lesson_without_evaluation_plan():
    with pytest.raises(
        ValueError,
        match="No evaluation plan for lesson",
    ):
        build_runtime_evaluation_config_from_candidate(
            load_candidate(),
            "a1-u1-l99",
        )


def test_runtime_config_rejects_mismatched_feedback_lesson():
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )
    feedback_plan = config.feedback_plan.model_copy(
        update={"lesson_id": "a1-u1-l99"}
    )

    with pytest.raises(
        ValidationError,
        match="feedback plan must match lesson_id",
    ):
        ProductionEvaluationRuntimeConfig(
            lesson_id=config.lesson_id,
            evaluation_plan=config.evaluation_plan,
            feedback_plan=feedback_plan,
        )


def test_runtime_config_rejects_unknown_feedback_criterion():
    config = build_runtime_evaluation_config_from_candidate(
        load_candidate(),
        "a1-u1-l1",
    )
    first_rule = config.feedback_plan.rules[0].model_copy(
        update={"criterion_id": "unknown-criterion"}
    )
    feedback_plan = config.feedback_plan.model_copy(
        update={
            "rules": [
                first_rule,
                *config.feedback_plan.rules[1:],
            ]
        }
    )

    with pytest.raises(
        ValidationError,
        match="unknown criteria",
    ):
        ProductionEvaluationRuntimeConfig(
            lesson_id=config.lesson_id,
            evaluation_plan=config.evaluation_plan,
            feedback_plan=feedback_plan,
        )
