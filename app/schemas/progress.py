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


class ProgressRecommendation(BaseModel):
    user_id: str
    accuracy: float
    message: str


class SkillMastery(BaseModel):
    user_id: str
    skill_id: str
    total_attempts: int
    correct_attempts: int
    mastery_score: float


class ReviewRecommendation(BaseModel):
    user_id: str
    skill_id: str
    mastery_score: float
    should_review: bool
    message: str


class StudentDashboard(BaseModel):
    user_id: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    recommendation: str


class NextAction(BaseModel):
    user_id: str
    action_type: str
    target_id: str
    message: str
