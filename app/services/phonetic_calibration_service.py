from hashlib import sha256
from pathlib import Path

from app.schemas.phonetic_calibration import (
    PhoneticCalibrationMeasurement,
    PhoneticCalibrationSample,
    RegionalRepresentativePhoneticCalibrationCoverage,
    RegionalRepresentativePhoneticCalibrationSample,
    RepresentativePhoneticCalibrationCoverage,
    RepresentativePhoneticCalibrationObservation,
    RepresentativePhoneticCalibrationSample,
)
from app.services.production_audio_phonetic_analyzer import (
    AcousticPhoneticScorer,
)
from app.services.phonetic_calibration_manifest_service import (
    load_phonetic_calibration_manifest,
    load_representative_phonetic_calibration_manifest,
)
from app.services.phonetic_analyzer_runtime_service import (
    build_runtime_acoustic_phonetic_scorer,
)


def measure_phonetic_calibration_sample(
    sample: PhoneticCalibrationSample,
    scorer: AcousticPhoneticScorer,
    *,
    corpus_dir: Path,
) -> PhoneticCalibrationMeasurement:
    """Measure one verified calibration sample without pedagogical decisions.

    Mide una muestra verificada sin tomar decisiones pedagógicas.
    """

    corpus_root = corpus_dir.resolve()
    audio_path = (corpus_root / sample.audio_path).resolve()

    if not audio_path.is_relative_to(corpus_root):
        raise ValueError("Calibration audio must stay inside corpus directory")

    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)

    actual_sha256 = sha256(audio_path.read_bytes()).hexdigest()
    if actual_sha256 != sample.audio_sha256:
        raise ValueError("Calibration audio SHA-256 does not match sample")

    measurement = scorer.score(
        audio_path,
        reference_text=sample.reference_text,
    )

    return PhoneticCalibrationMeasurement(
        sample_id=sample.sample_id,
        score=measurement.score,
        analyzer_id=measurement.analyzer_id,
        analyzer_version=measurement.analyzer_version,
        analyzed_at=measurement.analyzed_at,
    )


def measure_phonetic_calibration_corpus(
    samples: list[PhoneticCalibrationSample],
    scorer: AcousticPhoneticScorer,
    *,
    corpus_dir: Path,
) -> list[PhoneticCalibrationMeasurement]:
    """Measure a controlled corpus while preserving sample identity.

    Mide un corpus controlado preservando la identidad de cada muestra.
    """

    seen_sample_ids: set[str] = set()
    measurements: list[PhoneticCalibrationMeasurement] = []

    for sample in samples:
        if sample.sample_id in seen_sample_ids:
            raise ValueError("Calibration sample_id must be unique")
        seen_sample_ids.add(sample.sample_id)
        measurements.append(
            measure_phonetic_calibration_sample(
                sample,
                scorer,
                corpus_dir=corpus_dir,
            )
        )

    return measurements


def summarize_representative_phonetic_calibration_coverage(
    samples: list[RepresentativePhoneticCalibrationSample],
) -> RepresentativePhoneticCalibrationCoverage:
    """Summarize observable speaker and session coverage.

    Resume la cobertura observable de hablantes y sesiones.
    """
    return RepresentativePhoneticCalibrationCoverage(
        sample_count=len(samples),
        speaker_count=len({sample.speaker_id for sample in samples}),
        session_count=len({(sample.speaker_id, sample.session_id) for sample in samples}),
    )


def summarize_regional_representative_phonetic_calibration_coverage(
    samples: list[RegionalRepresentativePhoneticCalibrationSample],
) -> list[RegionalRepresentativePhoneticCalibrationCoverage]:
    """Summarize observable corpus coverage by pronunciation reference locale.

    Resume la cobertura observable del corpus por variante regional de referencia.
    """
    locales = sorted({sample.reference_locale for sample in samples})

    return [
        RegionalRepresentativePhoneticCalibrationCoverage(
            reference_locale=locale,
            sample_count=sum(
                sample.reference_locale == locale
                for sample in samples
            ),
            speaker_count=len(
                {
                    sample.speaker_id
                    for sample in samples
                    if sample.reference_locale == locale
                }
            ),
            session_count=len(
                {
                    (sample.speaker_id, sample.session_id)
                    for sample in samples
                    if sample.reference_locale == locale
                }
            ),
        )
        for locale in locales
    ]


def measure_representative_phonetic_calibration_corpus(
    samples: list[RepresentativePhoneticCalibrationSample],
    scorer: AcousticPhoneticScorer,
    *,
    corpus_dir: Path,
) -> list[RepresentativePhoneticCalibrationObservation]:
    """Measure a representative corpus while preserving speaker and session.

    Mide un corpus representativo preservando hablante y sesión.
    """
    measurements = measure_phonetic_calibration_corpus(
        samples,
        scorer,
        corpus_dir=corpus_dir,
    )
    return [
        RepresentativePhoneticCalibrationObservation(
            sample=sample,
            measurement=measurement,
        )
        for sample, measurement in zip(samples, measurements, strict=True)
    ]


def measure_runtime_phonetic_calibration_corpus(
    samples: list[PhoneticCalibrationSample],
    *,
    corpus_dir: Path,
) -> list[PhoneticCalibrationMeasurement]:
    """Measure a calibration corpus with the configured production scorer.

    Mide un corpus de calibración con el scorer productivo configurado.
    """
    return measure_phonetic_calibration_corpus(
        samples,
        build_runtime_acoustic_phonetic_scorer(),
        corpus_dir=corpus_dir,
    )


def measure_runtime_phonetic_calibration_manifest(
    manifest_path: Path,
) -> list[PhoneticCalibrationMeasurement]:
    """Measure every sample declared by one calibration manifest.

    Mide todas las muestras declaradas por un manifiesto de calibración.
    """
    samples = load_phonetic_calibration_manifest(manifest_path)
    return measure_runtime_phonetic_calibration_corpus(
        samples,
        corpus_dir=manifest_path.parent,
    )

def measure_runtime_representative_phonetic_calibration_manifest(
    manifest_path: Path,
) -> list[RepresentativePhoneticCalibrationObservation]:
    """Measure a representative manifest with the configured production scorer.

    Mide un manifiesto representativo con el scorer productivo configurado.
    """
    samples = load_representative_phonetic_calibration_manifest(manifest_path)
    return measure_representative_phonetic_calibration_corpus(
        samples,
        build_runtime_acoustic_phonetic_scorer(),
        corpus_dir=manifest_path.parent,
    )
