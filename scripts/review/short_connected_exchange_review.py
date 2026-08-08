from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from uuid import uuid4


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


from app.db.database import SessionLocal
from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReviewBatch,
)
from app.services.short_connected_exchange_local_review_service import (
    ShortConnectedExchangeLocalReviewPackage,
    prepare_short_connected_exchange_local_review,
)
from app.services.short_connected_exchange_review_persistence_service import (
    get_short_connected_exchange_reviews_by_submission,
    save_short_connected_exchange_production_reviews,
)


RESULTS = ("positive", "negative", "pending")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review one B181 submission locally and append one batch."
    )
    parser.add_argument("submission_id", type=int)
    parser.add_argument("--source-id", required=True)
    return parser


def _show_package(package, output: Callable[[str], None]) -> None:
    output(f"Submission: {package.submission_id}")
    output(f"Learner label: {package.user_id}")
    output(f"Submitted at: {package.submitted_at.isoformat()}")
    output(f"Lesson: {package.lesson_id}")
    output(f"Conversation: {package.conversation_id}")
    for index, production in enumerate(package.productions, start=1):
        output("")
        output(f"Production {index}")
        output(f"  production_id: {production.production_id}")
        output(f"  prompt_id: {production.prompt_id}")
        output(f"  turn_id: {production.turn_id}")
        output(f"  partner: {production.partner_intervention}")
        output(f"  audio_reference: {production.audio_reference}")
        output(f"  local_audio_path: {production.audio_path}")
        output(f"  evidence_id: {production.evidence_id}")
        for requirement in production.requirements:
            output(f"  {requirement.dimension}: {requirement.question}")
            output(
                "    allowed_results: " + " | ".join(requirement.allowed_results)
            )


def _read_result(
    prompt: str,
    input_fn: Callable[[str], str],
    output: Callable[[str], None],
) -> str:
    while True:
        result = input_fn(prompt).strip().lower()
        if result in RESULTS:
            return result
        output("Invalid result; use positive, negative, or pending.")


def _collect_decisions(package, input_fn, output):
    decisions = []
    for production in package.productions:
        for requirement in production.requirements:
            result = _read_result(
                f"{production.production_id} / {requirement.dimension}: ",
                input_fn,
                output,
            )
            decisions.append((production, requirement, result))
    if len(decisions) != 6:
        raise RuntimeError("B181 local review requires exactly six decisions")
    return decisions


def _show_summary(decisions, source_id, output):
    output("")
    output(f"Declared human reviewer label: {source_id}")
    output("Review batch summary:")
    for production, requirement, result in decisions:
        output(
            f"  {production.production_id} / "
            f"{requirement.dimension}: {result}"
        )


def _build_batch(decisions, source_id, now_fn, uuid_fn):
    reviewed_at = now_fn(UTC)
    return ShortConnectedExchangeProductionReviewBatch.model_validate(
        {
            "reviews": [
                {
                    "review_id": (
                        f"b181-local-{uuid_fn()}-"
                        f"{production.production_id}-{requirement.dimension}"
                    ),
                    "production_id": production.production_id,
                    "dimension": requirement.dimension,
                    "result": result,
                    "source_type": "human",
                    "source_id": source_id,
                    "source_version": None,
                    "reviewed_at": reviewed_at,
                }
                for production, requirement, result in decisions
            ]
        }
    )


def _show_history(history, output):
    output("")
    output(f"Complete append-only history for submission {history.submission_id}:")
    for production in history.productions:
        output(
            f"  production {production.production_id} "
            f"({production.prompt_id}, {production.turn_id})"
        )
        for review in production.reviews:
            output(
                f"    {review.reviewed_at.isoformat()} | {review.review_id} | "
                f"{review.dimension} | {review.result} | "
                f"{review.source_type}:{review.source_id}"
            )


def run_local_review(
    submission_id: int,
    source_id: str,
    *,
    input_fn: Callable[[str], str] = input,
    output: Callable[[str], None] = print,
    session_factory=SessionLocal,
    prepare_fn=prepare_short_connected_exchange_local_review,
    save_fn=save_short_connected_exchange_production_reviews,
    history_fn=get_short_connected_exchange_reviews_by_submission,
    now_fn=datetime.now,
    uuid_fn=uuid4,
) -> int:
    if not source_id.strip():
        raise ValueError("source_id cannot be blank")
    db = session_factory()
    write_started = False
    try:
        package = prepare_fn(submission_id, db)
        _show_package(package, output)
        decisions = _collect_decisions(package, input_fn, output)
        _show_summary(decisions, source_id, output)
        confirmation = input_fn("Persist this complete batch? [yes/no]: ")
        if confirmation.strip().lower() not in {"y", "yes"}:
            output("Review cancelled; no reviews were persisted.")
            return 0
        batch = _build_batch(decisions, source_id.strip(), now_fn, uuid_fn)
        write_started = True
        save_fn(batch, db)
        history = history_fn(submission_id, db)
        _show_history(history, output)
        return 0
    except KeyboardInterrupt:
        if write_started:
            output(
                "Review interrupted during or after persistence; inspect the "
                "submission history before retrying. No automatic retry was made."
            )
        else:
            output("Review interrupted before persistence; no reviews were written.")
        return 130
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run_local_review(args.submission_id, args.source_id)
    except Exception as error:
        print(f"Local B181 review failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
