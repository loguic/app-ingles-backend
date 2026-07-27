from datetime import UTC, datetime

import pytest

from app.schemas.evaluation import (
    ProductionEvaluationCriterion,
    ProductionEvaluationResultRecord,
)
from app.schemas.pedagogical_feedback import ProductionFeedbackRule
from app.services.pedagogical_feedback_service import (
    generate_pedagogical_feedback,
)


def build_criterion():
    return ProductionEvaluationCriterion(
        id="a1-u1-l1-c3-p1-semantic",
        evidence_definition_id="a1-u1-l1-ev3",
        conversation_id="a1-u1-l1-c3",
        prompt_id="a1-u1-l1-c3-p1",
        dimension="semantic",
        description="The learner states a name.",
        measurement_mode="binary",
        applicable_modalities=["text", "voice"],
    )


def build_result(status="passed"):
    return ProductionEvaluationResultRecord(
        evaluation_result_id=10,
        production_id=4,
        criterion_id="a1-u1-l1-c3-p1-semantic",
        status=status,
        score=None,
        evaluator_id="deterministic-semantic",
        evaluator_version="1.0",
        evaluated_at=datetime.now(UTC),
    )


def build_rule():
    return ProductionFeedbackRule(
        id="a1-u1-l1-c3-p1-feedback",
        criterion_id="a1-u1-l1-c3-p1-semantic",
        passed_message="You stated your name successfully.",
        passed_guidance="Continue using the same structure naturally.",
        failed_message="Your response did not clearly state a name.",
        failed_guidance="Try a structure such as My name is Ana.",
    )


def test_passed_result_generates_positive_feedback():
    feedback = generate_pedagogical_feedback(
        build_result(),
        build_criterion(),
        build_rule(),
    )

    assert feedback.evaluation_status == "passed"
    assert feedback.message == "You stated your name successfully."
    assert "same structure" in feedback.guidance


def test_failed_result_generates_retry_feedback():
    feedback = generate_pedagogical_feedback(
        build_result("failed"),
        build_criterion(),
        build_rule(),
    )

    assert feedback.evaluation_status == "failed"
    assert "did not clearly state" in feedback.message
    assert "My name is Ana" in feedback.guidance


def test_feedback_preserves_traceability():
    feedback = generate_pedagogical_feedback(
        build_result(),
        build_criterion(),
        build_rule(),
    )

    assert feedback.evaluation_result_id == 10
    assert feedback.production_id == 4
    assert feedback.criterion_id == build_criterion().id
    assert feedback.criterion_description == (
        "The learner states a name."
    )
    assert feedback.generator_id == (
        "deterministic-pedagogical-feedback"
    )
    assert feedback.generator_version == "1.0"


def test_result_must_match_criterion():
    result = build_result().model_copy(
        update={"criterion_id": "other-criterion"}
    )

    with pytest.raises(
        ValueError,
        match="result criterion_id must match criterion",
    ):
        generate_pedagogical_feedback(
            result,
            build_criterion(),
            build_rule(),
        )


def test_rule_must_match_criterion():
    rule = build_rule().model_copy(
        update={"criterion_id": "other-criterion"}
    )

    with pytest.raises(
        ValueError,
        match="Feedback rule criterion_id must match criterion",
    ):
        generate_pedagogical_feedback(
            build_result(),
            build_criterion(),
            rule,
        )
