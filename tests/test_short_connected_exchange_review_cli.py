from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.schemas.short_connected_exchange_review import (
    ShortConnectedExchangeProductionReviewRecord,
    ShortConnectedExchangeProductionReviewHistory,
    ShortConnectedExchangeSubmissionReviewHistory,
)
from app.services.short_connected_exchange_local_review_service import (
    LocalReviewProduction,
    LocalReviewRequirement,
    ShortConnectedExchangeLocalReviewPackage,
)
from scripts.review.short_connected_exchange_review import run_local_review
import scripts.review.short_connected_exchange_review as cli


NOW = datetime(2026, 8, 8, 15, 0, tzinfo=UTC)


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def package():
    requirements = (
        LocalReviewRequirement(
            dimension="intention_understanding",
            question="Intention question from active content?",
            allowed_results=("positive", "negative", "pending"),
        ),
        LocalReviewRequirement(
            dimension="contingent_response",
            question="Contingency question from active content?",
            allowed_results=("positive", "negative", "pending"),
        ),
    )
    return ShortConnectedExchangeLocalReviewPackage(
        submission_id=7,
        user_id="learner-label",
        submitted_at=NOW,
        lesson_id="a1-u1-l2",
        conversation_id="a1-u1-l2-c1",
        productions=tuple(
            LocalReviewProduction(
                production_id=index,
                prompt_id=f"prompt-{index}",
                turn_id=f"turn-{index}",
                partner_intervention=f"Partner intervention {index}",
                audio_reference=f"production-audio://audio-{index}",
                audio_path=Path(f"/private/audio/{index}.wav"),
                evidence_id=f"evidence-{index}",
                requirements=requirements,
            )
            for index in (1, 2, 3)
        ),
    )


def history(batch=None):
    reviews_by_production = {1: [], 2: [], 3: []}
    if batch is not None:
        for review in batch.reviews:
            reviews_by_production[review.production_id].append(
                ShortConnectedExchangeProductionReviewRecord.model_validate(
                    review.model_dump()
                )
            )
    return ShortConnectedExchangeSubmissionReviewHistory(
        submission_id=7,
        productions=[
            ShortConnectedExchangeProductionReviewHistory(
                production_id=index,
                prompt_id=f"prompt-{index}",
                turn_id=f"turn-{index}",
                reviews=reviews_by_production[index],
            )
            for index in (1, 2, 3)
        ],
    )


def run_with_answers(answers, **overrides):
    session = FakeSession()
    calls = SimpleNamespace(saved=[], histories=[])
    persisted = {"batch": None}

    def save_fn(batch, db):
        calls.saved.append((batch, db))
        persisted["batch"] = batch
        return batch.reviews

    def history_fn(submission_id, db):
        calls.histories.append((submission_id, db))
        return history(persisted["batch"])

    iterator = iter(answers)
    output = []
    kwargs = {
        "input_fn": lambda _prompt: next(iterator),
        "output": output.append,
        "session_factory": lambda: session,
        "prepare_fn": lambda submission_id, db: package(),
        "save_fn": save_fn,
        "history_fn": history_fn,
        "now_fn": lambda timezone: NOW,
        "uuid_fn": lambda: UUID("00000000-0000-0000-0000-000000000001"),
    }
    kwargs.update(overrides)
    result = run_local_review(7, "reviewer-local", **kwargs)
    return result, calls, output, session


def test_requires_nonblank_declared_source_id_without_opening_session():
    opened = []
    with pytest.raises(ValueError, match="source_id"):
        run_local_review(7, "  ", session_factory=lambda: opened.append(True))
    assert opened == []


