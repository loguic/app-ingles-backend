import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.services.command_acoustic_phonetic_scorer import (
    CommandAcousticPhoneticScorer,
)


def write_runner(tmp_path: Path, lines: list[str]) -> Path:
    runner = tmp_path / "runner.py"
    runner.write_text("\n".join(lines) + "\n")
    return runner


def test_returns_validated_measurement_from_isolated_command(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")

    runner = write_runner(
        tmp_path,
        [
            "import argparse, json",
            "from datetime import UTC, datetime",
            "parser = argparse.ArgumentParser()",
            "parser.add_argument(\"--audio\")",
            "parser.add_argument(\"--text\")",
            "parser.add_argument(\"--json\", action=\"store_true\")",
            "args = parser.parse_args()",
            "assert args.text == \"Hello, I am John.\"",
            "print(json.dumps({",
            "    \"score\": 0.88,",
            "    \"analyzer_id\": \"fake-command-analyzer\",",
            "    \"analyzer_version\": \"1.0\",",
            "    \"analyzed_at\": datetime(2026, 7, 28, tzinfo=UTC).isoformat(),",
            "}))",
        ],
    )

    result = CommandAcousticPhoneticScorer(
        [sys.executable, str(runner)],
    ).score(
        audio,
        reference_text="Hello, I am John.",
    )

    assert result.score == 0.88
    assert result.analyzer_id == "fake-command-analyzer"
    assert result.analyzer_version == "1.0"
    assert result.analyzed_at == datetime(2026, 7, 28, tzinfo=UTC)


def test_rejects_nonzero_analyzer_exit(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")
    runner = write_runner(
        tmp_path,
        [
            "import sys",
            "print(\"forced analyzer failure\", file=sys.stderr)",
            "raise SystemExit(7)",
        ],
    )

    with pytest.raises(
        RuntimeError,
        match="Acoustic analyzer failed: forced analyzer failure",
    ):
        CommandAcousticPhoneticScorer(
            [sys.executable, str(runner)],
        ).score(audio, reference_text="Hello, I am John.")


def test_rejects_invalid_analyzer_json(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")
    runner = write_runner(tmp_path, ["print(\"not-json\")"])

    with pytest.raises(
        ValueError,
        match="Acoustic analyzer returned invalid JSON",
    ):
        CommandAcousticPhoneticScorer(
            [sys.executable, str(runner)],
        ).score(audio, reference_text="Hello, I am John.")


def test_rejects_blank_reference_before_process_execution(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")

    with pytest.raises(
        ValueError,
        match="Acoustic analyzer requires non-blank reference text",
    ):
        CommandAcousticPhoneticScorer(
            [sys.executable, "does-not-need-to-exist.py"],
        ).score(audio, reference_text="   ")
