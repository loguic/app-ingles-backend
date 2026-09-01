from copy import deepcopy

import pytest
from pydantic import ValidationError

from app.schemas.content import LearnerProductionPrompt, Lesson
from app.services.content_service import get_lesson_by_id
from app.services.direct_english_construction_content_validation import (
    EXPECTED_CORRECTION_PRIORITIES,
    validate_direct_english_construction_lesson,
)


def build_lesson_payload() -> dict:
    lesson = get_lesson_by_id("a1-u1-l1")
    assert lesson is not None
    return lesson.model_dump(mode="json")


def production_prompt(payload: dict, function: str) -> dict:
    for conversation in payload["conversations"]:
        for turn in conversation["turns"]:
            prompt = turn.get("production_prompt")
            if prompt and prompt.get("production_function") == function:
                return prompt
    raise AssertionError("missing production function " + function)


def production_prompts(payload: dict, function: str) -> list[dict]:
    prompts = [
        prompt
        for conversation in payload["conversations"]
        for turn in conversation["turns"]
        if (prompt := turn.get("production_prompt")) is not None
        and prompt.get("production_function") == function
    ]
    if not prompts:
        raise AssertionError("missing production function " + function)
    return prompts


def learner_turn(payload: dict, function: str) -> dict:
    for conversation in payload["conversations"]:
        for turn in conversation["turns"]:
            prompt = turn.get("production_prompt")
            if prompt and prompt.get("production_function") == function:
                return turn
    raise AssertionError("missing production function " + function)


def validate_payload(payload: dict) -> Lesson:
    lesson = Lesson.model_validate(payload)
    validate_direct_english_construction_lesson(lesson)
    return lesson


def conversation(payload: dict, conversation_id: str) -> dict:
    return next(
        item
        for item in payload["conversations"]
        if item["id"] == conversation_id
    )


def build_v3_lesson_payload() -> dict:
    """Build isolated future content without activating the curriculum."""
    payload = build_lesson_payload()
    experience = payload["experience"]
    experience["contract_version"] = "3.0"
    payload["exercises"][0]["skill_ids"] = ["a1_introduce_yourself"]

    guided = conversation(payload, "a1-u1-l1-c-direct-guided")
    expanded = conversation(payload, "a1-u1-l1-c-direct-expanded")
    transfer = conversation(payload, "a1-u1-l1-c-direct-transfer")
    original_turns = {
        function: deepcopy(learner_turn(payload, function))
        for function in ("guided", "expanded", "transfer")
    }

    def copy_capture(function: str, target: dict) -> dict:
        turn = deepcopy(original_turns[function])
        turn["id"] = target["id"] + "-t-v3-" + function
        turn["production_prompt"]["id"] = target["id"] + "-p-v3-" + function
        return turn

    guided["turns"].extend(
        [copy_capture("expanded", guided), copy_capture("transfer", guided)]
    )
    expanded["turns"].extend(
        [copy_capture("guided", expanded), copy_capture("transfer", expanded)]
    )
    transfer["turns"][1].pop("production_prompt")

    experience["evidence_definitions"] = [
        {
            "id": "a1-u1-l1-ev-comprehension-v3",
            "skill_ids": ["a1_introduce_yourself"],
            "stage_id": "a1-u1-l1-s1",
            "activity_id": "a1-u1-l1-c1",
            "comprehension_exercise_id": "a1-u1-l1-q1",
            "evidence_type": "comprehension_result",
            "measurement_mode": "binary",
        },
        {
            "id": "a1-u1-l1-ev-guided-v3",
            "skill_ids": ["a1_introduce_yourself"],
            "stage_id": "a1-u1-l1-s2",
            "activity_id": guided["id"],
            "evidence_type": "guided_production",
            "measurement_mode": "completion",
        },
        {
            "id": "a1-u1-l1-ev-contextual-v3",
            "skill_ids": ["a1_introduce_yourself"],
            "stage_id": "a1-u1-l1-s3",
            "activity_id": expanded["id"],
            "evidence_type": "contextual_response",
            "measurement_mode": "completion",
        },
        {
            "id": "a1-u1-l1-ev-conversation-v3",
            "skill_ids": ["a1_introduce_yourself"],
            "stage_id": "a1-u1-l1-s4",
            "activity_id": transfer["id"],
            "evidence_type": "conversation_completion",
            "measurement_mode": "completion",
        },
    ]
    experience["completion_policy"]["required_evidence_ids"] = [
        item["id"] for item in experience["evidence_definitions"]
    ]
    return payload


