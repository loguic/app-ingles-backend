import os
from pathlib import Path

from app.services.command_acoustic_phonetic_scorer import (
    CommandAcousticPhoneticScorer,
)
from app.services.production_audio_phonetic_analyzer import (
    ProductionAudioPhoneticAnalyzer,
)


RUNNER_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "phonetic"
    / "wavlm_gop_runner.py"
)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(name + " is not configured")
    return value.strip()


def build_runtime_phonetic_analyzer() -> ProductionAudioPhoneticAnalyzer:
    """Build the acoustic analyzer from explicit runtime configuration.

    Construye el analizador acústico desde configuración runtime explícita.
    """
    python_path = _required_env("PHONETIC_ANALYZER_PYTHON")
    pipeline_path = _required_env("PHONETIC_ANALYZER_PIPELINE")
    pipeline_sha256 = _required_env(
        "PHONETIC_ANALYZER_PIPELINE_SHA256"
    )
    checkpoint_path = _required_env("PHONETIC_ANALYZER_CHECKPOINT")
    checkpoint_sha256 = _required_env(
        "PHONETIC_ANALYZER_CHECKPOINT_SHA256"
    )
    device = os.getenv("PHONETIC_ANALYZER_DEVICE", "cpu").strip() or "cpu"

    try:
        timeout_seconds = float(
            os.getenv("PHONETIC_ANALYZER_TIMEOUT_SECONDS", "120")
        )
    except ValueError as error:
        raise RuntimeError(
            "PHONETIC_ANALYZER_TIMEOUT_SECONDS must be numeric"
        ) from error

    scorer = CommandAcousticPhoneticScorer(
        [
            python_path,
            str(RUNNER_PATH),
            "--pipeline",
            pipeline_path,
            "--pipeline-sha256",
            pipeline_sha256,
            "--checkpoint",
            checkpoint_path,
            "--checkpoint-sha256",
            checkpoint_sha256,
            "--device",
            device,
        ],
        timeout_seconds=timeout_seconds,
    )

    return ProductionAudioPhoneticAnalyzer(scorer)

