from collections import defaultdict

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationModelHumanObservation,
    PhoneticCalibrationModelHumanSummary,
)


def summarize_phonetic_calibration_model_human_observations(
    observations: list[PhoneticCalibrationModelHumanObservation],
) -> list[PhoneticCalibrationModelHumanSummary]:
    """Summarize model-human observations by versioned context.

    Resume observaciones modelo-humano por contexto versionado.
    """
    grouped: dict[
        tuple[str, str, str],
        list[PhoneticCalibrationModelHumanObservation],
    ] = defaultdict(list)

    for observation in observations:
        grouped[
            (
                observation.analyzer_id,
                observation.analyzer_version,
                observation.rubric_version,
            )
        ].append(observation)

    summaries: list[PhoneticCalibrationModelHumanSummary] = []

    for (analyzer_id, analyzer_version, rubric_version), group in sorted(
        grouped.items()
    ):
        scores = [item.score for item in group]
        label_counts = {
            "acceptable": sum(item.label_counts["acceptable"] for item in group),
            "variant": sum(item.label_counts["variant"] for item in group),
            "known_error": sum(item.label_counts["known_error"] for item in group),
        }

        summaries.append(
            PhoneticCalibrationModelHumanSummary(
                analyzer_id=analyzer_id,
                analyzer_version=analyzer_version,
                rubric_version=rubric_version,
                observation_count=len(group),
                sample_count=len({item.sample_id for item in group}),
                score_min=min(scores),
                score_max=max(scores),
                score_mean=sum(scores) / len(scores),
                label_counts=label_counts,
                unanimous_count=sum(item.unanimous for item in group),
            )
        )

    return summaries
