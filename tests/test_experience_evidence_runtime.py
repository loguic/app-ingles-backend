from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

import app.services.direct_english_construction_execution_service as direct_execution_service
from app.db.database import Base
from app.db.models import (
    ConversationAttempt,
    DirectEnglishConstructionAttempt,
    DirectEnglishConstructionAttemptProduction,
    ExperienceAttempt,
    ExperienceComprehensionResponse,
    ExperienceEvidenceState,
    ProductionEvaluationResult,
    ShortConnectedExchangeProductionReview,
    UserProgress,
)
from app.schemas.content import Lesson
from app.schemas.conversation_attempt import ConversationAttemptCreate
from app.schemas.conversation_production import ConversationProductionSubmission
from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptFinalize,
    DirectEnglishConstructionAttemptStart,
)
from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReviewBatch,
)
from app.services.content_service import get_lesson_context_by_id
from app.services.conversation_attempt_service import save_conversation_attempt
from app.services.conversation_production_persistence_service import (
    save_active_conversation_production_submission,
)
from app.services.direct_english_construction_execution_service import (
    finalize_direct_english_construction_attempt,
    start_direct_english_construction_attempt,
)
from app.services.direct_english_construction_content_validation import (
    validate_direct_english_construction_lesson,
)
from app.services.experience_attempt_service import (
    get_experience_attempt_state,
    save_experience_comprehension_response,
)
from app.services.experience_evidence_service import accredit_evidence_states
from app.services.production_audio_storage_service import store_production_audio
from app.services.short_connected_exchange_review_persistence_service import (
    save_short_connected_exchange_production_reviews,
)


NOW = datetime(2026, 8, 30, 10, 0, tzinfo=UTC)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def comprehension_lesson() -> Lesson:
    return Lesson.model_validate(
        {
            "id": "runtime-lesson",
            "title": "Runtime lesson",
            "conversations": [
                {
                    "id": "runtime-context",
                    "title": "Context",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "runtime-context-turn",
                            "speaker": "partner",
                            "en": "Hello from Madrid.",
                        }
                    ],
                },
                {
                    "id": "runtime-final",
                    "title": "Final",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "runtime-final-turn",
                            "speaker": "partner",
                            "en": "Goodbye.",
                        }
                    ],
                },
            ],
            "exercises": [
                {
                    "id": "runtime-question",
                    "type": "mcq",
                    "prompt": "Where is the speaker from?",
                    "options": ["Madrid", "London"],
                    "answer_index": 0,
                    "skill_ids": ["runtime-skill"],
                }
            ],
            "experience": {
                "contract_version": "2.0",
                "mission": {
                    "id": "runtime-mission",
                    "title": "Understand and close",
                    "situation": "Listen and finish.",
                    "observable_outcome": "Answer and complete.",
                    "success_criteria": ["Complete both sources."],
                },
                "skill_ids": ["runtime-skill"],
                "stages": [
                    {
                        "id": "runtime-stage-context",
                        "type": "comprehension",
                        "instruction": "Understand.",
                        "activity_ids": ["runtime-context"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "runtime-stage-final",
                        "type": "applied_conversation",
                        "instruction": "Complete.",
                        "activity_ids": ["runtime-final"],
                        "completion_condition": "evidence_recorded",
                    },
                ],
                "evidence_definitions": [
                    {
                        "id": "runtime-comprehension",
                        "skill_ids": ["runtime-skill"],
                        "stage_id": "runtime-stage-context",
                        "activity_id": "runtime-context",
                        "comprehension_exercise_id": "runtime-question",
                        "evidence_type": "comprehension_result",
                        "measurement_mode": "binary",
                    },
                    {
                        "id": "runtime-conversation",
                        "skill_ids": ["runtime-skill"],
                        "stage_id": "runtime-stage-final",
                        "activity_id": "runtime-final",
                        "evidence_type": "conversation_completion",
                        "measurement_mode": "completion",
                    },
                ],
                "completion_policy": {
                    "practiced_stage_ids": [
                        "runtime-stage-context",
                        "runtime-stage-final",
                    ],
                    "required_evidence_ids": [
                        "runtime-comprehension",
                        "runtime-conversation",
                    ],
                },
            },
        }
    )


