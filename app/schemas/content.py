from pydantic import BaseModel
from typing import List, Optional, Literal

class Example(BaseModel):
    en: str
    es: Optional[str] = None

class ExerciseMCQ(BaseModel):
    id: str
    type: Literal["mcq"] = "mcq"  # Multiple Choice Question / Pregunta de opción múltiple
    prompt: str
    options: List[str]
    answer_index: int

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
