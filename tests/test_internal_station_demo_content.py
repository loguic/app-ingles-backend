from app.services.internal_station_demo_content_service import (
    load_internal_station_demo_content,
)


def test_internal_station_demo_content_has_two_reusable_situations():
    content = load_internal_station_demo_content()

    assert [item.id for item in content.situations] == [
        "station-toilet",
        "station-exit",
    ]
    assert all(item.reference_audio_provisional for item in content.situations)
    assert all(item.retry_orientation for item in content.situations)


def test_internal_station_demo_content_is_not_active_curriculum():
    content = load_internal_station_demo_content()

    assert content.scope == "internal_demo"
    assert content.active_curriculum is False