def direct_english_v3_lesson() -> Lesson:
    """Future active content used only to exercise the closed v3 mapping."""

    def capture(group: str, function: str, support_level: str) -> dict:
        prompt = {
            "id": group + "-prompt-" + function,
            "accepted_modalities": ["voice", "text"],
            "required": True,
            "production_function": function,
            "primary_modality": "voice",
            "fallback_modalities": ["text"],
            "support_level": support_level,
            "allow_full_answer_model": False,
        }
        if function == "transfer":
            prompt["transfer_bank_id"] = group + "-transfer-bank"
            prompt["transfer_variants"] = [
                {"id": group + "-transfer-one", "prompt": "What is your name?"},
                {"id": group + "-transfer-two", "prompt": "Where are you from?"},
            ]
        return {
            "id": group + "-turn-" + function,
            "speaker": "learner",
            "en": "Produce the " + function + " response.",
            "production_prompt": prompt,
        }

    def direct_activity(group: str) -> dict:
        return {
            "id": group,
            "title": group,
            "mode": "guided",
            "turns": [
                capture(group, "guided", "anchors"),
                capture(group, "expanded", "initial_word"),
                capture(group, "transfer", "none"),
            ],
        }

    lesson = Lesson.model_validate(
        {
            "id": "direct-v3-lesson",
            "title": "Direct English v3 mapping",
            "conversations": [
                {
                    "id": "direct-v3-comprehension",
                    "title": "Listen",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "direct-v3-comprehension-turn",
                            "speaker": "partner",
                            "en": "Hello.",
                        }
                    ],
                },
                direct_activity("direct-v3-guided"),
                direct_activity("direct-v3-contextual"),
                {
                    "id": "direct-v3-conversation",
                    "title": "Complete the conversation",
                    "mode": "guided",
                    "turns": [
                        {
                            "id": "direct-v3-conversation-turn",
                            "speaker": "partner",
                            "en": "Nice to meet you.",
                        }
                    ],
                },
            ],
            "exercises": [
                {
                    "id": "direct-v3-question",
                    "type": "mcq",
                    "prompt": "Choose the greeting.",
                    "options": ["Hello", "Goodbye"],
                    "answer_index": 0,
                    "skill_ids": ["direct-v3-skill"],
                }
            ],
            "experience": {
                "contract_version": "3.0",
                "pedagogical_method": "direct_english_construction",
                "mission": {
                    "id": "direct-v3-mission",
                    "title": "Produce two complete direct-English attempts",
                    "situation": "Meet and respond.",
                    "observable_outcome": "Complete each three-capture attempt.",
                    "success_criteria": ["Complete the required evidence."],
                },
                "skill_ids": ["direct-v3-skill"],
                "stages": [
                    {
                        "id": "direct-v3-stage-comprehension",
                        "type": "comprehension",
                        "instruction": "Understand.",
                        "activity_ids": ["direct-v3-comprehension"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "direct-v3-stage-guided",
                        "type": "guided_production",
                        "instruction": "Introduce yourself.",
                        "activity_ids": ["direct-v3-guided"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "direct-v3-stage-contextual",
                        "type": "assisted_response",
                        "instruction": "Respond socially.",
                        "activity_ids": ["direct-v3-contextual"],
                        "completion_condition": "evidence_recorded",
                    },
                    {
                        "id": "direct-v3-stage-conversation",
                        "type": "applied_conversation",
                        "instruction": "Complete the conversation.",
                        "activity_ids": ["direct-v3-conversation"],
                        "completion_condition": "evidence_recorded",
                    },
                ],
                "evidence_definitions": [
                    {
                        "id": "direct-v3-comprehension-evidence",
                        "skill_ids": ["direct-v3-skill"],
                        "stage_id": "direct-v3-stage-comprehension",
                        "activity_id": "direct-v3-comprehension",
                        "comprehension_exercise_id": "direct-v3-question",
                        "evidence_type": "comprehension_result",
                        "measurement_mode": "binary",
                    },
                    {
                        "id": "direct-v3-guided-evidence",
                        "skill_ids": ["direct-v3-skill"],
                        "stage_id": "direct-v3-stage-guided",
                        "activity_id": "direct-v3-guided",
                        "evidence_type": "guided_production",
                        "measurement_mode": "completion",
                    },
                    {
                        "id": "direct-v3-contextual-evidence",
                        "skill_ids": ["direct-v3-skill"],
                        "stage_id": "direct-v3-stage-contextual",
                        "activity_id": "direct-v3-contextual",
                        "evidence_type": "contextual_response",
                        "measurement_mode": "completion",
                    },
                    {
                        "id": "direct-v3-conversation-evidence",
                        "skill_ids": ["direct-v3-skill"],
                        "stage_id": "direct-v3-stage-conversation",
                        "activity_id": "direct-v3-conversation",
                        "evidence_type": "conversation_completion",
                        "measurement_mode": "completion",
                    },
                ],
                "completion_policy": {
                    "practiced_stage_ids": [
                        "direct-v3-stage-comprehension",
                        "direct-v3-stage-guided",
                        "direct-v3-stage-contextual",
                        "direct-v3-stage-conversation",
                    ],
                    "required_evidence_ids": [
                        "direct-v3-comprehension-evidence",
                        "direct-v3-guided-evidence",
                        "direct-v3-contextual-evidence",
                        "direct-v3-conversation-evidence",
                    ],
                },
            },
        }
    )
    validate_direct_english_construction_lesson(lesson)
    return lesson


