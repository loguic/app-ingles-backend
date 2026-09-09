from copy import deepcopy
from dataclasses import FrozenInstanceError, fields
import unicodedata

import pytest

from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.content import ExerciseVisualOption
from app.schemas.pedagogical_feedback import ProductionFeedbackRule
from app.schemas.pedagogical_unit import (
    LessonCapabilityClaim,
    PedagogicalUnitCandidate,
    ValidationFinding,
    ValidationReport,
)
from app.services.pedagogical_candidate_payload_identity import (
    PAYLOAD_SCHEMA_VERSION,
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)
from tests.test_pedagogical_validation_service import (
    build_candidate_payload,
    build_visual_context_candidate_payload,
)


def candidate_payload() -> dict:
    return {
        "specification": {
            "unit_id": "a1-u1",
            "level": "A1",
            "title": "Lección café",
            "learner_outcome": "Introduce yourself.",
            "skills": [
                {
                    "id": "a1_introduce_yourself",
                    "description": "Introduce yourself clearly.",
                    "required_stages": ["introduce"],
                }
            ],
            "required_evidence": ["One introduction."],
            "lesson_scope": ["Introductions."],
            "language_scope": ["My name is..."],
            "pronunciation_scope": ["Sentence stress."],
            "content_constraints": ["Use A1 language."],
            "technical_constraints": ["Use existing contracts."],
            "acceptance_criteria": ["Produce one introduction."],
        },
        "candidate_unit": {
            "id": "a1-u1",
            "title": "Lección café",
            "lessons": [
                {
                    "id": "a1-u1-l1",
                    "title": "Presentaciones",
                }
            ],
        },
        "evaluation_plans": [
            {
                "lesson_id": "a1-u1-l1",
                "criteria": [
                    {
                        "id": "a1-u1-l1-semantic",
                        "evidence_definition_id": "a1-u1-l1-ev1",
                        "conversation_id": "a1-u1-l1-c1",
                        "prompt_id": "a1-u1-l1-p1",
                        "dimension": "semantic",
                        "description": "States a name.",
                        "measurement_mode": "score",
                        "success_threshold": 0.0,
                        "applicable_modalities": ["text"],
                    }
                ],
            }
        ],
        "feedback_plans": [
            {
                "lesson_id": "a1-u1-l1",
                "rules": [
                    {
                        "id": "a1-u1-l1-semantic-feedback",
                        "criterion_id": "a1-u1-l1-semantic",
                        "passed_message": "Clear introduction.",
                        "passed_guidance": "Continue.",
                        "failed_message": "Introduction incomplete.",
                        "failed_guidance": "State your name.",
                    }
                ],
            }
        ],
        "lesson_capability_plans": [
            {
                "lesson_id": "a1-u1-l1",
                "claims": [],
                "prerequisites": [],
            }
        ],
        "skill_coverage": [
            {
                "skill_id": "a1_introduce_yourself",
                "introduced_in_lesson_id": "a1-u1-l1",
                "modalities": ["speaking"],
                "status": "complete",
            }
        ],
        "required_resource_ids": ["audio/á.wav", "audio/b.wav"],
        "validation_report": {"status": "passed", "findings": []},
        "pending_human_decisions": [],
        "proposed_change_summary": ["Add the reviewed candidate."],
    }


def candidate(**updates) -> PedagogicalUnitCandidate:
    payload = candidate_payload()
    payload.update(updates)
    return PedagogicalUnitCandidate.model_validate(payload)


def identity(
    value: PedagogicalUnitCandidate,
    revision: str = "revision-01",
) -> CandidatePayloadIdentity:
    return derive_candidate_payload_identity(
        value,
        candidate_revision=revision,
    )


def test_identity_contract_is_frozen_and_exact() -> None:
    result = identity(candidate())

    assert PAYLOAD_SCHEMA_VERSION == "1.0"
    assert [field.name for field in fields(result)] == [
        "unit_id",
        "candidate_revision",
        "payload_schema_version",
        "content_digest",
    ]
    assert result.unit_id == "a1-u1"
    assert result.payload_schema_version == "1.0"
    assert result.content_digest.startswith("sha256:")
    assert len(result.content_digest) == len("sha256:") + 64
    with pytest.raises(FrozenInstanceError):
        result.unit_id = "a1-u2"  # type: ignore[misc]


def test_derivation_is_deterministic_and_revision_is_not_hashed() -> None:
    value = candidate()

    first = identity(value)
    repeated = identity(value)
    other_revision = identity(value, "  revision-02  ")

    assert first == repeated
    assert other_revision.candidate_revision == "  revision-02  "
    assert other_revision.content_digest == first.content_digest


@pytest.mark.parametrize("invalid_revision", ["", "   ", None, 1])
def test_revision_must_be_a_non_blank_string(invalid_revision) -> None:
    with pytest.raises(ValueError, match="non-blank string"):
        derive_candidate_payload_identity(
            candidate(),
            candidate_revision=invalid_revision,
        )


