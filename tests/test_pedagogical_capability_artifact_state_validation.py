from copy import deepcopy

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_capability_artifact_state_validation import (
    VALIDATOR_ID,
    validate_capability_artifact_state_compatibility,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_capability_artifact_reference_validation import (
    build_capability_candidate_payload,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


def build_candidate(
    state: str,
    artifact_ids: list[str],
    *,
    mutate=None,
) -> PedagogicalUnitCandidate:
    payload = build_capability_candidate_payload()
    if mutate is not None:
        mutate(payload)
    claim = payload["lesson_capability_plans"][0]["claims"][0]
    claim["preparation_state"] = state
    claim["artifact_ids"] = artifact_ids
    return PedagogicalUnitCandidate.model_validate(payload)


def findings(candidate: PedagogicalUnitCandidate):
    return validate_capability_artifact_state_compatibility(candidate)


def set_stage(payload: dict, stage_type: str) -> None:
    payload["candidate_unit"]["lessons"][0]["experience"]["stages"][0][
        "type"
    ] = stage_type


def move_existing_evidence_to_second_stage(payload: dict) -> None:
    """Keep existing evidence valid while changing the claimed stage.

    Mantiene válida la evidencia existente al cambiar la etapa del claim.
    """
    experience = payload["candidate_unit"]["lessons"][0]["experience"]
    experience["stages"].append(
        {
            "id": "a1-u1-l1-s2",
            "type": "evidence",
            "instruction": "Record evidence.",
            "activity_ids": ["a1-u1-l1-c1"],
            "completion_condition": "evidence_recorded",
        }
    )
    experience["evidence_definitions"][0]["stage_id"] = "a1-u1-l1-s2"
    experience["completion_policy"]["practiced_stage_ids"] = [
        "a1-u1-l1-s2"
    ]


def test_minimal_exposure_combination_is_valid():
    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-e1"],
        mutate=lambda payload: set_stage(payload, "encounter"),
    )

    assert findings(candidate) == []


def test_minimal_instruction_combination_is_valid():
    candidate = build_candidate(
        "INSTRUCTION_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ls1"],
        mutate=lambda payload: set_stage(payload, "language_support"),
    )

    assert findings(candidate) == []


def test_minimal_practice_combination_is_valid():
    candidate = build_candidate(
        "PRACTICE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-c1"],
        mutate=lambda payload: set_stage(payload, "guided_production"),
    )

    assert findings(candidate) == []


def test_minimal_automatic_evidence_gate_is_valid():
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ],
    )

    assert findings(candidate) == []


def test_skill_absent_from_experience_is_rejected():
    def mutate(payload):
        payload["candidate_unit"]["lessons"][0]["experience"][
            "skill_ids"
        ] = ["a1_other_skill"]
        payload["candidate_unit"]["lessons"][0]["experience"][
            "evidence_definitions"
        ][0]["skill_ids"] = ["a1_other_skill"]

    result = findings(
        build_candidate(
            "EXPOSURE_AVAILABLE",
            ["a1-u1-l1-s1", "a1-u1-l1-e1"],
            mutate=mutate,
        )
    )

    assert len(result) == 1
    assert "Skill is not linked" in result[0].message


@pytest.mark.parametrize(
    ("state", "artifact_ids", "stage_type"),
    [
        ("EXPOSURE_AVAILABLE", ["a1-u1-l1-e1"], "encounter"),
        ("INSTRUCTION_AVAILABLE", ["a1-u1-l1-ls1"], "language_support"),
        ("PRACTICE_AVAILABLE", ["a1-u1-l1-c1"], "guided_production"),
        ("EVIDENCE_GATE_AVAILABLE", ["a1-u1-l1-ev1"], "evidence"),
    ],
)
def test_compatible_stage_is_required(state, artifact_ids, stage_type):
    result = findings(
        build_candidate(
            state,
            artifact_ids,
            mutate=lambda payload: set_stage(payload, stage_type),
        )
    )

    assert len(result) == 1
    assert "LessonStage is required" in result[0].message


