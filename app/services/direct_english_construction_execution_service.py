"""Persist deterministic direct-English construction executions.

Persiste ejecuciones deterministas de construcción directa en inglés.
"""

from datetime import UTC, datetime
import hashlib

from sqlalchemy import case
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    DirectEnglishConstructionAttempt as AttemptModel,
    DirectEnglishConstructionAttemptProduction as AttemptProductionModel,
    DirectEnglishConstructionProductionOrientation as OrientationModel,
    LearnerProduction as ProductionModel,
)
from app.schemas.content import Lesson, TransferPromptVariant
from app.schemas.direct_english_construction_execution import (
    DirectEnglishConstructionAttemptFinalize,
    DirectEnglishConstructionAttemptProductionRecord,
    DirectEnglishConstructionAttemptRecord,
    DirectEnglishConstructionAttemptStart,
    DirectEnglishConstructionOrientationCreate,
    DirectEnglishConstructionOrientationRecord,
    DirectEnglishConstructionRetryPreparation,
    DirectEnglishConstructionRetryPreparationRequest,
)
from app.services.content_service import build_content_tree
from app.services.conversation_production_persistence_service import (
    _add_validated_conversation_production_submission,
)
from app.services.conversation_production_validation import (
    validate_conversation_production_submission,
)
from app.services.direct_english_construction_content_validation import (
    validate_direct_english_construction_lesson,
)
from app.services.experience_evidence_service import (
    accredit_evidence_states,
    resolve_experience_attempt,
    validate_attempt_source_context,
)
from app.services.production_audio_storage_service import (
    resolve_production_audio_path,
)


SELECTOR_VERSION = "sha256-v1"
FUNCTION_ORDER = {"guided": 0, "expanded": 1, "transfer": 2}
SUPPORT_RANK = {"none": 0, "initial_word": 1, "anchors": 2, "model": 3}


class DirectEnglishConstructionExecutionError(Exception):
    """Base error for direct-English execution persistence."""


class DirectEnglishConstructionAttemptAlreadyExistsError(
    DirectEnglishConstructionExecutionError
):
    """Raised when an attempt identity already exists."""


class DirectEnglishConstructionReferenceNotFoundError(
    DirectEnglishConstructionExecutionError
):
    """Raised when required content or persistence is absent."""


class DirectEnglishConstructionInvariantError(
    DirectEnglishConstructionExecutionError
):
    """Raised when execution evidence contradicts its content."""


class DirectEnglishConstructionStateConflictError(
    DirectEnglishConstructionExecutionError
):
    """Raised when persisted attempt state changed concurrently."""


def _resolve_lesson(
    level_id: str,
    unit_id: str,
    lesson_id: str,
) -> Lesson:
    tree = build_content_tree()
    for level in tree.levels:
        if level.code != level_id:
            continue
        for unit in level.units:
            if unit.id != unit_id:
                continue
            for lesson in unit.lessons:
                if lesson.id == lesson_id:
                    try:
                        validate_direct_english_construction_lesson(lesson)
                    except ValueError as exc:
                        raise DirectEnglishConstructionInvariantError(
                            "Direct-English lesson content is invalid"
                        ) from exc
                    if (
                        lesson.experience is None
                        or lesson.experience.pedagogical_method
                        != "direct_english_construction"
                    ):
                        raise DirectEnglishConstructionInvariantError(
                            "Lesson is not a direct-English construction experience"
                        )
                    return lesson
    raise DirectEnglishConstructionReferenceNotFoundError(
        "Direct-English lesson hierarchy does not exist"
    )


def _transfer_prompt(lesson: Lesson):
    for conversation in lesson.conversations:
        for turn in conversation.turns:
            prompt = turn.production_prompt
            if prompt is not None and prompt.production_function == "transfer":
                return prompt
    raise DirectEnglishConstructionInvariantError(
        "Direct-English lesson has no transfer prompt"
    )


