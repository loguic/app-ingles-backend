import hashlib
import sys
from pathlib import Path

import pytest

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.services.phonetic_analyzer_runtime_service import (
    build_runtime_phonetic_analyzer,
)
from app.services.production_audio_storage_service import (
    store_production_audio,
)


def test_runtime_configuration_executes_versioned_runner(
    tmp_path,
    monkeypatch,
):
    pipeline = tmp_path / "fake_pipeline.py"
    pipeline.write_text("\n".join([
        "import argparse, json",
        "p=argparse.ArgumentParser()",
        "p.add_argument(\"--audio\")",
        "p.add_argument(\"--text\")",
        "p.add_argument(\"--checkpoint\")",
        "p.add_argument(\"--device\")",
        "p.add_argument(\"--json\", action=\"store_true\")",
        "a=p.parse_args()",
        "print(json.dumps({\"text\": a.text, \"overall_score\": 88.4}))",
    ]) + "\n")

    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint")
    audio_dir = tmp_path / "audio"

    monkeypatch.setenv("PRODUCTION_AUDIO_DIR", str(audio_dir))
    monkeypatch.setenv("PHONETIC_ANALYZER_PYTHON", sys.executable)
    monkeypatch.setenv("PHONETIC_ANALYZER_PIPELINE", str(pipeline))
    monkeypatch.setenv(
        "PHONETIC_ANALYZER_PIPELINE_SHA256",
        hashlib.sha256(pipeline.read_bytes()).hexdigest(),
    )
    monkeypatch.setenv(
        "PHONETIC_ANALYZER_CHECKPOINT",
        str(checkpoint),
    )
    monkeypatch.setenv(
        "PHONETIC_ANALYZER_CHECKPOINT_SHA256",
        hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
    )
    monkeypatch.setenv("PHONETIC_ANALYZER_TIMEOUT_SECONDS", "5")

    upload = store_production_audio(
        b"RIFF" + bytes(4) + b"WAVE" + bytes(16)
    )
    production = LearnerProductionRecord(
        production_id=21,
        prompt_id="a1-test-p1",
        turn_id="a1-test-t1",
        modality="voice",
        response_text=None,
        audio_reference=upload.audio_reference,
    )
    criterion = ProductionEvaluationCriterion(
        id="pronunciation-target",
        evidence_definition_id="evidence-pronunciation",
        conversation_id="a1-test-c1",
        prompt_id="a1-test-p1",
        dimension="phonetic",
        description="Pronounce the phrase.",
        measurement_mode="score",
        success_threshold=0.80,
        applicable_modalities=["voice"],
    )

    evidence = build_runtime_phonetic_analyzer().analyze(
        production,
        criterion,
        reference_text="Hello, I am John.",
    )

    assert evidence.score == 0.884
    assert evidence.analyzer_id == "wavlm-gop-phoneme-scorer"
    assert "|pipeline-sha256:" in evidence.analyzer_version
    assert "|checkpoint-sha256:" in evidence.analyzer_version


def test_runtime_configuration_requires_python(monkeypatch):
    monkeypatch.delenv("PHONETIC_ANALYZER_PYTHON", raising=False)

    with pytest.raises(
        RuntimeError,
        match="PHONETIC_ANALYZER_PYTHON is not configured",
    ):
        build_runtime_phonetic_analyzer()

