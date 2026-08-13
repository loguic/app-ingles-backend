import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_capability_artifact_reference_validation import (
    build_lesson_capability_artifact_index,
    validate_capability_artifact_references,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


VALIDATOR_ID = "capability_artifact_reference_integrity"


def build_capability_candidate_payload() -> dict:
    """Build one candidate containing every identifiable artifact type.

    Construye una candidata con todos los tipos de artefacto identificables.
    """
    payload = deepcopy(build_candidate_payload())
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["conversations"] = [
        {
            "id": "a1-u1-l1-c1",
            "title": "Meeting someone",
            "mode": "free",
            "turns": [
                {
                    "id": "a1-u1-l1-c1-t1",
                    "speaker": "learner",
                    "en": "Introduce yourself.",
                    "choices": [
                        {
                            "id": "a1-u1-l1-c1-ch1",
                            "en": "Hello.",
                        }
                    ],
                    "production_prompt": {
                        "id": "a1-u1-l1-c1-p1",
                        "accepted_modalities": ["text", "voice"],
                        "production_function": "transfer",
                        "support_level": "none",
                        "transfer_bank_id": "introductions",
                        "transfer_variants": [
                            {
                                "id": "a1-u1-l1-c1-p1-v1",
                                "prompt": "Introduce yourself at work.",
                            },
                            {
                                "id": "a1-u1-l1-c1-p1-v2",
                                "prompt": "Introduce yourself in class.",
                            },
                        ],
                    },
                }
            ],
        }
    ]
    lesson["experience"] = {
        "contract_version": "2.0",
        "mission": {
            "id": "a1-u1-l1-m1",
            "title": "Introduce yourself",
            "situation": "Meet someone.",
            "observable_outcome": "State your name.",
            "success_criteria": ["The learner states a name."],
        },
        "skill_ids": ["a1_introduce_yourself"],
        "stages": [
            {
                "id": "a1-u1-l1-s1",
                "type": "evidence",
                "instruction": "Introduce yourself.",
                "activity_ids": ["a1-u1-l1-c1"],
                "completion_condition": "evidence_recorded",
            }
        ],
        "language_support": [
            {
                "id": "a1-u1-l1-ls1",
                "type": "expression",
                "en": "Hello, I am...",
                "stage_ids": ["a1-u1-l1-s1"],
            }
        ],
        "evidence_definitions": [
            {
                "id": "a1-u1-l1-ev1",
                "skill_ids": ["a1_introduce_yourself"],
                "stage_id": "a1-u1-l1-s1",
                "activity_id": "a1-u1-l1-c1",
                "production_prompt_id": "a1-u1-l1-c1-p1",
                "evidence_type": "contextual_response",
                "measurement_mode": "completion",
            }
        ],
        "completion_policy": {
            "practiced_stage_ids": ["a1-u1-l1-s1"],
            "required_evidence_ids": ["a1-u1-l1-ev1"],
        },
    }
    payload["evaluation_plans"] = [
        {
            "lesson_id": "a1-u1-l1",
            "criteria": [
                {
                    "id": "a1-u1-l1-semantic",
                    "evidence_definition_id": "a1-u1-l1-ev1",
                    "conversation_id": "a1-u1-l1-c1",
                    "prompt_id": "a1-u1-l1-c1-p1",
                    "dimension": "semantic",
                    "description": "The response states a name.",
                    "measurement_mode": "binary",
                    "applicable_modalities": ["text", "voice"],
                }
            ],
            "semantic_rules": [
                {
                    "id": "a1-u1-l1-semantic-rule",
                    "criterion_id": "a1-u1-l1-semantic",
                    "patterns": ["\\b(?:am|name)\\b"],
                }
            ],
        }
    ]
    payload["lesson_capability_plans"] = [
        {
            "lesson_id": "a1-u1-l1",
            "claims": [
                {
                    "skill_id": "a1_introduce_yourself",
                    "preparation_state": "EXPOSURE_AVAILABLE",
                    "artifact_ids": ["a1-u1-l1-m1"],
                }
            ],
        }
    ]
    return payload


def build_candidate(artifact_ids: list[str]) -> PedagogicalUnitCandidate:
    payload = build_capability_candidate_payload()
    payload["lesson_capability_plans"][0]["claims"][0][
        "artifact_ids"
    ] = artifact_ids
    return PedagogicalUnitCandidate.model_validate(payload)


@pytest.mark.parametrize(
    ("artifact_id", "artifact_type"),
    [
        ("a1-u1-l1-m1", "Mission"),
        ("a1-u1-l1-s1", "LessonStage"),
        ("a1-u1-l1-ls1", "LanguageSupportItem"),
        ("a1-u1-l1-e1", "Example"),
        ("a1-u1-l1-c1", "Conversation"),
        ("a1-u1-l1-c1-t1", "ConversationTurn"),
        ("a1-u1-l1-c1-ch1", "ConversationChoice"),
        ("a1-u1-l1-c1-p1", "LearnerProductionPrompt"),
        ("a1-u1-l1-c1-p1-v1", "TransferPromptVariant"),
        ("a1-u1-l1-q1", "ExerciseMCQ"),
        ("a1-u1-l1-ev1", "EvidenceDefinition"),
        ("a1-u1-l1-semantic", "ProductionEvaluationCriterion"),
        ("a1-u1-l1-semantic-rule", "SemanticEvaluationRule"),
    ],
)
def test_local_artifact_resolves_with_its_real_type(
    artifact_id: str,
    artifact_type: str,
):
    candidate = build_candidate([artifact_id])

    index = build_lesson_capability_artifact_index(
        candidate,
        "a1-u1-l1",
    )

    assert len(index[artifact_id]) == 1
    assert index[artifact_id][0].artifact_type == artifact_type
    assert validate_capability_artifact_references(candidate) == []


def test_legacy_candidate_without_capability_plans_has_no_findings():
    candidate = PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )

    assert candidate.lesson_capability_plans == []
    assert validate_capability_artifact_references(candidate) == []


