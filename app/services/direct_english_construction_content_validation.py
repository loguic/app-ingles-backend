from app.schemas.content import Lesson, LearnerProductionPrompt


EXPECTED_SKILL_ID = "a1_introduce_yourself"
EXPECTED_STAGE_TYPES = [
    "encounter",
    "guided_production",
    "applied_conversation",
    "evidence",
    "closure",
]
EXPECTED_FUNCTIONS = {"guided", "expanded", "transfer"}
EXPECTED_CORRECTION_PRIORITIES = [
    "relevance",
    "direct_english_construction",
    "intelligibility",
    "secondary_accuracy",
]


def _production_entries(lesson: Lesson):
    return [
        (conversation, turn, turn.production_prompt)
        for conversation in lesson.conversations
        for turn in conversation.turns
        if turn.production_prompt is not None
        and turn.production_prompt.production_function is not None
    ]


def _require_complete_prompt(prompt: LearnerProductionPrompt) -> None:
    required_values = {
        "production_function": prompt.production_function,
        "primary_modality": prompt.primary_modality,
        "support_level": prompt.support_level,
        "allow_full_answer_model": prompt.allow_full_answer_model,
    }
    missing = [
        field_name
        for field_name, value in required_values.items()
        if value is None
    ]
    if missing:
        raise ValueError(
            "Direct construction production prompt requires: "
            + ", ".join(missing)
        )


def _validate_v3_direct_english_construction_lesson(lesson: Lesson) -> None:
    """Validate the closed v3 one-source-to-one-evidence mapping."""
    experience = lesson.experience
    if experience is None:  # pragma: no cover - caller guards it.
        raise ValueError("Direct construction lesson requires an experience")

    evidence_by_id = {
        item.id: item for item in experience.evidence_definitions
    }
    required_evidence = [
        evidence_by_id[item_id]
        for item_id in experience.completion_policy.required_evidence_ids
    ]
    required_types = [item.evidence_type for item in required_evidence]
    if sorted(required_types) != sorted(
        [
            "comprehension_result",
            "guided_production",
            "contextual_response",
            "conversation_completion",
        ]
    ):
        raise ValueError(
            "Direct construction v3 requires exactly four canonical evidence"
        )

    direct_evidence = [
        item
        for item in required_evidence
        if item.evidence_type in {"guided_production", "contextual_response"}
    ]
    if [item.evidence_type for item in direct_evidence] != [
        "guided_production",
        "contextual_response",
    ]:
        raise ValueError(
            "Direct construction v3 requires guided then contextual evidence"
        )
    if len({item.activity_id for item in direct_evidence}) != 2:
        raise ValueError(
            "Direct construction v3 evidence activities must be distinct"
        )

    conversations_by_id = {
        conversation.id: conversation for conversation in lesson.conversations
    }
    direct_activity_ids = {item.activity_id for item in direct_evidence}
    for evidence in direct_evidence:
        conversation = conversations_by_id.get(evidence.activity_id)
        if conversation is None:
            raise ValueError(
                "Direct construction v3 evidence activity is unavailable"
            )
        entries = [
            turn.production_prompt
            for turn in conversation.turns
            if turn.production_prompt is not None
            and turn.production_prompt.production_function is not None
        ]
        functions = [item.production_function for item in entries]
        if set(functions) != EXPECTED_FUNCTIONS or len(functions) != 3:
            raise ValueError(
                "Direct construction v3 evidence requires guided, expanded "
                "and transfer captures"
            )
        for prompt in entries:
            _require_complete_prompt(prompt)
            if not prompt.required:
                raise ValueError(
                    "Direct construction v3 prompts must be required"
                )
            if prompt.primary_modality != "voice":
                raise ValueError(
                    "Direct construction v3 requires voice as primary modality"
                )
            if set(prompt.accepted_modalities) != {"voice", "text"}:
                raise ValueError(
                    "Direct construction v3 requires text fallback"
                )
            if prompt.fallback_modalities != ["text"]:
                raise ValueError(
                    "Direct construction v3 requires text fallback"
                )
            if prompt.production_function == "transfer" and (
                prompt.transfer_bank_id is None
                or not 1 <= len(prompt.transfer_variants) <= 4
            ):
                raise ValueError(
                    "Direct construction v3 transfer requires a bank with one "
                    "to four variants"
                )

    direct_entries = [
        (conversation, turn.production_prompt)
        for conversation in lesson.conversations
        for turn in conversation.turns
        if turn.production_prompt is not None
        and turn.production_prompt.production_function in EXPECTED_FUNCTIONS
    ]
    if any(
        conversation.id not in direct_activity_ids
        for conversation, _ in direct_entries
    ):
        raise ValueError(
            "Direct construction v3 captures must belong to direct evidence"
        )


