from pydantic import BaseModel
from typing import List, Optional

class Example(BaseModel):
    en: str
    es: Optional[str] = None

class Lesson(BaseModel):
    id: str
    title: str
    objective: Optional[str] = None
    vocabulary: List[str] = []
    grammar: List[str] = []
    examples: List[Example] = []

class Unit(BaseModel):
    id: str
    title: str
    lessons: List[Lesson] = []

class Level(BaseModel):
    code: str  # A1, A2, B1...
    units: List[Unit] = []

class ContentTreeResponse(BaseModel):
    levels: List[Level]
