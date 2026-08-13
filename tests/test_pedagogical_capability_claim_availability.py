from copy import deepcopy

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_capability_claim_availability import (
    derive_capability_claim_availabilities,
    validate_capability_claim_availability,
)
from app.services.pedagogical_validation_service import (
    validate_pedagogical_candidate,
)
from tests.test_pedagogical_capability_artifact_reference_validation import (
    build_capability_candidate_payload,
)
from tests.test_pedagogical_validation_service import build_candidate_payload


VALIDATOR_ID = "capability_claim_availability_integrity"


def _availabilities(candidate: PedagogicalUnitCandidate):
    return derive_capability_claim_availabilities(candidate).availabilities


def _candidate(
    artifact_ids: list[str],
    *,
    stage_ids: tuple[str, ...] = ("stage-z", "stage-a"),
) -> PedagogicalUnitCandidate:
    payload = build_capability_candidate_payload()
    lesson = payload["candidate_unit"]["lessons"][0]
    experience = lesson["experience"]
    first = experience["stages"][0]
    first["id"] = stage_ids[0]
    first["type"] = "encounter"
    first["activity_ids"] = ["a1-u1-l1-e1", "a1-u1-l1-c1"]
    experience["evidence_definitions"][0]["stage_id"] = stage_ids[0]
    experience["language_support"][0]["stage_ids"] = [stage_ids[0]]
    experience["completion_policy"]["practiced_stage_ids"] = [stage_ids[0]]
    if len(stage_ids) > 1:
        experience["stages"].append(
            {
                "id": stage_ids[1],
                "type": "encounter",
                "instruction": "Meet the expression again.",
                "activity_ids": ["a1-u1-l1-e1"],
                "completion_condition": "all_activities_completed",
            }
        )
    claim = payload["lesson_capability_plans"][0]["claims"][0]
    claim["preparation_state"] = "EXPOSURE_AVAILABLE"
    claim["artifact_ids"] = artifact_ids
    return PedagogicalUnitCandidate.model_validate(payload)


def _evidence_candidate(artifact_ids: list[str]) -> PedagogicalUnitCandidate:
    payload = build_capability_candidate_payload()
    claim = payload["lesson_capability_plans"][0]["claims"][0]
    claim["preparation_state"] = "EVIDENCE_GATE_AVAILABLE"
    claim["artifact_ids"] = artifact_ids
    return PedagogicalUnitCandidate.model_validate(payload)


def test_one_stage_artifact_derives_its_stage():
    result = _availabilities(
        _candidate(["stage-z", "a1-u1-l1-e1"], stage_ids=("stage-z",))
    )

    assert result[0].point.stage_id == "stage-z"
    assert result[0].point.stage_index == 0


def test_artifacts_in_same_stage_derive_that_stage():
    result = _availabilities(
        _candidate(["stage-z", "a1-u1-l1-e1"], stage_ids=("stage-z",))
    )

    assert result[0].point.stage_id == "stage-z"


def test_latest_real_stage_wins_and_ids_do_not_define_order():
    result = _availabilities(
        _candidate(["stage-z", "a1-u1-l1-e1"])
    )

    assert result[0].point.stage_id == "stage-a"
    assert result[0].point.stage_index == 1


def test_multiple_support_associations_use_latest_stage():
    candidate = _candidate(["stage-z", "a1-u1-l1-ls1"])
    candidate.candidate_unit.lessons[0].experience.language_support[0].stage_ids = [
        "stage-z",
        "stage-a",
    ]

    assert _availabilities(candidate)[0].point.stage_id == "stage-a"


def test_nested_artifact_uses_owning_conversation_stage():
    result = _availabilities(
        _candidate(["stage-z", "a1-u1-l1-c1-t1"])
    )

    assert result[0].point.stage_id == "stage-z"


def test_conversation_choice_uses_owning_conversation_stage():
    candidate = _evidence_candidate(
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-c1-ch1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ]
    )

    assert _availabilities(candidate)[0].point.stage_id == "a1-u1-l1-s1"


