import pytest
from pydantic import ValidationError

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationDescriptiveReport,
    PhoneticCalibrationHumanEvidenceIdentity,
    PhoneticCalibrationModelHumanSummary,
)
from app.services.phonetic_calibration_comparable_artifact_context_service import (
    build_phonetic_calibration_comparable_artifact_context,
)
from app.services.phonetic_calibration_descriptive_report_artifact_service import (
    build_phonetic_calibration_descriptive_report_artifact,
)


def report(analyzer_version: str) -> PhoneticCalibrationDescriptiveReport:
    return PhoneticCalibrationDescriptiveReport(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        summary=PhoneticCalibrationModelHumanSummary(
            analyzer_id="wavlm-gop-phoneme-scorer",
            analyzer_version=analyzer_version,
            rubric_version="phonetic-rubric/1.0",
            observation_count=1,
            sample_count=1,
            score_min=0.70,
            score_max=0.70,
            score_mean=0.70,
            label_counts={
                "acceptable": 1,
                "variant": 0,
                "known_error": 0,
            },
            unanimous_count=1,
        ),
    )


def artifact(analyzer_version: str):
    return build_phonetic_calibration_descriptive_report_artifact(
        report(analyzer_version),
        "phonetic-calibration-report/1.0",
    )


def human_evidence(
    evidence_sha256: str = "c" * 64,
) -> PhoneticCalibrationHumanEvidenceIdentity:
    return PhoneticCalibrationHumanEvidenceIdentity(
        rubric_version="phonetic-rubric/1.0",
        sample_count=3,
        evidence_sha256=evidence_sha256,
    )


def test_builds_comparable_context_with_same_human_evidence():
    context = build_phonetic_calibration_comparable_artifact_context(
        artifact("wavlm-gop-runner/1.0"),
        artifact("wavlm-gop-runner/2.0"),
        human_evidence(),
        human_evidence(),
    )

    assert context.artifact_comparison.left_analyzer_version == (
        "wavlm-gop-runner/1.0"
    )
    assert context.artifact_comparison.right_analyzer_version == (
        "wavlm-gop-runner/2.0"
    )
    assert context.human_evidence_compatibility.same_evidence is True


def test_rejects_context_with_different_human_evidence():
    with pytest.raises(
        ValidationError,
        match="requires the same human evidence",
    ):
        build_phonetic_calibration_comparable_artifact_context(
            artifact("wavlm-gop-runner/1.0"),
            artifact("wavlm-gop-runner/2.0"),
            human_evidence("c" * 64),
            human_evidence("d" * 64),
        )