def select_direct_english_transfer_variant(
    lesson: Lesson,
    attempt_id: str,
) -> tuple[str, TransferPromptVariant]:
    """Select one transfer variant without random or global state.

    Selecciona una variante sin aleatoriedad ni estado global.
    """
    prompt = _transfer_prompt(lesson)
    if prompt.transfer_bank_id is None or not prompt.transfer_variants:
        raise DirectEnglishConstructionInvariantError(
            "Transfer prompt bank is unavailable"
        )
    variants = sorted(prompt.transfer_variants, key=lambda item: item.id)
    canonical_input = "\x1f".join(
        (
            SELECTOR_VERSION,
            attempt_id,
            lesson.id,
            prompt.transfer_bank_id,
        )
    ).encode("utf-8")
    index = int.from_bytes(
        hashlib.sha256(canonical_input).digest(),
        byteorder="big",
    ) % len(variants)
    return prompt.transfer_bank_id, variants[index]


def _execution_entries(lesson: Lesson) -> dict[str, tuple]:
    if lesson.experience is None:
        raise DirectEnglishConstructionInvariantError(
            "Direct-English lesson has no experience"
        )
    evidence_by_activity = {
        item.activity_id: item
        for item in lesson.experience.evidence_definitions
    }
    entries: dict[str, tuple] = {}
    for conversation in lesson.conversations:
        for turn in conversation.turns:
            prompt = turn.production_prompt
            if prompt is None or prompt.production_function is None:
                continue
            evidence = evidence_by_activity.get(conversation.id)
            if evidence is None:
                raise DirectEnglishConstructionInvariantError(
                    "Production conversation has no evidence definition"
                )
            entries[prompt.production_function] = (
                conversation,
                turn,
                prompt,
                evidence,
            )
    return entries


def _normalize_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _completion_requirements_met(
    status: str,
    records: list[DirectEnglishConstructionAttemptProductionRecord],
) -> bool:
    if status != "finalized" or len(records) != 3:
        return False
    if {item.production_function for item in records} != set(FUNCTION_ORDER):
        return False
    for item in records:
        if item.modality_used != "voice":
            return False
        if (
            SUPPORT_RANK[item.support_used]
            > SUPPORT_RANK[item.configured_support_level]
        ):
            return False
        if item.production_function == "transfer" and item.support_used != "none":
            return False
    return True


def _orientation_record(
    orientation: OrientationModel | None,
) -> DirectEnglishConstructionOrientationRecord | None:
    if orientation is None:
        return None
    return DirectEnglishConstructionOrientationRecord(
        orientation_id=orientation.orientation_id,
        priority=orientation.priority,
        guidance_text=orientation.guidance_text,
        source_type=orientation.source_type,
        source_id=orientation.source_id,
        source_version=orientation.source_version,
        created_at=orientation.created_at,
    )


def _next_retry_support_level(
    configured_support_level: str,
    support_used: str,
    production_function: str,
) -> str:
    """Withdraw support without interpreting learner performance.

    Retira apoyo sin interpretar el rendimiento del estudiante.
    """
    if production_function == "transfer":
        return "none"
    reduced_rank = max(SUPPORT_RANK[support_used] - 1, SUPPORT_RANK["none"])
    next_rank = min(reduced_rank, SUPPORT_RANK[configured_support_level])
    return next(
        level for level, rank in SUPPORT_RANK.items() if rank == next_rank
    )