@pytest.mark.parametrize(
    ("state", "artifact_ids", "stage_type"),
    [
        (
            "EXPOSURE_AVAILABLE",
            ["a1-u1-l1-s1", "a1-u1-l1-e1"],
            "guided_production",
        ),
        (
            "INSTRUCTION_AVAILABLE",
            ["a1-u1-l1-s1", "a1-u1-l1-ls1"],
            "encounter",
        ),
        (
            "PRACTICE_AVAILABLE",
            ["a1-u1-l1-s1", "a1-u1-l1-c1"],
            "evidence",
        ),
    ],
)
def test_incompatible_stage_is_rejected(state, artifact_ids, stage_type):
    result = findings(
        build_candidate(
            state,
            artifact_ids,
            mutate=lambda payload: set_stage(payload, stage_type),
        )
    )

    assert len(result) == 1


def test_activity_outside_practice_stage_is_rejected():
    def mutate(payload):
        move_existing_evidence_to_second_stage(payload)
        set_stage(payload, "guided_production")
        payload["candidate_unit"]["lessons"][0]["experience"]["stages"][0][
            "activity_ids"
        ] = ["a1-u1-l1-q1"]

    result = findings(
        build_candidate(
            "PRACTICE_AVAILABLE",
            ["a1-u1-l1-s1", "a1-u1-l1-c1"],
            mutate=mutate,
        )
    )

    assert len(result) == 1
    assert "no compatible executable learner action" in result[0].message


@pytest.mark.parametrize(
    "artifact_id",
    ["a1-u1-l1-m1", "a1-u1-l1-e1"],
)
def test_contextual_content_without_stage_is_rejected(artifact_id):
    candidate = build_candidate("EXPOSURE_AVAILABLE", [artifact_id])

    assert len(findings(candidate)) == 1


def test_mission_and_stage_without_contextual_content_are_rejected():
    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-m1"],
        mutate=lambda payload: set_stage(payload, "encounter"),
    )

    assert len(findings(candidate)) == 1


def test_language_support_must_reference_instruction_stage():
    def mutate(payload):
        set_stage(payload, "language_support")
        payload["candidate_unit"]["lessons"][0]["experience"][
            "language_support"
        ][0]["stage_ids"] = ["a1-u1-l1-s2"]
        payload["candidate_unit"]["lessons"][0]["experience"]["stages"].append(
            {
                "id": "a1-u1-l1-s2",
                "type": "closure",
                "instruction": "Close.",
                "activity_ids": [],
                "completion_condition": "acknowledged",
            }
        )

    candidate = build_candidate(
        "INSTRUCTION_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ls1"],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


def test_passive_conversation_is_not_practice():
    def mutate(payload):
        move_existing_evidence_to_second_stage(payload)
        set_stage(payload, "guided_production")
        turn = payload["candidate_unit"]["lessons"][0]["conversations"][0][
            "turns"
        ][0]
        turn["speaker"] = "partner"
        turn["choices"] = []
        turn["production_prompt"] = None
        evidence = payload["candidate_unit"]["lessons"][0]["experience"][
            "evidence_definitions"
        ][0]
        evidence.update(
            {
                "activity_id": "a1-u1-l1-q1",
                "evidence_type": "exercise_result",
                "production_prompt_id": None,
            }
        )
        payload["candidate_unit"]["lessons"][0]["experience"]["stages"][1][
            "activity_ids"
        ] = ["a1-u1-l1-q1"]

    candidate = build_candidate(
        "PRACTICE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-c1"],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


def test_mcq_without_claim_skill_is_not_practice():
    def mutate(payload):
        move_existing_evidence_to_second_stage(payload)
        set_stage(payload, "comprehension")
        payload["candidate_unit"]["lessons"][0]["experience"]["stages"][0][
            "activity_ids"
        ] = ["a1-u1-l1-q1"]
        payload["candidate_unit"]["lessons"][0]["exercises"][0][
            "skill_ids"
        ] = ["a1_other_skill"]

    candidate = build_candidate(
        "PRACTICE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-q1"],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


