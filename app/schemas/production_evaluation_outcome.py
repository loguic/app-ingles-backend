from pydantic import BaseModel, Field

from app.schemas.evaluation import ProductionEvaluationResultRecord
from app.schemas.pedagogical_feedback import ProductionFeedbackRecord


class ProductionEvaluationOutcome(BaseModel):
    """Represent one atomic evaluation and feedback outcome.

    Representa un resultado atómico de evaluación y feedback.
    """

    production_id: int = Field(gt=0)
    evaluation_results: list[
        ProductionEvaluationResultRecord
    ] = Field(min_length=1)
    feedbacks: list[ProductionFeedbackRecord] = Field(min_length=1)
