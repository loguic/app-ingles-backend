from app.schemas.phonetic_calibration import PhoneticCalibrationHumanLabel
from app.services.phonetic_calibration_human_agreement_service import (
    summarize_phonetic_calibration_human_agreements,
)


def build_label(
    labeler_id: str,
    label: str,
    rubric_version: str = "phonetic-rubric/1.0",
) -> PhoneticCalibrationHumanLabel:
    return PhoneticCalibrationHumanLabel(
        sample_id="human-001",
        labeler_id=labeler_id,
        rubric_version=rubric_version,
        label=label,
    )


def test_summarizes_observed_disagreement():
    agreements = summarize_phonetic_calibration_human_agreements([
        build_label("labeler-001", "acceptable"),
        build_label("labeler-002", "variant"),
    ])

    assert len(agreements) == 1
    assert agreements[0].label_count == 2
    assert agreements[0].labeler_count == 2
    assert agreements[0].label_counts == {
        "acceptable": 1,
        "variant": 1,
        "known_error": 0,
    }
    assert agreements[0].unanimous is False


def test_reports_unanimous_observation():
    agreements = summarize_phonetic_calibration_human_agreements([
        build_label("labeler-001", "acceptable"),
        build_label("labeler-002", "acceptable"),
    ])

    assert agreements[0].unanimous is True


def test_keeps_rubric_versions_separate():
    agreements = summarize_phonetic_calibration_human_agreements([
        build_label("labeler-001", "acceptable", "phonetic-rubric/1.0"),
        build_label("labeler-001", "known_error", "phonetic-rubric/2.0"),
    ])

    assert len(agreements) == 2
    assert [item.rubric_version for item in agreements] == [
        "phonetic-rubric/1.0",
        "phonetic-rubric/2.0",
    ]

def test_summarizes_versioned_b142_human_labels_example():
    from pathlib import Path

    from app.services.phonetic_calibration_manifest_service import (
        load_phonetic_calibration_human_labels,
    )

    labels = load_phonetic_calibration_human_labels(
        Path("calibration/phonetic/human-labels.example.json")
    )
    agreements = summarize_phonetic_calibration_human_agreements(labels)

    assert len(agreements) == 1
    agreement = agreements[0]
    assert agreement.sample_id == "human-001"
    assert agreement.rubric_version == "phonetic-rubric/1.0"
    assert agreement.label_count == 2
    assert agreement.labeler_count == 2
    assert agreement.label_counts == {
        "acceptable": 1,
        "variant": 1,
        "known_error": 0,
    }
    assert agreement.unanimous is False
