from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.semantic_evaluation import SemanticEvaluationRule


EvaluationDimension = Literal["semantic", "phonetic"]
EvaluationMeasurementMode = Literal["binary", "score"]
EvaluationModality = Literal["text", "voice"]
EvaluationStatus = Literal["passed", "failed"]


class ProductionEvaluationCriterion(BaseModel):
    """Define one evaluable criterion for a learner production.

    Define un criterio evaluable para una producción del estudiante.
    """

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    evidence_definition_id: str
    conversation_id: str
    prompt_id: str
    dimension: EvaluationDimension
    description: str = Field(min_length=1)
    measurement_mode: EvaluationMeasurementMode
    success_threshold: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    applicable_modalities: list[EvaluationModality] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_evaluation_contract(
        self,
    ) -> "ProductionEvaluationCriterion":
        """Protect score and modality invariants.

        Protege los invariantes de puntuación y modalidad.
        """
        if len(self.applicable_modalities) != len(
            set(self.applicable_modalities)
        ):
            raise ValueError(
                "Evaluation criterion modalities must be unique"
            )

        if (
            self.measurement_mode == "score"
            and self.success_threshold is None
        ):
            raise ValueError(
                "Score evaluation criterion requires success_threshold"
            )

        if (
            self.measurement_mode != "score"
            and self.success_threshold is not None
        ):
            raise ValueError(
                "Only score evaluation criterion can define "
                "success_threshold"
            )

        if (
            self.dimension == "phonetic"
            and self.applicable_modalities != ["voice"]
        ):
            raise ValueError(
                "Phonetic evaluation criterion requires voice modality"
            )

        return self


class ProductionEvaluationResult(BaseModel):
    """Represent one evaluated learner production without mastery claims.

    Representa una producción evaluada sin afirmar dominio.
    """

    production_id: int = Field(gt=0)
    criterion_id: str
    status: EvaluationStatus
    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    evaluator_id: str = Field(min_length=1)
    evaluator_version: str = Field(min_length=1)
    evaluated_at: datetime

class LessonProductionEvaluationPlan(BaseModel):
    """Group the evaluation criteria declared for one lesson.

    Agrupa los criterios de evaluación declarados para una lección.
    """

    lesson_id: str
    criteria: list[ProductionEvaluationCriterion] = Field(min_length=1)
    semantic_rules: list[SemanticEvaluationRule] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_unique_criterion_ids(
        self,
    ) -> "LessonProductionEvaluationPlan":
        """Keep criterion identifiers unique inside one lesson.

        Mantiene únicos los identificadores de criterios en una lección.
        """
        criterion_ids = [
            criterion.id
            for criterion in self.criteria
        ]

        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError(
                "Lesson evaluation criterion IDs must be unique"
            )

        rule_ids = [rule.id for rule in self.semantic_rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError(
                "Lesson semantic evaluation rule IDs must be unique"
            )

        semantic_criterion_ids = {
            criterion.id
            for criterion in self.criteria
            if criterion.dimension == "semantic"
        }
        rule_criterion_ids = [
            rule.criterion_id
            for rule in self.semantic_rules
        ]

        if len(rule_criterion_ids) != len(set(rule_criterion_ids)):
            raise ValueError(
                "Semantic criteria can define only one rule"
            )

        unknown_criterion_ids = sorted(
            set(rule_criterion_ids) - semantic_criterion_ids
        )
        if unknown_criterion_ids:
            raise ValueError(
                "Semantic rules reference unknown semantic criteria: "
                + ", ".join(unknown_criterion_ids)
            )

        return self

