from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, func

from app.db.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    level_id = Column(String, index=True, nullable=False)
    unit_id = Column(String, index=True, nullable=False)
    lesson_id = Column(String, index=True, nullable=False)
    exercise_id = Column(String, index=True, nullable=False)
    selected_index = Column(Integer, nullable=False)
    correct = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ConversationAttempt(Base):
    __tablename__ = "conversation_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    level_id = Column(String, index=True, nullable=False)
    unit_id = Column(String, index=True, nullable=False)
    lesson_id = Column(String, index=True, nullable=False)
    conversation_id = Column(String, index=True, nullable=False)
    mode = Column(String, nullable=False)
    visited_turn_ids = Column(JSON, nullable=False)
    selected_choice_ids = Column(JSON, nullable=False)
    completed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
