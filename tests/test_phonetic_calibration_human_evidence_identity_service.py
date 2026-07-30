import pytest

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
)
from app.services.phonetic_calibration_human_evidence_identity_service import (
    build_phonetic_calibration_human_evidence_identity,
)


def agreement(
    sample_id: str,
    *,
    rubric_version: str = "phonetic-rubric/1.0",
    acceptable: int = 2,
    variant: int = 0,
    known_error: int = 0,
) -> PhoneticCalibrationHumanAgreement:
    counts = {
        "acceptable": acceptable,
        "variant": variant,
        "known_error": known_error,
    }
    return PhoneticCalibrationHumanAgreement(
        sample_id=sample_id,
        rubric_version=rubric_version,
        label_count=sum(counts.values()),
        labeler_count=sum(counts.values()),
        label_counts=counts,
        unanimous=sum(count > 0 for count in counts.values()) == 1,
    )


def test_same_human_evidence_in_different_order_has_same_identity():
    first = build_phonetic_calibration_human_evidence_identity(
        [
            agreement("sample-2", variant=1, acceptable=1),
            agreement("sample-1"),
        ],
        "phonetic-rubric/1.0",
    )
    second = build_phonetic_calibration_human_evidence_identity(
        [
            agreement("sample-1"),
            agreement("sample-2", variant=1, acceptable=1),
        ],
        "phonetic-rubric/1.0",
    )

    assert first == second
    assert first.sample_count == 2


def test_changed_human_evidence_changes_identity():
    first = build_phonetic_calibration_human_evidence_identity(
        [agreement("sample-1")],
        "phonetic-rubric/1.0",
    )
    second = build_phonetic_calibration_human_evidence_identity(
        [agreement("sample-1", acceptable=1, variant=1)],
        "phonetic-rubric/1.0",
    )

    assert first.evidence_sha256 != second.evidence_sha256


def test_ignores_agreements_from_other_rubrics():
    identity = build_phonetic_calibration_human_evidence_identity(
        [
            agreement("sample-1"),
            agreement(
                "sample-2",
                rubric_version="phonetic-rubric/2.0",
                known_error=2,
                acceptable=0,
            ),
        ],
        "phonetic-rubric/1.0",
    )

    expected = build_phonetic_calibration_human_evidence_identity(
        [agreement("sample-1")],
        "phonetic-rubric/1.0",
    )

    assert identity == expected
    assert identity.sample_count == 1


def test_rejects_rubric_without_matching_agreements():
    with pytest.raises(
        ValueError,
        match="Human evidence identity requires matching agreements",
    ):
        build_phonetic_calibration_human_evidence_identity(
            [agreement("sample-1")],
            "phonetic-rubric/2.0",
        )