def test_active_first_lesson_is_valid_direct_construction_content():
    lesson = validate_payload(build_lesson_payload())
    experience = lesson.experience

    assert lesson.id == "a1-u1-l1"
    assert lesson.title == "Introduce yourself directly"
    assert experience is not None
    assert experience.skill_ids == ["a1_introduce_yourself"]
    assert [stage.type for stage in experience.stages] == [
        "encounter",
        "guided_production",
        "applied_conversation",
        "evidence",
        "closure",
    ]
    assert experience.correction_policy is not None
    assert experience.correction_policy.priorities == (
        EXPECTED_CORRECTION_PRIORITIES
    )


def test_v3_requires_two_direct_attempt_activities_with_three_captures_each():
    lesson = validate_payload(build_v3_lesson_payload())
    assert lesson.experience is not None
    assert lesson.experience.contract_version == "3.0"
    assert [
        item.evidence_type
        for item in lesson.experience.evidence_definitions
    ] == [
        "comprehension_result",
        "guided_production",
        "contextual_response",
        "conversation_completion",
    ]


def test_v3_rejects_a_direct_attempt_activity_without_all_three_captures():
    payload = build_v3_lesson_payload()
    contextual = conversation(payload, "a1-u1-l1-c-direct-expanded")
    contextual["turns"] = contextual["turns"][:-1]

    with pytest.raises(ValueError, match="requires guided, expanded and transfer"):
        validate_payload(payload)


def test_v3_accepts_one_transfer_variant_per_direct_activity():
    payload = build_v3_lesson_payload()
    for prompt in production_prompts(payload, "transfer"):
        prompt["transfer_variants"] = prompt["transfer_variants"][:1]

    lesson = validate_payload(payload)

    assert all(
        len(prompt.transfer_variants) == 1
        for conversation in lesson.conversations
        for turn in conversation.turns
        if (prompt := turn.production_prompt) is not None
        and prompt.production_function == "transfer"
    )


def test_v3_rejects_transfer_without_a_bank():
    payload = build_v3_lesson_payload()
    transfer_prompt = production_prompts(payload, "transfer")[0]
    transfer_prompt.pop("transfer_bank_id")
    transfer_prompt["transfer_variants"] = []

    with pytest.raises(ValueError, match="v3 transfer requires a bank"):
        validate_payload(payload)


def test_v3_rejects_transfer_bank_without_variants():
    payload = build_v3_lesson_payload()
    production_prompts(payload, "transfer")[0]["transfer_variants"] = []

    with pytest.raises(ValidationError, match="one to four variants"):
        Lesson.model_validate(payload)


def test_v3_rejects_transfer_bank_with_five_variants():
    payload = build_v3_lesson_payload()
    prompt = production_prompts(payload, "transfer")[0]
    prompt["transfer_variants"].append(
        {"id": "a1-u1-l1-transfer-v5", "prompt": "What makes you happy?"}
    )

    with pytest.raises(ValidationError, match="at most 4 items"):
        Lesson.model_validate(payload)


