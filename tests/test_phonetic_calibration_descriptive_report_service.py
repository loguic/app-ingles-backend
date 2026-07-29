from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanLabelScoreDistribution,
    PhoneticCalibrationHumanLabelScoreOverlap,
    PhoneticCalibrationModelHumanSummary,
)
from app.services.phonetic_calibration_descriptive_report_service import (
    build_phonetic_calibration_descriptive_reports,
)


def summary(
    analyzer_version: str = "wavlm-gop-runner/1.0",
) -> PhoneticCalibrationModelHumanSummary:
    return PhoneticCalibrationModelHumanSummary(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        observation_count=2,
        sample_count=2,
        score_min=0.20,
        score_max=0.90,
        score_mean=0.55,
        label_counts={
            "acceptable": 1,
            "variant": 1,
            "known_error": 0,
        },
        unanimous_count=1,
    )


def distribution(
    label: str,
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
) -> PhoneticCalibrationHumanLabelScoreDistribution:
    return PhoneticCalibrationHumanLabelScoreDistribution(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        label=label,
        observation_count=1,
        sample_count=1,
        score_q25=0.50,
        score_median=0.60,
        score_q75=0.70,
    )


def overlap(
    left_label: str,
    right_label: str,
    *,
    analyzer_version: str = "wavlm-gop-runner/1.0",
) -> PhoneticCalibrationHumanLabelScoreOverlap:
    return PhoneticCalibrationHumanLabelScoreOverlap(
        analyzer_id="wavlm-gop-phoneme-scorer",
        analyzer_version=analyzer_version,
        rubric_version="phonetic-rubric/1.0",
        left_label=left_label,
        right_label=right_label,
        overlap_lower=0.55,
        overlap_upper=0.65,
        overlap_width=0.10,
        overlaps=True,
    )


def test_builds_report_with_only_matching_versioned_evidence():
    reports = build_phonetic_calibration_descriptive_reports(
        summaries=[summary()],
        distributions=[
            distribution("variant"),
            distribution("acceptable"),
            distribution("known_error", analyzer_version="wavlm-gop-runner/2.0"),
        ],
        overlaps=[
            overlap("variant", "known_error"),
            overlap(
                "acceptable",
                "variant",
                analyzer_version="wavlm-gop-runner/2.0",
            ),
        ],
    )

    assert len(reports) == 1
    report = reports[0]
    assert [item.label for item in report.score_distributions] == [
        "acceptable",
        "variant",
    ]
    assert len(report.overlaps) == 1
    assert report.overlaps[0].left_label == "variant"


def test_builds_empty_collections_when_no_matching_evidence_exists():
    reports = build_phonetic_calibration_descriptive_reports(
        summaries=[summary()],
        distributions=[
            distribution("acceptable", analyzer_version="wavlm-gop-runner/2.0")
        ],
        overlaps=[
            overlap(
                "acceptable",
                "variant",
                analyzer_version="wavlm-gop-runner/2.0",
            )
        ],
    )

    assert reports[0].score_distributions == []
    assert reports[0].overlaps == []


def test_sorts_reports_by_versioned_context():
    reports = build_phonetic_calibration_descriptive_reports(
        summaries=[
            summary("wavlm-gop-runner/2.0"),
            summary("wavlm-gop-runner/1.0"),
        ],
        distributions=[],
        overlaps=[],
    )

    assert [report.analyzer_version for report in reports] == [
        "wavlm-gop-runner/1.0",
        "wavlm-gop-runner/2.0",
    ]
