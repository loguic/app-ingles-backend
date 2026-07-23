from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.content import Unit


SkillStage = Literal[
    "introduce",
    "practice",
    "apply",
    "evaluate",
    "consolidate",
]


LearningModality = Literal[
    "listening",
    "speaking",
    "reading",
    "writing",
    "pronunciation",
]

CoverageStatus = Literal["complete", "incomplete", "pending_approval"]


class SkillCoverage(BaseModel):
    """Record observable coverage for one Skill.

    Registra la cobertura observable de un Skill.
    """

    # Skill represented by this coverage record.
    # Skill representado por este registro de cobertura.
    skill_id: str = Field(pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

    introduced_in_lesson_id: str | None = None
    practice_activity_ids: list[str] = Field(default_factory=list)
    application_activity_ids: list[str] = Field(default_factory=list)
    evaluation_evidence_ids: list[str] = Field(default_factory=list)
    consolidation_activity_ids: list[str] = Field(default_factory=list)
    modalities: list[LearningModality] = Field(default_factory=list)
    status: CoverageStatus = "incomplete"


ValidationSeverity = Literal["error", "warning", "information"]
ValidationStatus = Literal["passed", "failed", "pending"]


class ValidationFinding(BaseModel):
    """Describe one reproducible validation result.

    Describe un resultado reproducible de validación.
    """

    validator_id: str = Field(pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
    severity: ValidationSeverity
    message: str = Field(min_length=1)
    reference_ids: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """Aggregate deterministic validation findings.

    Agrupa los resultados de las validaciones deterministas.
    """

    status: ValidationStatus
    findings: list[ValidationFinding] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_status_consistency(self) -> "ValidationReport":
        """Keep the global status consistent with its findings.

        Mantiene el estado global coherente con sus hallazgos.
        """
        has_errors = any(
            finding.severity == "error"
            for finding in self.findings
        )
        if self.status == "passed" and has_errors:
            raise ValueError("passed validation reports cannot contain errors")
        if self.status == "failed" and not has_errors:
            raise ValueError("failed validation reports require an error")
        return self


class SkillSpecification(BaseModel):
    """Define one measurable learner capability.

    Define una capacidad medible del estudiante.
    """

    # Stable pedagogical identifier shared across content and progress.
    # Identificador pedagógico estable compartido por contenido y progreso.
    id: str = Field(pattern=r"^[a-z0-9]+(?:_[a-z0-9]+)*$")

    # Observable capability the learner must demonstrate.
    # Capacidad observable que deberá demostrar el estudiante.
    description: str = Field(min_length=1)

    # Explicit stages required from the generated unit.
    # Etapas explícitas que deberá cubrir la unidad generada.
    required_stages: list[SkillStage] = Field(min_length=1)

class ContentLimits(BaseModel):
    """Define optional quantitative limits for candidate content.

    Define límites cuantitativos opcionales para el contenido candidato.
    """

    min_lessons: int | None = Field(default=None, ge=0)
    max_lessons: int | None = Field(default=None, ge=0)
    min_examples_per_lesson: int | None = Field(default=None, ge=0)
    max_examples_per_lesson: int | None = Field(default=None, ge=0)
    min_conversations_per_lesson: int | None = Field(default=None, ge=0)
    max_conversations_per_lesson: int | None = Field(default=None, ge=0)
    min_exercises_per_lesson: int | None = Field(default=None, ge=0)
    max_exercises_per_lesson: int | None = Field(default=None, ge=0)
    min_options_per_exercise: int | None = Field(default=None, ge=0)
    max_options_per_exercise: int | None = Field(default=None, ge=0)
    min_turns_per_conversation: int | None = Field(default=None, ge=0)
    max_turns_per_conversation: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_limit_pairs(self) -> "ContentLimits":
        """Keep every declared minimum below its maximum.

        Mantiene cada mínimo declarado por debajo de su máximo.
        """
        pairs = [
            ("min_lessons", "max_lessons"),
            ("min_examples_per_lesson", "max_examples_per_lesson"),
            ("min_conversations_per_lesson", "max_conversations_per_lesson"),
            ("min_exercises_per_lesson", "max_exercises_per_lesson"),
            ("min_options_per_exercise", "max_options_per_exercise"),
            ("min_turns_per_conversation", "max_turns_per_conversation"),
        ]

        for minimum_field, maximum_field in pairs:
            minimum = getattr(self, minimum_field)
            maximum = getattr(self, maximum_field)
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError("minimum cannot exceed maximum")

        return self

class PedagogicalUnitSpecification(BaseModel):
    """Define the approved input contract for one complete unit.

    Define el contrato de entrada aprobado para una unidad completa.
    """

    unit_id: str = Field(pattern=r"^[a-z][0-9]-u[1-9][0-9]*$")
    level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    title: str = Field(min_length=1)
    learner_outcome: str = Field(min_length=1)

    # Previous capabilities may be empty for the first unit of a level.
    # Las capacidades previas pueden estar vacías en la primera unidad.
    prerequisites: list[str] = Field(default_factory=list)

    skills: list[SkillSpecification] = Field(min_length=1)
    required_evidence: list[str] = Field(min_length=1)
    lesson_scope: list[str] = Field(min_length=1)
    language_scope: list[str] = Field(min_length=1)
    pronunciation_scope: list[str] = Field(min_length=1)
    content_constraints: list[str] = Field(min_length=1)
    content_limits: ContentLimits = Field(default_factory=ContentLimits)
    technical_constraints: list[str] = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)


    @model_validator(mode="after")
    def validate_unit_level_consistency(self) -> "PedagogicalUnitSpecification":
        """Match the unit identifier prefix with its CEFR level.

        Comprueba que el prefijo de la unidad coincida con su nivel CEFR.
        """
        expected_prefix = self.level.lower() + "-"
        if not self.unit_id.startswith(expected_prefix):
            raise ValueError("unit_id prefix must match level")
        return self

class PedagogicalUnitCandidate(BaseModel):
    """Represent one isolated unit proposed for human approval.

    Representa una unidad aislada propuesta para aprobación humana.
    """

    specification: PedagogicalUnitSpecification
    candidate_unit: Unit
    skill_coverage: list[SkillCoverage] = Field(min_length=1)
    required_resource_ids: list[str] = Field(default_factory=list)
    validation_report: ValidationReport
    pending_human_decisions: list[str] = Field(default_factory=list)
    proposed_change_summary: list[str] = Field(min_length=1)


    @model_validator(mode="after")
    def validate_candidate_consistency(self) -> "PedagogicalUnitCandidate":
        """Match the candidate unit and coverage with its specification.

        Vincula la unidad candidata y su cobertura con la especificación.
        """
        if self.candidate_unit.id != self.specification.unit_id:
            raise ValueError("candidate unit ID must match specification unit_id")

        skill_ids = [skill.id for skill in self.specification.skills]
        coverage_ids = [coverage.skill_id for coverage in self.skill_coverage]

        if len(coverage_ids) != len(set(coverage_ids)):
            raise ValueError("Skill coverage IDs must be unique")

        missing_ids = sorted(set(skill_ids) - set(coverage_ids))
        if missing_ids:
            raise ValueError(
                "Missing Skill coverage: " + ", ".join(missing_ids)
            )

        unknown_ids = sorted(set(coverage_ids) - set(skill_ids))
        if unknown_ids:
            raise ValueError(
                "Unknown Skill coverage: " + ", ".join(unknown_ids)
            )

        return self
