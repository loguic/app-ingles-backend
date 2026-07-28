from pathlib import Path
from typing import Protocol

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.phonetic_evidence import (
    AcousticPhoneticMeasurement,
    PhoneticEvaluationEvidence,
)
from app.services.production_audio_storage_service import (
    resolve_production_audio_path,
)


class AcousticPhoneticScorer(Protocol):
    """Score one resolved audio file against explicit reference text.

    Puntúa un audio resuelto contra un texto de referencia explícito.
    """

    def score(
        self,
        audio_path: Path,
        *,
        reference_text: str,
    ) -> AcousticPhoneticMeasurement:
        ...


class ProductionAudioPhoneticAnalyzer:
    """Bridge stored production audio to a domain-neutral acoustic scorer.

    Conecta audio almacenado con un scorer acústico neutral al dominio.
    """

    def __init__(
        self,
        scorer: AcousticPhoneticScorer,
        *,
        storage_dir: Path | None = None,
    ) -> None:
        self._scorer = scorer
        self._storage_dir = storage_dir

    def analyze(
        self,
        production: LearnerProductionRecord,
        criterion: ProductionEvaluationCriterion,
        *,
        reference_text: str,
    ) -> PhoneticEvaluationEvidence:
        if production.modality != "voice":
            raise ValueError(
                "Production audio analyzer requires voice production"
            )

        if production.audio_reference is None:
            raise ValueError(
                "Voice production requires audio reference"
            )

        audio_path = resolve_production_audio_path(
            production.audio_reference,
            storage_dir=self._storage_dir,
        )

        measurement = self._scorer.score(
            audio_path,
            reference_text=reference_text,
        )

        return PhoneticEvaluationEvidence(
            production_id=production.production_id,
            criterion_id=criterion.id,
            audio_reference=production.audio_reference,
            score=measurement.score,
            analyzer_id=measurement.analyzer_id,
            analyzer_version=measurement.analyzer_version,
            analyzed_at=measurement.analyzed_at,
        )
