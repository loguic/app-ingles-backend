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
