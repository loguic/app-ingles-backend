from datetime import UTC, datetime

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.phonetic_evidence import AcousticPhoneticMeasurement
from app.services.production_audio_phonetic_analyzer import (
    ProductionAudioPhoneticAnalyzer,
)
from app.services.production_audio_storage_service import (
    store_production_audio,
)


WAV_PAYLOAD = b"RIFF" + bytes(4) + b"WAVE" + bytes(16)


def make_criterion():
    return ProductionEvaluationCriterion(
        id="pronunciation-target",
        evidence_definition_id="evidence-pronunciation",
        conversation_id="a1-test-c1",
        prompt_id="a1-test-p1",
        dimension="phonetic",
        description="Pronounce the target phrase clearly.",
        measurement_mode="score",
        success_threshold=0.80,
        applicable_modalities=["voice"],
    )


class FakeAcousticScorer:
    def __init__(self):
        self.calls = []

    def score(self, audio_path, *, reference_text):
        self.calls.append((audio_path, reference_text))
        return AcousticPhoneticMeasurement(
            score=0.93,
            analyzer_id="fake-acoustic",
            analyzer_version="1.0",
            analyzed_at=datetime(2026, 7, 28, tzinfo=UTC),
        )


def test_resolves_private_audio_and_builds_traceable_evidence(tmp_path):
    upload = store_production_audio(
        WAV_PAYLOAD,
        storage_dir=tmp_path,
    )
    production = LearnerProductionRecord(
        production_id=9,
        prompt_id="a1-test-p1",
        turn_id="a1-test-t1",
        modality="voice",
        response_text=None,
        audio_reference=upload.audio_reference,
    )
    scorer = FakeAcousticScorer()
    analyzer = ProductionAudioPhoneticAnalyzer(
        scorer,
        storage_dir=tmp_path,
    )

    evidence = analyzer.analyze(
        production,
        make_criterion(),
        reference_text="Hello, I am John.",
    )

    assert evidence.production_id == 9
    assert evidence.criterion_id == "pronunciation-target"
    assert evidence.audio_reference == upload.audio_reference
    assert evidence.score == 0.93
    assert evidence.analyzer_id == "fake-acoustic"
    assert scorer.calls[0][0].is_file()
    assert scorer.calls[0][0].parent == tmp_path.resolve()
    assert scorer.calls[0][1] == "Hello, I am John."


def test_rejects_non_voice_production(tmp_path):
    production = LearnerProductionRecord(
        production_id=9,
        prompt_id="a1-test-p1",
        turn_id="a1-test-t1",
        modality="text",
        response_text="Hello, I am John.",
        audio_reference=None,
    )

    with pytest.raises(
        ValueError,
        match="Production audio analyzer requires voice production",
    ):
        ProductionAudioPhoneticAnalyzer(
            FakeAcousticScorer(),
            storage_dir=tmp_path,
        ).analyze(
            production,
            make_criterion(),
            reference_text="Hello, I am John.",
        )


def test_rejects_unknown_private_audio_reference(tmp_path):
    production = LearnerProductionRecord(
        production_id=9,
        prompt_id="a1-test-p1",
        turn_id="a1-test-t1",
        modality="voice",
        response_text=None,
        audio_reference=(
            "production-audio://"
            "11111111-1111-1111-1111-111111111111"
        ),
    )

    with pytest.raises(
        FileNotFoundError,
        match="Production audio does not exist",
    ):
        ProductionAudioPhoneticAnalyzer(
            FakeAcousticScorer(),
            storage_dir=tmp_path,
        ).analyze(
            production,
            make_criterion(),
            reference_text="Hello, I am John.",
        )