def test_production_prompt_uses_owning_conversation_stage():
    candidate = _evidence_candidate(
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ]
    )

    assert _availabilities(candidate)[0].point.stage_id == "a1-u1-l1-s1"


def test_evidence_definition_uses_its_declared_stage():
    candidate = _evidence_candidate(
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-c1-ch1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ]
    )

    assert _availabilities(candidate)[0].point.stage_id == "a1-u1-l1-s1"


def test_evaluation_criterion_uses_its_owned_evidence_stage():
    candidate = _evidence_candidate(
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ]
    )

    assert _availabilities(candidate)[0].point.stage_id == "a1-u1-l1-s1"


def test_semantic_rule_uses_criterion_and_evidence_owner_stage():
    candidate = _evidence_candidate(
        [
            "a1-u1-l1-s1",
            "a1-u1-l1-c1-p1",
            "a1-u1-l1-ev1",
            "a1-u1-l1-semantic",
            "a1-u1-l1-semantic-rule",
        ]
    )

    assert _availabilities(candidate)[0].point.stage_id == "a1-u1-l1-s1"


def test_compatible_claim_with_mission_is_not_given_an_invented_position():
    candidate = _candidate(
        ["a1-u1-l1-m1", "stage-z", "a1-u1-l1-e1"],
        stage_ids=("stage-z",),
    )

    derivation = derive_capability_claim_availabilities(candidate)
    findings = validate_capability_claim_availability(candidate)

    assert derivation.availabilities == ()
    assert len(derivation.derivation_errors) == 1
    assert "Mission" not in derivation.derivation_errors[0].cause
    assert "a1-u1-l1-m1 has no canonical stage" in derivation.derivation_errors[0].cause
    assert len(findings) == 1
    assert findings[0].validator_id == VALIDATOR_ID


def test_unpositioned_compatible_artifact_produces_one_finding():
    candidate = _candidate(["stage-z", "a1-u1-l1-e1"], stage_ids=("stage-z",))
    candidate.candidate_unit.lessons[0].experience.stages[0].activity_ids = [
        "a1-u1-l1-c1"
    ]

    findings = validate_capability_claim_availability(candidate)

    assert len(findings) == 1
    assert findings[0].validator_id == VALIDATOR_ID


def test_unknown_stage_relation_produces_one_finding():
    candidate = _candidate(["stage-z", "a1-u1-l1-ls1"])
    candidate.candidate_unit.lessons[0].experience.language_support[0].stage_ids = [
        "stage-z",
        "missing-stage"
    ]

    findings = validate_capability_claim_availability(candidate)

    assert len(findings) == 1
    assert "unknown stage missing-stage" in findings[0].message


def test_invalid_reference_and_incompatible_claim_are_skipped():
    invalid_reference = _candidate(["stage-z"])
    invalid_reference.lesson_capability_plans[0].claims[0].artifact_ids = ["missing"]
    incompatible = _candidate(["stage-z"])
    incompatible.lesson_capability_plans[0].claims[0].preparation_state = (
        "PRACTICE_AVAILABLE"
    )

    assert validate_capability_claim_availability(invalid_reference) == []
    assert validate_capability_claim_availability(incompatible) == []
    assert derive_capability_claim_availabilities(incompatible).availabilities == ()
    assert derive_capability_claim_availabilities(incompatible).derivation_errors == ()


def test_derivation_is_reproducible():
    candidate = _candidate(["stage-z", "a1-u1-l1-e1"])

    assert derive_capability_claim_availabilities(
        candidate
    ) == derive_capability_claim_availabilities(candidate)


