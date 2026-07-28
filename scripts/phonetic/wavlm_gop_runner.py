import argparse
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


ANALYZER_ID = "wavlm-gop-phoneme-scorer"
RUNNER_VERSION = "1.0"


def calculate_sha256(path: Path) -> str:
    # Hash large checkpoints incrementally without loading them into memory.
    # Calcula checkpoints grandes por bloques sin cargarlos en memoria.
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sha256(
    path: Path,
    expected_sha256: str,
    *,
    label: str,
) -> str:
    # Verify runtime artifacts before any external model code executes.
    # Verifica artefactos runtime antes de ejecutar código externo del modelo.
    if not path.is_file():
        raise FileNotFoundError(label + " does not exist")

    expected = expected_sha256.strip().lower()
    if len(expected) != 64 or any(
        char not in "0123456789abcdef"
        for char in expected
    ):
        raise ValueError(
            label + " SHA-256 must be 64 hexadecimal characters"
        )

    actual = calculate_sha256(path)
    if actual != expected:
        raise ValueError(label + " SHA-256 mismatch")

    return actual

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--pipeline", required=True)
    parser.add_argument("--pipeline-sha256", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-sha256", required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.text.strip():
        raise ValueError("Reference text cannot be blank")

    pipeline_path = Path(args.pipeline)
    actual_pipeline_sha256 = verify_sha256(
        pipeline_path,
        args.pipeline_sha256,
        label="WavLM/GOP pipeline",
    )

    checkpoint_path = Path(args.checkpoint)
    actual_checkpoint_sha256 = verify_sha256(
        checkpoint_path,
        args.checkpoint_sha256,
        label="WavLM/GOP checkpoint",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(pipeline_path),
            "--audio",
            args.audio,
            "--text",
            args.text,
            "--checkpoint",
            args.checkpoint,
            "--device",
            args.device,
            "--json",
        ],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )

    if completed.returncode != 0:
        detail = completed.stderr.strip()
        raise RuntimeError(
            "WavLM/GOP pipeline failed"
            + (": " + detail if detail else "")
        )

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(
            "WavLM/GOP pipeline returned invalid JSON"
        ) from error

    if payload.get("text") != args.text:
        raise ValueError(
            "WavLM/GOP result text does not match reference text"
        )

    overall_score = payload.get("overall_score")
    if (
        not isinstance(overall_score, (int, float))
        or isinstance(overall_score, bool)
        or not 0.0 <= float(overall_score) <= 100.0
    ):
        raise ValueError(
            "WavLM/GOP overall_score must be between 0 and 100"
        )

    measurement = {
        "score": float(overall_score) / 100.0,
        "analyzer_id": ANALYZER_ID,
        "analyzer_version": (
            f"wavlm-gop-runner/{RUNNER_VERSION}"
            f"|pipeline-sha256:{actual_pipeline_sha256}"
            f"|checkpoint-sha256:{actual_checkpoint_sha256}"
        ),
        "analyzed_at": datetime.now(UTC).isoformat(),
    }

    print(json.dumps(measurement))


if __name__ == "__main__":
    main()

