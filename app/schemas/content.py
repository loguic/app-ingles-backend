from pydantic import BaseModel
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

class ExerciseMCQ(BaseModel):
    id: str
    type: Literal["mcq"] = "mcq"  # Multiple Choice Question / Pregunta de opción múltiple
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
