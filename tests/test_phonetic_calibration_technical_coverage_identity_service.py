import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationModelHumanObservation,
)
from app.services.phonetic_calibration_technical_coverage_identity_service import (
    build_phonetic_calibration_technical_coverage_identity,
)


def observation(
    sample_id: str,
    *,
    analyzer_id: str = "wavlm-gop-phoneme-scorer",
    analyzer_version: str = "wavlm-gop-runner/1.0",
    rubric_version: str = "phonetic-rubric/1.0",
    score: float = 0.70,
) -> PhoneticCalibrationModelHumanObservation:
    return PhoneticCalibrationModelHumanObservation(
        sample_id=sample_id,
        analyzer_id=analyzer_id,
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        score=score,
        label_count=1,
        labeler_count=1,
        label_counts={
            "acceptable": 1,
            "variant": 0,
            "known_error": 0,
        },
        unanimous=True,
    )


def build_identity(observations):
    return build_phonetic_calibration_technical_coverage_identity(
        observations,
        "wavlm-gop-phoneme-scorer",
        "wavlm-gop-runner/1.0",
        "phonetic-rubric/1.0",
    )


def test_same_sample_coverage_in_different_order_has_same_identity():
    first = build_identity([
        observation("sample-2"),
        observation("sample-1"),
    ])
    second = build_identity([
        observation("sample-1"),
        observation("sample-2"),
    ])

    assert first == second
    assert first.sample_count == 2


def test_duplicate_observation_does_not_change_sample_coverage_identity():
    first = build_identity([observation("sample-1")])
    second = build_identity([
        observation("sample-1"),
        observation("sample-1", score=0.80),
    ])

    assert first == second
    assert first.sample_count == 1


def test_different_sample_coverage_changes_identity():
    first = build_identity([observation("sample-1")])
    second = build_identity([
        observation("sample-1"),
        observation("sample-2"),
    ])

    assert first.sample_ids_sha256 != second.sample_ids_sha256
    assert second.sample_count == 2


def test_ignores_observations_from_other_versioned_contexts():
    identity = build_identity([
        observation("sample-1"),
        observation(
            "sample-2",
            analyzer_version="wavlm-gop-runner/2.0",
        ),
        observation(
            "sample-3",
            rubric_version="phonetic-rubric/2.0",
        ),
    ])

    expected = build_identity([observation("sample-1")])

    assert identity == expected


def test_rejects_context_without_matching_observations():
    with pytest.raises(
        ValueError,
        match="Technical coverage identity requires matching observations",
    ):
        build_identity([
            observation(
                "sample-1",
                analyzer_version="wavlm-gop-runner/2.0",
            )
        ])
