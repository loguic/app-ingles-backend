from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    RegionalRepresentativePhoneticCalibrationSample,
)
from app.services.phonetic_calibration_regional_human_evidence_coverage_service import (
    summarize_regional_phonetic_calibration_human_evidence_coverage,
)


def sample(
    sample_id: str,
    speaker_id: str,
    session_id: str,
    reference_locale: str,
) -> RegionalRepresentativePhoneticCalibrationSample:
    return RegionalRepresentativePhoneticCalibrationSample(
        sample_id=sample_id,
        reference_text="Hello, I am John.",
        audio_path=f"audio/{sample_id}.wav",
        audio_sha256="a" * 64,
        expected_class="unlabeled",
        speaker_id=speaker_id,
        session_id=session_id,
        reference_locale=reference_locale,
    )


def agreement(
    sample_id: str,
    rubric_version: str,
    *,
    label_counts: dict,
    unanimous: bool,
) -> PhoneticCalibrationHumanAgreement:
    return PhoneticCalibrationHumanAgreement(
        sample_id=sample_id,
        rubric_version=rubric_version,
        label_count=sum(label_counts.values()),
        labeler_count=sum(label_counts.values()),
        label_counts=label_counts,
        unanimous=unanimous,
    )


def label(
    sample_id: str,
    labeler_id: str,
    rubric_version: str,
    value: str,
) -> PhoneticCalibrationHumanLabel:
    return PhoneticCalibrationHumanLabel(
        sample_id=sample_id,
        labeler_id=labeler_id,
        rubric_version=rubric_version,
        label=value,
    )


def test_summarizes_regional_human_evidence_by_locale_and_rubric():
    samples = [
        sample("human-001", "speaker-001", "session-001", "en-US"),
        sample("human-002", "speaker-001", "session-002", "en-US"),
        sample("human-003", "speaker-002", "session-001", "en-GB"),
    ]
    agreements = [
        agreement(
            "human-001",
            "phonetic-rubric/1.0",
            label_counts={"acceptable": 2, "variant": 0, "known_error": 0},
            unanimous=True,
        ),
        agreement(
            "human-002",
            "phonetic-rubric/1.0",
            label_counts={"acceptable": 0, "variant": 1, "known_error": 1},
            unanimous=False,
        ),
        agreement(
            "human-003",
            "phonetic-rubric/1.0",
            label_counts={"acceptable": 1, "variant": 1, "known_error": 0},
            unanimous=False,
        ),
    ]
    labels = [
        label("human-001", "labeler-001", "phonetic-rubric/1.0", "acceptable"),
        label("human-001", "labeler-002", "phonetic-rubric/1.0", "acceptable"),
        label("human-002", "labeler-001", "phonetic-rubric/1.0", "variant"),
        label("human-002", "labeler-002", "phonetic-rubric/1.0", "known_error"),
        label("human-003", "labeler-001", "phonetic-rubric/1.0", "acceptable"),
        label("human-003", "labeler-003", "phonetic-rubric/1.0", "variant"),
    ]

    coverage = summarize_regional_phonetic_calibration_human_evidence_coverage(
        samples,
        agreements,
        labels,
    )

    assert [(item.reference_locale, item.rubric_version) for item in coverage] == [
        ("en-GB", "phonetic-rubric/1.0"),
        ("en-US", "phonetic-rubric/1.0"),
    ]

    us = coverage[1]
    assert us.sample_count == 2
    assert us.speaker_count == 1
    assert us.session_count == 2
    assert us.label_count == 4
    assert us.labeler_count == 2
    assert us.label_counts == {
        "acceptable": 2,
        "variant": 1,
        "known_error": 1,
    }
    assert us.unanimous_sample_count == 1


def test_preserves_separate_rubric_versions():
    samples = [sample("human-001", "speaker-001", "session-001", "en-US")]
    agreements = [
        agreement(
            "human-001",
            "phonetic-rubric/1.0",
            label_counts={"acceptable": 1, "variant": 0, "known_error": 0},
            unanimous=True,
        ),
        agreement(
            "human-001",
            "phonetic-rubric/2.0",
            label_counts={"acceptable": 0, "variant": 1, "known_error": 0},
            unanimous=True,
        ),
    ]
    labels = [
        label("human-001", "labeler-001", "phonetic-rubric/1.0", "acceptable"),
        label("human-001", "labeler-001", "phonetic-rubric/2.0", "variant"),
    ]

    coverage = summarize_regional_phonetic_calibration_human_evidence_coverage(
        samples,
        agreements,
        labels,
    )

    assert [item.rubric_version for item in coverage] == [
        "phonetic-rubric/1.0",
        "phonetic-rubric/2.0",
    ]


def test_ignores_samples_without_human_agreement():
    samples = [
        sample("human-001", "speaker-001", "session-001", "en-US"),
        sample("human-002", "speaker-002", "session-001", "en-GB"),
    ]
    agreements = [
        agreement(
            "human-001",
            "phonetic-rubric/1.0",
            label_counts={"acceptable": 1, "variant": 0, "known_error": 0},
            unanimous=True,
        )
    ]
    labels = [
        label("human-001", "labeler-001", "phonetic-rubric/1.0", "acceptable")
    ]

    coverage = summarize_regional_phonetic_calibration_human_evidence_coverage(
        samples,
        agreements,
        labels,
    )

    assert len(coverage) == 1
    assert coverage[0].reference_locale == "en-US"


def test_returns_empty_coverage_without_agreements():
    assert summarize_regional_phonetic_calibration_human_evidence_coverage(
        [sample("human-001", "speaker-001", "session-001", "en-US")],
        [],
        [],
    ) == []
