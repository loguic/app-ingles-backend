from typing import Protocol

from app.schemas.conversation_production import LearnerProductionRecord
from app.schemas.evaluation import ProductionEvaluationCriterion
from app.schemas.phonetic_evidence import PhoneticEvaluationEvidence


class PhoneticAnalyzer(Protocol):
    # Produce acoustic evidence without deciding pedagogical success.
    # Produce evidencia acústica sin decidir el éxito pedagógico.
    def analyze(
        self,
        production: LearnerProductionRecord,
        criterion: ProductionEvaluationCriterion,
        *,
        reference_text: str,
    ) -> PhoneticEvaluationEvidence:
        ...