def add_attempt(
    db,
    *,
    attempt_id="experience-1",
    user_id="runtime-user",
    lesson_id="runtime-lesson",
    unit_id="runtime-unit",
):
    attempt = ExperienceAttempt(
        attempt_id=attempt_id,
        user_id=user_id,
        level_id="A1",
        unit_id=unit_id,
        lesson_id=lesson_id,
        experience_contract_version="2.0",
        status="in_progress",
        started_at=NOW,
        completed_at=None,
    )
    db.add(attempt)
    db.commit()
    return attempt


@pytest.fixture()
def synthetic_content(monkeypatch):
    lesson = comprehension_lesson()

    def lesson_context(lesson_id):
        if lesson_id == lesson.id:
            return "A1", "runtime-unit", lesson
        return None

    monkeypatch.setattr(
        "app.services.experience_evidence_service.get_lesson_context_by_id",
        lesson_context,
    )
    monkeypatch.setattr(
        "app.services.experience_attempt_service.get_lesson_context_by_id",
        lesson_context,
    )
    monkeypatch.setattr(
        "app.services.conversation_attempt_service."
        "get_conversation_context_by_id",
        lambda conversation_id: (
            "A1",
            "runtime-unit",
            lesson.id,
            next(
                item
                for item in lesson.conversations
                if item.id == conversation_id
            ),
        )
        if conversation_id in {item.id for item in lesson.conversations}
        else None,
    )
    return lesson


def evidence_statuses(db, attempt_id):
    return {
        item.evidence_definition_id: item.status
        for item in db.query(ExperienceEvidenceState).filter(
            ExperienceEvidenceState.experience_attempt_id == attempt_id
        )
    }


def test_comprehension_is_backend_graded_and_later_correct_supersedes_pending(
    db, synthetic_content
):
    attempt = add_attempt(db)
    db.add(
        UserProgress(
            user_id=attempt.user_id,
            level_id="A1",
            unit_id="runtime-unit",
            lesson_id=attempt.lesson_id,
            exercise_id="runtime-question",
            selected_index=0,
            correct=True,
        )
    )
    db.commit()

    incorrect = save_experience_comprehension_response(
        attempt.attempt_id, "runtime-question", 1, db
    )
    assert incorrect.is_correct is False
    assert evidence_statuses(db, attempt.attempt_id) == {
        "runtime-comprehension": "pending"
    }
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "in_progress"

    correct = save_experience_comprehension_response(
        attempt.attempt_id, "runtime-question", 0, db
    )
    assert correct.is_correct is True
    assert db.query(ExperienceComprehensionResponse).count() == 2
    assert evidence_statuses(db, attempt.attempt_id) == {
        "runtime-comprehension": "satisfied"
    }
    state = get_experience_attempt_state(attempt.attempt_id, db)
    assert state is not None
    assert [item.status for item in state.evidence_states] == [
        "satisfied",
        "pending",
    ]


def test_comprehension_contract_is_static_and_unambiguous():
    payload = comprehension_lesson().model_dump()
    definition = payload["experience"]["evidence_definitions"][0]
    definition.pop("comprehension_exercise_id")
    with pytest.raises(ValueError, match="requires comprehension_exercise_id"):
        Lesson.model_validate(payload)

    payload = comprehension_lesson().model_dump()
    payload["experience"]["evidence_definitions"][0][
        "measurement_mode"
    ] = "completion"
    with pytest.raises(ValueError, match="must use binary"):
        Lesson.model_validate(payload)

    payload = comprehension_lesson().model_dump()
    duplicate = dict(payload["experience"]["evidence_definitions"][0])
    duplicate["id"] = "runtime-comprehension-duplicate"
    payload["experience"]["evidence_definitions"].append(duplicate)
    payload["experience"]["completion_policy"][
        "required_evidence_ids"
    ].append(duplicate["id"])
    with pytest.raises(ValueError, match="exercise IDs must be unique"):
        Lesson.model_validate(payload)


