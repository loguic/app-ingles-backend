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


@pytest.mark.parametrize("variant_count", [1, 5])
def test_rejects_transfer_bank_outside_two_to_four_variants(variant_count):
    payload = build_lesson_payload()
    prompt = production_prompt(payload, "transfer")
    source = prompt["transfer_variants"]
    if variant_count == 1:
        prompt["transfer_variants"] = source[:1]
    else:
        prompt["transfer_variants"].append(
            {"id": "a1-u1-l1-transfer-v5", "prompt": "What makes you happy?"}
        )

    with pytest.raises(ValidationError):
        Lesson.model_validate(payload)


def test_rejects_duplicate_transfer_variant_ids():
    payload = build_lesson_payload()
    variants = production_prompt(payload, "transfer")["transfer_variants"]
    variants[1]["id"] = variants[0]["id"]

    with pytest.raises(ValidationError, match="variant IDs must be unique"):
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