def test_reuses_regional_audio_and_adds_shadowing_before_production():
    lesson = validate_payload(build_lesson_payload())
    experience = lesson.experience
    assert experience is not None
    reinforcement = experience.pronunciation_reinforcement
    assert reinforcement is not None

    assert reinforcement.stage_id == experience.stages[0].id
    assert reinforcement.shadowing is True
    assert reinforcement.phonetic_targets == ["/iː/"]
    assert [item.locale for item in reinforcement.pronunciations] == [
        "en-US",
        "en-GB",
    ]
    assert all(
        "a1_u1_l1_c1_t3" in item.audio_asset
        for item in reinforcement.pronunciations
    )


def test_defines_exactly_three_distinct_production_evidences():
    lesson = validate_payload(build_lesson_payload())
    experience = lesson.experience
    assert experience is not None
    prompts = [
        turn.production_prompt
        for conversation in lesson.conversations
        for turn in conversation.turns
        if turn.production_prompt is not None
        and turn.production_prompt.production_function is not None
    ]

    assert [item.production_function for item in prompts] == [
        "guided",
        "expanded",
        "transfer",
    ]
    assert len({item.id for item in prompts}) == 3
    assert len(experience.evidence_definitions) == 3
    assert len({item.id for item in experience.evidence_definitions}) == 3
    assert set(experience.completion_policy.required_evidence_ids) == {
        item.id for item in experience.evidence_definitions
    }


def test_voice_is_primary_and_text_is_only_recorded_fallback():
    lesson = validate_payload(build_lesson_payload())
    prompts = [
        turn.production_prompt
        for conversation in lesson.conversations
        for turn in conversation.turns
        if turn.production_prompt is not None
        and turn.production_prompt.production_function is not None
    ]

    assert all(item.primary_modality == "voice" for item in prompts)
    assert all(item.fallback_modalities == ["text"] for item in prompts)
    assert all(set(item.accepted_modalities) == {"voice", "text"} for item in prompts)


def test_rejects_text_as_only_demonstration_modality():
    payload = build_lesson_payload()
    prompt = production_prompt(payload, "guided")
    prompt["accepted_modalities"] = ["text"]
    prompt["primary_modality"] = "text"
    prompt["fallback_modalities"] = []

    with pytest.raises(ValueError, match="requires voice as primary"):
        validate_payload(payload)


@pytest.mark.parametrize(
    ("function", "support_level"),
    [("guided", "initial_word"), ("expanded", "anchors")],
)
def test_rejects_invalid_or_increasing_support(function, support_level):
    payload = build_lesson_payload()
    production_prompt(payload, function)["support_level"] = support_level

    with pytest.raises(ValueError, match="support must progress"):
        validate_payload(payload)


def test_rejects_transfer_with_language_support():
    payload = build_lesson_payload()
    payload["experience"]["language_support"][0]["stage_ids"].append(
        "a1-u1-l1-s4"
    )

    with pytest.raises(ValueError, match="Transfer stage cannot expose"):
        validate_payload(payload)


@pytest.mark.parametrize("function", ["expanded", "transfer"])
def test_rejects_full_answer_model_for_independent_production(function):
    payload = build_lesson_payload()
    production_prompt(payload, function)["allow_full_answer_model"] = True

    with pytest.raises(ValidationError, match="cannot allow a full answer"):
        Lesson.model_validate(payload)


@pytest.mark.parametrize("variant_count", [0, 5])
def test_schema_rejects_empty_or_oversized_transfer_bank(variant_count):
    payload = build_lesson_payload()
    prompt = production_prompt(payload, "transfer")
    source = prompt["transfer_variants"]
    if variant_count == 0:
        prompt["transfer_variants"] = []
    else:
        prompt["transfer_variants"].append(
            {"id": "a1-u1-l1-transfer-v5", "prompt": "What makes you happy?"}
        )

    with pytest.raises(ValidationError):
        Lesson.model_validate(payload)


def test_v2_rejects_one_transfer_variant():
    payload = build_lesson_payload()
    prompt = production_prompt(payload, "transfer")
    prompt["transfer_variants"] = prompt["transfer_variants"][:1]

    with pytest.raises(ValueError, match="v2 transfer requires two to four"):
        validate_payload(payload)