def test_satisfied_is_monotonic_and_exact_retry_is_no_op(
    db, synthetic_content
):
    attempt = add_attempt(db)
    correct = save_experience_comprehension_response(
        attempt.attempt_id, "runtime-question", 0, db
    )
    state = db.get(
        ExperienceEvidenceState,
        (attempt.attempt_id, "runtime-comprehension"),
    )
    original_accredited_at = state.accredited_at
    original_source_id = state.comprehension_response_id

    incorrect = save_experience_comprehension_response(
        attempt.attempt_id, "runtime-question", 1, db
    )
    assert incorrect.is_correct is False
    state = db.get(
        ExperienceEvidenceState,
        (attempt.attempt_id, "runtime-comprehension"),
    )
    assert state.status == "satisfied"
    assert state.comprehension_response_id == original_source_id
    assert state.accredited_at == original_accredited_at

    definition = synthetic_content.experience.evidence_definitions[0]
    accredit_evidence_states(
        attempt,
        synthetic_content,
        [
            (
                definition,
                "satisfied",
                "comprehension_response",
                correct.response_id,
            )
        ],
        db,
        accredited_at=NOW + timedelta(hours=1),
    )
    db.commit()
    state = db.get(
        ExperienceEvidenceState,
        (attempt.attempt_id, "runtime-comprehension"),
    )
    assert state.accredited_at == original_accredited_at


def test_comprehension_source_state_and_completion_roll_back_together(
    db, synthetic_content, monkeypatch
):
    attempt = add_attempt(db)
    monkeypatch.setattr(
        "app.services.experience_attempt_service.accredit_evidence_states",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError("forced evidence failure")
        ),
    )
    with pytest.raises(RuntimeError, match="forced evidence failure"):
        save_experience_comprehension_response(
            attempt.attempt_id, "runtime-question", 0, db
        )
    assert db.query(ExperienceComprehensionResponse).count() == 0
    assert db.query(ExperienceEvidenceState).count() == 0
    persisted = db.get(ExperienceAttempt, attempt.attempt_id)
    assert persisted.status == "in_progress"
    assert persisted.completed_at is None


def test_completion_requires_all_same_attempt_evidence(db, synthetic_content):
    attempt = add_attempt(db)
    save_experience_comprehension_response(
        attempt.attempt_id, "runtime-question", 0, db
    )
    command = ConversationAttemptCreate(
        user_id=attempt.user_id,
        level_id="A1",
        unit_id="runtime-unit",
        lesson_id=attempt.lesson_id,
        conversation_id="runtime-final",
        mode="guided",
        visited_turn_ids=["runtime-final-turn"],
        experience_attempt_id=attempt.attempt_id,
    )
    save_conversation_attempt(command, db)
    completed = db.get(ExperienceAttempt, attempt.attempt_id)
    assert completed.status == "completed"
    assert completed.completed_at is not None
    assert set(evidence_statuses(db, attempt.attempt_id).values()) == {
        "satisfied"
    }
    with pytest.raises(ValueError, match="already completed"):
        save_experience_comprehension_response(
            attempt.attempt_id, "runtime-question", 0, db
        )


def test_invalid_comprehension_rolls_back_without_pending_state(
    db, synthetic_content
):
    attempt = add_attempt(db)
    with pytest.raises(ValueError, match="out of range"):
        save_experience_comprehension_response(
            attempt.attempt_id, "runtime-question", 3, db
        )
    with pytest.raises(ValueError, match="exactly one"):
        save_experience_comprehension_response(
            attempt.attempt_id, "unknown-question", 0, db
        )
    assert db.query(ExperienceComprehensionResponse).count() == 0
    assert db.query(ExperienceEvidenceState).count() == 0


def test_invalid_or_incompatible_source_does_not_create_pending_state(
    db, synthetic_content
):
    attempt = add_attempt(db)
    definition = synthetic_content.experience.evidence_definitions[0]
    with pytest.raises(ValueError, match="source does not exist"):
        accredit_evidence_states(
            attempt,
            synthetic_content,
            [
                (
                    definition,
                    "pending",
                    "comprehension_response",
                    "missing-response",
                )
            ],
            db,
        )
    with pytest.raises(ValueError, match="incompatible with source type"):
        accredit_evidence_states(
            attempt,
            synthetic_content,
            [(definition, "pending", "conversation_attempt", 999)],
            db,
        )
    db.rollback()
    assert db.query(ExperienceEvidenceState).count() == 0


def test_contract_version_mismatch_rejects_source_before_persistence(
    db, synthetic_content
):
    attempt = add_attempt(db)
    attempt.experience_contract_version = "stale-contract"
    db.commit()
    with pytest.raises(ValueError, match="hierarchy does not match"):
        save_experience_comprehension_response(
            attempt.attempt_id, "runtime-question", 0, db
        )
    assert db.query(ExperienceComprehensionResponse).count() == 0
    assert db.query(ExperienceEvidenceState).count() == 0


