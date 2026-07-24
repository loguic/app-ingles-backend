from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal


class Pronunciation(BaseModel):
    # English locale represented by this pronunciation variant.
    # Variante regional de inglés representada por esta pronunciación.
    locale: Literal["en-US", "en-GB"]

    # IPA transcription for the selected English variant.
    # Transcripción IPA correspondiente a la variante de inglés seleccionada.
    ipa: str

    # Local audio asset matching the locale and IPA transcription.
    # Recurso de audio local coherente con la variante y su transcripción IPA.
    audio_asset: str


class Example(BaseModel):
    # Stable identifier for progress, analytics, and future assessments.
    # Identificador estable para progreso, analítica y evaluaciones futuras.
    id: str
    en: str
    es: Optional[str] = None

    # Available pronunciation variants for this example sentence.
    # Variantes de pronunciación disponibles para esta frase de ejemplo.
    pronunciations: List[Pronunciation] = []


class ConversationChoice(BaseModel):
    # Stable identifier for analytics and future persisted sessions.
    # Identificador estable para analítica y futuras sesiones persistidas.
    id: str

    # Learner response represented by this branch option.
    # Respuesta del estudiante representada por esta opción de rama.
    en: str
    es: Optional[str] = None

    # Optional audio references for regional listening and speaking practice.
    # Referencias opcionales para práctica regional de escucha y habla.
    pronunciations: List[Pronunciation] = Field(default_factory=list)

    # Destination selected by this option; None closes the current route.
    # Destino elegido por esta opción; None cierra la ruta actual.
    next_turn_id: Optional[str] = None


class ConversationTurn(BaseModel):
    # Stable identifier for progress, evaluation and future analytics.
    # Identificador estable para progreso, evaluación y analítica futura.
    id: str

    # Role responsible for this turn in the conversation.
    # Rol responsable de este turno dentro de la conversación.
    speaker: Literal["partner", "learner"]

    en: str
    es: Optional[str] = None

    # Optional reference audio for listening and pronunciation practice.
    # Audio de referencia opcional para escucha y práctica oral.
    pronunciations: List[Pronunciation] = Field(default_factory=list)

    # Deterministic destination used by branching conversations.
    # Destino determinista utilizado por conversaciones ramificadas.
    next_turn_id: Optional[str] = None

    # Alternative learner responses available from this turn.
    # Respuestas alternativas del estudiante disponibles desde este turno.
    choices: List[ConversationChoice] = Field(default_factory=list)


