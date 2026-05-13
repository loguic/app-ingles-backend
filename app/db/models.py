from sqlalchemy import Column, DateTime, Integer, String, func

from app.db.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    level_id = Column(String, nullable=False)
    unit_id = Column(String, nullable=False)
    lesson_id = Column(String, nullable=False)
    exercise_id = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    result = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