def test_wrong_user_bound_conversation_rolls_back(db, synthetic_content):
    attempt = add_attempt(db)
    command = ConversationAttemptCreate(
        user_id="other-user",
        level_id="A1",
        unit_id="runtime-unit",
        lesson_id=attempt.lesson_id,
        conversation_id="runtime-final",
        mode="guided",
        visited_turn_ids=["runtime-final-turn"],
        experience_attempt_id=attempt.attempt_id,
    )
    with pytest.raises(ValueError, match="user or hierarchy"):
        save_conversation_attempt(command, db)
    assert db.query(ConversationAttempt).count() == 0
    assert db.query(ExperienceEvidenceState).count() == 0


def test_legacy_unbound_conversation_remains_non_accrediting(
    db, synthetic_content
):
    command = ConversationAttemptCreate(
        user_id="legacy-user",
        level_id="A1",
        unit_id="runtime-unit",
        lesson_id="runtime-lesson",
        conversation_id="runtime-final",
        mode="guided",
        visited_turn_ids=["runtime-final-turn"],
    )
    result = save_conversation_attempt(command, db)
    assert result.experience_attempt_id is None
    assert db.query(ConversationAttempt).count() == 1
    assert db.query(ExperienceEvidenceState).count() == 0


def test_database_rejects_cross_attempt_typed_source(db, synthetic_content):
    first = add_attempt(db, attempt_id="experience-first")
    second = add_attempt(
        db,
        attempt_id="experience-second",
        user_id="runtime-user-second",
    )
    response = save_experience_comprehension_response(
        first.attempt_id, "runtime-question", 1, db
    )
    db.add(
        ExperienceEvidenceState(
            experience_attempt_id=second.attempt_id,
            evidence_definition_id="runtime-comprehension",
            evidence_type="comprehension_result",
            status="pending",
            source_type="comprehension_response",
            comprehension_response_id=response.response_id,
            accredited_at=NOW,
        )
    )
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def _active_attempt(db, lesson_id, user_id, attempt_id):
    context = get_lesson_context_by_id(lesson_id)
    assert context is not None
    level_id, unit_id, lesson = context
    attempt = ExperienceAttempt(
        attempt_id=attempt_id,
        user_id=user_id,
        level_id=level_id,
        unit_id=unit_id,
        lesson_id=lesson.id,
        experience_contract_version=lesson.experience.contract_version,
        status="in_progress",
        started_at=NOW,
        completed_at=None,
    )
    db.add(attempt)
    db.commit()
    return attempt, lesson


def _audio_references(tmp_path, count):
    return [
        store_production_audio(
            b"RIFF\x04\x00\x00\x00WAVE",
            storage_dir=tmp_path,
        ).audio_reference
        for _ in range(count)
    ]


def _v3_attempt(db, lesson: Lesson, attempt_id: str) -> ExperienceAttempt:
    attempt = ExperienceAttempt(
        attempt_id=attempt_id,
        user_id="direct-v3-user",
        level_id="A1",
        unit_id="direct-v3-unit",
        lesson_id=lesson.id,
        experience_contract_version="3.0",
        status="in_progress",
        started_at=NOW,
        completed_at=None,
    )
    db.add(attempt)
    db.commit()
    return attempt


def _bind_v3_direct_execution(monkeypatch, db, lesson: Lesson) -> None:
    monkeypatch.setattr(
        direct_execution_service,
        "_resolve_lesson",
        lambda _level_id, _unit_id, _lesson_id: lesson,
    )
    monkeypatch.setattr(
        direct_execution_service,
        "resolve_experience_attempt",
        lambda attempt_id, _db, **_kwargs: (
            db.get(ExperienceAttempt, attempt_id),
            lesson,
        ),
    )
    monkeypatch.setattr(
        "app.services.experience_attempt_service.get_lesson_context_by_id",
        lambda lesson_id: (
            ("A1", "direct-v3-unit", lesson)
            if lesson_id == lesson.id
            else None
        ),
    )
    monkeypatch.setattr(
        "app.services.experience_attempt_service."
        "get_lesson_context_by_id_and_contract_version",
        lambda lesson_id, contract_version: (
            ("A1", "direct-v3-unit", lesson)
            if lesson_id == lesson.id and contract_version == "3.0"
            else None
        ),
    )


def _v3_start_command(attempt: ExperienceAttempt, source_id: str):
    return DirectEnglishConstructionAttemptStart.model_validate(
        {
            "attempt_id": source_id,
            "user_id": attempt.user_id,
            "level_id": attempt.level_id,
            "unit_id": attempt.unit_id,
            "lesson_id": attempt.lesson_id,
            "experience_attempt_id": attempt.attempt_id,
            "started_at": NOW,
        }
    )


