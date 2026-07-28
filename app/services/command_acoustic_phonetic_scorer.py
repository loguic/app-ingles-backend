import json
import subprocess
from pathlib import Path

from app.schemas.phonetic_evidence import AcousticPhoneticMeasurement


class CommandAcousticPhoneticScorer:
    """Execute an isolated acoustic analyzer through a strict JSON contract.

    Ejecuta un analizador acústico aislado mediante un contrato JSON estricto.
    """

    def __init__(
        self,
        command: list[str],
        *,
        timeout_seconds: float = 30.0,
    ) -> None:
        if not command:
            raise ValueError("Acoustic analyzer command cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("Acoustic analyzer timeout must be positive")

        self._command = list(command)
        self._timeout_seconds = timeout_seconds

    def score(
        self,
        audio_path: Path,
        *,
        reference_text: str,
    ) -> AcousticPhoneticMeasurement:
        if not audio_path.is_file():
            raise FileNotFoundError("Acoustic analyzer audio does not exist")

        if not reference_text.strip():
            raise ValueError(
                "Acoustic analyzer requires non-blank reference text"
            )

        try:
            completed = subprocess.run(
                [
                    *self._command,
                    "--audio",
                    str(audio_path),
                    "--text",
                    reference_text,
                    "--json",
                ],
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Acoustic analyzer timed out"
            ) from error

        if completed.returncode != 0:
            detail = completed.stderr.strip()
            raise RuntimeError(
                "Acoustic analyzer failed"
                + (": " + detail if detail else "")
            )

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Acoustic analyzer returned invalid JSON"
            ) from error

        return AcousticPhoneticMeasurement.model_validate(payload)
