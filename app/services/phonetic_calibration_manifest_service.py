import json
from pathlib import Path

from pydantic import TypeAdapter

from app.schemas.phonetic_calibration import PhoneticCalibrationSample


_SAMPLES = TypeAdapter(list[PhoneticCalibrationSample])


def load_phonetic_calibration_manifest(
    manifest_path: Path,
) -> list[PhoneticCalibrationSample]:
    """Load and validate one phonetic calibration manifest.

    Carga y valida un manifiesto de calibración fonética.
    """
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Calibration manifest contains invalid JSON") from error

    return _SAMPLES.validate_python(payload)
