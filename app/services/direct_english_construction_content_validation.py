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
    direct_evidence_ids = {item.id for item in direct_evidence}
    for evidence in experience.evidence_definitions:
        qualitative_requirements = [
            requirement
            for requirement in evidence.external_review_requirements
            if requirement.production_function is not None
        ]
        if qualitative_requirements and evidence.id not in direct_evidence_ids:
            raise ValueError(
                "Direct construction v3 qualitative review requires direct "
                "production evidence"
            )
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
        for requirement in evidence.external_review_requirements:
            if (
                requirement.production_function is not None
                and requirement.production_function not in functions
            ):
                raise ValueError(
                    "Direct construction v3 qualitative review function "
                    "requires an available capture"
                )
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


def _validate_stage_bound_evidence_v1_lesson(lesson: Lesson) -> None:
    """Validate stage-bound oral evidence without changing historical v3.

    Valida evidencia oral por etapa sin alterar Direct English v3 historico.

    Content integrity only: guidance delivery and learner outcomes require
    independent runtime evidence. / Solo integridad de contenido.
    """
    experience = lesson.experience
    if experience is None:  # pragma: no cover - caller guards it.
        raise ValueError("Stage-bound profile requires an experience")

    expected_stages = [
        "comprehension", "language_support", "guided_production",
        "guided_production", "adaptive_feedback", "assisted_response",
        "evidence",
    ]
    stages = experience.stages
    if [stage.type for stage in stages] != expected_stages:
        raise ValueError("Stage-bound profile requires seven ordered stages")
    if any(stage.mode != "required" for stage in stages):
        raise ValueError("Stage-bound profile requires mandatory stages")
    if [stage.completion_condition for stage in stages] != [
        "all_activities_completed", "acknowledged", "any_activity_completed",
        "evidence_recorded", "acknowledged", "evidence_recorded",
        "evidence_recorded",
    ]:
        raise ValueError("Stage-bound profile has incompatible stage gates")
    if experience.completion_policy.practiced_stage_ids != [stage.id for stage in stages]:
        raise ValueError("Stage-bound profile must preserve the stage sequence")
    if not experience.completion_policy.allow_retry:
        raise ValueError("Stage-bound profile must permit retries")

    correction = experience.correction_policy
    if (correction is None or correction.max_guidance_items != 1
            or correction.priorities != EXPECTED_CORRECTION_PRIORITIES):
        raise ValueError("Stage-bound profile requires bounded guidance policy")

    definitions = experience.evidence_definitions
    required_ids = experience.completion_policy.required_evidence_ids
    if (len(definitions) != 4 or len(required_ids) != 4
            or [item.id for item in definitions] != required_ids
            or not all(item.required for item in definitions)):
        raise ValueError("Stage-bound profile requires four ordered mandatory evidence")
    if [item.evidence_type for item in definitions] != [
        "comprehension_result", "guided_production",
        "guided_production", "contextual_response",
    ]:
        raise ValueError("Stage-bound profile has incompatible evidence types")
    if [item.stage_id for item in definitions] != [
        stages[0].id, stages[3].id, stages[5].id, stages[6].id,
    ]:
        raise ValueError("Stage-bound evidence must bind to exact stages")

    conversations = {c.id: c for c in lesson.conversations}
    exercises = {e.id for e in lesson.exercises}
    comprehension = definitions[0]
    if (comprehension.activity_id not in stages[0].activity_ids
            or comprehension.activity_id not in conversations
            or comprehension.comprehension_exercise_id not in stages[0].activity_ids
            or comprehension.comprehension_exercise_id not in exercises
            or comprehension.external_review_requirements):
        raise ValueError("Stage-bound comprehension must bind to question and scene")

    practice_activities = stages[2].activity_ids
    if len(practice_activities) != 1 or practice_activities[0] not in conversations:
        raise ValueError("Stage-bound profile requires one preparatory conversation")
    practice = conversations[practice_activities[0]]
    practice_prompts = [t.production_prompt for t in practice.turns
                        if t.production_prompt is not None
                        and t.production_prompt.production_function is not None]
    if len(practice_prompts) != 1:
        raise ValueError("Stage-bound profile requires one preparatory capture")
    scaffold = practice_prompts[0]
    _require_complete_prompt(scaffold)
    if (scaffold.production_function != "guided" or not scaffold.required
            or scaffold.support_level != "anchors"
            or scaffold.primary_modality != "voice"
            or set(scaffold.accepted_modalities) != {"voice", "text"}
            or scaffold.fallback_modalities != ["text"]
            or scaffold.allow_full_answer_model is not False
            or len(scaffold.visible_support) < 2):
        raise ValueError("Stage-bound preparatory production must remain scaffolded")

    direct_ids: set[str] = set()
    capture_ids: set[str] = {practice.id}
    prompt_ids: set[str] = {scaffold.id}
    initial_context = None
    expected_functions = ("guided", "expanded", "transfer")
    for index, function in enumerate(expected_functions, start=1):
        evidence = definitions[index]
        stage = stages[[3, 5, 6][index - 1]]
        if stage.activity_ids != [evidence.activity_id]:
            raise ValueError("Stage-bound direct evidence must own its stage activity")
        conversation = conversations.get(evidence.activity_id)
        if conversation is None or conversation.id in capture_ids:
            raise ValueError("Stage-bound direct evidence requires distinct conversation")
        capture_ids.add(conversation.id)
        direct_ids.add(conversation.id)
        entries = [t.production_prompt for t in conversation.turns
                   if t.production_prompt is not None
                   and t.production_prompt.production_function is not None]
        if len(entries) != 1:
            raise ValueError("Stage-bound direct evidence requires one oral capture")
        prompt = entries[0]
        _require_complete_prompt(prompt)
        if (prompt.id in prompt_ids or evidence.production_prompt_id != prompt.id
                or prompt.production_function != function or not prompt.required):
            raise ValueError("Stage-bound evidence requires exact prompt and function")
        prompt_ids.add(prompt.id)
        if (prompt.primary_modality != "voice"
                or prompt.accepted_modalities != ["voice"]
                or prompt.fallback_modalities
                or prompt.allow_full_answer_model is not False):
            raise ValueError("Stage-bound oral evidence forbids text accreditation")
        requirements = evidence.external_review_requirements
        if (len(requirements) != 2
                or {r.dimension for r in requirements} != {"relevance", "intelligibility"}
                or any(r.production_function != function for r in requirements)):
            raise ValueError("Stage-bound evidence requires qualitative review")
        if function == "guided":
            if (prompt.support_level != "initial_word"
                    or len(prompt.visible_support) != 1
                    or len(prompt.visible_support[0].split()) != 1):
                raise ValueError("Stage-bound initial oral request permits one word")
            initial_context = conversation.context
        elif prompt.support_level != "none" or prompt.visible_support:
            raise ValueError("Stage-bound retry and transfer must have no answer cues")
        if function == "transfer":
            if not prompt.transfer_bank_id or not prompt.transfer_variants:
                raise ValueError("Stage-bound transfer requires a prompt bank")
            if conversation.context.strip().casefold() == (initial_context or "").strip().casefold():
                raise ValueError("Stage-bound transfer context must differ")
        elif prompt.transfer_bank_id is not None or prompt.transfer_variants:
            raise ValueError("Only stage-bound transfer may use a prompt bank")

    # Exactly the four declared production captures; no hidden or extraneous
    # capture may enter the execution graph. / Sin capturas extra ocultas.
    all_captures = [
        (c.id, p.id)
        for c in lesson.conversations
        for turn in c.turns
        if (p := turn.production_prompt) is not None
        and p.production_function is not None
    ]
    if (len(all_captures) != 4 or {c for c, _ in all_captures} != capture_ids
            or {p for _, p in all_captures} != prompt_ids):
        raise ValueError("Stage-bound profile has unbound production captures")
    if stages[4].activity_ids:
        raise ValueError("Stage-bound guidance must be a separately recorded event")


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

    if experience.direct_english_execution_profile == "stage_bound_evidence_v1":
        _validate_stage_bound_evidence_v1_lesson(lesson)
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