def included_field_variants(
    value: PedagogicalUnitCandidate,
) -> list[PedagogicalUnitCandidate]:
    criterion = value.evaluation_plans[0].criteria[0]
    rule = value.feedback_plans[0].rules[0]
    capability_plan = value.lesson_capability_plans[0]
    coverage = value.skill_coverage[0]
    return [
        value.model_copy(
            update={
                "specification": value.specification.model_copy(
                    update={"title": "A different specification"}
                )
            }
        ),
        value.model_copy(
            update={
                "candidate_unit": value.candidate_unit.model_copy(
                    update={"title": "A different unit"}
                )
            }
        ),
        value.model_copy(
            update={
                "evaluation_plans": [
                    value.evaluation_plans[0].model_copy(
                        update={
                            "criteria": [
                                criterion.model_copy(
                                    update={"description": "Changed."}
                                )
                            ]
                        }
                    )
                ]
            }
        ),
        value.model_copy(
            update={
                "feedback_plans": [
                    value.feedback_plans[0].model_copy(
                        update={
                            "rules": [
                                rule.model_copy(
                                    update={"passed_message": "Changed."}
                                )
                            ]
                        }
                    )
                ]
            }
        ),
        value.model_copy(
            update={
                "lesson_capability_plans": [
                    capability_plan.model_copy(
                        update={
                            "claims": [
                                LessonCapabilityClaim(
                                    skill_id="a1_introduce_yourself",
                                    preparation_state="EXPOSURE_AVAILABLE",
                                    artifact_ids=["a1-u1-l1"],
                                )
                            ]
                        }
                    )
                ]
            }
        ),
        value.model_copy(
            update={
                "skill_coverage": [
                    coverage.model_copy(update={"status": "incomplete"})
                ]
            }
        ),
        value.model_copy(
            update={"required_resource_ids": ["audio/changed.wav"]}
        ),
    ]


def test_each_included_field_family_changes_the_digest() -> None:
    value = candidate()
    original_digest = identity(value).content_digest

    assert all(
        identity(changed).content_digest != original_digest
        for changed in included_field_variants(value)
    )


def test_excluded_metadata_does_not_change_the_digest() -> None:
    value = candidate()
    original_digest = identity(value).content_digest
    changed_report = ValidationReport(
        status="pending",
        findings=[
            ValidationFinding(
                validator_id="review_pending",
                severity="warning",
                message="Review remains pending.",
            )
        ],
    )
    variants = [
        value.model_copy(update={"validation_report": changed_report}),
        value.model_copy(
            update={"pending_human_decisions": ["Review wording."]}
        ),
        value.model_copy(
            update={"proposed_change_summary": ["Different summary."]}
        ),
    ]

    assert all(
        identity(changed).content_digest == original_digest
        for changed in variants
    )


def test_required_resource_sequence_order_is_preserved() -> None:
    value = candidate()
    reversed_resources = value.model_copy(
        update={
            "required_resource_ids": list(
                reversed(value.required_resource_ids)
            )
        }
    )

    assert (
        identity(reversed_resources).content_digest
        != identity(value).content_digest
    )


def test_defaults_unset_and_none_converge_after_validation() -> None:
    omitted_payload = candidate_payload()
    explicit_payload = deepcopy(omitted_payload)
    explicit_payload["specification"]["content_limits"] = {
        "min_lessons": None,
        "max_lessons": None,
        "min_examples_per_lesson": None,
        "max_examples_per_lesson": None,
        "min_conversations_per_lesson": None,
        "max_conversations_per_lesson": None,
        "min_exercises_per_lesson": None,
        "max_exercises_per_lesson": None,
        "min_options_per_exercise": None,
        "max_options_per_exercise": None,
        "min_turns_per_conversation": None,
        "max_turns_per_conversation": None,
    }
    explicit_payload["candidate_unit"]["lessons"][0]["objective"] = None

    omitted = PedagogicalUnitCandidate.model_validate(omitted_payload)
    explicit = PedagogicalUnitCandidate.model_validate(explicit_payload)

    assert identity(omitted).content_digest == identity(explicit).content_digest


def visual_context_candidate(**metadata: object) -> PedagogicalUnitCandidate:
    payload = build_visual_context_candidate_payload()
    payload["required_resource_ids"].append(
        "visual/a1_u1_l1_meeting.svg"
    )
    payload["candidate_unit"]["lessons"][0]["experience"][
        "visual_contexts"
    ][0].update(metadata)
    return PedagogicalUnitCandidate.model_validate(payload)


def test_visual_context_legacy_defaults_and_none_have_one_digest() -> None:
    legacy = visual_context_candidate()
    explicit_none = visual_context_candidate(
        resource_type=None,
        autoplay_once=None,
        replay_allowed=None,
    )

    assert identity(legacy).content_digest == identity(explicit_none).content_digest


