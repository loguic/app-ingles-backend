from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
)
from app.services.content_service import (
    get_conversation_context_by_id,
    get_lesson_by_id,
)
from app.services.production_audio_storage_service import (
    resolve_production_audio_path,
)
from app.services.short_connected_exchange_review_persistence_service import (
    B181_CONVERSATION_ID,
    B181_LESSON_ID,
)


class ShortConnectedExchangeLocalReviewError(RuntimeError):
    """Report a submission that cannot be reviewed locally."""


@dataclass(frozen=True)
class LocalReviewRequirement:
    dimension: str
    question: str
    allowed_results: tuple[str, ...]


@dataclass(frozen=True)
class LocalReviewProduction:
    production_id: int
    prompt_id: str
    turn_id: str
    partner_intervention: str
    audio_reference: str
    audio_path: Path
    evidence_id: str
    requirements: tuple[LocalReviewRequirement, ...]


@dataclass(frozen=True)
class ShortConnectedExchangeLocalReviewPackage:
    submission_id: int
    user_id: str
    submitted_at: datetime
    lesson_id: str
    conversation_id: str
    productions: tuple[LocalReviewProduction, ...]


def _active_review_context():
    context = get_conversation_context_by_id(B181_CONVERSATION_ID)
    if context is None:
        raise ShortConnectedExchangeLocalReviewError(
            "Active B181 conversation does not exist"
        )
    level_id, unit_id, lesson_id, conversation = context
    if lesson_id != B181_LESSON_ID:
        raise ShortConnectedExchangeLocalReviewError(
            "Active B181 conversation hierarchy is invalid"
        )
    lesson = get_lesson_by_id(lesson_id)
    if lesson is None or lesson.experience is None:
        raise ShortConnectedExchangeLocalReviewError(
            "Active B181 review rubric does not exist"
        )
    return level_id, unit_id, lesson, conversation


def _review_definition_by_prompt(lesson, conversation):
    evidence_by_prompt = {}
    for evidence in lesson.experience.evidence_definitions:
        prompt_id = evidence.production_prompt_id
        if prompt_id is not None:
            evidence_by_prompt.setdefault(prompt_id, []).append(evidence)

    definitions = {}
    partner_by_learner_turn = {}
    for turn in conversation.turns:
        if turn.speaker == "partner" and turn.next_turn_id is not None:
            partner_by_learner_turn.setdefault(turn.next_turn_id, []).append(turn)

    for turn in conversation.turns:
        prompt = turn.production_prompt
        if prompt is None:
            continue
        evidence = evidence_by_prompt.get(prompt.id, [])
        partners = partner_by_learner_turn.get(turn.id, [])
        if len(evidence) != 1 or len(partners) != 1:
            raise ShortConnectedExchangeLocalReviewError(
                "Each B181 prompt requires one evidence and one partner intervention"
            )
        requirements = tuple(
            LocalReviewRequirement(
                dimension=requirement.dimension,
                question=requirement.question,
                allowed_results=tuple(requirement.allowed_results),
            )
            for requirement in evidence[0].external_review_requirements
        )
        if not requirements:
            raise ShortConnectedExchangeLocalReviewError(
                "B181 review requirements do not exist"
            )
        definitions[prompt.id] = (
            turn.id,
            partners[0].en,
            evidence[0].id,
            requirements,
        )
    if len(definitions) != 3:
        raise ShortConnectedExchangeLocalReviewError(
            "B181 must define exactly three production prompts"
        )
    return definitions


def prepare_short_connected_exchange_local_review(
    submission_id: int,
    db: Session,
    *,
    storage_dir: Path | None = None,
) -> ShortConnectedExchangeLocalReviewPackage:
    """Prepare one local, read-only B181 human-review package."""
    submission = db.get(SubmissionModel, submission_id)
    if submission is None:
        raise ShortConnectedExchangeLocalReviewError(
            "Conversation production submission does not exist"
        )

    level_id, unit_id, lesson, conversation = _active_review_context()
    if (
        submission.level_id != level_id
        or submission.unit_id != unit_id
        or submission.lesson_id != lesson.id
        or submission.conversation_id != conversation.id
    ):
        raise ShortConnectedExchangeLocalReviewError(
            "Submission does not belong to active B181 content"
        )

    definitions = _review_definition_by_prompt(lesson, conversation)
    rows = (
        db.query(ProductionModel)
        .filter(ProductionModel.submission_id == submission.id)
        .all()
    )
    if len(rows) != 3 or {row.prompt_id for row in rows} != set(definitions):
        raise ShortConnectedExchangeLocalReviewError(
            "B181 submission must contain its three canonical productions"
        )
    by_prompt = {row.prompt_id: row for row in rows}

    productions = []
    for prompt_id, definition in definitions.items():
        turn_id, intervention, evidence_id, requirements = definition
        production = by_prompt[prompt_id]
        if production.turn_id != turn_id:
            raise ShortConnectedExchangeLocalReviewError(
                "B181 production turn does not match its prompt"
            )
        if production.modality != "voice" or not production.audio_reference:
            raise ShortConnectedExchangeLocalReviewError(
                "B181 local review requires three voice productions"
            )
        try:
            audio_path = resolve_production_audio_path(
                production.audio_reference,
                storage_dir=storage_dir,
            )
        except (RuntimeError, ValueError, FileNotFoundError) as error:
            raise ShortConnectedExchangeLocalReviewError(str(error)) from error
        productions.append(
            LocalReviewProduction(
                production_id=production.id,
                prompt_id=production.prompt_id,
                turn_id=production.turn_id,
                partner_intervention=intervention,
                audio_reference=production.audio_reference,
                audio_path=audio_path,
                evidence_id=evidence_id,
                requirements=requirements,
            )
        )

    return ShortConnectedExchangeLocalReviewPackage(
        submission_id=submission.id,
        user_id=submission.user_id,
        submitted_at=submission.submitted_at,
        lesson_id=submission.lesson_id,
        conversation_id=submission.conversation_id,
        productions=tuple(productions),
    )
