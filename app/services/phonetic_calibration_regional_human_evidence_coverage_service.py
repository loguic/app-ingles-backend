from collections import defaultdict

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationHumanAgreement,
    PhoneticCalibrationHumanLabel,
    RegionalPhoneticCalibrationHumanEvidenceCoverage,
    RegionalRepresentativePhoneticCalibrationSample,
)


def summarize_regional_phonetic_calibration_human_evidence_coverage(
    samples: list[RegionalRepresentativePhoneticCalibrationSample],
    agreements: list[PhoneticCalibrationHumanAgreement],
    labels: list[PhoneticCalibrationHumanLabel],
) -> list[RegionalPhoneticCalibrationHumanEvidenceCoverage]:
    """Summarize reviewed human evidence by reference locale and rubric.

    Resume evidencia humana revisada por variante de referencia y rúbrica.
    """
    samples_by_id = {sample.sample_id: sample for sample in samples}

    grouped_agreements: dict[
        tuple[str, str],
        list[tuple[RegionalRepresentativePhoneticCalibrationSample, PhoneticCalibrationHumanAgreement]],
    ] = defaultdict(list)

    for agreement in agreements:
        sample = samples_by_id.get(agreement.sample_id)
        if sample is None:
            continue

        grouped_agreements[
            (sample.reference_locale, agreement.rubric_version)
        ].append((sample, agreement))

    coverage: list[RegionalPhoneticCalibrationHumanEvidenceCoverage] = []

    for (reference_locale, rubric_version), group in sorted(grouped_agreements.items()):
        sample_ids = {sample.sample_id for sample, _agreement in group}

        matching_labels = [
            label
            for label in labels
            if label.sample_id in sample_ids
            and label.rubric_version == rubric_version
        ]

        coverage.append(
            RegionalPhoneticCalibrationHumanEvidenceCoverage(
                reference_locale=reference_locale,
                rubric_version=rubric_version,
                sample_count=len(sample_ids),
                speaker_count=len(
                    {sample.speaker_id for sample, _agreement in group}
                ),
                session_count=len(
                    {
                        (sample.speaker_id, sample.session_id)
                        for sample, _agreement in group
                    }
                ),
                label_count=sum(
                    agreement.label_count
                    for _sample, agreement in group
                ),
                labeler_count=len(
                    {label.labeler_id for label in matching_labels}
                ),
                label_counts={
                    "acceptable": sum(
                        agreement.label_counts["acceptable"]
                        for _sample, agreement in group
                    ),
                    "variant": sum(
                        agreement.label_counts["variant"]
                        for _sample, agreement in group
                    ),
                    "known_error": sum(
                        agreement.label_counts["known_error"]
                        for _sample, agreement in group
                    ),
                },
                unanimous_sample_count=sum(
                    agreement.unanimous
                    for _sample, agreement in group
                ),
            )
        )

    return coverage
