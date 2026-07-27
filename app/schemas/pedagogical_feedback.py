from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationStatus


class ProductionFeedbackRule(BaseModel):
    """Declare deterministic feedback for one evaluation criterion.

    Declara feedback determinista para un criterio evaluativo.
    """

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    criterion_id: str
    passed_message: str = Field(min_length=1)
    passed_guidance: str = Field(min_length=1)
    failed_message: str = Field(min_length=1)
    failed_guidance: str = Field(min_length=1)


class ProductionFeedback(BaseModel):
    """Represent traceable pedagogical feedback for one evaluation.

    Representa feedback pedagógico trazable para una evaluación.
    """

    evaluation_result_id: int = Field(gt=0)
    production_id: int = Field(gt=0)
    criterion_id: str
    evaluation_status: EvaluationStatus
    criterion_description: str = Field(min_length=1)
    message: str = Field(min_length=1)
    guidance: str = Field(min_length=1)
    generator_id: str = Field(min_length=1)
    generator_version: str = Field(min_length=1)


class LessonProductionFeedbackPlan(BaseModel):
    """Declare feedback rules available for one lesson.

    Declara las reglas de feedback disponibles para una lección.
    """

    lesson_id: str
    rules: list[ProductionFeedbackRule] = Field(min_length=1)

    @classmethod
    def _rule_ids(cls, rules):
        return [rule.id for rule in rules]

    def model_post_init(self, __context) -> None:
        rule_ids = self._rule_ids(self.rules)
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError(
                "Lesson feedback rule IDs must be unique"
            )

        criterion_ids = [
            rule.criterion_id
            for rule in self.rules
        ]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError(
                "Feedback criteria can define only one rule"
            )


class ProductionFeedbackRecord(ProductionFeedback):
    """Expose the persistent identity and timestamp of feedback.

    Expone la identidad persistente y fecha del feedback.
    """

    feedback_id: int = Field(gt=0)
    generated_at: datetime
