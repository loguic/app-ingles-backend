"""Validate the static B181 short connected exchange contract.

Valida el contrato estático del intercambio breve conectado de B181.
"""

from app.schemas.content import Lesson


EXPECTED_LESSON_ID = "a1-u1-l2"
EXPECTED_SKILL_ID = "a1_maintain_short_connected_exchange"
EXPECTED_SKILL_TITLE = "Maintain a short connected exchange"
EXPECTED_SKILL_DEFINITION = (
    "Listen to three brief related oral interventions in a familiar "
    "situation and respond in the learner's own words, maintaining the "
    "topic through an unexpected related question and a natural closing "
    "reaction without increasing visible support."
)
EXPECTED_SKILL_EXCLUSIONS = (
    "general_listening",
    "long_conversation",
    "grammar_perfection",
    "automatic_semantic_evaluation",
    "progress",
    "mastery",
    "global_fluency",
)
EXPECTED_CONVERSATION_ID = "a1-u1-l2-c1"
EXPECTED_TURN_IDS = [
    f"a1-u1-l2-c1-t{index}"
    for index in range(1, 8)
]
EXPECTED_PROMPT_IDS = [
    "a1-u1-l2-p-place",
    "a1-u1-l2-p-interest",
    "a1-u1-l2-p-unexpected-where",
]
EXPECTED_EVIDENCE_IDS = [
    "a1-u1-l2-ev-place-response",
    "a1-u1-l2-ev-interest-response",
    "a1-u1-l2-ev-unexpected-followup-response",
]
EXPECTED_PARTNER_TEXTS = [
    "Where are you from?",
    "Oh, nice! What do you like doing in your free time?",
    "Nice. Where do you usually do that?",
    "Oh, I see. Thanks for telling me. It was nice talking with you. See you!",
]
EXPECTED_AUDIO_ASSETS = [
    [
        "audio/a1_u1_l2_c1_t1_us.wav",
        "audio/a1_u1_l2_c1_t1_uk.wav",
    ],
    [
        "audio/a1_u1_l2_c1_t3_us.wav",
        "audio/a1_u1_l2_c1_t3_uk.wav",
    ],
    [
        "audio/a1_u1_l2_c1_t5_us.wav",
        "audio/a1_u1_l2_c1_t5_uk.wav",
    ],
    [
        "audio/a1_u1_l2_c1_t7_us.wav",
        "audio/a1_u1_l2_c1_t7_uk.wav",
    ],
]
EXPECTED_REVIEW_QUESTIONS = {
    "intention_understanding": (
        "¿La respuesta demuestra comprensión suficiente de la intención "
        "principal de la intervención?"
    ),
    "contingent_response": (
        "¿La respuesta constituye una reacción pertinente a esa "
        "intervención y mantiene el intercambio?"
    ),
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_short_connected_exchange_lesson(lesson: Lesson) -> None:
    """Validate structure without claiming comprehension or contingency.

    Valida la estructura sin afirmar comprensión ni contingencia.
    """
    _require(lesson.id == EXPECTED_LESSON_ID, "B181 requires a1-u1-l2")
    _require(
        lesson.title == "Keep the conversation going",
        "B181 lesson title is invalid",
    )
    experience = lesson.experience
    _require(experience is not None, "B181 requires LessonExperience")
    _require(
        experience.pedagogical_method == "short_connected_exchange",
        "B181 requires the short connected exchange method",
    )
    _require(
        experience.skill_ids == [EXPECTED_SKILL_ID],
        "B181 requires the connected exchange Skill",
    )
    _require(
        len(lesson.conversations) == 1,
        "B181 requires exactly one conversation",
    )
    conversation = lesson.conversations[0]
    _require(
        conversation.id == EXPECTED_CONVERSATION_ID,
        "B181 conversation ID is invalid",
    )
    _require(conversation.mode == "free", "B181 conversation must be free")
    _require(
        [turn.id for turn in conversation.turns] == EXPECTED_TURN_IDS,
        "B181 requires seven ordered turns",
    )
    _require(
        [turn.speaker for turn in conversation.turns]
        == [
            "partner",
            "learner",
            "partner",
            "learner",
            "partner",
            "learner",
            "partner",
        ],
        "B181 requires four partner interventions and three learner turns",
    )
    _require(
        conversation.start_turn_id == EXPECTED_TURN_IDS[0],
        "B181 conversation must start at the first intervention",
    )
    _require(
        [turn.next_turn_id for turn in conversation.turns]
        == EXPECTED_TURN_IDS[1:] + [None],
        "B181 conversation turns must form one connected sequence",
    )

    policy = conversation.audio_first_policy
    _require(policy is not None, "B181 requires an audio-first policy")
    _require(
        policy.primary_presentation == "audio"
        and policy.audio_replay_allowed
        and policy.transcript_initially_hidden
        and policy.transcript_access == "contingency_accessibility"
        and policy.transcript_use_interpretation
        == "assisted_not_exclusively_auditory"
        and policy.transcript_is_answer_model is False,
        "B181 audio-first or transcript contingency policy is invalid",
    )

    partner_turns = conversation.turns[::2]
    _require(
        [turn.en for turn in partner_turns] == EXPECTED_PARTNER_TEXTS,
        "B181 partner intervention text is invalid",
    )
    _require(
        all(
            [item.locale for item in turn.pronunciations] == ["en-US", "en-GB"]
            and all(
                item.audio_asset.strip() and item.ipa.strip()
                for item in turn.pronunciations
            )
            for turn in partner_turns
        ),
        "B181 partner interventions require referenced en-US and en-GB audio",
    )
    _require(
        [
            [item.audio_asset for item in turn.pronunciations]
            for turn in partner_turns
        ]
        == EXPECTED_AUDIO_ASSETS,
        "B181 audio asset references are invalid",
    )
    _require(
        conversation.turns[4].interaction_function == "unexpected_follow_up",
        "B181 third intervention must be marked unexpected",
    )
    _require(
        conversation.turns[6].interaction_function == "reaction_closure",
        "B181 final intervention must be marked as reaction and closure",
    )
    _require(
        all(
            turn.interaction_function is None
            for turn in conversation.turns[:4]
        ),
        "Only the approved B181 turns can have interaction functions",
    )

    prompts = [
        turn.production_prompt
        for turn in conversation.turns[1::2]
    ]
    _require(
        all(prompt is not None for prompt in prompts),
        "B181 requires three productions",
    )
    _require(
        [prompt.id for prompt in prompts] == EXPECTED_PROMPT_IDS,
        "B181 requires three unique approved prompts",
    )
    _require(
        [prompt.production_function for prompt in prompts]
        == [
            "contingent_response",
            "contingent_response",
            "unexpected_contingent_response",
        ],
        "B181 production functions are invalid",
    )
    _require(
        all(
            prompt.required
            and prompt.primary_modality == "voice"
            and prompt.accepted_modalities == ["voice", "text"]
            and prompt.fallback_modalities == ["text"]
            and prompt.allow_full_answer_model is False
            for prompt in prompts
        ),
        "B181 productions require voice, text fallback, and no full model",
    )
    _require(
        [prompt.support_level for prompt in prompts]
        == ["anchors", "initial_word", "none"],
        "B181 support must decrease from anchors to initial_word to none",
    )
    _require(
        [prompt.visible_support for prompt in prompts]
        == [
            ["Place", "I", "am from", "live"],
            ["Interest / free time", "I"],
            [],
        ],
        "B181 visible support does not match the approved withdrawal",
    )

    evidence = experience.evidence_definitions
    _require(
        [item.id for item in evidence] == EXPECTED_EVIDENCE_IDS,
        "B181 requires three distinct evidence definitions",
    )
    _require(
        [item.production_prompt_id for item in evidence] == EXPECTED_PROMPT_IDS,
        "B181 evidence must map one-to-one to production prompts",
    )
    for item in evidence:
        _require(
            item.skill_ids == [EXPECTED_SKILL_ID]
            and item.activity_id == EXPECTED_CONVERSATION_ID
            and item.evidence_type == "contextual_response"
            and item.measurement_mode == "completion",
            "B181 evidence structure is invalid",
        )
        requirements = item.external_review_requirements
        _require(
            [requirement.dimension for requirement in requirements]
            == ["intention_understanding", "contingent_response"],
            "B181 evidence requires intention and contingency review",
        )
        _require(
            all(
                requirement.allowed_results
                == ["positive", "negative", "pending"]
                and requirement.question
                == EXPECTED_REVIEW_QUESTIONS[requirement.dimension]
                and requirement.positive_required_for_completion
                for requirement in requirements
            ),
            "B181 external review rubric is invalid",
        )

    _require(
        experience.completion_policy.required_evidence_ids
        == EXPECTED_EVIDENCE_IDS,
        "B181 completion must require all three evidence definitions",
    )
