from pydantic import BaseModel, model_validator

from app.schemas.evaluation import LessonProductionEvaluationPlan
from app.schemas.pedagogical_feedback import LessonProductionFeedbackPlan


class ProductionEvaluationRuntimeConfig(BaseModel):
    """Provide evaluation and feedback configuration to runtime.

    Proporciona al runtime la configuración de evaluación y feedback.
    """

    lesson_id: str
    evaluation_plan: LessonProductionEvaluationPlan
    feedback_plan: LessonProductionFeedbackPlan

    @model_validator(mode="after")
    def validate_runtime_consistency(
        self,
    ) -> "ProductionEvaluationRuntimeConfig":
        """Keep runtime plans aligned with one lesson and criteria.

        Mantiene los planes runtime alineados con una lección y criterios.
        """
        if self.evaluation_plan.lesson_id != self.lesson_id:
            raise ValueError(
                "Runtime evaluation plan must match lesson_id"
            )

        if self.feedback_plan.lesson_id != self.lesson_id:
            raise ValueError(
                "Runtime feedback plan must match lesson_id"
            )

        criterion_ids = {
            criterion.id
            for criterion in self.evaluation_plan.criteria
        }
        unknown_feedback_criteria = sorted(
            {
                rule.criterion_id
                for rule in self.feedback_plan.rules
            }
            - criterion_ids
        )

        if unknown_feedback_criteria:
            raise ValueError(
                "Runtime feedback references unknown criteria: "
                + ", ".join(unknown_feedback_criteria)
            )

        return self
