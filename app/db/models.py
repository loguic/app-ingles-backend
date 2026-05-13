from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.db.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    exercise_id = Column(String, index=True, nullable=False)
    selected_index = Column(Integer, nullable=False)
    correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