@pytest.mark.parametrize("variant_count", [2, 4])
def test_v2_accepts_two_to_four_transfer_variants(variant_count):
    payload = build_lesson_payload()
    prompt = production_prompt(payload, "transfer")
    prompt["transfer_variants"] = prompt["transfer_variants"][:variant_count]

    lesson = validate_payload(payload)

    validated_prompt = production_prompt(
        lesson.model_dump(mode="json"), "transfer"
    )
    assert len(validated_prompt["transfer_variants"]) == variant_count


def test_rejects_duplicate_transfer_variant_ids():
    payload = build_lesson_payload()
    variants = production_prompt(payload, "transfer")["transfer_variants"]
    variants[1]["id"] = variants[0]["id"]

    with pytest.raises(ValidationError, match="variant IDs must be unique"):
        Lesson.model_validate(payload)


def test_rejects_duplicate_normalized_transfer_variant_prompts():
    payload = build_lesson_payload()
    variants = production_prompt(payload, "transfer")["transfer_variants"]
    variants[1]["prompt"] = "  " + variants[0]["prompt"].upper() + "  "

    with pytest.raises(ValidationError, match="variant prompts must be unique"):
        Lesson.model_validate(payload)


def test_v3_rejects_duplicate_transfer_variant_ids_and_prompts():
    payload = build_v3_lesson_payload()
    variants = production_prompts(payload, "transfer")[0]["transfer_variants"]
    variants[1]["id"] = variants[0]["id"]

    with pytest.raises(ValidationError, match="variant IDs must be unique"):
        Lesson.model_validate(payload)

    payload = build_v3_lesson_payload()
    variants = production_prompts(payload, "transfer")[0]["transfer_variants"]
    variants[1]["prompt"] = "  " + variants[0]["prompt"].upper() + "  "

    with pytest.raises(ValidationError, match="variant prompts must be unique"):
        Lesson.model_validate(payload)


def test_rejects_transfer_prompt_equal_to_expansion_prompt():
    payload = build_lesson_payload()
    learner_turn(payload, "transfer")["en"] = learner_turn(
        payload, "expanded"
    )["en"]

    with pytest.raises(ValueError, match="must differ from expansion"):
        validate_payload(payload)


def test_rejects_incomplete_completion_policy():
    payload = build_lesson_payload()
    payload["experience"]["evidence_definitions"][2]["required"] = False
    payload["experience"]["completion_policy"]["required_evidence_ids"].pop()

    with pytest.raises(ValueError, match="requires distinct evidence"):
        validate_payload(payload)


def test_rejects_more_than_one_correction_or_wrong_priority_order():
    payload = build_lesson_payload()
    payload["experience"]["correction_policy"]["max_guidance_items"] = 2
    with pytest.raises(ValueError, match="allows one guidance item"):
        validate_payload(payload)

    payload = build_lesson_payload()
    priorities = payload["experience"]["correction_policy"]["priorities"]
    priorities[0], priorities[1] = priorities[1], priorities[0]
    with pytest.raises(ValueError, match="priorities are out of order"):
        validate_payload(payload)


def test_legacy_production_prompt_remains_compatible():
    prompt = LearnerProductionPrompt(
        id="legacy-prompt",
        accepted_modalities=["text"],
    )

    assert prompt.production_function is None
    assert prompt.primary_modality is None
    assert prompt.fallback_modalities == []
    assert prompt.support_level is None
    assert prompt.allow_full_answer_model is None
    assert prompt.transfer_variants == []


def test_validator_does_not_add_semantic_progress_or_mastery_contracts():
    lesson = validate_payload(deepcopy(build_lesson_payload()))

    assert "progress" not in type(lesson).model_fields
    assert "mastery" not in type(lesson).model_fields
    assert "semantic_classifier" not in type(lesson).model_fields