@pytest.mark.parametrize(
    "artifact_id",
    [
        "a1-u1-l1-c1-ch1",
        "a1-u1-l1-c1-p1",
        "a1-u1-l1-c1-p1-v1",
    ],
)
def test_conversation_descendant_requires_executable_owner(artifact_id):
    def mutate(payload):
        move_existing_evidence_to_second_stage(payload)
        set_stage(payload, "guided_production")
        payload["candidate_unit"]["lessons"][0]["experience"]["stages"][0][
            "activity_ids"
        ] = ["a1-u1-l1-q1"]

    candidate = build_candidate(
        "PRACTICE_AVAILABLE",
        ["a1-u1-l1-s1", artifact_id],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


@pytest.mark.parametrize(
    "artifact_id",
    [
        "a1-u1-l1-c1-ch1",
        "a1-u1-l1-c1-p1",
        "a1-u1-l1-c1-p1-v1",
        "a1-u1-l1-q1",
        "a1-u1-l1-ev1",
        "a1-u1-l1-semantic",
        "a1-u1-l1-semantic-rule",
    ],
)
def test_explicitly_forbidden_type_cannot_support_exposure(artifact_id):
    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-e1", artifact_id],
        mutate=lambda payload: set_stage(payload, "encounter"),
    )

    assert len(findings(candidate)) == 1
    assert "cannot support exposure" in findings(candidate)[0].message


@pytest.mark.parametrize(
    "artifact_id",
    [
        "a1-u1-l1-m1",
        "a1-u1-l1-c1-ch1",
        "a1-u1-l1-c1-p1",
        "a1-u1-l1-c1-p1-v1",
        "a1-u1-l1-q1",
        "a1-u1-l1-ev1",
        "a1-u1-l1-semantic",
        "a1-u1-l1-semantic-rule",
    ],
)
def test_explicitly_forbidden_type_cannot_support_instruction(artifact_id):
    candidate = build_candidate(
        "INSTRUCTION_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ls1", artifact_id],
        mutate=lambda payload: set_stage(payload, "language_support"),
    )

    assert len(findings(candidate)) == 1
    assert "cannot support instruction" in findings(candidate)[0].message


def test_evidence_definition_alone_is_rejected():
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ev1"],
    )

    assert len(findings(candidate)) == 1


def test_evidence_skill_must_match_claim():
    def mutate(payload):
        experience = payload["candidate_unit"]["lessons"][0]["experience"]
        experience["skill_ids"].append("a1_other_skill")
        experience["evidence_definitions"][0]["skill_ids"] = ["a1_other_skill"]

    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


def add_second_evidence_stage(payload: dict) -> None:
    payload["candidate_unit"]["lessons"][0]["experience"]["stages"].append(
        {
            "id": "a1-u1-l1-s2",
            "type": "evidence",
            "instruction": "Record evidence.",
            "activity_ids": ["a1-u1-l1-c1"],
            "completion_condition": "evidence_recorded",
        }
    )


def test_claim_stage_must_match_evidence_stage():
    def mutate(payload):
        add_second_evidence_stage(payload)

    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s2",
            "a1-u1-l1-ev1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ],
        mutate=mutate,
    )

    assert len(findings(candidate)) == 1


def test_claim_activity_must_match_evidence_activity():
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-q1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ],
    )

    assert len(findings(candidate)) == 1


def configure_mcq_evidence(payload: dict) -> None:
    lesson = payload["candidate_unit"]["lessons"][0]
    lesson["experience"]["stages"][0]["activity_ids"] = ["a1-u1-l1-q1"]
    evidence = lesson["experience"]["evidence_definitions"][0]
    evidence.update(
        {
            "activity_id": "a1-u1-l1-q1",
            "evidence_type": "exercise_result",
            "measurement_mode": "binary",
            "production_prompt_id": None,
        }
    )
    payload["evaluation_plans"] = []


def test_mcq_evidence_gate_is_valid():
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ev1", "a1-u1-l1-q1"],
        mutate=configure_mcq_evidence,
    )

    assert findings(candidate) == []


def configure_external_review(payload: dict) -> None:
    payload["evaluation_plans"] = []
    evidence = payload["candidate_unit"]["lessons"][0]["experience"][
        "evidence_definitions"
    ][0]
    evidence["external_review_requirements"] = [
        {
            "dimension": "contingent_response",
            "allowed_results": ["positive", "negative", "pending"],
            "question": "Does the response address the prompt?",
        }
    ]


