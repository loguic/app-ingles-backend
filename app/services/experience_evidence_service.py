"""Authoritative source-bound evidence state for ExperienceAttempt."""

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.db.models import (
    ConversationAttempt,
    ConversationProductionSubmission,
    DirectEnglishConstructionAttempt,
    ExperienceAttempt,
    ExperienceComprehensionResponse,
    ExperienceEvidenceState,
)
from app.schemas.experience_attempt import ExperienceEvidenceStateRecord
from app.services.content_service import get_lesson_context_by_id


_STATUS_RANK = {"pending": 0, "needs_review": 1, "satisfied": 2}
_SOURCE_FIELDS = {
    "comprehension_response": "comprehension_response_id",
    "conversation_production_submission": (
        "conversation_production_submission_id"
    ),
    "conversation_attempt": "conversation_attempt_id",
    "direct_english_construction_attempt": (
        "direct_english_construction_attempt_id"
    ),
}
_SOURCE_MODELS = {
    "comprehension_response": ExperienceComprehensionResponse,
    "conversation_production_submission": ConversationProductionSubmission,
    "conversation_attempt": ConversationAttempt,
    "direct_english_construction_attempt": DirectEnglishConstructionAttempt,
}
_SOURCE_PRIMARY_KEYS = {
    "comprehension_response": "response_id",
    "conversation_production_submission": "id",
    "conversation_attempt": "id",
    "direct_english_construction_attempt": "attempt_id",
}
_ALLOWED_SOURCES = {
    "comprehension_result": {"comprehension_response"},
    "conversation_completion": {"conversation_attempt"},
    "guided_production": {"direct_english_construction_attempt"},
    "contextual_response": {
        "conversation_production_submission",
        "direct_english_construction_attempt",
    },
}


def resolve_experience_attempt(
    attempt_id: str,
    db: Session,
    *,
    for_update: bool,
    require_in_progress: bool,
):
    """Resolve and optionally lock an attempt with its exact active content."""
    query = db.query(ExperienceAttempt).filter(
        ExperienceAttempt.attempt_id == attempt_id
    )
    if for_update:
        query = query.with_for_update()
    attempt = query.one_or_none()
    if attempt is None:
        raise ValueError(f"Experience attempt '{attempt_id}' not found")
    if require_in_progress and attempt.status != "in_progress":
        raise ValueError("Experience attempt is already completed")

    context = get_lesson_context_by_id(attempt.lesson_id)
    if context is None:
        raise ValueError("Experience hierarchy does not match the content tree")
    level_id, unit_id, lesson = context
    if (
        level_id != attempt.level_id
        or unit_id != attempt.unit_id
        or lesson.id != attempt.lesson_id
        or lesson.experience is None
        or lesson.experience.contract_version
        != attempt.experience_contract_version
    ):
        raise ValueError("Experience hierarchy does not match the content tree")
    return attempt, lesson


def validate_attempt_source_context(
    attempt: ExperienceAttempt,
    *,
    user_id: str,
    level_id: str,
    unit_id: str,
    lesson_id: str,
) -> None:
    if (
        attempt.user_id != user_id
        or attempt.level_id != level_id
        or attempt.unit_id != unit_id
        or attempt.lesson_id != lesson_id
    ):
        raise ValueError(
            "Source user or hierarchy does not match the experience attempt"
        )


def required_evidence_definitions(lesson) -> list:
    experience = lesson.experience
    if experience is None:  # pragma: no cover - guarded by resolution.
        raise ValueError(f"Lesson '{lesson.id}' has no experience")
    by_id = {item.id: item for item in experience.evidence_definitions}
    try:
        return [
            by_id[evidence_id]
            for evidence_id in experience.completion_policy.required_evidence_ids
        ]
    except KeyError as error:  # pragma: no cover - content schema guards this.
        raise ValueError(
            "Completion policy references unknown required evidence"
        ) from error


def _source_reference(source_type: str, source_id):
    if source_type not in _SOURCE_FIELDS:
        raise ValueError("Unsupported authoritative evidence source type")
    return {
        field_name: source_id if field_name == _SOURCE_FIELDS[source_type] else None
        for field_name in _SOURCE_FIELDS.values()
    }


def _validate_source_row(
    experience_attempt_id: str,
    source_type: str,
    source_id,
    db: Session,
) -> None:
    model = _SOURCE_MODELS.get(source_type)
    primary_key = _SOURCE_PRIMARY_KEYS.get(source_type)
    if model is None or primary_key is None:
        raise ValueError("Unsupported authoritative evidence source type")
    row = (
        db.query(model)
        .filter(getattr(model, primary_key) == source_id)
        .one_or_none()
    )
    if row is None:
        raise ValueError("Authoritative evidence source does not exist")
    if row.experience_attempt_id != experience_attempt_id:
        raise ValueError(
            "Authoritative evidence source belongs to another experience attempt"
        )