def validate_direct_english_construction_lesson(lesson: Lesson) -> None:
    """Validate the deterministic structure of one direct-English lesson.

    Valida la estructura determinista de una lección de inglés directo.

    This validator does not classify free meaning, relevance, literalness,
    progress or mastery. / Este validador no clasifica significado libre,
    pertinencia, literalidad, progreso ni mastery.
    """
    experience = lesson.experience
    if (
        experience is None
        or experience.pedagogical_method
        != "direct_english_construction"
    ):
        return

    if experience.contract_version == "3.0":
        _validate_v3_direct_english_construction_lesson(lesson)
        return

    if experience.skill_ids != [EXPECTED_SKILL_ID]:
        raise ValueError(
            "Direct construction lesson requires a1_introduce_yourself"
        )

    stage_types = [stage.type for stage in experience.stages]
    if stage_types != EXPECTED_STAGE_TYPES:
        raise ValueError(
            "Direct construction lesson requires the complete ordered stages"
        )

    reinforcement = experience.pronunciation_reinforcement
    if reinforcement is None or not reinforcement.shadowing:
        raise ValueError(
            "Direct construction lesson requires pronunciation shadowing"
        )
    if reinforcement.stage_id != experience.stages[0].id:
        raise ValueError(
            "Pronunciation reinforcement must precede learner production"
        )

    available_pronunciations = [
        pronunciation
        for example in lesson.examples
        for pronunciation in example.pronunciations
    ] + [
        pronunciation
        for conversation in lesson.conversations
        for turn in conversation.turns
        for pronunciation in turn.pronunciations
    ]
    if any(
        pronunciation not in available_pronunciations
        for pronunciation in reinforcement.pronunciations
    ):
        raise ValueError(
            "Pronunciation reinforcement must reuse lesson audio references"
        )

    entries = _production_entries(lesson)
    functions = [
        prompt.production_function for _, _, prompt in entries
    ]
    if set(functions) != EXPECTED_FUNCTIONS or len(functions) != 3:
        raise ValueError(
            "Direct construction lesson requires exactly guided, expanded "
            "and transfer productions"
        )

    entries_by_function = {
        prompt.production_function: (conversation, turn, prompt)
        for conversation, turn, prompt in entries
    }
    prompts = [prompt for _, _, prompt in entries]
    for prompt in prompts:
        _require_complete_prompt(prompt)
        if not prompt.required:
            raise ValueError(
                "Direct construction production prompts must be required"
            )
        if prompt.primary_modality != "voice":
            raise ValueError(
                "Direct construction evidence requires voice as primary modality"
            )
        if set(prompt.accepted_modalities) != {"voice", "text"}:
            raise ValueError(
                "Direct construction records voice with text fallback"
            )
        if prompt.fallback_modalities != ["text"]:
            raise ValueError(
                "Text must be the only direct construction fallback modality"
            )

    prompt_ids = [prompt.id for prompt in prompts]
    if len(prompt_ids) != len(set(prompt_ids)):
        raise ValueError("Direct construction prompt IDs must be unique")

    expected_support = {
        "guided": "anchors",
        "expanded": "initial_word",
        "transfer": "none",
    }
    actual_support = {
        function: entries_by_function[function][2].support_level
        for function in EXPECTED_FUNCTIONS
    }
    if actual_support != expected_support:
        raise ValueError(
            "Direct construction support must progress from anchors to "
            "initial_word to none"
        )
    support_rank = {"model": 3, "anchors": 2, "initial_word": 1, "none": 0}
    ordered_support = [
        support_rank[actual_support[function]]
        for function in ("guided", "expanded", "transfer")
    ]
    if ordered_support != sorted(ordered_support, reverse=True):
        raise ValueError("Direct construction support cannot increase")

    for function in ("expanded", "transfer"):
        if entries_by_function[function][2].allow_full_answer_model:
            raise ValueError(
                function.capitalize()
                + " production cannot provide a full answer model"
            )

    stage_by_function = {
        "guided": experience.stages[1],
        "expanded": experience.stages[2],
        "transfer": experience.stages[3],
    }
    for function, stage in stage_by_function.items():
        conversation = entries_by_function[function][0]
        if conversation.id not in stage.activity_ids:
            raise ValueError(
                "Direct construction production must belong to its ordered stage"
            )

    transfer_stage_id = experience.stages[3].id
    if any(
        transfer_stage_id in item.stage_ids
        for item in experience.language_support
    ):
        raise ValueError("Transfer stage cannot expose language support")

    supports_by_stage = {
        stage.id: [
            item
            for item in experience.language_support
            if stage.id in item.stage_ids
        ]
        for stage in experience.stages
    }
    if not any(
        item.type == "reference_expression"
        for item in supports_by_stage[experience.stages[0].id]
    ):
        raise ValueError("Model stage requires one complete reference expression")
    guided_supports = supports_by_stage[experience.stages[1].id]
    if len(guided_supports) < 2 or any(
        item.type != "pattern" for item in guided_supports
    ):
        raise ValueError("Guided stage requires Persona and Verbo anchors")
    expanded_supports = supports_by_stage[experience.stages[2].id]
    if len(expanded_supports) != 1 or (
        expanded_supports[0].type != "word"
        or expanded_supports[0].en.strip() != "I"
    ):
        raise ValueError("Expanded stage requires only the initial word I")

    expanded_turn = entries_by_function["expanded"][1]
    transfer_turn = entries_by_function["transfer"][1]
    transfer_prompt = entries_by_function["transfer"][2]
    if expanded_turn.en.strip().casefold() == transfer_turn.en.strip().casefold():
        raise ValueError("Transfer prompt must differ from expansion prompt")
    if transfer_prompt.transfer_bank_id is None:
        raise ValueError("Transfer production requires a prompt bank")
    if not 2 <= len(transfer_prompt.transfer_variants) <= 4:
        raise ValueError(
            "Direct construction v2 transfer requires two to four variants"
        )
    if any(
        item.prompt.strip().casefold()
        == expanded_turn.en.strip().casefold()
        for item in transfer_prompt.transfer_variants
    ):
        raise ValueError(
            "Transfer variants must differ from the expansion prompt"
        )

    evidence_by_activity = {
        evidence.activity_id: evidence
        for evidence in experience.evidence_definitions
        if evidence.required
    }
    required_evidence = []
    for function in ("guided", "expanded", "transfer"):
        conversation_id = entries_by_function[function][0].id
        evidence = evidence_by_activity.get(conversation_id)
        if evidence is None:
            raise ValueError(
                "Direct construction production requires distinct evidence"
            )
        required_evidence.append(evidence)
    evidence_ids = [evidence.id for evidence in required_evidence]
    if len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("Direct construction evidence IDs must be distinct")
    if set(experience.completion_policy.required_evidence_ids) != set(
        evidence_ids
    ) or len(experience.completion_policy.required_evidence_ids) != 3:
        raise ValueError(
            "Completion policy must require exactly direct construction evidence"
        )
    if experience.completion_policy.practiced_stage_ids != [
        stage.id for stage in experience.stages[:4]
    ]:
        raise ValueError(
            "Completion policy must preserve the complete practice sequence"
        )

    correction = experience.correction_policy
    if correction is None:
        raise ValueError("Direct construction lesson requires correction policy")
    if correction.max_guidance_items != 1:
        raise ValueError("Direct construction allows one guidance item")
    if correction.priorities != EXPECTED_CORRECTION_PRIORITIES:
        raise ValueError(
            "Direct construction correction priorities are out of order"
        )
