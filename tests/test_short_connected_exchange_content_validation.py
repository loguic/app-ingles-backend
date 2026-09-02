import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.content import Lesson
from app.services.short_connected_exchange_content_validation import (
    EXPECTED_AUDIO_ASSETS,
    EXPECTED_CONVERSATION_ID,
    EXPECTED_EVIDENCE_IDS,
    EXPECTED_PROMPT_IDS,
    EXPECTED_SKILL_DEFINITION,
    EXPECTED_SKILL_EXCLUSIONS,
    EXPECTED_SKILL_ID,
    EXPECTED_SKILL_TITLE,
    EXPECTED_TURN_IDS,
    validate_short_connected_exchange_lesson,
)


CONTENT_PATH = Path(__file__).resolve().parents[1] / "content" / "content_tree.json"


def lesson_payload(lesson_id: str = "a1-u1-l2") -> dict:
    tree = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    return next(
        lesson
        for level in tree["levels"]
        for unit in level["units"]
        for lesson in unit["lessons"]
        if lesson["id"] == lesson_id
    )


def b181_lesson() -> Lesson:
    return Lesson.model_validate(lesson_payload())


def test_b181_lesson_skill_and_connected_sequence_are_valid():
    lesson = b181_lesson()

    validate_short_connected_exchange_lesson(lesson)

    conversation = lesson.conversations[0]
    assert lesson.id == "a1-u1-l2"
    assert lesson.title == "Keep the conversation going"
    assert lesson.experience.skill_ids == [EXPECTED_SKILL_ID]
    assert EXPECTED_SKILL_TITLE == "Maintain a short connected exchange"
    assert "unexpected related question" in EXPECTED_SKILL_DEFINITION
    assert {"progress", "mastery", "global_fluency"}.issubset(
        EXPECTED_SKILL_EXCLUSIONS
    )
    assert conversation.id == EXPECTED_CONVERSATION_ID
    assert [turn.id for turn in conversation.turns] == EXPECTED_TURN_IDS
    assert [turn.speaker for turn in conversation.turns].count("partner") == 4
    assert [turn.speaker for turn in conversation.turns].count("learner") == 3


def test_b181_audio_first_transcript_contingency_and_pending_assets():
    conversation = b181_lesson().conversations[0]
    policy = conversation.audio_first_policy

    assert policy.primary_presentation == "audio"
    assert policy.audio_replay_allowed is True
    assert policy.transcript_initially_hidden is True
    assert policy.transcript_access == "contingency_accessibility"
    assert (
        policy.transcript_use_interpretation
        == "assisted_not_exclusively_auditory"
    )
    assert policy.transcript_is_answer_model is False
    assert (
        policy.transcript_reveal_after_first_response_to_exercise_id
        is None
    )
    assert [item.locale for item in conversation.turns[0].pronunciations] == [
        "en-US",
        "en-GB",
    ]
    assert all(
        item.audio_asset.startswith("audio/a1_u1_l2_c1_")
        for turn in conversation.turns[::2]
        for item in turn.pronunciations
    )
    assert [
        [item.audio_asset for item in turn.pronunciations]
        for turn in conversation.turns[::2]
    ] == EXPECTED_AUDIO_ASSETS


def test_b181_three_voice_productions_have_decreasing_support():
    prompts = [
        turn.production_prompt
        for turn in b181_lesson().conversations[0].turns[1::2]
    ]

    assert [prompt.id for prompt in prompts] == EXPECTED_PROMPT_IDS
    assert [prompt.primary_modality for prompt in prompts] == ["voice"] * 3
    assert [prompt.fallback_modalities for prompt in prompts] == [["text"]] * 3
    assert [prompt.support_level for prompt in prompts] == [
        "anchors",
        "initial_word",
        "none",
    ]
    assert all(prompt.allow_full_answer_model is False for prompt in prompts)
    assert prompts[2].visible_support == []


