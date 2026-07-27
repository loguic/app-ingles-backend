import pytest
from pydantic import ValidationError

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate


def build_candidate() -> dict:
    """Build one minimal valid candidate. / Construye una candidata mínima válida."""
    return {
        "specification": {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Introductions",
            "learner_outcome": "Introduce yourself.",
            "skills": [
                {
                    "id": "a1_introduce_yourself",
                    "description": "Introduce yourself in a short exchange.",
                    "required_stages": ["introduce"],
                }
            ],
            "required_evidence": ["Observable introduction."],
            "lesson_scope": ["Introduce yourself."],
            "language_scope": ["Basic introduction language."],
            "pronunciation_scope": ["Basic spoken introduction."],
            "content_constraints": ["Keep the exchange at A1 level."],
            "technical_constraints": ["Use stable identifiers."],
            "acceptance_criteria": ["The learner can introduce themselves."],
        },
        "candidate_unit": {
            "id": "a1-u1",
            "title": "Introductions",
            "lessons": [
                {
                    "id": "a1-u1-l1",
                    "title": "Introduce yourself",
                }
            ],
        },
        "skill_coverage": [
            {
                "skill_id": "a1_introduce_yourself",
                "introduced_in_lesson_id": "a1-u1-l1",
                "status": "incomplete",
            }
        ],
        "validation_report": {
            "status": "passed",
            "findings": [],
        },
        "proposed_change_summary": [
            "Add traceable production evaluation contracts."
        ],
    }


def build_plan() -> dict:
    """Build one lesson evaluation plan. / Construye un plan evaluativo de lección."""
    return {
        "lesson_id": "a1-u1-l1",
        "criteria": [
            {
                "id": "a1-u1-l1-c1-p1-semantic",
                "evidence_definition_id": "a1-u1-l1-ev1",
                "conversation_id": "a1-u1-l1-c1",
                "prompt_id": "a1-u1-l1-c1-p1",
                "dimension": "semantic",
                "description": "The learner states a name.",
                "measurement_mode": "binary",
                "applicable_modalities": ["text", "voice"],
            }
        ],
    }


def test_candidate_remains_compatible_without_evaluation_plans():
    candidate = PedagogicalUnitCandidate.model_validate(build_candidate())

    assert candidate.evaluation_plans == []


def test_candidate_accepts_plan_for_existing_lesson():
    payload = build_candidate()
    payload["evaluation_plans"] = [build_plan()]

    candidate = PedagogicalUnitCandidate.model_validate(payload)

    assert candidate.evaluation_plans[0].lesson_id == "a1-u1-l1"


def test_candidate_rejects_duplicate_lesson_plans():
    payload = build_candidate()
    plan = build_plan()
    payload["evaluation_plans"] = [plan, plan]

    with pytest.raises(
        ValidationError,
        match="Evaluation plan lesson IDs must be unique",
    ):
        PedagogicalUnitCandidate.model_validate(payload)


def test_candidate_rejects_plan_for_unknown_lesson():
    payload = build_candidate()
    plan = build_plan()
    plan["lesson_id"] = "a1-u1-l9"
    payload["evaluation_plans"] = [plan]

    with pytest.raises(
        ValidationError,
        match="Evaluation plans reference unknown lessons",
    ):
        PedagogicalUnitCandidate.model_validate(payload)
