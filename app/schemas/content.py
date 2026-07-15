from pydantic import BaseModel, Field
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


class Conversation(BaseModel):
    # Stable identifier for the complete conversational activity.
    # Identificador estable para la actividad conversacional completa.
    id: str

    title: str
    context: Optional[str] = None

    # Future modes can extend this contract without changing Lesson.
    # Los modos futuros podrán ampliar este contrato sin cambiar Lesson.
    mode: Literal["guided", "branching", "free"] = "guided"

    turns: List[ConversationTurn] = Field(default_factory=list)


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
