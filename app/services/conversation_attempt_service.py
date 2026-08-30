from sqlalchemy.orm import Session

from app.db.models import ConversationAttempt
from app.schemas.content import Conversation
from app.schemas.conversation_attempt import ConversationAttemptCreate, ConversationAttemptRecord
from app.services.content_service import get_conversation_context_by_id
from app.services.experience_evidence_service import (
    accredit_evidence_states,
    required_evidence_definitions,
    resolve_experience_attempt,
    validate_attempt_source_context,
)


def validate_completed_conversation_attempt(
    record: ConversationAttemptCreate,
    conversation: Conversation,
) -> None:
    """Validate that an attempt represents one complete real route.
    Valida que un intento represente una ruta real y completada.
    """
    if record.mode != conversation.mode:
        raise ValueError("Attempt mode does not match the conversation mode")

    if conversation.mode == "guided":
        expected_turn_ids = [turn.id for turn in conversation.turns]

        if record.visited_turn_ids != expected_turn_ids:
            raise ValueError("Guided attempt must visit every turn in order")
        if record.selected_choice_ids:
            raise ValueError("Guided attempts cannot contain selected choices")
        return

    if conversation.mode != "branching":
        raise ValueError("Unsupported conversation mode")

    current_turn_id = conversation.start_turn_id
    expected_turn_ids: list[str] = []
    expected_choice_ids: list[str] = []
    selected_choice_index = 0

    while current_turn_id is not None:
        turn = next(
            (item for item in conversation.turns if item.id == current_turn_id),
            None,
        )
        if turn is None:
            raise ValueError("Conversation route references an unknown turn")

        expected_turn_ids.append(turn.id)

        if turn.choices:
            if selected_choice_index >= len(record.selected_choice_ids):
                raise ValueError("Branching attempt is missing a selected choice")

            selected_choice_id = record.selected_choice_ids[selected_choice_index]
            choice = next(
                (item for item in turn.choices if item.id == selected_choice_id),
                None,
            )
            if choice is None:
                raise ValueError("Selected choice does not belong to the active turn")

            expected_choice_ids.append(choice.id)
            selected_choice_index += 1
            current_turn_id = choice.next_turn_id
        else:
            current_turn_id = turn.next_turn_id

    if record.visited_turn_ids != expected_turn_ids:
        raise ValueError("Visited turns do not match the completed route")
    if record.selected_choice_ids != expected_choice_ids:
        raise ValueError("Selected choices do not match the completed route")


def save_conversation_attempt(
    record: ConversationAttemptCreate,
    db: Session,
) -> ConversationAttemptRecord:
    """Validate and save one completed conversation attempt.
    Valida y guarda un intento conversacional completado.
    """
    try:
        context = get_conversation_context_by_id(record.conversation_id)
        if context is None:
            raise ValueError("Conversation does not exist")

        level_id, unit_id, lesson_id, conversation = context
        if (
            record.level_id != level_id
            or record.unit_id != unit_id
            or record.lesson_id != lesson_id
        ):
            raise ValueError(
                "Conversation hierarchy does not match the content tree"
            )

        validate_completed_conversation_attempt(record, conversation)
        attempt = None
        lesson = None
        definitions = []
        if record.experience_attempt_id is not None:
            attempt, lesson = resolve_experience_attempt(
                record.experience_attempt_id,
                db,
                for_update=True,
                require_in_progress=True,
            )
            validate_attempt_source_context(
                attempt,
                user_id=record.user_id,
                level_id=record.level_id,
                unit_id=record.unit_id,
                lesson_id=record.lesson_id,
            )
            definitions = [
                definition
                for definition in required_evidence_definitions(lesson)
                if definition.evidence_type == "conversation_completion"
                and definition.activity_id == record.conversation_id
            ]
            if not definitions:
                raise ValueError(
                    "Conversation does not map to required completion evidence"
                )

        item = ConversationAttempt(
            user_id=record.user_id,
            level_id=record.level_id,
            unit_id=record.unit_id,
            lesson_id=record.lesson_id,
            conversation_id=record.conversation_id,
            mode=record.mode,
            visited_turn_ids=list(record.visited_turn_ids),
            selected_choice_ids=list(record.selected_choice_ids),
            experience_attempt_id=record.experience_attempt_id,
        )

        db.add(item)
        db.flush()
        if attempt is not None and lesson is not None:
            accredit_evidence_states(
                attempt,
                lesson,
                [
                    (
                        definition,
                        "satisfied",
                        "conversation_attempt",
                        item.id,
                    )
                    for definition in definitions
                ],
                db,
            )
        db.refresh(item)
        result = ConversationAttemptRecord(
            user_id=item.user_id,
            level_id=item.level_id,
            unit_id=item.unit_id,
            lesson_id=item.lesson_id,
            conversation_id=item.conversation_id,
            mode=item.mode,
            visited_turn_ids=item.visited_turn_ids,
            selected_choice_ids=item.selected_choice_ids,
            experience_attempt_id=item.experience_attempt_id,
            completed_at=item.completed_at,
        )
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def get_conversation_attempts_by_user(
    user_id: str,
    db: Session,
) -> list[ConversationAttemptRecord]:
    """Return saved conversation attempts for one user.
    Devuelve los intentos conversacionales guardados de un usuario.
    """
    items = (
        db.query(ConversationAttempt)
        .filter(ConversationAttempt.user_id == user_id)
        .order_by(
            ConversationAttempt.completed_at.asc(),
            ConversationAttempt.id.asc(),
        )
        .all()
    )

    return [
        ConversationAttemptRecord(
            user_id=item.user_id,
            level_id=item.level_id,
            unit_id=item.unit_id,
            lesson_id=item.lesson_id,
            conversation_id=item.conversation_id,
            mode=item.mode,
            visited_turn_ids=item.visited_turn_ids,
            selected_choice_ids=item.selected_choice_ids,
            experience_attempt_id=item.experience_attempt_id,
            completed_at=item.completed_at,
        )
        for item in items
    ]