def test_b181_marks_unexpected_followup_and_reaction_closure():
    turns = b181_lesson().conversations[0].turns

    assert turns[4].id == "a1-u1-l2-c1-t5"
    assert turns[4].interaction_function == "unexpected_follow_up"
    assert turns[5].production_prompt.production_function == (
        "unexpected_contingent_response"
    )
    assert turns[6].id == "a1-u1-l2-c1-t7"
    assert turns[6].interaction_function == "reaction_closure"
    assert turns[6].production_prompt is None


def test_b181_evidence_requires_both_external_review_dimensions():
    evidence = b181_lesson().experience.evidence_definitions

    assert [item.id for item in evidence] == EXPECTED_EVIDENCE_IDS
    assert [item.production_prompt_id for item in evidence] == EXPECTED_PROMPT_IDS
    for item in evidence:
        assert [
            requirement.dimension
            for requirement in item.external_review_requirements
        ] == ["intention_understanding", "contingent_response"]
        assert all(
            requirement.allowed_results == ["positive", "negative", "pending"]
            and requirement.positive_required_for_completion
            for requirement in item.external_review_requirements
        )
        assert all(
            "result" not in type(requirement).model_fields
            and "outcome" not in type(requirement).model_fields
            for requirement in item.external_review_requirements
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda lesson: lesson.conversations[0].turns.reverse(),
            "seven ordered turns",
        ),
        (
            lambda lesson: setattr(
                lesson.conversations[0].turns[3].production_prompt,
                "support_level",
                "model",
            ),
            "support must decrease",
        ),
        (
            lambda lesson: setattr(
                lesson.conversations[0].turns[3].production_prompt,
                "allow_full_answer_model",
                True,
            ),
            "no full model",
        ),
        (
            lambda lesson: setattr(
                lesson.conversations[0].turns[4],
                "interaction_function",
                None,
            ),
            "marked unexpected",
        ),
        (
            lambda lesson: setattr(
                lesson.conversations[0].turns[6],
                "interaction_function",
                None,
            ),
            "reaction and closure",
        ),
        (
            lambda lesson: lesson.experience.evidence_definitions[
                0
            ].external_review_requirements.pop(),
            "intention and contingency review",
        ),
        (
            lambda lesson: setattr(
                lesson.conversations[0].turns[0].pronunciations[0],
                "audio_asset",
                "audio/wrong.wav",
            ),
            "audio asset references",
        ),
    ],
)
def test_b181_validator_rejects_broken_contract(mutation, message):
    lesson = b181_lesson().model_copy(deep=True)
    mutation(lesson)

    with pytest.raises(ValueError, match=message):
        validate_short_connected_exchange_lesson(lesson)


def test_schema_rejects_audio_first_policy_that_exposes_transcript_first():
    payload = lesson_payload()
    payload["conversations"][0]["audio_first_policy"][
        "transcript_initially_hidden"
    ] = False

    with pytest.raises(ValidationError, match="initially hidden"):
        Lesson.model_validate(payload)


def test_evidence_rejects_unknown_production_prompt():
    payload = lesson_payload()
    payload["experience"]["evidence_definitions"][0][
        "production_prompt_id"
    ] = "unknown-prompt"

    with pytest.raises(ValidationError, match="unknown production prompt"):
        Lesson.model_validate(payload)


def test_legacy_lesson_and_b180_semantics_remain_compatible():
    legacy = Lesson.model_validate({"id": "legacy", "title": "Legacy"})
    b180 = Lesson.model_validate(lesson_payload("a1-u1-l1"))

    assert legacy.experience is None
    assert legacy.conversations == []
    assert b180.title == "Introduce yourself directly"
    assert b180.experience.pedagogical_method == "direct_english_construction"
    assert b180.experience.skill_ids == ["a1_introduce_yourself"]
    assert [item.id for item in b180.experience.evidence_definitions] == [
        "a1-u1-l1-ev-guided",
        "a1-u1-l1-ev-expanded",
        "a1-u1-l1-ev-transfer",
    ]


def test_b181_contract_does_not_claim_semantics_progress_or_mastery():
    lesson = b181_lesson()
    serialized = json.dumps(lesson.model_dump())

    assert '"progress"' not in serialized
    assert '"mastery"' not in serialized
    assert '"semantic_result"' not in serialized
    assert '"literal_response"' not in serialized
