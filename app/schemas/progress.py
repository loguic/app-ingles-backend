from pydantic import BaseModel

class ProgressRecord(BaseModel):
    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    exercise_id: str
    selected_index: int
    correct: bool

class ProgressStats(BaseModel):
    user_id: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
