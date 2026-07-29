from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pytest

from app.schemas.phonetic_calibration import PhoneticCalibrationSample
from app.schemas.phonetic_evidence import AcousticPhoneticMeasurement
from app.services.phonetic_calibration_service import (
    measure_phonetic_calibration_sample,
    measure_phonetic_calibration_corpus,
)


class FakeAcousticPhoneticScorer:
    def __init__(self) -> None:
        self.audio_path: Path | None = None
        self.reference_text: str | None = None

    def score(
        self,
        audio_path: Path,
        *,
        reference_text: str,
    ) -> AcousticPhoneticMeasurement:
        self.audio_path = audio_path
        self.reference_text = reference_text
        return AcousticPhoneticMeasurement(
            score=0.884,
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version="wavlm-gop-runner/1.0",
            analyzed_at=datetime.now(UTC),
        )


def build_sample(audio_path: str, audio_sha256: str) -> PhoneticCalibrationSample:
    return PhoneticCalibrationSample(
        sample_id="human-001",
        reference_text="Hello, I am John.",
        audio_path=audio_path,
        audio_sha256=audio_sha256,
        expected_class="acceptable",
    )


def test_measures_verified_sample_and_forwards_reference_text(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    audio_path = corpus_dir / "human-001.wav"
    audio_path.write_bytes(b"controlled-human-audio")
    digest = sha256(audio_path.read_bytes()).hexdigest()
    scorer = FakeAcousticPhoneticScorer()

    result = measure_phonetic_calibration_sample(
        build_sample("human-001.wav", digest),
        scorer,
        corpus_dir=corpus_dir,
    )

    assert result.sample_id == "human-001"
    assert result.score == 0.884
    assert scorer.audio_path == audio_path.resolve()
    assert scorer.reference_text == "Hello, I am John."


def test_rejects_sha256_mismatch(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "human-001.wav").write_bytes(b"audio")

    with pytest.raises(ValueError, match="SHA-256"):
        measure_phonetic_calibration_sample(
            build_sample("human-001.wav", "a" * 64),
            FakeAcousticPhoneticScorer(),
            corpus_dir=corpus_dir,
        )


def test_rejects_missing_audio(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        measure_phonetic_calibration_sample(
            build_sample("missing.wav", "a" * 64),
            FakeAcousticPhoneticScorer(),
            corpus_dir=corpus_dir,
        )


def test_rejects_audio_outside_corpus(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"audio")
    digest = sha256(outside.read_bytes()).hexdigest()

    with pytest.raises(ValueError, match="inside corpus"):
        measure_phonetic_calibration_sample(
            build_sample("../outside.wav", digest),
            FakeAcousticPhoneticScorer(),
            corpus_dir=corpus_dir,
        )


def test_measures_calibration_corpus_in_order(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    first = corpus_dir / "first.wav"
    second = corpus_dir / "second.wav"
    first.write_bytes(b"first-audio")
    second.write_bytes(b"second-audio")
    samples = [
        build_sample("first.wav", sha256(first.read_bytes()).hexdigest()),
        PhoneticCalibrationSample(
            sample_id="human-002",
            reference_text="Hello, I am Joan.",
            audio_path="second.wav",
            audio_sha256=sha256(second.read_bytes()).hexdigest(),
            expected_class="variant",
        ),
    ]

    results = measure_phonetic_calibration_corpus(
        samples,
        FakeAcousticPhoneticScorer(),
        corpus_dir=corpus_dir,
    )

    assert [result.sample_id for result in results] == [
        "human-001",
        "human-002",
    ]


def test_rejects_duplicate_sample_id_in_corpus(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    audio = corpus_dir / "human.wav"
    audio.write_bytes(b"audio")
    digest = sha256(audio.read_bytes()).hexdigest()
    sample = build_sample("human.wav", digest)

    with pytest.raises(ValueError, match="sample_id must be unique"):
        measure_phonetic_calibration_corpus(
            [sample, sample],
            FakeAcousticPhoneticScorer(),
            corpus_dir=corpus_dir,
        )


def test_runtime_calibration_uses_shared_configured_scorer(tmp_path, monkeypatch):
    import app.services.phonetic_calibration_service as service

    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    audio = corpus_dir / "human.wav"
    audio.write_bytes(b"human-audio")
    digest = sha256(audio.read_bytes()).hexdigest()
    scorer = FakeAcousticPhoneticScorer()

    monkeypatch.setattr(
        service,
        "build_runtime_acoustic_phonetic_scorer",
        lambda: scorer,
    )

    results = service.measure_runtime_phonetic_calibration_corpus(
        [build_sample("human.wav", digest)],
        corpus_dir=corpus_dir,
    )

    assert [result.sample_id for result in results] == ["human-001"]
    assert scorer.reference_text == "Hello, I am John."