def test_unknown_artifact_is_rejected():
    findings = validate_capability_artifact_references(
        build_candidate(["a1-u1-l1-unknown"])
    )

    assert len(findings) == 1
    assert findings[0].validator_id == VALIDATOR_ID
    assert "is unknown" in findings[0].message


def test_artifact_owned_only_by_another_lesson_is_rejected():
    payload = build_capability_candidate_payload()
    payload["candidate_unit"]["lessons"][1]["examples"] = [
        {"id": "a1-u1-l2-e1", "en": "Hello again."}
    ]
    payload["lesson_capability_plans"][0]["claims"][0][
        "artifact_ids"
    ] = ["a1-u1-l2-e1"]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_capability_artifact_references(candidate)

    assert len(findings) == 1
    assert "belongs to another lesson: a1-u1-l2" in findings[0].message


def test_artifact_collision_between_types_is_rejected():
    payload = build_capability_candidate_payload()
    payload["candidate_unit"]["lessons"][0]["experience"]["mission"][
        "id"
    ] = "a1-u1-l1-s1"
    payload["lesson_capability_plans"][0]["claims"][0][
        "artifact_ids"
    ] = ["a1-u1-l1-s1"]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_capability_artifact_references(candidate)

    assert len(findings) == 1
    assert "is ambiguous" in findings[0].message
    assert "LessonStage" in findings[0].message
    assert "Mission" in findings[0].message


@pytest.mark.parametrize("artifact_kind", ["criterion", "rule"])
def test_evaluation_artifact_from_another_lesson_is_rejected(
    artifact_kind: str,
):
    payload = build_capability_candidate_payload()
    evaluation_plan = payload["evaluation_plans"][0]
    evaluation_plan["lesson_id"] = "a1-u1-l2"
    artifact_id = (
        evaluation_plan["criteria"][0]["id"]
        if artifact_kind == "criterion"
        else evaluation_plan["semantic_rules"][0]["id"]
    )
    payload["lesson_capability_plans"][0]["claims"][0][
        "artifact_ids"
    ] = [artifact_id]
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    findings = validate_capability_artifact_references(candidate)

    assert len(findings) == 1
    assert "belongs to another lesson: a1-u1-l2" in findings[0].message


def test_validator_is_integrated_into_candidate_validation():
    report = validate_pedagogical_candidate(
        build_candidate(["a1-u1-l1-unknown"])
    )

    assert report.status == "failed"
    assert any(
        finding.validator_id == VALIDATOR_ID
        for finding in report.findings
    )


def test_canonical_legacy_candidate_keeps_prior_capability_behavior():
    candidate_path = Path(
        "content/candidates/a1-u1/pedagogical-unit-candidate-v2.json"
    )
    candidate = PedagogicalUnitCandidate.model_validate_json(
        candidate_path.read_text(encoding="utf-8")
    )

    report = validate_pedagogical_candidate(candidate)

    assert candidate.lesson_capability_plans == []
    assert all(
        finding.validator_id != VALIDATOR_ID
        for finding in report.findings
    )