def test_lesson_index_uses_candidate_list_and_keeps_lessons_isolated():
    payload = build_capability_candidate_payload()
    first_lesson = payload["candidate_unit"]["lessons"][0]
    first_lesson["id"] = "lesson-z"
    first_lesson["experience"]["stages"][0]["type"] = "encounter"
    payload["candidate_unit"]["lessons"] = [
        first_lesson,
        deepcopy(first_lesson),
    ]
    second = payload["candidate_unit"]["lessons"][1]
    second["id"] = "lesson-a"
    second["experience"]["mission"]["id"] = "mission-second"
    second["experience"]["stages"][0]["activity_ids"].append(
        "a1-u1-l1-e1"
    )
    payload["lesson_capability_plans"] = [
        {
            "lesson_id": "lesson-a",
            "claims": [
                {
                    "skill_id": "a1_introduce_yourself",
                    "preparation_state": "EXPOSURE_AVAILABLE",
                    "artifact_ids": [
                        "a1-u1-l1-s1",
                        "a1-u1-l1-e1",
                    ],
                }
            ],
        }
    ]
    payload["evaluation_plans"] = []
    candidate = PedagogicalUnitCandidate.model_validate(payload)

    result = _availabilities(candidate)

    assert result[0].lesson_id == "lesson-a"
    assert result[0].lesson_index == 1


def test_batch_and_validator_report_every_unpositionable_claim_in_order():
    candidate = _candidate(
        ["stage-z", "a1-u1-l1-e1"],
        stage_ids=("stage-z",),
    )
    lesson = candidate.candidate_unit.lessons[0]
    lesson.experience.stages[0].activity_ids = ["a1-u1-l1-c1"]
    first = candidate.lesson_capability_plans[0].claims[0]
    second = first.model_copy(
        update={
            "artifact_ids": [
                "a1-u1-l1-m1",
                "stage-z",
                "a1-u1-l1-c1",
            ]
        }
    )
    candidate.lesson_capability_plans[0].claims.append(second)

    derivation = derive_capability_claim_availabilities(candidate)
    findings = validate_capability_claim_availability(candidate)

    assert derivation.availabilities == ()
    assert [error.artifact_ids for error in derivation.derivation_errors] == [
        ("stage-z", "a1-u1-l1-e1"),
        ("a1-u1-l1-m1", "stage-z", "a1-u1-l1-c1"),
    ]
    assert len(findings) == 2
    assert [tuple(finding.reference_ids[2:]) for finding in findings] == [
        ("stage-z", "a1-u1-l1-e1"),
        ("a1-u1-l1-m1", "stage-z", "a1-u1-l1-c1"),
    ]


def test_legacy_candidate_empty_plan_and_required_stages_do_not_intervene():
    legacy = PedagogicalUnitCandidate.model_validate(build_candidate_payload())
    with_empty_plan = _candidate(["stage-z"])
    with_empty_plan.lesson_capability_plans[0].claims = []
    changed_coverage = _candidate(
        ["stage-z", "a1-u1-l1-e1"],
        stage_ids=("stage-z",),
    )
    changed_coverage.specification.skills[0].required_stages = ["consolidate"]

    assert validate_capability_claim_availability(legacy) == []
    assert validate_capability_claim_availability(with_empty_plan) == []
    assert _availabilities(changed_coverage)[0].point.stage_id == "stage-z"


def test_pure_api_returns_structured_error_for_unpositionable_claim():
    candidate = _candidate(["stage-z", "a1-u1-l1-e1"], stage_ids=("stage-z",))
    candidate.candidate_unit.lessons[0].experience.stages[0].activity_ids = [
        "a1-u1-l1-c1"
    ]

    derivation = derive_capability_claim_availabilities(candidate)

    assert derivation.availabilities == ()
    assert len(derivation.derivation_errors) == 1
    error = derivation.derivation_errors[0]
    assert error.lesson_id == candidate.candidate_unit.lessons[0].id
    assert error.skill_id == "a1_introduce_yourself"
    assert error.preparation_state == "EXPOSURE_AVAILABLE"
    assert error.artifact_ids == ("stage-z", "a1-u1-l1-e1")


def test_integrates_with_candidate_validation():
    candidate = _candidate(["stage-z", "a1-u1-l1-e1"], stage_ids=("stage-z",))
    candidate.candidate_unit.lessons[0].experience.stages[0].activity_ids = [
        "a1-u1-l1-c1"
    ]

    report = validate_pedagogical_candidate(candidate)

    assert any(finding.validator_id == VALIDATOR_ID for finding in report.findings)