def prepare_direct_english_construction_retry(
    request: DirectEnglishConstructionRetryPreparationRequest,
    db: Session,
) -> DirectEnglishConstructionRetryPreparation:
    """Prepare one focused retry without writing or selecting a variant.

    Prepara un reintento focal sin escribir ni seleccionar una variante.
    """
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.attempt_id == request.previous_attempt_id)
        .one_or_none()
    )
    if attempt is None:
        raise DirectEnglishConstructionReferenceNotFoundError(
            "Previous direct-English construction attempt does not exist"
        )
    if attempt.status != "finalized":
        raise DirectEnglishConstructionStateConflictError(
            "Previous direct-English construction attempt is not finalized"
        )
    row = (
        db.query(
            AttemptProductionModel,
            ProductionModel,
            SubmissionModel,
            OrientationModel,
        )
        .join(
            ProductionModel,
            ProductionModel.id
            == AttemptProductionModel.learner_production_id,
        )
        .join(
            SubmissionModel,
            SubmissionModel.id == ProductionModel.submission_id,
        )
        .outerjoin(
            OrientationModel,
            OrientationModel.attempt_production_id
            == AttemptProductionModel.id,
        )
        .filter(
            AttemptProductionModel.attempt_id == request.previous_attempt_id,
            AttemptProductionModel.production_function
            == request.production_function,
        )
        .one_or_none()
    )
    if row is None:
        raise DirectEnglishConstructionReferenceNotFoundError(
            "Previous direct-English attempt production does not exist"
        )
    link, production, submission, orientation = row
    orientation_record = _orientation_record(orientation)
    if orientation_record is None:
        raise DirectEnglishConstructionReferenceNotFoundError(
            "Previous direct-English production has no orientation"
        )
    lesson = _resolve_lesson(
        attempt.level_id,
        attempt.unit_id,
        attempt.lesson_id,
    )
    entry = _execution_entries(lesson).get(request.production_function)
    if entry is None:
        raise DirectEnglishConstructionInvariantError(
            "Active content has no retry production function"
        )
    conversation, _turn, prompt, _evidence = entry
    if (
        submission.conversation_id != conversation.id
        or production.prompt_id != prompt.id
    ):
        raise DirectEnglishConstructionInvariantError(
            "Previous production contradicts active retry content"
        )
    is_transfer = request.production_function == "transfer"
    return DirectEnglishConstructionRetryPreparation(
        previous_attempt_id=attempt.attempt_id,
        production_function=request.production_function,
        orientation=orientation_record,
        conversation_id=conversation.id,
        prompt_id=prompt.id,
        previous_configured_support_level=link.configured_support_level,
        previous_support_used=link.support_used,
        next_support_level=_next_retry_support_level(
            link.configured_support_level,
            link.support_used,
            link.production_function,
        ),
        transfer_bank_id=attempt.transfer_bank_id if is_transfer else None,
        previous_transfer_variant_id=(
            attempt.transfer_variant_id if is_transfer else None
        ),
        previous_transfer_prompt_snapshot=(
            attempt.transfer_prompt_snapshot if is_transfer else None
        ),
        transfer_selection_policy=(
            "new_attempt_selector" if is_transfer else None
        ),
        requires_new_attempt_id=True,
    )


def get_direct_english_construction_attempt(
    attempt_id: str,
    db: Session,
) -> DirectEnglishConstructionAttemptRecord:
    """Recover one attempt explicitly without committing or lazy loading.

    Recupera un intento explícitamente sin commit ni lazy loading.
    """
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.attempt_id == attempt_id)
        .one_or_none()
    )
    if attempt is None:
        raise DirectEnglishConstructionReferenceNotFoundError(
            "Direct-English construction attempt does not exist"
        )

    rows = (
        db.query(AttemptProductionModel, ProductionModel, OrientationModel)
        .join(
            ProductionModel,
            ProductionModel.id
            == AttemptProductionModel.learner_production_id,
        )
        .outerjoin(
            OrientationModel,
            OrientationModel.attempt_production_id
            == AttemptProductionModel.id,
        )
        .filter(AttemptProductionModel.attempt_id == attempt_id)
        .order_by(
            case(
                FUNCTION_ORDER,
                value=AttemptProductionModel.production_function,
            )
        )
        .all()
    )
    productions = [
        DirectEnglishConstructionAttemptProductionRecord(
            production_function=link.production_function,
            evidence_id=link.evidence_id,
            production_id=production.id,
            prompt_id=production.prompt_id,
            modality_used=production.modality,
            configured_support_level=link.configured_support_level,
            support_used=link.support_used,
            orientation=_orientation_record(orientation),
        )
        for link, production, orientation in rows
    ]
    return DirectEnglishConstructionAttemptRecord(
        attempt_id=attempt.attempt_id,
        user_id=attempt.user_id,
        level_id=attempt.level_id,
        unit_id=attempt.unit_id,
        lesson_id=attempt.lesson_id,
        status=attempt.status,
        transfer_bank_id=attempt.transfer_bank_id,
        transfer_variant_id=attempt.transfer_variant_id,
        transfer_prompt_snapshot=attempt.transfer_prompt_snapshot,
        selector_version=attempt.selector_version,
        started_at=attempt.started_at,
        finalized_at=attempt.finalized_at,
        experience_attempt_id=attempt.experience_attempt_id,
        productions=productions,
        completion_requirements_met=_completion_requirements_met(
            attempt.status,
            productions,
        ),
    )


