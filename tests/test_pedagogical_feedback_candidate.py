import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_feedback_service import (
    generate_candidate_pedagogical_feedback,
)


CANDIDATE_PATH = Path(
    "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
)


def load_candidate():
    return PedagogicalUnitCandidate.model_validate(
        json.loads(CANDIDATE_PATH.read_text())
    )


def build_result(criterion_id, status="passed"):
    return ProductionEvaluationResultRecord(
        evaluation_result_id=20,
        production_id=8,
        criterion_id=criterion_id,
        status=status,
        score=None,
        evaluator_id="deterministic-semantic",
        evaluator_version="1.0",
        evaluated_at=datetime.now(UTC),
    )


def test_candidate_declares_three_feedback_rules():
    candidate = load_candidate()
    plan = candidate.feedback_plans[0]

    assert plan.lesson_id == "a1-u1-l1"
    assert len(plan.rules) == 3
    assert {rule.criterion_id for rule in plan.rules} == {
        criterion.id
        for criterion in candidate.evaluation_plans[0].criteria
    }


def test_name_feedback_resolves_from_candidate():
    feedback = generate_candidate_pedagogical_feedback(
        load_candidate(),
        "a1-u1-l1",
        build_result("a1-u1-l1-c3-p1-semantic"),
    )

    assert feedback.evaluation_result_id == 20
    assert feedback.production_id == 8
    assert feedback.evaluation_status == "passed"
    assert "name successfully" in feedback.message


def test_failed_origin_feedback_is_actionable():
    feedback = generate_candidate_pedagogical_feedback(
        load_candidate(),
        "a1-u1-l1",
        build_result(
            "a1-u1-l1-c3-p2-semantic",
            "failed",
        ),
    )

    assert feedback.evaluation_status == "failed"
    assert "origin" in feedback.message
    assert "I am from Ecuador" in feedback.guidance


def test_unknown_lesson_cannot_generate_feedback():
    with pytest.raises(
        ValueError,
        match="No evaluation plan for lesson",
    ):
        generate_candidate_pedagogical_feedback(
            load_candidate(),
            "a1-u1-l99",
            build_result("a1-u1-l1-c3-p1-semantic"),
        )


def test_unknown_criterion_cannot_generate_feedback():
    with pytest.raises(
        ValueError,
        match="unknown criterion",
    ):
        generate_candidate_pedagogical_feedback(
            load_candidate(),
            "a1-u1-l1",
            build_result("unknown-criterion"),
        )