def test_conversation_external_review_gate_is_valid_without_invented_id():
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-ev1", "a1-u1-l1-c1-p1"],
        mutate=configure_external_review,
    )

    assert findings(candidate) == []
    assert all(
        "ExternalReviewRequirement" not in artifact_id
        for artifact_id in candidate.lesson_capability_plans[0].claims[0].artifact_ids
    )


def test_conversation_choice_external_review_gate_is_valid_without_prompt():
    def mutate(payload):
        configure_external_review(payload)
        lesson = payload["candidate_unit"]["lessons"][0]
        turn = lesson["conversations"][0]["turns"][0]
        turn["production_prompt"] = None
        evidence = lesson["experience"]["evidence_definitions"][0]
        evidence["production_prompt_id"] = None
        evidence["evidence_type"] = "conversation_completion"

    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-c1-ch1",
        ],
        mutate=mutate,
    )

    assert findings(candidate) == []
    turn = candidate.candidate_unit.lessons[0].conversations[0].turns[0]
    assert turn.production_prompt is None


def test_conversation_choice_without_evaluation_mechanism_is_rejected():
    def mutate(payload):
        payload["evaluation_plans"] = []
        lesson = payload["candidate_unit"]["lessons"][0]
        turn = lesson["conversations"][0]["turns"][0]
        turn["production_prompt"] = None
        evidence = lesson["experience"]["evidence_definitions"][0]
        evidence["production_prompt_id"] = None
        evidence["evidence_type"] = "conversation_completion"
        evidence["external_review_requirements"] = []

    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-c1-ch1",
        ],
        mutate=mutate,
    )

    result = findings(candidate)

    assert len(result) == 1
    assert result[0].validator_id == VALIDATOR_ID
    assert "evaluable gate" in result[0].message


@pytest.mark.parametrize(
    "artifact_id",
    ["a1-u1-l1-semantic", "a1-u1-l1-semantic-rule"],
)
def test_evaluation_contract_alone_cannot_create_gate(artifact_id):
    candidate = build_candidate(
        "EVIDENCE_GATE_AVAILABLE",
        ["a1-u1-l1-s1", artifact_id],
    )

    assert len(findings(candidate)) == 1


def test_pronunciation_reinforcement_participates_through_stage_only():
    def mutate(payload):
        set_stage(payload, "encounter")
        payload["candidate_unit"]["lessons"][0]["experience"][
            "pronunciation_reinforcement"
        ] = {
            "stage_id": "a1-u1-l1-s1",
            "reference_text": "Hello.",
            "listening_objective": "Notice the rhythm.",
            "pronunciations": [
                {
                    "locale": "en-US",
                    "ipa": "/həˈloʊ/",
                    "audio_asset": "audio/hello.wav",
                }
            ],
        }

    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-s1"],
        mutate=mutate,
    )

    assert findings(candidate) == []
    assert candidate.lesson_capability_plans[0].claims[0].artifact_ids == [
        "a1-u1-l1-s1"
    ]


def test_unresolved_reference_is_left_only_to_slice_three():
    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-unknown"],
    )

    assert findings(candidate) == []
    report = validate_pedagogical_candidate(candidate)
    assert sum(
        finding.validator_id == VALIDATOR_ID
        for finding in report.findings
    ) == 0


def test_legacy_candidate_without_plans_has_no_findings():
    candidate = PedagogicalUnitCandidate.model_validate(
        build_candidate_payload()
    )

    assert candidate.lesson_capability_plans == []
    assert findings(candidate) == []


def test_validator_is_integrated_with_one_finding_per_claim():
    candidate = build_candidate(
        "EXPOSURE_AVAILABLE",
        ["a1-u1-l1-s1", "a1-u1-l1-m1"],
        mutate=lambda payload: set_stage(payload, "encounter"),
    )

    report = validate_pedagogical_candidate(candidate)
    state_findings = [
        finding
        for finding in report.findings
        if finding.validator_id == VALIDATOR_ID
    ]

    assert report.status == "failed"
    assert len(state_findings) == 1
    assert state_findings[0].reference_ids == [
        "a1-u1-l1",
        "a1_introduce_yourself",
        "a1-u1-l1-s1",
        "a1-u1-l1-m1",
    ]
