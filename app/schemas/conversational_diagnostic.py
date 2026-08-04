from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


DiagnosticAgeProfile = Literal["6-8", "9-12", "13-17", "adult"]
DiagnosticSessionStatus = Literal[
    "in_progress",
    "provisional",
    "completed",
    "cancelled",
]


class ConversationalDiagnosticSession(BaseModel):
    """Represent one traceable conversational diagnostic session.

    Representa una sesión trazable de diagnóstico conversacional.
    """

    diagnostic_session_id: str
    user_id: str
    age_profile: DiagnosticAgeProfile
    status: DiagnosticSessionStatus = "in_progress"
    started_at: datetime
    completed_at: datetime | None = None

    @model_validator(mode="after")
    def validate_session_timeline(
        self,
    ) -> "ConversationalDiagnosticSession":
        """Protect the temporal coherence of the session.

        Protege la coherencia temporal de la sesión.
        """
        if self.status == "in_progress" and self.completed_at is not None:
            raise ValueError(
                "In-progress diagnostic session cannot define completed_at"
            )

        if self.status != "in_progress" and self.completed_at is None:
            raise ValueError(
                "Finished diagnostic session requires completed_at"
            )

        if (
            self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError(
                "Diagnostic session completed_at cannot precede started_at"
            )

        return self

DiagnosticAutonomyLevel = Literal[
    "supported",
    "developing",
    "independent",
]


class ConversationalDiagnosticContext(BaseModel):
    """Store minimal authorized context for one diagnostic session.

    Conserva el contexto mínimo autorizado de una sesión diagnóstica.
    """

    context_id: str
    diagnostic_session_id: str
    usual_languages: list[str] = Field(min_length=1)
    previous_english_contact: str
    general_interests: list[str] = Field(default_factory=list)
    learning_goals: list[str] = Field(default_factory=list)
    autonomy_level: DiagnosticAutonomyLevel
    responsible_adult_present: bool | None = None
    audio_authorized: bool = False

    @model_validator(mode="after")
    def validate_context_lists(
        self,
    ) -> "ConversationalDiagnosticContext":
        """Require unique, non-blank contextual values.

        Exige valores contextuales únicos y no vacíos.
        """
        collections = {
            "usual_languages": self.usual_languages,
            "general_interests": self.general_interests,
            "learning_goals": self.learning_goals,
        }

        for field_name, values in collections.items():
            normalized = [value.strip() for value in values]

            if any(not value for value in normalized):
                raise ValueError(
                    field_name + " cannot contain blank values"
                )

            if len(normalized) != len(set(normalized)):
                raise ValueError(
                    field_name + " must contain unique values"
                )

        if not self.context_id.strip():
            raise ValueError("context_id cannot be blank")

        if not self.previous_english_contact.strip():
            raise ValueError(
                "previous_english_contact cannot be blank"
            )

        return self

DiagnosticActivityStage = Literal[
    "adaptation",
    "listening_comprehension",
    "initial_response",
    "guided_construction",
    "connected_exchange",
    "transfer",
    "context_selection",
]
DiagnosticActivityModality = Literal[
    "listening",
    "text",
    "voice",
    "selection",
]
DiagnosticEvidenceType = Literal[
    "comprehension",
    "spontaneous_production",
    "supported_production",
    "connected_exchange",
    "transfer",
    "motivating_context",
]
DiagnosticSupportType = Literal[
    "visual",
    "repetition",
    "keyword",
    "pattern",
    "example",
    "translation",
]


class ConversationalDiagnosticActivity(BaseModel):
    """Declare one activity inside a diagnostic session.

    Declara una actividad dentro de una sesión diagnóstica.
    """

    activity_id: str
    diagnostic_session_id: str
    context_id: str
    prompt_id: str
    stage: DiagnosticActivityStage
    communicative_intention: str
    modality: DiagnosticActivityModality
    expected_evidence_type: DiagnosticEvidenceType
    available_supports: list[DiagnosticSupportType] = Field(
        default_factory=list
    )
    transfer_variant_id: str | None = None
    sequence_order: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_activity_contract(
        self,
    ) -> "ConversationalDiagnosticActivity":
        """Protect activity content and transfer invariants.

        Protege el contenido y los invariantes de transferencia.
        """
        if not self.prompt_id.strip():
            raise ValueError("prompt_id cannot be blank")

        if not self.communicative_intention.strip():
            raise ValueError(
                "communicative_intention cannot be blank"
            )

        if len(self.available_supports) != len(
            set(self.available_supports)
        ):
            raise ValueError(
                "available_supports must contain unique values"
            )

        if self.stage == "transfer":
            if (
                self.transfer_variant_id is None
                or not self.transfer_variant_id.strip()
            ):
                raise ValueError(
                    "Transfer activity requires transfer_variant_id"
                )
        elif self.transfer_variant_id is not None:
            raise ValueError(
                "Only transfer activity can define transfer_variant_id"
            )

        if (
            self.expected_evidence_type == "transfer"
            and self.stage != "transfer"
        ):
            raise ValueError(
                "Transfer evidence requires transfer activity"
            )

        return self

DiagnosticSupportUsageType = Literal[
    "none",
    "visual",
    "repetition",
    "keyword",
    "pattern",
    "example",
    "translation",
]
DiagnosticSupportLevel = Literal[
    "none",
    "minimal",
    "moderate",
    "full",
]


class DiagnosticSupportUsage(BaseModel):
    """Record one support actually used during a diagnostic response.

    Registra un apoyo utilizado durante una respuesta diagnóstica.
    """

    diagnostic_session_id: str
    activity_id: str
    production_id: int = Field(gt=0)
    support_type: DiagnosticSupportUsageType
    support_level: DiagnosticSupportLevel
    sequence_order: int = Field(gt=0)
    provided_at: datetime
    withdrawn_afterward: bool = False

    @model_validator(mode="after")
    def validate_support_usage(
        self,
    ) -> "DiagnosticSupportUsage":
        """Keep support type and intensity semantically coherent.

        Mantiene coherentes el tipo y la intensidad del apoyo.
        """
        if (
            self.support_type == "none"
            and self.support_level != "none"
        ):
            raise ValueError(
                "No-support usage requires none support_level"
            )

        if (
            self.support_type != "none"
            and self.support_level == "none"
        ):
            raise ValueError(
                "Used support requires a non-none support_level"
            )

        if (
            self.support_type == "none"
            and self.withdrawn_afterward
        ):
            raise ValueError(
                "No-support usage cannot be marked as withdrawn"
            )

        return self

DiagnosticDimension = Literal[
    "listening_comprehension",
    "response_initiation",
    "direct_english_construction",
    "oral_production",
    "continuity",
    "linguistic_retrieval",
    "intelligibility",
    "support_need",
    "transfer",
    "motivating_context",
]


DiagnosticObservationEvidenceRole = Literal[
    "strength",
    "development_need",
    "priority_blockage",
    "context_relevance",
]


class ConversationalDiagnosticObservation(BaseModel):
    """Describe one traceable diagnostic observation.

    Describe una observación diagnóstica trazable.
    """

    observation_id: str
    diagnostic_session_id: str
    activity_id: str
    production_id: int | None = Field(default=None, gt=0)
    evaluation_result_ids: list[int] = Field(default_factory=list)
    dimension: DiagnosticDimension
    evidence_role: DiagnosticObservationEvidenceRole
    context_reference: str | None = None
    description: str
    support_level: DiagnosticSupportLevel
    observer_id: str
    observer_version: str
    observed_at: datetime

    @model_validator(mode="after")
    def validate_observation_contract(
        self,
    ) -> "ConversationalDiagnosticObservation":
        """Protect descriptive and traceability invariants.

        Protege los invariantes descriptivos y de trazabilidad.
        """
        text_fields = {
            "observation_id": self.observation_id,
            "diagnostic_session_id": self.diagnostic_session_id,
            "activity_id": self.activity_id,
            "description": self.description,
            "observer_id": self.observer_id,
            "observer_version": self.observer_version,
        }

        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(field_name + " cannot be blank")

        if any(
            evaluation_result_id <= 0
            for evaluation_result_id in self.evaluation_result_ids
        ):
            raise ValueError(
                "evaluation_result_ids must contain positive values"
            )

        if len(self.evaluation_result_ids) != len(
            set(self.evaluation_result_ids)
        ):
            raise ValueError(
                "evaluation_result_ids must contain unique values"
            )

        if (
            self.evidence_role == "context_relevance"
            and self.dimension != "motivating_context"
        ):
            raise ValueError(
                "Context relevance requires motivating_context dimension"
            )

        if (
            self.dimension == "motivating_context"
            and self.evidence_role != "context_relevance"
        ):
            raise ValueError(
                "Motivating context requires context_relevance role"
            )

        if self.evidence_role == "context_relevance":
            if (
                self.context_reference is None
                or not self.context_reference.strip()
            ):
                raise ValueError(
                    "Context relevance requires context_reference"
                )
        elif self.context_reference is not None:
            raise ValueError(
                "Only context relevance can define context_reference"
            )

        return self

InitialConversationalProfileStatus = Literal[
    "provisional",
    "confirmed",
]


InitialProfileRecommendedMethod = Literal[
    "direct-english-construction",
]


class InitialConversationalProfilePlan(BaseModel):
    """Represent explicit pedagogical decisions for one initial profile.

    Representa decisiones pedagógicas explícitas para un perfil inicial.
    """

    target_capacity: str
    recommended_support_level: DiagnosticSupportLevel
    recommended_method: InitialProfileRecommendedMethod
    first_lesson_id: str
    review_criterion: str

    @model_validator(mode="after")
    def validate_profile_plan(
        self,
    ) -> "InitialConversationalProfilePlan":
        """Require usable and explicit pedagogical recommendations.

        Exige recomendaciones pedagógicas utilizables y explícitas.
        """
        text_fields = {
            "target_capacity": self.target_capacity,
            "recommended_method": self.recommended_method,
            "first_lesson_id": self.first_lesson_id,
            "review_criterion": self.review_criterion,
        }

        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(field_name + " cannot be blank")

        return self


class InitialConversationalProfile(BaseModel):
    """Represent one revisable initial conversational profile.

    Representa un perfil conversacional inicial y revisable.
    """

    profile_id: str
    diagnostic_session_id: str
    status: InitialConversationalProfileStatus
    priority_blockage: str
    target_capacity: str
    recommended_support_level: DiagnosticSupportLevel
    relevant_contexts: list[str] = Field(min_length=1)
    recommended_method: InitialProfileRecommendedMethod
    first_lesson_id: str
    review_criterion: str
    evidence_summary: str
    generated_at: datetime
    generator_id: str
    generator_version: str

    @model_validator(mode="after")
    def validate_initial_profile(
        self,
    ) -> "InitialConversationalProfile":
        """Protect descriptive and recommendation invariants.

        Protege los invariantes descriptivos y de recomendación.
        """
        text_fields = {
            "profile_id": self.profile_id,
            "diagnostic_session_id": self.diagnostic_session_id,
            "priority_blockage": self.priority_blockage,
            "target_capacity": self.target_capacity,
            "recommended_method": self.recommended_method,
            "first_lesson_id": self.first_lesson_id,
            "review_criterion": self.review_criterion,
            "evidence_summary": self.evidence_summary,
            "generator_id": self.generator_id,
            "generator_version": self.generator_version,
        }

        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(field_name + " cannot be blank")

        normalized_contexts = [
            context.strip()
            for context in self.relevant_contexts
        ]

        if any(not context for context in normalized_contexts):
            raise ValueError(
                "relevant_contexts cannot contain blank values"
            )

        if len(normalized_contexts) != len(
            set(normalized_contexts)
        ):
            raise ValueError(
                "relevant_contexts must contain unique values"
            )

        return self


class InitialConversationalProfileEvidence(BaseModel):
    """Link one initial profile to one diagnostic observation.

    Vincula un perfil inicial con una observación diagnóstica.
    """

    profile_id: str
    observation_id: str

    @model_validator(mode="after")
    def validate_profile_evidence_link(
        self,
    ) -> "InitialConversationalProfileEvidence":
        """Require non-blank traceability identifiers.

        Exige identificadores de trazabilidad no vacíos.
        """
        if not self.profile_id.strip():
            raise ValueError("profile_id cannot be blank")

        if not self.observation_id.strip():
            raise ValueError("observation_id cannot be blank")

        return self
