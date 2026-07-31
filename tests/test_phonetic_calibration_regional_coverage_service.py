from app.schemas.phonetic_calibration import (
    RegionalRepresentativePhoneticCalibrationSample,
)
from app.services.phonetic_calibration_service import (
    summarize_regional_representative_phonetic_calibration_coverage,
)


def sample(
    index: int,
    speaker_id: str,
    session_id: str,
    reference_locale: str,
) -> RegionalRepresentativePhoneticCalibrationSample:
    return RegionalRepresentativePhoneticCalibrationSample(
        sample_id=f"human-{index:03d}",
        reference_text="Hello, I am John.",
        audio_path=f"audio/human-{index:03d}.wav",
        audio_sha256="a" * 64,
        expected_class="unlabeled",
        speaker_id=speaker_id,
        session_id=session_id,
        reference_locale=reference_locale,
    )


def test_summarizes_coverage_independently_by_reference_locale():
    coverage = summarize_regional_representative_phonetic_calibration_coverage(
        [
            sample(1, "speaker-001", "session-001", "en-US"),
            sample(2, "speaker-001", "session-002", "en-US"),
            sample(3, "speaker-002", "session-001", "en-US"),
            sample(4, "speaker-001", "session-001", "en-GB"),
            sample(5, "speaker-003", "session-001", "en-GB"),
        ]
    )

    assert [item.reference_locale for item in coverage] == ["en-GB", "en-US"]

    gb, us = coverage

    assert gb.sample_count == 2
    assert gb.speaker_count == 2
    assert gb.session_count == 2

    assert us.sample_count == 3
    assert us.speaker_count == 2
    assert us.session_count == 3


def test_returns_empty_coverage_for_empty_corpus():
    assert summarize_regional_representative_phonetic_calibration_coverage([]) == []
