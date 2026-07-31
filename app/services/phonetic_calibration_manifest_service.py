import json
from pathlib import Path

from pydantic import TypeAdapter

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabel,
    PhoneticCalibrationSample,
    RegionalRepresentativePhoneticCalibrationSample,
    RepresentativePhoneticCalibrationSample,
)


_HUMAN_LABELS = TypeAdapter(list[PhoneticCalibrationHumanLabel])
_SAMPLES = TypeAdapter(list[PhoneticCalibrationSample])
_REPRESENTATIVE_SAMPLES = TypeAdapter(list[RepresentativePhoneticCalibrationSample])
_REGIONAL_REPRESENTATIVE_SAMPLES = TypeAdapter(
    list[RegionalRepresentativePhoneticCalibrationSample]
)


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


def load_representative_phonetic_calibration_manifest(
    manifest_path: Path,
) -> list[RepresentativePhoneticCalibrationSample]:
    """Load and validate one representative phonetic calibration manifest.

    Carga y valida un manifiesto representativo de calibración fonética.
    """
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Calibration manifest contains invalid JSON") from error

    return _REPRESENTATIVE_SAMPLES.validate_python(payload)

def load_regional_representative_phonetic_calibration_manifest(
    manifest_path: Path,
) -> list[RegionalRepresentativePhoneticCalibrationSample]:
    """Load and validate one regionally referenced representative manifest.

    Carga y valida un manifiesto representativo con referencia regional.
    """
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Calibration manifest contains invalid JSON") from error

    return _REGIONAL_REPRESENTATIVE_SAMPLES.validate_python(payload)


def load_phonetic_calibration_human_labels(
    labels_path: Path,
) -> list[PhoneticCalibrationHumanLabel]:
    """Load and validate independent human calibration labels.

    Carga y valida etiquetas humanas independientes de calibración.
    """
    if not labels_path.is_file():
        raise FileNotFoundError(labels_path)

    try:
        payload = json.loads(labels_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Calibration labels contain invalid JSON") from error

    return _HUMAN_LABELS.validate_python(payload)
