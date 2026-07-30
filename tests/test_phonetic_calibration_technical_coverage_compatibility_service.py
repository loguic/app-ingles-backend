from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalCoverageIdentity,
)
from app.services.phonetic_calibration_technical_coverage_compatibility_service import (
    compare_phonetic_calibration_technical_coverage,
)


def identity(
    analyzer_version: str,
    *,
    analyzer_id: str = "wavlm-gop-phoneme-scorer",
    rubric_version: str = "phonetic-rubric/1.0",
    sample_count: int = 3,
    sample_ids_sha256: str = "a" * 64,
) -> PhoneticCalibrationTechnicalCoverageIdentity:
    return PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id=analyzer_id,
        analyzer_version=analyzer_version,
        rubric_version=rubric_version,
        sample_count=sample_count,
        sample_ids_sha256=sample_ids_sha256,
    )


def test_same_coverage_allows_different_analyzers():
    compatibility = compare_phonetic_calibration_technical_coverage(
        identity("wavlm-gop-runner/1.0"),
        identity(
            "other-runner/2.0",
            analyzer_id="other-analyzer",
        ),
    )

    assert compatibility.same_coverage is True


def test_different_sample_set_is_not_same_coverage():
    compatibility = compare_phonetic_calibration_technical_coverage(
        identity("wavlm-gop-runner/1.0"),
        identity(
            "wavlm-gop-runner/2.0",
            sample_ids_sha256="b" * 64,
        ),
    )

    assert compatibility.same_coverage is False


def test_different_sample_count_is_not_same_coverage():
    compatibility = compare_phonetic_calibration_technical_coverage(
        identity("wavlm-gop-runner/1.0"),
        identity(
            "wavlm-gop-runner/2.0",
            sample_count=4,
        ),
    )

    assert compatibility.same_coverage is False


def test_different_rubric_is_not_same_coverage():
    compatibility = compare_phonetic_calibration_technical_coverage(
        identity("wavlm-gop-runner/1.0"),
        identity(
            "wavlm-gop-runner/2.0",
            rubric_version="phonetic-rubric/2.0",
        ),
    )

    assert compatibility.same_coverage is False