def test_collects_six_results_and_persists_one_human_batch():
    result, calls, output, session = run_with_answers(
        ["positive", "negative", "pending", "positive", "negative", "pending", "yes"]
    )

    assert result == 0
    assert len(calls.saved) == 1
    batch = calls.saved[0][0]
    assert len(batch.reviews) == 6
    assert [item.result for item in batch.reviews] == [
        "positive",
        "negative",
        "pending",
        "positive",
        "negative",
        "pending",
    ]
    assert {item.source_type for item in batch.reviews} == {"human"}
    assert {item.source_id for item in batch.reviews} == {"reviewer-local"}
    assert {item.source_version for item in batch.reviews} == {None}
    assert all(
        item.reviewed_at.tzinfo is UTC and item.reviewed_at.utcoffset() is not None
        for item in batch.reviews
    )
    assert len({item.review_id for item in batch.reviews}) == 6
    assert calls.histories == [(7, calls.saved[0][1])]
    assert any("Complete append-only history" in line for line in output)
    assert not any("consensus" in line.lower() or "current" in line.lower() for line in output)
    assert session.closed is True


def test_invalid_input_is_reprompted_without_partial_write():
    result, calls, output, _ = run_with_answers(
        ["invalid", "positive", "negative", "pending", "positive", "negative", "pending", "no"]
    )
    assert result == 0
    assert calls.saved == []
    assert calls.histories == []
    assert any("Invalid result" in line for line in output)


@pytest.mark.parametrize("confirmation", ["no", "", "cancel"])
def test_cancellation_before_confirmation_never_writes(confirmation):
    result, calls, output, _ = run_with_answers(
        ["pending"] * 6 + [confirmation]
    )
    assert result == 0
    assert calls.saved == []
    assert calls.histories == []
    assert any("no reviews were persisted" in line for line in output)


def test_interruption_before_confirmation_never_writes():
    def interrupt(_prompt):
        raise KeyboardInterrupt

    result, calls, output, _ = run_with_answers([], input_fn=interrupt)
    assert result == 130
    assert calls.saved == []
    assert calls.histories == []
    assert any("before persistence" in line for line in output)


def test_persistence_error_is_not_retried_and_history_is_not_read():
    calls = []

    def fail_once(batch, db):
        calls.append((batch, db))
        raise RuntimeError("database unavailable")

    with pytest.raises(RuntimeError, match="database unavailable"):
        run_with_answers(["pending"] * 6 + ["yes"], save_fn=fail_once)
    assert len(calls) == 1


def test_interruption_during_write_reports_ambiguous_state_without_retry():
    calls = []

    def interrupt(batch, db):
        calls.append((batch, db))
        raise KeyboardInterrupt

    result, _, output, _ = run_with_answers(
        ["pending"] * 6 + ["yes"],
        save_fn=interrupt,
    )
    assert result == 130
    assert len(calls) == 1
    assert any("inspect the submission history" in line for line in output)


def test_display_is_local_and_contains_no_recognition_or_technical_results():
    result, _, output, _ = run_with_answers(["pending"] * 6 + ["no"])
    rendered = "\n".join(output)
    assert result == 0
    assert "/private/audio/1.wav" in rendered
    assert "Intention question from active content?" in rendered
    assert "recognized_text" not in rendered
    assert "score" not in rendered.lower()
    assert "feedback" not in rendered.lower()


def test_complete_history_is_rendered_without_dropping_prior_reviews():
    prior = {
        "review_id": "prior-review",
        "production_id": 1,
        "dimension": "intention_understanding",
        "result": "negative",
        "source_type": "human",
        "source_id": "earlier-reviewer",
        "source_version": None,
        "reviewed_at": NOW,
    }

    def history_with_prior(submission_id, db):
        result = history()
        result.productions[0].reviews.append(
            ShortConnectedExchangeProductionReviewRecord.model_validate(prior)
        )
        return result

    result, calls, output, _ = run_with_answers(
        ["pending"] * 6 + ["yes"],
        history_fn=history_with_prior,
    )
    assert result == 0
    assert len(calls.saved) == 1
    assert "prior-review" in "\n".join(output)


def test_cli_has_no_http_flutter_socket_or_shell_execution_dependency():
    source = Path(cli.__file__).read_text(encoding="utf-8").lower()
    assert "fastapi" not in source
    assert "flutter" not in source
    assert "import socket" not in source
    assert "shell=true" not in source.replace(" ", "")