def accredit_evidence_states(
    attempt: ExperienceAttempt,
    lesson,
    updates: Iterable[tuple[object, str, str, object]],
    db: Session,
    *,
    accredited_at: datetime | None = None,
) -> None:
    """Apply effective state updates without owning commit or rollback."""
    now = accredited_at or datetime.now(timezone.utc)
    required_ids = {
        item.id for item in required_evidence_definitions(lesson)
    }
    for definition, status, source_type, source_id in updates:
        if definition.id not in required_ids:
            raise ValueError("Source does not map to required experience evidence")
        if status not in _STATUS_RANK:
            raise ValueError("Unsupported experience evidence status")
        if source_type not in _ALLOWED_SOURCES.get(
            definition.evidence_type, set()
        ):
            raise ValueError("Evidence definition is incompatible with source type")
        _validate_source_row(
            attempt.attempt_id,
            source_type,
            source_id,
            db,
        )

        state = db.get(
            ExperienceEvidenceState,
            (attempt.attempt_id, definition.id),
        )
        references = _source_reference(source_type, source_id)
        if state is not None:
            if state.evidence_type != definition.evidence_type:
                raise ValueError(
                    "Persisted evidence type contradicts active content"
                )
            same_source = (
                state.source_type == source_type
                and getattr(state, _SOURCE_FIELDS[source_type]) == source_id
            )
            if same_source and state.status == status:
                continue
            if state.status == "satisfied":
                continue
            if _STATUS_RANK[status] < _STATUS_RANK[state.status]:
                continue
            state.status = status
            state.source_type = source_type
            for field_name, value in references.items():
                setattr(state, field_name, value)
            state.accredited_at = now
            continue

        db.add(
            ExperienceEvidenceState(
                experience_attempt_id=attempt.attempt_id,
                evidence_definition_id=definition.id,
                evidence_type=definition.evidence_type,
                status=status,
                source_type=source_type,
                accredited_at=now,
                **references,
            )
        )

    db.flush()
    _complete_if_ready(attempt, lesson, db, completed_at=now)
    db.flush()


def _complete_if_ready(
    attempt: ExperienceAttempt,
    lesson,
    db: Session,
    *,
    completed_at: datetime,
) -> None:
    required = required_evidence_definitions(lesson)
    states = (
        db.query(ExperienceEvidenceState)
        .filter(
            ExperienceEvidenceState.experience_attempt_id
            == attempt.attempt_id,
            ExperienceEvidenceState.evidence_definition_id.in_(
                [item.id for item in required]
            ),
        )
        .all()
    )
    satisfied_ids = {
        state.evidence_definition_id
        for state in states
        if state.status == "satisfied"
    }
    if satisfied_ids == {item.id for item in required}:
        attempt.status = "completed"
        attempt.completed_at = completed_at


def effective_evidence_records(
    attempt: ExperienceAttempt,
    lesson,
    db: Session,
) -> list[ExperienceEvidenceStateRecord]:
    """Merge persisted effective rows with derived pending in policy order."""
    definitions = required_evidence_definitions(lesson)
    states = {
        state.evidence_definition_id: state
        for state in db.query(ExperienceEvidenceState)
        .filter(
            ExperienceEvidenceState.experience_attempt_id
            == attempt.attempt_id
        )
        .all()
    }
    records: list[ExperienceEvidenceStateRecord] = []
    required_ids = {item.id for item in definitions}
    if set(states) - required_ids:
        raise ValueError(
            "Persisted evidence state is not required by active content"
        )
    for definition in definitions:
        state = states.get(definition.id)
        if state is None:
            records.append(
                ExperienceEvidenceStateRecord(
                    evidence_definition_id=definition.id,
                    evidence_type=definition.evidence_type,
                    status="pending",
                )
            )
            continue
        if state.evidence_type != definition.evidence_type:
            raise ValueError(
                "Persisted evidence type contradicts active content"
            )
        if state.source_type not in _ALLOWED_SOURCES.get(
            state.evidence_type, set()
        ):
            raise ValueError("Persisted evidence source is incompatible")
        source_id = getattr(state, _SOURCE_FIELDS[state.source_type])
        _validate_source_row(
            attempt.attempt_id,
            state.source_type,
            source_id,
            db,
        )
        records.append(
            ExperienceEvidenceStateRecord(
                evidence_definition_id=definition.id,
                evidence_type=definition.evidence_type,
                status=state.status,
            )
        )
    return records
