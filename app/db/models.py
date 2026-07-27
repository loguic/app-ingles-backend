from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)

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

class ConversationProductionSubmission(Base):
    """Persist one group of captured learner productions.

    Persiste una entrega de producciones capturadas del estudiante.
    """

    __tablename__ = "conversation_production_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    level_id = Column(String, index=True, nullable=False)
    unit_id = Column(String, index=True, nullable=False)
    lesson_id = Column(String, index=True, nullable=False)
    conversation_id = Column(String, index=True, nullable=False)
    submitted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class LearnerProduction(Base):
    """Persist one captured response without evaluating it.

    Persiste una respuesta capturada sin evaluarla.
    """

    __tablename__ = "learner_productions"
    __table_args__ = (
        UniqueConstraint(
            "submission_id",
            "prompt_id",
            name="uq_learner_production_submission_prompt",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer,
        ForeignKey(
            "conversation_production_submissions.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )
    prompt_id = Column(String, index=True, nullable=False)
    turn_id = Column(String, index=True, nullable=False)
    modality = Column(String, nullable=False)
    response_text = Column(Text, nullable=True)
    audio_reference = Column(String, nullable=True)


class ProductionEvaluationResult(Base):
    """Persist one evaluation separately from the captured production.

    Persiste una evaluación separada de la producción capturada.
    """

    __tablename__ = "production_evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    production_id = Column(
        Integer,
        ForeignKey("learner_productions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    criterion_id = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    evaluator_id = Column(String, nullable=False)
    evaluator_version = Column(String, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), nullable=False)