def test_visual_context_type_and_playback_change_the_digest() -> None:
    legacy = visual_context_candidate()
    static_image = visual_context_candidate(resource_type="static_image")
    microvideo = visual_context_candidate(
        resource_type="microvideo",
        autoplay_once=True,
        replay_allowed=True,
    )
    microvideo_without_replay = visual_context_candidate(
        resource_type="microvideo",
        autoplay_once=True,
        replay_allowed=False,
    )

    digests = {
        identity(candidate).content_digest
        for candidate in (
            legacy,
            static_image,
            microvideo,
            microvideo_without_replay,
        )
    }

    assert len(digests) == 4


def visual_mcq_candidate(**changes: object) -> PedagogicalUnitCandidate:
    payload = build_candidate_payload()
    exercise = payload["candidate_unit"]["lessons"][0]["exercises"][0]
    options = [
        {
            "resource_id": "visual/a1-u1-l1-need.svg",
            "accessibility_label": "A person seeking assistance.",
        },
        {
            "resource_id": "visual/a1-u1-l1-greeting.svg",
            "accessibility_label": "Two people meeting.",
        },
        {
            "resource_id": "visual/a1-u1-l1-farewell.svg",
            "accessibility_label": "Two people leaving.",
        },
    ]
    exercise.update({"options": options, **changes})
    payload["required_resource_ids"].extend(
        option["resource_id"] for option in options
    )
    return PedagogicalUnitCandidate.model_validate(payload)


def test_textual_mcq_legacy_dump_and_digest_are_unchanged() -> None:
    payload = build_candidate_payload()
    value = PedagogicalUnitCandidate.model_validate(payload)
    exercise_payload = payload["candidate_unit"]["lessons"][0]["exercises"][0]

    assert value.candidate_unit.lessons[0].exercises[0].model_dump(
        mode="json"
    ) == {"type": "mcq", **exercise_payload}
    assert identity(value, "legacy-text-mcq").content_digest == (
        "sha256:8fbf2eef13753134acafe5352abd212f1edac7297abf495f6219757014acfdd0"
    )


def test_visual_mcq_fields_change_the_digest_deterministically() -> None:
    original = visual_mcq_candidate()
    changed_resource = visual_mcq_candidate()
    changed_resource_option = (
        changed_resource.candidate_unit.lessons[0].exercises[0].options[0]
    )
    assert isinstance(changed_resource_option, ExerciseVisualOption)
    changed_resource_option.resource_id = "visual/a1-u1-l1-need-alternate.svg"
    changed_resource.required_resource_ids[2] = changed_resource_option.resource_id
    changed_label = visual_mcq_candidate()
    changed_label_option = (
        changed_label.candidate_unit.lessons[0].exercises[0].options[0]
    )
    assert isinstance(changed_label_option, ExerciseVisualOption)
    changed_label_option.accessibility_label = (
        "A person asking a worker for assistance."
    )
    changed_order = visual_mcq_candidate()
    changed_order.candidate_unit.lessons[0].exercises[0].options.reverse()
    changed_answer_index = visual_mcq_candidate(answer_index=1)

    digests = {
        identity(value, "visual-mcq").content_digest
        for value in (
            original,
            changed_resource,
            changed_label,
            changed_order,
            changed_answer_index,
        )
    }

    assert len(digests) == 5
    assert (
        identity(original, "visual-mcq").content_digest
        == identity(original, "visual-mcq").content_digest
    )


def test_unicode_is_deterministic_but_not_normalized() -> None:
    value = candidate()
    repeated = candidate()
    decomposed_payload = candidate_payload()
    decomposed_payload["specification"]["title"] = unicodedata.normalize(
        "NFD", decomposed_payload["specification"]["title"]
    )
    decomposed = PedagogicalUnitCandidate.model_validate(decomposed_payload)

    assert identity(value).content_digest == identity(repeated).content_digest
    assert identity(value).content_digest != identity(decomposed).content_digest


def test_float_representation_preserves_negative_zero() -> None:
    positive_payload = candidate_payload()
    negative_payload = candidate_payload()
    negative_payload["evaluation_plans"][0]["criteria"][0][
        "success_threshold"
    ] = -0.0
    positive = PedagogicalUnitCandidate.model_validate(positive_payload)
    negative = PedagogicalUnitCandidate.model_validate(negative_payload)

    assert isinstance(
        positive.evaluation_plans[0].criteria[0].success_threshold,
        float,
    )
    assert identity(positive).content_digest != identity(negative).content_digest


def test_golden_candidate_payload_digest_and_input_immutability() -> None:
    value = candidate()
    before = deepcopy(value.model_dump(mode="json"))

    result = identity(value, "golden-revision")

    assert result.content_digest == (
        "sha256:b0ba248338e388e688fc8e3b25f325441e8d27ac2017b834bc78a8f08cfbb592"
    )
    assert value.model_dump(mode="json") == before