def _v3_finalize_command(
    attempt: ExperienceAttempt,
    source,
    lesson: Lesson,
    tmp_path,
    *,
    text_function: str | None = None,
):
    entries = direct_execution_service._execution_entries(
        lesson,
        source.evidence_definition_id,
    )
    audio_references = iter(
        _audio_references(
            tmp_path,
            2 if text_function is not None else 3,
        )
    )
    captures = []
    for function in ("guided", "expanded", "transfer"):
        conversation, turn, prompt, _evidence = entries[function]
        production = {
            "prompt_id": prompt.id,
            "turn_id": turn.id,
            "modality": "text" if function == text_function else "voice",
        }
        if function == text_function:
            production["response_text"] = "Text fallback."
        else:
            production["audio_reference"] = next(audio_references)
        capture = {
            "production_function": function,
            "submission": {
                "user_id": attempt.user_id,
                "level_id": attempt.level_id,
                "unit_id": attempt.unit_id,
                "lesson_id": attempt.lesson_id,
                "conversation_id": conversation.id,
                "productions": [production],
            },
            "support_used": prompt.support_level,
        }
        if function == "transfer":
            capture["transfer_variant_id"] = source.transfer_variant_id
        captures.append(capture)
    return DirectEnglishConstructionAttemptFinalize.model_validate(
        {
            "attempt_id": source.attempt_id,
            "captures": captures,
            "finalized_at": NOW + timedelta(minutes=5),
        }
    )


