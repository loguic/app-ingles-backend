from pathlib import Path

from app.schemas.internal_station_demo import InternalStationDemoContent


_CONTENT_PATH = (
    Path(__file__).resolve().parents[2]
    / "content"
    / "internal_demo"
    / "station_situations.v1.json"
)


def load_internal_station_demo_content() -> InternalStationDemoContent:
    """Load non-runtime demo content without selecting active curriculum."""

    return InternalStationDemoContent.model_validate_json(_CONTENT_PATH.read_bytes())