def start_direct_english_construction_attempt(
    command: DirectEnglishConstructionAttemptStart,
    db: Session,
) -> DirectEnglishConstructionAttemptRecord:
    """Select and persist one immutable transfer variant.

    Selecciona y persiste una variante de transferencia inmutable.
    """
    lesson = _resolve_lesson(
        command.level_id,
        command.unit_id,
        command.lesson_id,
    )
    try:
        if command.experience_attempt_id is not None:
            experience_attempt, experience_lesson = resolve_experience_attempt(
                command.experience_attempt_id,
                db,
                for_update=True,
                require_in_progress=True,
            )
            validate_attempt_source_context(
                experience_attempt,
                user_id=command.user_id,
                level_id=command.level_id,
                unit_id=command.unit_id,
                lesson_id=command.lesson_id,
            )
            if experience_lesson.id != lesson.id:
                raise DirectEnglishConstructionInvariantError(
                    "Direct-English source does not belong to experience"
                )
        if (
            db.query(AttemptModel.attempt_id)
            .filter(AttemptModel.attempt_id == command.attempt_id)
            .first()
            is not None
        ):
            raise DirectEnglishConstructionAttemptAlreadyExistsError(
                "Direct-English construction attempt already exists"
            )
        bank_id, variant = select_direct_english_transfer_variant(
            lesson,
            command.attempt_id,
        )
        attempt = AttemptModel(
            attempt_id=command.attempt_id,
            user_id=command.user_id,
            level_id=command.level_id,
            unit_id=command.unit_id,
            lesson_id=command.lesson_id,
            experience_attempt_id=command.experience_attempt_id,
            transfer_bank_id=bank_id,
            transfer_variant_id=variant.id,
            transfer_prompt_snapshot=variant.prompt,
            selector_version=SELECTOR_VERSION,
            status="started",
            started_at=command.started_at,
            finalized_at=None,
        )
        db.add(attempt)
        db.flush()
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DirectEnglishConstructionAttemptAlreadyExistsError(
            "Direct-English construction attempt already exists"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DirectEnglishConstructionExecutionError(
            "Could not start direct-English construction attempt"
        ) from exc
    except Exception:
        db.rollback()
        raise
    return get_direct_english_construction_attempt(command.attempt_id, db)


def save_direct_english_construction_orientation(
    command: DirectEnglishConstructionOrientationCreate,
    db: Session,
) -> DirectEnglishConstructionOrientationRecord:
    """Persist one externally selected orientation without overwriting.

    Persiste una orientación seleccionada externamente sin sobrescribir.
    """
    try:
        attempt = (
            db.query(AttemptModel)
            .filter(AttemptModel.attempt_id == command.attempt_id)
            .one_or_none()
        )
        if attempt is None:
            raise DirectEnglishConstructionReferenceNotFoundError(
                "Direct-English construction attempt does not exist"
            )
        if attempt.status != "finalized":
            raise DirectEnglishConstructionStateConflictError(
                "Direct-English construction attempt is not finalized"
            )
        link = (
            db.query(AttemptProductionModel)
            .filter(
                AttemptProductionModel.attempt_id == command.attempt_id,
                AttemptProductionModel.production_function
                == command.production_function,
            )
            .one_or_none()
        )
        if link is None:
            raise DirectEnglishConstructionReferenceNotFoundError(
                "Direct-English attempt production does not exist"
            )
        lesson = _resolve_lesson(
            attempt.level_id,
            attempt.unit_id,
            attempt.lesson_id,
        )
        correction_policy = (
            lesson.experience.correction_policy
            if lesson.experience is not None
            else None
        )
        if (
            correction_policy is None
            or command.priority not in correction_policy.priorities
        ):
            raise DirectEnglishConstructionInvariantError(
                "Orientation priority is not permitted by active content"
            )
        if (
            db.query(OrientationModel.orientation_id)
            .filter(
                (OrientationModel.orientation_id == command.orientation_id)
                | (OrientationModel.attempt_production_id == link.id)
            )
            .first()
            is not None
        ):
            raise DirectEnglishConstructionInvariantError(
                "Direct-English production already has an orientation"
            )
        orientation = OrientationModel(
            orientation_id=command.orientation_id,
            attempt_production_id=link.id,
            priority=command.priority,
            guidance_text=command.guidance_text,
            source_type=command.source_type,
            source_id=command.source_id,
            source_version=command.source_version,
            created_at=command.created_at,
        )
        db.add(orientation)
        db.flush()
        db.commit()
        record = _orientation_record(orientation)
        if record is None:  # pragma: no cover - construction guarantees it.
            raise DirectEnglishConstructionExecutionError(
                "Could not reconstruct direct-English orientation"
            )
        return record
    except DirectEnglishConstructionExecutionError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise DirectEnglishConstructionInvariantError(
            "Direct-English production already has an orientation"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DirectEnglishConstructionExecutionError(
            "Could not save direct-English construction orientation"
        ) from exc
    except Exception:
        db.rollback()
        raise


def _finalize_direct_english_construction_attempt(
    command: DirectEnglishConstructionAttemptFinalize,
    db: Session,
) -> DirectEnglishConstructionAttemptRecord:
    """Persist three productions and finalize their attempt atomically.

    Persiste tres producciones y finaliza su intento atómicamente.
    """
    attempt = (
        db.query(AttemptModel)
        .filter(AttemptModel.attempt_id == command.attempt_id)
        .with_for_update()
        .one_or_none()
    )
    if attempt is None:
        raise DirectEnglishConstructionReferenceNotFoundError(
            "Direct-English construction attempt does not exist"
        )
    if attempt.status != "started":
        raise DirectEnglishConstructionStateConflictError(
            "Direct-English construction attempt is not started"
        )
    if _normalize_timestamp(command.finalized_at) < _normalize_timestamp(
        attempt.started_at
    ):
        raise DirectEnglishConstructionInvariantError(
            "finalized_at cannot precede started_at"
        )

    lesson = _resolve_lesson(
        attempt.level_id,
        attempt.unit_id,
        attempt.lesson_id,
    )
    experience_attempt = None
    experience_lesson = None
    if attempt.experience_attempt_id is not None:
        experience_attempt, experience_lesson = resolve_experience_attempt(
            attempt.experience_attempt_id,
            db,
            for_update=True,
            require_in_progress=True,
        )
        validate_attempt_source_context(
            experience_attempt,
            user_id=attempt.user_id,
            level_id=attempt.level_id,
            unit_id=attempt.unit_id,
            lesson_id=attempt.lesson_id,
        )
        if experience_lesson.id != lesson.id:
            raise DirectEnglishConstructionInvariantError(
                "Direct-English source does not belong to experience"
            )
    entries = _execution_entries(lesson)
    captures = {
        item.production_function: item for item in command.captures
    }
    ordered_functions = ("guided", "expanded", "transfer")

    # Validate the complete aggregate before adding any row.
    # Valida el agregado completo antes de añadir ninguna fila.
    for function in ordered_functions:
        capture = captures[function]
        conversation, turn, prompt, _evidence = entries[function]
        submission = capture.submission
        if submission.experience_attempt_id not in (
            None,
            attempt.experience_attempt_id,
        ):
            raise DirectEnglishConstructionInvariantError(
                "Production submission experience binding is incompatible"
            )
        if (
            submission.user_id != attempt.user_id
            or submission.level_id != attempt.level_id
            or submission.unit_id != attempt.unit_id
            or submission.lesson_id != attempt.lesson_id
        ):
            raise DirectEnglishConstructionInvariantError(
                "Production submission hierarchy or user is incompatible"
            )
        if submission.conversation_id != conversation.id:
            raise DirectEnglishConstructionInvariantError(
                "Production conversation is incompatible with its function"
            )
        if len(submission.productions) != 1:
            raise DirectEnglishConstructionInvariantError(
                "Each direct-English function requires one production"
            )
        captured = submission.productions[0]
        if captured.prompt_id != prompt.id or captured.turn_id != turn.id:
            raise DirectEnglishConstructionInvariantError(
                "Production prompt or turn is incompatible with its function"
            )
        if function == "transfer" and (
            capture.transfer_variant_id != attempt.transfer_variant_id
        ):
            raise DirectEnglishConstructionInvariantError(
                "Transfer capture does not use the selected variant"
            )
        try:
            validate_conversation_production_submission(
                submission,
                conversation,
            )
        except ValueError as exc:
            raise DirectEnglishConstructionInvariantError(
                "Production submission contradicts active content"
            ) from exc
        captured = submission.productions[0]
        if attempt.experience_attempt_id is not None and captured.modality == "voice":
            try:
                resolve_production_audio_path(captured.audio_reference or "")
            except (RuntimeError, ValueError, FileNotFoundError) as exc:
                raise DirectEnglishConstructionInvariantError(
                    "Direct-English voice production audio is unavailable"
                ) from exc

    try:
        for function in ordered_functions:
            capture = captures[function]
            conversation, _turn, prompt, evidence = entries[function]
            _submission, productions = (
                _add_validated_conversation_production_submission(
                    capture.submission,
                    conversation,
                    db,
                    experience_attempt_id=attempt.experience_attempt_id,
                )
            )
            db.add(
                AttemptProductionModel(
                    attempt_id=attempt.attempt_id,
                    learner_production_id=productions[0].id,
                    production_function=function,
                    evidence_id=evidence.id,
                    configured_support_level=prompt.support_level,
                    support_used=capture.support_used,
                )
            )
        db.flush()
        rowcount = (
            db.query(AttemptModel)
            .filter(
                AttemptModel.attempt_id == attempt.attempt_id,
                AttemptModel.status == "started",
            )
            .update(
                {
                    AttemptModel.status: "finalized",
                    AttemptModel.finalized_at: command.finalized_at,
                },
                synchronize_session=False,
            )
        )
        if rowcount != 1:
            raise DirectEnglishConstructionStateConflictError(
                "Direct-English construction attempt changed concurrently"
            )
        attempt.status = "finalized"
        attempt.finalized_at = command.finalized_at
        db.flush()
        if experience_attempt is not None and experience_lesson is not None:
            accredit_evidence_states(
                experience_attempt,
                experience_lesson,
                [
                    (
                        entries[function][3],
                        (
                            "satisfied"
                            if captures[function]
                            .submission.productions[0]
                            .modality
                            == "voice"
                            and SUPPORT_RANK[captures[function].support_used]
                            <= SUPPORT_RANK[
                                entries[function][2].support_level
                            ]
                            and (
                                function != "transfer"
                                or captures[function].support_used == "none"
                            )
                            else "pending"
                        ),
                        "direct_english_construction_attempt",
                        attempt.attempt_id,
                    )
                    for function in ordered_functions
                ],
                db,
            )
        db.commit()
    except DirectEnglishConstructionExecutionError:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise DirectEnglishConstructionInvariantError(
            "Direct-English execution violates persistent integrity"
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DirectEnglishConstructionExecutionError(
            "Could not finalize direct-English construction attempt"
        ) from exc
    except Exception:
        db.rollback()
        raise
    return get_direct_english_construction_attempt(command.attempt_id, db)


def finalize_direct_english_construction_attempt(
    command: DirectEnglishConstructionAttemptFinalize,
    db: Session,
) -> DirectEnglishConstructionAttemptRecord:
    """Own rollback for validation and persistence under one transaction."""
    try:
        return _finalize_direct_english_construction_attempt(command, db)
    except Exception:
        db.rollback()
        raise