class Conversation(BaseModel):
    # Stable identifier for the complete conversational activity.
    # Identificador estable para la actividad conversacional completa.
    id: str

    title: str
    context: Optional[str] = None

    # Future modes can extend this contract without changing Lesson.
    # Los modos futuros podrán ampliar este contrato sin cambiar Lesson.
    mode: Literal["guided", "branching", "free"] = "guided"

    # Explicit graph entry point for branching conversations.
    # Punto de entrada explícito del grafo para conversaciones ramificadas.
    start_turn_id: Optional[str] = None

    turns: List[ConversationTurn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_conversation_graph(self) -> "Conversation":
        """Validate stable IDs and branching graph integrity.

        Valida identificadores estables y la integridad del grafo ramificado.
        """
        turn_ids = [turn.id for turn in self.turns]
        if len(turn_ids) != len(set(turn_ids)):
            raise ValueError("Conversation turn IDs must be unique")

        choice_ids = [
            choice.id
            for turn in self.turns
            for choice in turn.choices
        ]
        if len(choice_ids) != len(set(choice_ids)):
            raise ValueError("Conversation choice IDs must be unique")

        turn_id_set = set(turn_ids)
        if self.start_turn_id is not None and self.start_turn_id not in turn_id_set:
            raise ValueError("Conversation start_turn_id must reference an existing turn")

        referenced_turn_ids = {
            target
            for turn in self.turns
            for target in (
                [turn.next_turn_id]
                + [choice.next_turn_id for choice in turn.choices]
            )
            if target is not None
        }
        unknown_turn_ids = sorted(referenced_turn_ids - turn_id_set)
        if unknown_turn_ids:
            raise ValueError(
                "Conversation transitions reference unknown turns: "
                + ", ".join(unknown_turn_ids)
            )

        if self.mode != "branching":
            return self

        if not self.turns:
            raise ValueError("Branching conversations must contain turns")
        if self.start_turn_id is None:
            raise ValueError("Branching conversations require start_turn_id")
        if not choice_ids:
            raise ValueError("Branching conversations require at least one choice")

        for turn in self.turns:
            if turn.choices and turn.speaker != "learner":
                raise ValueError(
                    f"Turn {turn.id} defines choices but is not a learner turn"
                )
            if len(turn.choices) == 1:
                raise ValueError(
                    f"Turn {turn.id} must define at least two branching choices"
                )
            if turn.next_turn_id is not None and turn.choices:
                raise ValueError(
                    f"Turn {turn.id} cannot define next_turn_id and choices together"
                )

        adjacency = {
            turn.id: [
                target
                for target in (
                    [turn.next_turn_id]
                    + [choice.next_turn_id for choice in turn.choices]
                )
                if target is not None
            ]
            for turn in self.turns
        }

        reachable = set()
        pending = [self.start_turn_id]
        while pending:
            current = pending.pop()
            if current in reachable:
                continue
            reachable.add(current)
            pending.extend(adjacency[current])

        unreachable = sorted(turn_id_set - reachable)
        if unreachable:
            raise ValueError(
                "Branching conversation contains unreachable turns: "
                + ", ".join(unreachable)
            )

        # Reject every reachable cycle. A graph with one terminal branch and
        # another cyclic branch would otherwise pass the terminal-route check.
        # Rechaza todo ciclo alcanzable. Un grafo con una rama terminal y otra
        # cíclica podría superar de otro modo la validación de cierre.
        visit_state: dict[str, Literal["visiting", "visited"]] = {}

        def visit(turn_id: str) -> None:
            state = visit_state.get(turn_id)
            if state == "visiting":
                raise ValueError(
                    f"Branching conversation contains a reachable cycle at {turn_id}"
                )
            if state == "visited":
                return

            visit_state[turn_id] = "visiting"
            for target in adjacency[turn_id]:
                visit(target)
            visit_state[turn_id] = "visited"

        visit(self.start_turn_id)

        has_terminal_route = any(
            not adjacency[turn.id]
            or any(choice.next_turn_id is None for choice in turn.choices)
            for turn in self.turns
            if turn.id in reachable
        )
        if not has_terminal_route:
            raise ValueError("Branching conversation requires a terminal route")

        return self


class Mission(BaseModel):
    """Define the communicative mission presented to the learner.

    Define la misión comunicativa presentada al estudiante.
    """

    id: str
    title: str
    situation: str
    observable_outcome: str
    success_criteria: List[str] = Field(min_length=1)


class LanguageSupportItem(BaseModel):
    """Provide contextual language support for one or more stages.

    Proporciona apoyo lingüístico contextual para una o varias etapas.
    """

    id: str
    type: Literal[
        "word",
        "expression",
        "pattern",
        "reference_expression",
        "hint",
    ]
    en: str
    es: Optional[str] = None
    pronunciations: List[Pronunciation] = Field(default_factory=list)
    usage_note: Optional[str] = None
    stage_ids: List[str] = Field(min_length=1)


class LessonStage(BaseModel):
    """Declare one ordered and executable pedagogical stage.

    Declara una etapa pedagógica ordenada y ejecutable.
    """

    id: str
    type: Literal[
        "encounter",
        "comprehension",
        "language_support",
        "guided_production",
        "assisted_response",
        "applied_conversation",
        "adaptive_feedback",
        "evidence",
        "closure",
    ]
    instruction: str
    activity_ids: List[str] = Field(default_factory=list)
    mode: Literal["required", "adaptive"] = "required"
    completion_condition: Literal[
        "acknowledged",
        "any_activity_completed",
        "all_activities_completed",
        "evidence_recorded",
    ]


class EvidenceDefinition(BaseModel):
    """Define measurable evidence without storing learner results.

    Define una evidencia medible sin almacenar resultados del estudiante.
    """

    id: str
    skill_ids: List[str] = Field(min_length=1)
    stage_id: str
    activity_id: str
    evidence_type: Literal[
        "comprehension_result",
        "contextual_response",
        "conversation_completion",
        "guided_production",
        "exercise_result",
    ]
    measurement_mode: Literal["completion", "binary", "score"]
    success_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    required: bool = True

    @model_validator(mode="after")
    def validate_success_threshold(self) -> "EvidenceDefinition":
        """Keep score thresholds consistent with the measurement mode.

        Mantiene los umbrales coherentes con el modo de medición.
        """
        if (
            self.measurement_mode == "score"
            and self.success_threshold is None
        ):
            raise ValueError("Score evidence requires success_threshold")

        if (
            self.measurement_mode != "score"
            and self.success_threshold is not None
        ):
            raise ValueError(
                "Only score evidence can define success_threshold"
            )

        return self


class CompletionPolicy(BaseModel):
    """Define practiced, completed and reinforcement requirements.

    Define los requisitos de práctica, finalización y refuerzo.
    """

    practiced_stage_ids: List[str] = Field(min_length=1)
    required_evidence_ids: List[str] = Field(min_length=1)
    reinforcement_on_failure: bool = True
    allow_retry: bool = True


class LessonExperience(BaseModel):
    """Orchestrate the public professional lesson experience.

    Orquesta la experiencia profesional pública de la lección.
    """

    contract_version: Literal["2.0"] = "2.0"
    mission: Mission
    skill_ids: List[str] = Field(min_length=1)
    stages: List[LessonStage] = Field(min_length=1)
    language_support: List[LanguageSupportItem] = Field(
        default_factory=list
    )
    evidence_definitions: List[EvidenceDefinition] = Field(min_length=1)
    completion_policy: CompletionPolicy

    @model_validator(mode="after")
    def validate_internal_integrity(self) -> "LessonExperience":
        # Validate the relationships owned by this aggregate.
        # Valida las relaciones pertenecientes a este agregado.

        def reject_duplicates(label: str, values: List[str]) -> None:
            seen: set[str] = set()
            duplicates: set[str] = set()

            for value in values:
                if value in seen:
                    duplicates.add(value)
                else:
                    seen.add(value)

            if duplicates:
                raise ValueError(
                    label
                    + " must be unique: "
                    + ", ".join(sorted(duplicates))
                )

        reject_duplicates(
            "LessonExperience skill_ids",
            self.skill_ids,
        )

        stage_ids = [stage.id for stage in self.stages]
        support_ids = [item.id for item in self.language_support]
        evidence_ids = [
            evidence.id
            for evidence in self.evidence_definitions
        ]

        reject_duplicates(
            "LessonExperience stage IDs",
            stage_ids,
        )
        reject_duplicates(
            "Language support IDs",
            support_ids,
        )
        reject_duplicates(
            "Evidence definition IDs",
            evidence_ids,
        )

        stage_id_set = set(stage_ids)
        skill_id_set = set(self.skill_ids)
        evidence_id_set = set(evidence_ids)
        stages_by_id = {
            stage.id: stage
            for stage in self.stages
        }

        for item in self.language_support:
            reject_duplicates(
                "Language support "
                + item.id
                + " stage_ids",
                item.stage_ids,
            )

            unknown_stage_ids = sorted(
                set(item.stage_ids) - stage_id_set
            )
            if unknown_stage_ids:
                raise ValueError(
                    "Language support "
                    + item.id
                    + " references unknown stages: "
                    + ", ".join(unknown_stage_ids)
                )

        for evidence in self.evidence_definitions:
            reject_duplicates(
                "Evidence "
                + evidence.id
                + " skill_ids",
                evidence.skill_ids,
            )

            unknown_skill_ids = sorted(
                set(evidence.skill_ids) - skill_id_set
            )
            if unknown_skill_ids:
                raise ValueError(
                    "Evidence "
                    + evidence.id
                    + " references unknown Skills: "
                    + ", ".join(unknown_skill_ids)
                )

            if evidence.stage_id not in stage_id_set:
                raise ValueError(
                    "Evidence "
                    + evidence.id
                    + " references unknown stage: "
                    + evidence.stage_id
                )

            stage = stages_by_id[evidence.stage_id]
            if evidence.activity_id not in stage.activity_ids:
                raise ValueError(
                    "Evidence "
                    + evidence.id
                    + " activity_id must be declared by stage "
                    + evidence.stage_id
                    + ": "
                    + evidence.activity_id
                )

        practiced_stage_ids = (
            self.completion_policy.practiced_stage_ids
        )
        required_evidence_ids = (
            self.completion_policy.required_evidence_ids
        )

        reject_duplicates(
            "Completion policy practiced_stage_ids",
            practiced_stage_ids,
        )
        reject_duplicates(
            "Completion policy required_evidence_ids",
            required_evidence_ids,
        )

        unknown_practiced_stage_ids = sorted(
            set(practiced_stage_ids) - stage_id_set
        )
        if unknown_practiced_stage_ids:
            raise ValueError(
                "Completion policy references unknown practiced stages: "
                + ", ".join(unknown_practiced_stage_ids)
            )

        unknown_required_evidence_ids = sorted(
            set(required_evidence_ids) - evidence_id_set
        )
        if unknown_required_evidence_ids:
            raise ValueError(
                "Completion policy references unknown required evidence: "
                + ", ".join(unknown_required_evidence_ids)
            )

        declared_required_ids = {
            evidence.id
            for evidence in self.evidence_definitions
            if evidence.required
        }
        policy_required_ids = set(required_evidence_ids)

        if declared_required_ids != policy_required_ids:
            missing_ids = sorted(
                declared_required_ids - policy_required_ids
            )
            unexpected_ids = sorted(
                policy_required_ids - declared_required_ids
            )
            details: List[str] = []

            if missing_ids:
                details.append(
                    "missing " + ", ".join(missing_ids)
                )
            if unexpected_ids:
                details.append(
                    "unexpected " + ", ".join(unexpected_ids)
                )

            raise ValueError(
                "Completion policy required_evidence_ids must match "
                "required evidence definitions: "
                + "; ".join(details)
            )

        activity_conditions = {
            "any_activity_completed",
            "all_activities_completed",
            "evidence_recorded",
        }

        for stage in self.stages:
            if (
                stage.completion_condition in activity_conditions
                and not stage.activity_ids
            ):
                raise ValueError(
                    "Stage "
                    + stage.id
                    + " with completion_condition "
                    + stage.completion_condition
                    + " requires at least one activity"
                )

        return self


class ExerciseMCQ(BaseModel):
    id: str
    # Multiple Choice Question / Pregunta de opción múltiple
    type: Literal["mcq"] = "mcq"
    prompt: str
    options: List[str]
    answer_index: int
    skill_ids: List[str] = []


class Lesson(BaseModel):
    id: str
    title: str
    objective: Optional[str] = None
    experience: Optional[LessonExperience] = None
    vocabulary: List[str] = []
    grammar: List[str] = []
    examples: List[Example] = []
    conversations: List[Conversation] = Field(default_factory=list)
    exercises: List[ExerciseMCQ] = []


class Unit(BaseModel):
    id: str
    title: str
    lessons: List[Lesson] = []


class Level(BaseModel):
    code: str  # A1, A2, B1...
    units: List[Unit] = []


class ContentTreeResponse(BaseModel):
    levels: List[Level]


class ExerciseSubmission(BaseModel):
    selected_index: int


class ExerciseResult(BaseModel):
    correct: bool
