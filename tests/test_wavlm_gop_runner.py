import hashlib
import json
import subprocess
import sys
from pathlib import Path


RUNNER = Path("scripts/phonetic/wavlm_gop_runner.py")


def write_fake_pipeline(tmp_path: Path, lines: list[str]) -> Path:
    path = tmp_path / "fake_pipeline.py"
    path.write_text("\n".join(lines) + "\n")
    return path


def run_runner(tmp_path: Path, pipeline: Path, text="Hello, I am John."):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint")

    return subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--pipeline",
            str(pipeline),
            "--pipeline-sha256",
            hashlib.sha256(pipeline.read_bytes()).hexdigest(),
            "--checkpoint",
            str(checkpoint),
            "--checkpoint-sha256",
            hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            "--device",
            "cpu",
            "--audio",
            str(audio),
            "--text",
            text,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_normalizes_real_pipeline_shape_to_neutral_measurement(tmp_path):
    pipeline = write_fake_pipeline(
        tmp_path,
        [
            "import argparse, json",
            "p=argparse.ArgumentParser()",
            "p.add_argument(\"--audio\")",
            "p.add_argument(\"--text\")",
            "p.add_argument(\"--checkpoint\")",
            "p.add_argument(\"--device\")",
            "p.add_argument(\"--json\", action=\"store_true\")",
            "a=p.parse_args()",
            "print(json.dumps({",
            "    \"text\": a.text,",
            "    \"overall_score\": 88.4,",
            "    \"n_phonemes\": 10,",
            "    \"n_errors\": 1,",
            "    \"words\": [{\"word\": \"John\"}],",
            "}))",
        ],
    )

    completed = run_runner(tmp_path, pipeline)

    assert completed.returncode == 0
    result = json.loads(completed.stdout)
    assert result["score"] == 0.884
    assert result["analyzer_id"] == "wavlm-gop-phoneme-scorer"
    assert "wavlm-gop-runner/1.0" in result["analyzer_version"]
    assert "|pipeline-sha256:" in result["analyzer_version"]
    assert "|checkpoint-sha256:" in result["analyzer_version"]
    assert "analyzed_at" in result


def test_rejects_result_for_different_reference_text(tmp_path):
    pipeline = write_fake_pipeline(
        tmp_path,
        [
            "import json",
            "print(json.dumps({",
            "    \"text\": \"Different text\",",
            "    \"overall_score\": 88.4,",
            "}))",
        ],
    )

    completed = run_runner(tmp_path, pipeline)

    assert completed.returncode != 0
    assert (
        "result text does not match reference text"
        in completed.stderr
    )


def test_rejects_score_outside_model_scale(tmp_path):
    pipeline = write_fake_pipeline(
        tmp_path,
        [
            "import argparse, json",
            "p=argparse.ArgumentParser()",
            "p.add_argument(\"--audio\")",
            "p.add_argument(\"--text\")",
            "p.add_argument(\"--checkpoint\")",
            "p.add_argument(\"--device\")",
            "p.add_argument(\"--json\", action=\"store_true\")",
            "a=p.parse_args()",
            "print(json.dumps({",
            "    \"text\": a.text,",
            "    \"overall_score\": 120.0,",
            "}))",
        ],
    )

    completed = run_runner(tmp_path, pipeline)

    assert completed.returncode != 0
    assert "overall_score must be between 0 and 100" in completed.stderr

def test_rejects_checkpoint_sha256_mismatch(tmp_path):
    pipeline = write_fake_pipeline(
        tmp_path,
        ["print(\"should not execute\")"],
    )
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"tampered-checkpoint")

    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--pipeline",
            str(pipeline),
            "--pipeline-sha256",
            hashlib.sha256(pipeline.read_bytes()).hexdigest(),
            "--checkpoint",
            str(checkpoint),
            "--checkpoint-sha256",
            "0" * 64,
            "--device",
            "cpu",
            "--audio",
            str(audio),
            "--text",
            "Hello, I am John.",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "checkpoint SHA-256 mismatch" in completed.stderr



def test_rejects_pipeline_sha256_mismatch(tmp_path):
    pipeline = write_fake_pipeline(
        tmp_path,
        ["print(\"should not execute\")"],
    )
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF" + bytes(4) + b"WAVE")
    checkpoint = tmp_path / "checkpoint.pt"
    checkpoint.write_bytes(b"checkpoint")

    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--pipeline",
            str(pipeline),
            "--pipeline-sha256",
            "0" * 64,
            "--checkpoint",
            str(checkpoint),
            "--checkpoint-sha256",
            hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            "--device",
            "cpu",
            "--audio",
            str(audio),
            "--text",
            "Hello, I am John.",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "pipeline SHA-256 mismatch" in completed.stderr
