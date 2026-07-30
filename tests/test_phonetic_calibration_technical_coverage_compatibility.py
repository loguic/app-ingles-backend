from app.schemas.phonetic_calibration import (
    PhoneticCalibrationTechnicalCoverageCompatibility,
    PhoneticCalibrationTechnicalCoverageIdentity,
)


def identity(
    analyzer_version: str,
    sample_ids_sha256: str,
    *,
    sample_count: int = 3,
) -> PhoneticCalibrationTechnicalCoverageIdentity:
    return PhoneticCalibrationTechnicalCoverageIdentity(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        sample_count=sample_count,
        sample_ids_sha256=sample_ids_sha256,
    )


def test_accepts_matching_technical_coverage_compatibility():
    left = identity("wavlm-gop-runner/1.0", "a" * 64)
    right = identity("wavlm-gop-runner/2.0", "a" * 64)

    compatibility = PhoneticCalibrationTechnicalCoverageCompatibility(
        left=left,
        right=right,
        same_coverage=True,
    )

    assert compatibility.left == left
    assert compatibility.right == right
    assert compatibility.same_coverage is True


def test_accepts_non_matching_technical_coverage_compatibility():
    left = identity("wavlm-gop-runner/1.0", "a" * 64)
    right = identity("wavlm-gop-runner/2.0", "b" * 64)

    compatibility = PhoneticCalibrationTechnicalCoverageCompatibility(
        left=left,
        right=right,
        same_coverage=False,
    )

    assert compatibility.left.sample_ids_sha256 == "a" * 64
    assert compatibility.right.sample_ids_sha256 == "b" * 64
    assert compatibility.same_coverage is False
