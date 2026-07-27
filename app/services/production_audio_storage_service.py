import os
from pathlib import Path
from uuid import UUID, uuid4

from app.schemas.production_audio import ProductionAudioUploadRecord


PRODUCTION_AUDIO_REFERENCE_PREFIX = "production-audio://"
MAX_PRODUCTION_AUDIO_BYTES = 10 * 1024 * 1024


def get_production_audio_storage_dir() -> Path:
    """Return the configured private production-audio directory.

    Devuelve el directorio privado configurado para audios de producción.
    """
    configured = os.getenv("PRODUCTION_AUDIO_DIR")
    if not configured or not configured.strip():
        raise RuntimeError("PRODUCTION_AUDIO_DIR is not configured")

    return Path(configured).expanduser().resolve()


def _validate_wav(payload: bytes) -> None:
    """Reject empty, oversized or non-WAVE payloads.

    Rechaza contenido vacío, demasiado grande o que no sea WAVE.
    """
    if not payload:
        raise ValueError("Production audio cannot be empty")

    if len(payload) > MAX_PRODUCTION_AUDIO_BYTES:
        raise ValueError("Production audio exceeds maximum size")

    if (
        len(payload) < 12
        or payload[0:4] != b"RIFF"
        or payload[8:12] != b"WAVE"
    ):
        raise ValueError("Production audio must be WAV")


def store_production_audio(
    payload: bytes,
    *,
    storage_dir: Path | None = None,
) -> ProductionAudioUploadRecord:
    """Store validated audio privately and return an opaque reference.

    Guarda audio validado de forma privada y devuelve una referencia opaca.
    """
    _validate_wav(payload)

    root = (
        storage_dir.resolve()
        if storage_dir is not None
        else get_production_audio_storage_dir()
    )
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(0o700)

    audio_id = uuid4()
    destination = root / f"{audio_id}.wav"
    temporary = root / f".{audio_id}.tmp"

    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
        temporary.chmod(0o600)
        temporary.replace(destination)
        destination.chmod(0o600)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return ProductionAudioUploadRecord(
        audio_reference=(
            PRODUCTION_AUDIO_REFERENCE_PREFIX + str(audio_id)
        ),
        size_bytes=len(payload),
    )


def resolve_production_audio_path(
    audio_reference: str,
    *,
    storage_dir: Path | None = None,
) -> Path:
    """Resolve one trusted opaque reference to its private WAV path.

    Resuelve una referencia opaca confiable hacia su WAV privado.
    """
    if not audio_reference.startswith(
        PRODUCTION_AUDIO_REFERENCE_PREFIX
    ):
        raise ValueError("Unsupported production audio reference")

    raw_id = audio_reference.removeprefix(
        PRODUCTION_AUDIO_REFERENCE_PREFIX
    )

    try:
        audio_id = UUID(raw_id)
    except ValueError as error:
        raise ValueError(
            "Invalid production audio reference"
        ) from error

    root = (
        storage_dir.resolve()
        if storage_dir is not None
        else get_production_audio_storage_dir()
    )
    path = (root / f"{audio_id}.wav").resolve()

    if path.parent != root:
        raise ValueError("Invalid production audio reference")

    if not path.is_file():
        raise FileNotFoundError(
            "Production audio does not exist"
        )

    return path


def read_production_audio(
    audio_reference: str,
    *,
    storage_dir: Path | None = None,
) -> bytes:
    """Read bytes for internal analyzers without exposing server paths.

    Lee bytes para analizadores internos sin exponer rutas del servidor.
    """
    return resolve_production_audio_path(
        audio_reference,
        storage_dir=storage_dir,
    ).read_bytes()
