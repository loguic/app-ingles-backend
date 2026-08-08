from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import (
    ConversationProductionSubmission as SubmissionModel,
    LearnerProduction as ProductionModel,
)
from app.services.production_audio_storage_service import store_production_audio
from app.services.short_connected_exchange_local_review_service import (
    ShortConnectedExchangeLocalReviewError,
    prepare_short_connected_exchange_local_review,
)


PROMPTS = (
    ("a1-u1-l2-p-place", "a1-u1-l2-c1-t2"),
    ("a1-u1-l2-p-interest", "a1-u1-l2-c1-t4"),
    ("a1-u1-l2-p-unexpected-where", "a1-u1-l2-c1-t6"),
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def wav_payload(label: bytes) -> bytes:
    return b"RIFF" + (36 + len(label)).to_bytes(4, "little") + b"WAVE" + label


def create_submission(db, audio_dir, *, conversation_id="a1-u1-l2-c1"):
    submission = SubmissionModel(
        user_id="local-review-learner",
        level_id="A1",
        unit_id="a1-u1",
        lesson_id=(
            "a1-u1-l2" if conversation_id == "a1-u1-l2-c1" else "a1-u1-l1"
        ),
        conversation_id=conversation_id,
    )
    db.add(submission)
    db.flush()
    productions = []
    for index, (prompt_id, turn_id) in enumerate(PROMPTS):
        audio = store_production_audio(
            wav_payload(f"voice-{index}".encode()),
            storage_dir=audio_dir,
        )
        production = ProductionModel(
            submission_id=submission.id,
            prompt_id=prompt_id,
            turn_id=turn_id,
            modality="voice",
            response_text=None,
            audio_reference=audio.audio_reference,
        )
        db.add(production)
        productions.append(production)
    db.commit()
    return submission, productions


def test_prepares_three_canonical_voice_productions_with_active_rubric(db, tmp_path):
    submission, _ = create_submission(db, tmp_path)

    package = prepare_short_connected_exchange_local_review(
        submission.id,
        db,
        storage_dir=tmp_path,
    )

    assert len(package.productions) == 3
    assert [item.partner_intervention for item in package.productions] == [
        "Where are you from?",
        "Oh, nice! What do you like doing in your free time?",
        "Nice. Where do you usually do that?",
    ]
    assert [item.evidence_id for item in package.productions] == [
        "a1-u1-l2-ev-place-response",
        "a1-u1-l2-ev-interest-response",
        "a1-u1-l2-ev-unexpected-followup-response",
    ]
    for production in package.productions:
        assert production.audio_path.parent == tmp_path.resolve()
        assert production.audio_path.is_file()
        assert [item.dimension for item in production.requirements] == [
            "intention_understanding",
            "contingent_response",
        ]
        assert all(item.question for item in production.requirements)
        assert all(
            item.allowed_results == ("positive", "negative", "pending")
            for item in production.requirements
        )
    assert package.productions[0].requirements[0].question == (
        "¿La respuesta demuestra comprensión suficiente de la intención "
        "principal de la intervención?"
    )
    assert package.productions[0].requirements[1].question == (
        "¿La respuesta constituye una reacción pertinente a esa intervención "
        "y mantiene el intercambio?"
    )
    serialized_names = {
        name
        for production in package.productions
        for name in vars(production)
    }
    assert "recognized_text" not in serialized_names
    assert "technical_result" not in serialized_names
    assert "score" not in serialized_names


def test_rejects_missing_or_out_of_scope_submission(db, tmp_path):
    with pytest.raises(ShortConnectedExchangeLocalReviewError, match="does not exist"):
        prepare_short_connected_exchange_local_review(999, db, storage_dir=tmp_path)

    submission, _ = create_submission(
        db,
        tmp_path,
        conversation_id="a1-u1-l1-c3",
    )
    with pytest.raises(ShortConnectedExchangeLocalReviewError, match="active B181"):
        prepare_short_connected_exchange_local_review(
            submission.id,
            db,
            storage_dir=tmp_path,
        )


def test_rejects_noncanonical_or_nonvoice_productions(db, tmp_path):
    submission, productions = create_submission(db, tmp_path)
    productions[0].prompt_id = "unknown-prompt"
    db.commit()
    with pytest.raises(ShortConnectedExchangeLocalReviewError, match="canonical"):
        prepare_short_connected_exchange_local_review(
            submission.id,
            db,
            storage_dir=tmp_path,
        )

    productions[0].prompt_id = PROMPTS[0][0]
    productions[0].modality = "text"
    productions[0].response_text = "response"
    productions[0].audio_reference = None
    db.commit()
    with pytest.raises(ShortConnectedExchangeLocalReviewError, match="voice"):
        prepare_short_connected_exchange_local_review(
            submission.id,
            db,
            storage_dir=tmp_path,
        )


@pytest.mark.parametrize(
    ("reference", "message"),
    [
        ("file:///tmp/voice.wav", "Unsupported"),
        ("production-audio://not-a-uuid", "Invalid"),
        (
            "production-audio://00000000-0000-0000-0000-000000000001",
            "does not exist",
        ),
        ("production-audio://../../etc/passwd", "Invalid"),
    ],
)
def test_rejects_unsafe_or_missing_audio_reference(db, tmp_path, reference, message):
    submission, productions = create_submission(db, tmp_path)
    productions[0].audio_reference = reference
    db.commit()

    with pytest.raises(ShortConnectedExchangeLocalReviewError, match=message):
        prepare_short_connected_exchange_local_review(
            submission.id,
            db,
            storage_dir=tmp_path,
        )


def test_resolved_audio_cannot_escape_storage_root(db, tmp_path):
    submission, productions = create_submission(db, tmp_path)
    productions[0].audio_reference = f"production-audio://{uuid4()}/../../outside"
    db.commit()

    with pytest.raises(ShortConnectedExchangeLocalReviewError, match="Invalid"):
        prepare_short_connected_exchange_local_review(
            submission.id,
            db,
            storage_dir=tmp_path,
        )