def test_v3_direct_english_uses_one_server_selected_evidence_per_attempt(
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    lesson = direct_english_v3_lesson()
    experience = _v3_attempt(db, lesson, "experience-direct-v3")
    _bind_v3_direct_execution(monkeypatch, db, lesson)

    first = start_direct_english_construction_attempt(
        _v3_start_command(experience, "direct-v3-guided-source"),
        db,
    )
    persisted_first = db.get(
        DirectEnglishConstructionAttempt,
        first.attempt_id,
    )
    assert persisted_first.evidence_definition_id == "direct-v3-guided-evidence"
    assert db.query(ExperienceEvidenceState).count() == 0

    finalize_direct_english_construction_attempt(
        _v3_finalize_command(experience, persisted_first, lesson, tmp_path),
        db,
    )
    first_links = db.query(DirectEnglishConstructionAttemptProduction).filter_by(
        attempt_id=first.attempt_id
    )
    assert {
        link.evidence_id for link in first_links
    } == {"direct-v3-guided-evidence"}
    assert evidence_statuses(db, experience.attempt_id) == {
        "direct-v3-guided-evidence": "satisfied"
    }

    authoritative = get_experience_attempt_state(experience.attempt_id, db)
    assert authoritative is not None
    assert [item.evidence_definition_id for item in authoritative.evidence_states] == [
        "direct-v3-comprehension-evidence",
        "direct-v3-guided-evidence",
        "direct-v3-contextual-evidence",
        "direct-v3-conversation-evidence",
    ]
    assert [item.status for item in authoritative.evidence_states] == [
        "pending",
        "satisfied",
        "pending",
        "pending",
    ]

    second = start_direct_english_construction_attempt(
        _v3_start_command(experience, "direct-v3-contextual-source"),
        db,
    )
    persisted_second = db.get(
        DirectEnglishConstructionAttempt,
        second.attempt_id,
    )
    assert persisted_second.evidence_definition_id == "direct-v3-contextual-evidence"
    finalize_direct_english_construction_attempt(
        _v3_finalize_command(experience, persisted_second, lesson, tmp_path),
        db,
    )

    assert evidence_statuses(db, experience.attempt_id) == {
        "direct-v3-guided-evidence": "satisfied",
        "direct-v3-contextual-evidence": "satisfied",
    }
    assert db.query(DirectEnglishConstructionAttempt).count() == 2
    assert db.get(ExperienceAttempt, experience.attempt_id).status == "in_progress"


def test_v3_text_fallback_does_not_accredit_or_unlock_next_direct_evidence(
    db,
    tmp_path,
    monkeypatch,
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    lesson = direct_english_v3_lesson()
    experience = _v3_attempt(db, lesson, "experience-direct-v3-pending")
    _bind_v3_direct_execution(monkeypatch, db, lesson)

    first = start_direct_english_construction_attempt(
        _v3_start_command(experience, "direct-v3-pending-source"),
        db,
    )
    persisted_first = db.get(
        DirectEnglishConstructionAttempt,
        first.attempt_id,
    )
    finalize_direct_english_construction_attempt(
        _v3_finalize_command(
            experience,
            persisted_first,
            lesson,
            tmp_path,
            text_function="expanded",
        ),
        db,
    )
    assert evidence_statuses(db, experience.attempt_id) == {
        "direct-v3-guided-evidence": "pending"
    }

    retry = start_direct_english_construction_attempt(
        _v3_start_command(experience, "direct-v3-pending-retry"),
        db,
    )
    assert db.get(
        DirectEnglishConstructionAttempt,
        retry.attempt_id,
    ).evidence_definition_id == "direct-v3-guided-evidence"


def test_bound_direct_english_finalization_satisfies_and_completes(
    db, tmp_path, monkeypatch
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    attempt, lesson = _active_attempt(
        db, "a1-u1-l1", "direct-user", "experience-direct"
    )
    started = start_direct_english_construction_attempt(
        DirectEnglishConstructionAttemptStart(
            attempt_id="direct-source",
            user_id=attempt.user_id,
            level_id=attempt.level_id,
            unit_id=attempt.unit_id,
            lesson_id=attempt.lesson_id,
            started_at=NOW,
            experience_attempt_id=attempt.attempt_id,
        ),
        db,
    )
    audios = iter(_audio_references(tmp_path, 3))
    captures = []
    for function in ("guided", "expanded", "transfer"):
        conversation = next(
            item
            for item in lesson.conversations
            if any(
                turn.production_prompt is not None
                and turn.production_prompt.production_function == function
                for turn in item.turns
            )
        )
        turn = next(
            item
            for item in conversation.turns
            if item.production_prompt is not None
        )
        prompt = turn.production_prompt
        capture = {
            "production_function": function,
            "submission": {
                "user_id": attempt.user_id,
                "level_id": attempt.level_id,
                "unit_id": attempt.unit_id,
                "lesson_id": attempt.lesson_id,
                "conversation_id": conversation.id,
                "productions": [
                    {
                        "prompt_id": prompt.id,
                        "turn_id": turn.id,
                        "modality": "voice",
                        "audio_reference": next(audios),
                    }
                ],
            },
            "support_used": prompt.support_level,
        }
        if function == "transfer":
            capture["transfer_variant_id"] = started.transfer_variant_id
        captures.append(capture)
    finalize_direct_english_construction_attempt(
        DirectEnglishConstructionAttemptFinalize.model_validate(
            {
                "attempt_id": started.attempt_id,
                "captures": captures,
                "finalized_at": NOW + timedelta(minutes=5),
            }
        ),
        db,
    )
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "completed"
    assert set(evidence_statuses(db, attempt.attempt_id).values()) == {
        "satisfied"
    }


def test_bound_direct_english_text_fallback_is_valid_but_pending(
    db, tmp_path, monkeypatch
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    attempt, lesson = _active_attempt(
        db, "a1-u1-l1", "direct-pending-user", "experience-direct-pending"
    )
    started = start_direct_english_construction_attempt(
        DirectEnglishConstructionAttemptStart(
            attempt_id="direct-pending-source",
            user_id=attempt.user_id,
            level_id=attempt.level_id,
            unit_id=attempt.unit_id,
            lesson_id=attempt.lesson_id,
            started_at=NOW,
            experience_attempt_id=attempt.attempt_id,
        ),
        db,
    )
    audios = iter(_audio_references(tmp_path, 2))
    captures = []
    for function in ("guided", "expanded", "transfer"):
        conversation = next(
            item
            for item in lesson.conversations
            if any(
                turn.production_prompt is not None
                and turn.production_prompt.production_function == function
                for turn in item.turns
            )
        )
        turn = next(
            item
            for item in conversation.turns
            if item.production_prompt is not None
        )
        prompt = turn.production_prompt
        production = {
            "prompt_id": prompt.id,
            "turn_id": turn.id,
            "modality": "text" if function == "expanded" else "voice",
        }
        if function == "expanded":
            production["response_text"] = "I introduce myself."
        else:
            production["audio_reference"] = next(audios)
        capture = {
            "production_function": function,
            "submission": {
                "user_id": attempt.user_id,
                "level_id": attempt.level_id,
                "unit_id": attempt.unit_id,
                "lesson_id": attempt.lesson_id,
                "conversation_id": conversation.id,
                "productions": [production],
            },
            "support_used": prompt.support_level,
        }
        if function == "transfer":
            capture["transfer_variant_id"] = started.transfer_variant_id
        captures.append(capture)
    finalize_direct_english_construction_attempt(
        DirectEnglishConstructionAttemptFinalize.model_validate(
            {
                "attempt_id": started.attempt_id,
                "captures": captures,
                "finalized_at": NOW + timedelta(minutes=5),
            }
        ),
        db,
    )
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "in_progress"
    assert list(evidence_statuses(db, attempt.attempt_id).values()).count(
        "pending"
    ) == 1
    assert list(evidence_statuses(db, attempt.attempt_id).values()).count(
        "satisfied"
    ) == 2
    expanded = (
        db.query(DirectEnglishConstructionAttemptProduction)
        .filter_by(
            attempt_id=started.attempt_id,
            production_function="expanded",
        )
        .one()
    )
    db.add(
        ProductionEvaluationResult(
            production_id=expanded.learner_production_id,
            criterion_id="technical-phonetic-score",
            status="passed",
            score=1.0,
            evaluator_id="technical-evaluator",
            evaluator_version="1.0",
            evaluated_at=NOW + timedelta(minutes=6),
        )
    )
    db.commit()
    authoritative = get_experience_attempt_state(attempt.attempt_id, db)
    assert authoritative is not None
    assert [item.status for item in authoritative.evidence_states].count(
        "pending"
    ) == 1
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "in_progress"


def test_bound_b181_reviews_transition_needs_review_to_satisfied(
    db, tmp_path, monkeypatch
):
    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(tmp_path))
    attempt, lesson = _active_attempt(
        db, "a1-u1-l2", "review-user", "experience-review"
    )
    conversation = lesson.conversations[0]
    audios = iter(_audio_references(tmp_path, 3))
    submission = ConversationProductionSubmission.model_validate(
        {
            "user_id": attempt.user_id,
            "level_id": attempt.level_id,
            "unit_id": attempt.unit_id,
            "lesson_id": attempt.lesson_id,
            "conversation_id": conversation.id,
            "experience_attempt_id": attempt.attempt_id,
            "productions": [
                {
                    "prompt_id": turn.production_prompt.id,
                    "turn_id": turn.id,
                    "modality": "voice",
                    "audio_reference": next(audios),
                }
                for turn in conversation.turns
                if turn.production_prompt is not None
            ],
        }
    )
    persisted = save_active_conversation_production_submission(submission, db)
    assert set(evidence_statuses(db, attempt.attempt_id).values()) == {
        "needs_review"
    }
    review_rows = []
    for production in persisted.productions:
        for index, dimension in enumerate(
            ("intention_understanding", "contingent_response")
        ):
            review_rows.append(
                {
                    "review_id": (
                        f"insufficient-{production.production_id}-{dimension}"
                    ),
                    "production_id": production.production_id,
                    "dimension": dimension,
                    "result": "negative" if index == 0 else "pending",
                    "source_type": "external",
                    "source_id": "authorized-review",
                    "source_version": "1.0",
                    "reviewed_at": NOW + timedelta(minutes=2),
                }
            )
    save_short_connected_exchange_production_reviews(
        ShortConnectedExchangeProductionReviewBatch.model_validate(
            {"reviews": review_rows}
        ),
        db,
    )
    assert db.query(ShortConnectedExchangeProductionReview).count() == 6
    assert set(evidence_statuses(db, attempt.attempt_id).values()) == {
        "needs_review"
    }
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "in_progress"

    newer_audios = iter(_audio_references(tmp_path, 3))
    newer_submission = ConversationProductionSubmission.model_validate(
        {
            "user_id": attempt.user_id,
            "level_id": attempt.level_id,
            "unit_id": attempt.unit_id,
            "lesson_id": attempt.lesson_id,
            "conversation_id": conversation.id,
            "experience_attempt_id": attempt.attempt_id,
            "productions": [
                {
                    "prompt_id": turn.production_prompt.id,
                    "turn_id": turn.id,
                    "modality": "voice",
                    "audio_reference": next(newer_audios),
                }
                for turn in conversation.turns
                if turn.production_prompt is not None
            ],
        }
    )
    newer_persisted = save_active_conversation_production_submission(
        newer_submission,
        db,
    )
    assert {
        state.conversation_production_submission_id
        for state in db.query(ExperienceEvidenceState).filter_by(
            experience_attempt_id=attempt.attempt_id
        )
    } == {newer_persisted.submission_id}

    positive_rows = []
    for production in newer_persisted.productions:
        for dimension in ("intention_understanding", "contingent_response"):
            positive_rows.append(
                {
                    "review_id": (
                        f"positive-{production.production_id}-{dimension}"
                    ),
                    "production_id": production.production_id,
                    "dimension": dimension,
                    "result": "positive",
                    "source_type": "external",
                    "source_id": "authorized-review",
                    "source_version": "1.0",
                    "reviewed_at": NOW + timedelta(minutes=3),
                }
            )
    save_short_connected_exchange_production_reviews(
        ShortConnectedExchangeProductionReviewBatch.model_validate(
            {"reviews": positive_rows}
        ),
        db,
    )
    assert db.query(ShortConnectedExchangeProductionReview).count() == 12
    assert set(evidence_statuses(db, attempt.attempt_id).values()) == {
        "satisfied"
    }
    assert db.get(ExperienceAttempt, attempt.attempt_id).status == "completed"
