from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Float,
    Integer,
    Index,
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
        UniqueConstraint(
            "id",
            "prompt_id",
            name="uq_learner_production_id_prompt",
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


class ShortConnectedExchangeProductionReview(Base):
    """Persist one independent append-only review of a real production.

    Persiste una revisión independiente y append-only de una producción real.
    """

    __tablename__ = "short_connected_exchange_production_reviews"
    __table_args__ = (
        CheckConstraint(
            "length(trim(review_id)) > 0",
            name="ck_short_exchange_review_id_not_blank",
        ),
        CheckConstraint(
            "dimension IN ('intention_understanding', "
            "'contingent_response')",
            name="ck_short_exchange_review_dimension",
        ),
        CheckConstraint(
            "result IN ('positive', 'negative', 'pending')",
            name="ck_short_exchange_review_result",
        ),
        CheckConstraint(
            "source_type IN ('human', 'external')",
            name="ck_short_exchange_review_source_type",
        ),
        CheckConstraint(
            "length(trim(source_id)) > 0",
            name="ck_short_exchange_review_source_id",
        ),
        CheckConstraint(
            "(source_type = 'human' AND "
            "(source_version IS NULL OR length(trim(source_version)) > 0)) "
            "OR (source_type = 'external' AND source_version IS NOT NULL "
            "AND length(trim(source_version)) > 0)",
            name="ck_short_exchange_review_source_version",
        ),
        Index(
            "ix_short_exchange_review_history",
            "production_id",
            "dimension",
            "reviewed_at",
            "review_id",
        ),
    )

    review_id = Column(String, primary_key=True)
    production_id = Column(
        Integer,
        ForeignKey("learner_productions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    dimension = Column(String, nullable=False)
    result = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    source_version = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=False)


class DirectEnglishConstructionAttempt(Base):
    """Persist one complete direct-English execution identity.

    Persiste la identidad de una ejecución completa de inglés directo.
    """

    __tablename__ = "direct_english_construction_attempts"
    __table_args__ = (
        CheckConstraint(
            "length(trim(attempt_id)) > 0",
            name="ck_direct_english_attempt_id_not_blank",
        ),
        CheckConstraint(
            "length(trim(user_id)) > 0 "
            "AND length(trim(level_id)) > 0 "
            "AND length(trim(unit_id)) > 0 "
            "AND length(trim(lesson_id)) > 0",
            name="ck_direct_english_attempt_hierarchy_not_blank",
        ),
        CheckConstraint(
            "length(trim(transfer_bank_id)) > 0 "
            "AND length(trim(transfer_variant_id)) > 0 "
            "AND length(trim(transfer_prompt_snapshot)) > 0 "
            "AND length(trim(selector_version)) > 0",
            name="ck_direct_english_attempt_selection_not_blank",
        ),
        CheckConstraint(
            "status IN ('started', 'finalized')",
            name="ck_direct_english_attempt_status",
        ),
        CheckConstraint(
            "(status = 'started' AND finalized_at IS NULL) OR "
            "(status = 'finalized' AND finalized_at IS NOT NULL)",
            name="ck_direct_english_attempt_finalization",
        ),
        CheckConstraint(
            "finalized_at IS NULL OR finalized_at >= started_at",
            name="ck_direct_english_attempt_timeline",
        ),
    )

    attempt_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    level_id = Column(String, nullable=False)
    unit_id = Column(String, nullable=False)
    lesson_id = Column(String, nullable=False)
    transfer_bank_id = Column(String, nullable=False)
    transfer_variant_id = Column(String, nullable=False)
    transfer_prompt_snapshot = Column(Text, nullable=False)
    selector_version = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finalized_at = Column(DateTime(timezone=True), nullable=True)


class DirectEnglishConstructionAttemptProduction(Base):
    """Link one real production to its direct-English function.

    Vincula una producción real con su función de inglés directo.
    """

    __tablename__ = "direct_english_construction_attempt_productions"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "production_function",
            name="uq_direct_english_attempt_function",
        ),
        UniqueConstraint(
            "learner_production_id",
            name="uq_direct_english_attempt_learner_production",
        ),
        CheckConstraint(
            "production_function IN ('guided', 'expanded', 'transfer')",
            name="ck_direct_english_attempt_production_function",
        ),
        CheckConstraint(
            "configured_support_level IN "
            "('model', 'anchors', 'initial_word', 'none')",
            name="ck_direct_english_attempt_configured_support",
        ),
        CheckConstraint(
            "support_used IN ('model', 'anchors', 'initial_word', 'none')",
            name="ck_direct_english_attempt_support_used",
        ),
        CheckConstraint(
            "length(trim(evidence_id)) > 0",
            name="ck_direct_english_attempt_evidence_not_blank",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(
        String,
        ForeignKey(
            "direct_english_construction_attempts.attempt_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    learner_production_id = Column(
        Integer,
        ForeignKey("learner_productions.id"),
        nullable=False,
    )
    production_function = Column(String, nullable=False)
    evidence_id = Column(String, nullable=False)
    configured_support_level = Column(String, nullable=False)
    support_used = Column(String, nullable=False)


class DirectEnglishConstructionProductionOrientation(Base):
    """Persist one externally selected orientation without evaluating.

    Persiste una orientación seleccionada externamente sin evaluar.
    """

    __tablename__ = "direct_english_construction_production_orientations"
    __table_args__ = (
        CheckConstraint(
            "length(trim(orientation_id)) > 0",
            name="ck_direct_english_orientation_id_not_blank",
        ),
        UniqueConstraint(
            "attempt_production_id",
            name="uq_direct_english_orientation_attempt_production",
        ),
        CheckConstraint(
            "priority IN ('relevance', 'direct_english_construction', "
            "'intelligibility', 'secondary_accuracy')",
            name="ck_direct_english_orientation_priority",
        ),
        CheckConstraint(
            "source_type IN ('human', 'external')",
            name="ck_direct_english_orientation_source_type",
        ),
        CheckConstraint(
            "length(trim(guidance_text)) > 0 "
            "AND length(guidance_text) <= 2000",
            name="ck_direct_english_orientation_guidance",
        ),
        CheckConstraint(
            "length(trim(source_id)) > 0",
            name="ck_direct_english_orientation_source_id",
        ),
        CheckConstraint(
            "(source_type = 'human' AND "
            "(source_version IS NULL OR length(trim(source_version)) > 0)) "
            "OR (source_type = 'external' AND source_version IS NOT NULL "
            "AND length(trim(source_version)) > 0)",
            name="ck_direct_english_orientation_source_version",
        ),
    )

    orientation_id = Column(String, primary_key=True)
    attempt_production_id = Column(
        Integer,
        ForeignKey(
            "direct_english_construction_attempt_productions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    priority = Column(String, nullable=False)
    guidance_text = Column(Text, nullable=False)
    source_type = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    source_version = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)


class ProductionEvaluationResult(Base):
    """Persist one evaluation separately from the captured production.

    Persiste una evaluación separada de la producción capturada.
    """

    __tablename__ = "production_evaluation_results"
    __table_args__ = (
        UniqueConstraint(
            "id",
            "production_id",
            name="uq_evaluation_result_id_production",
        ),
    )

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


class ProductionFeedback(Base):
    """Persist pedagogical feedback separately from its evaluation.

    Persiste feedback pedagógico separado de su evaluación.
    """

    __tablename__ = "production_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_result_id = Column(
        Integer,
        ForeignKey(
            "production_evaluation_results.id",
            ondelete="CASCADE",
        ),
        index=True,
        nullable=False,
    )
    criterion_description = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    guidance = Column(Text, nullable=False)
    generator_id = Column(String, nullable=False)
    generator_version = Column(String, nullable=False)
    generated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class ConversationalDiagnosticSession(Base):
    """Persist one diagnostic execution, separate from learner progress.

    Persiste una ejecución diagnóstica separada del progreso del estudiante.
    """

    __tablename__ = "conversational_diagnostic_sessions"
    __table_args__ = (
        CheckConstraint(
            "age_profile IN ('6-8', '9-12', '13-17', 'adult')",
            name="ck_diagnostic_session_age_profile",
        ),
        CheckConstraint(
            "status IN ('in_progress', 'provisional', 'completed', 'cancelled')",
            name="ck_diagnostic_session_status",
        ),
        CheckConstraint(
            "(status = 'in_progress' AND completed_at IS NULL) OR "
            "(status <> 'in_progress' AND completed_at IS NOT NULL)",
            name="ck_diagnostic_session_completion",
        ),
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_diagnostic_session_timeline",
        ),
    )

    diagnostic_session_id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    age_profile = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ConversationalDiagnosticContext(Base):
    """Persist the minimal authorized context for one diagnostic session.

    Persiste el contexto mínimo autorizado de una sesión diagnóstica.
    """

    __tablename__ = "conversational_diagnostic_contexts"
    __table_args__ = (
        UniqueConstraint(
            "diagnostic_session_id",
            name="uq_diagnostic_context_session",
        ),
        UniqueConstraint(
            "diagnostic_session_id",
            "context_id",
            name="uq_diagnostic_context_session_context",
        ),
        CheckConstraint(
            "autonomy_level IN ('supported', 'developing', 'independent')",
            name="ck_diagnostic_context_autonomy",
        ),
    )

    context_id = Column(String, primary_key=True)
    diagnostic_session_id = Column(
        String,
        ForeignKey(
            "conversational_diagnostic_sessions.diagnostic_session_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    usual_languages = Column(JSON, nullable=False)
    previous_english_contact = Column(Text, nullable=False)
    general_interests = Column(JSON, nullable=False)
    learning_goals = Column(JSON, nullable=False)
    autonomy_level = Column(String, nullable=False)
    responsible_adult_present = Column(Boolean, nullable=True)
    audio_authorized = Column(Boolean, nullable=False)


class ConversationalDiagnosticActivity(Base):
    """Persist an activity declaration without learner production data.

    Persiste una actividad sin incorporar datos de producción del estudiante.
    """

    __tablename__ = "conversational_diagnostic_activities"
    __table_args__ = (
        UniqueConstraint(
            "diagnostic_session_id",
            "activity_id",
            name="uq_diagnostic_activity_session_activity",
        ),
        UniqueConstraint(
            "diagnostic_session_id",
            "activity_id",
            "prompt_id",
            name="uq_diagnostic_activity_session_activity_prompt",
        ),
        UniqueConstraint(
            "diagnostic_session_id",
            "sequence_order",
            name="uq_diagnostic_activity_session_order",
        ),
        ForeignKeyConstraint(
            ["diagnostic_session_id", "context_id"],
            [
                "conversational_diagnostic_contexts.diagnostic_session_id",
                "conversational_diagnostic_contexts.context_id",
            ],
            name="fk_diagnostic_activity_session_context",
            ondelete="CASCADE",
        ),
        CheckConstraint("sequence_order > 0", name="ck_diagnostic_activity_order"),
        CheckConstraint(
            "stage IN ('adaptation', 'listening_comprehension', "
            "'initial_response', 'guided_construction', 'connected_exchange', "
            "'transfer', 'context_selection')",
            name="ck_diagnostic_activity_stage",
        ),
        CheckConstraint(
            "modality IN ('listening', 'text', 'voice', 'selection')",
            name="ck_diagnostic_activity_modality",
        ),
        CheckConstraint(
            "expected_evidence_type IN ('comprehension', "
            "'spontaneous_production', 'supported_production', "
            "'connected_exchange', 'transfer', 'motivating_context')",
            name="ck_diagnostic_activity_evidence_type",
        ),
        CheckConstraint(
            "(stage = 'transfer' AND transfer_variant_id IS NOT NULL) OR "
            "(stage <> 'transfer' AND transfer_variant_id IS NULL)",
            name="ck_diagnostic_activity_transfer",
        ),
    )

    activity_id = Column(String, primary_key=True)
    diagnostic_session_id = Column(String, nullable=False)
    context_id = Column(String, nullable=False)
    prompt_id = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    communicative_intention = Column(Text, nullable=False)
    modality = Column(String, nullable=False)
    expected_evidence_type = Column(String, nullable=False)
    available_supports = Column(JSON, nullable=False)
    transfer_variant_id = Column(String, nullable=True)
    sequence_order = Column(Integer, nullable=False)


class ConversationalDiagnosticActivityProduction(Base):
    """Own one diagnostic production from exactly one activity.

    Asigna una producción diagnóstica a una única actividad propietaria.
    """

    __tablename__ = "conversational_diagnostic_activity_productions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["diagnostic_session_id", "activity_id", "prompt_id"],
            [
                "conversational_diagnostic_activities.diagnostic_session_id",
                "conversational_diagnostic_activities.activity_id",
                "conversational_diagnostic_activities.prompt_id",
            ],
            name="fk_activity_production_session_activity_prompt",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["production_id", "prompt_id"],
            ["learner_productions.id", "learner_productions.prompt_id"],
            name="fk_activity_production_production_prompt",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "diagnostic_session_id",
            "activity_id",
            "production_id",
            name="uq_activity_production_trace",
        ),
    )

    production_id = Column(Integer, primary_key=True)
    diagnostic_session_id = Column(String, nullable=False)
    activity_id = Column(String, nullable=False)
    prompt_id = Column(String, nullable=False)


class ConversationalDiagnosticSupportUsage(Base):
    """Persist support usage separately from production and observation.

    Persiste el uso de apoyo separado de producción y observación.
    """

    __tablename__ = "conversational_diagnostic_support_usages"
    __table_args__ = (
        ForeignKeyConstraint(
            ["diagnostic_session_id", "activity_id", "production_id"],
            [
                "conversational_diagnostic_activity_productions.diagnostic_session_id",
                "conversational_diagnostic_activity_productions.activity_id",
                "conversational_diagnostic_activity_productions.production_id",
            ],
            name="fk_diagnostic_support_activity_production",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "activity_id",
            "production_id",
            "sequence_order",
            name="uq_diagnostic_support_activity_production_order",
        ),
        CheckConstraint("sequence_order > 0", name="ck_diagnostic_support_order"),
        CheckConstraint(
            "support_type IN ('none', 'visual', 'repetition', 'keyword', "
            "'pattern', 'example', 'translation')",
            name="ck_diagnostic_support_type",
        ),
        CheckConstraint(
            "support_level IN ('none', 'minimal', 'moderate', 'full')",
            name="ck_diagnostic_support_level",
        ),
        CheckConstraint(
            "(support_type = 'none' AND support_level = 'none' "
            "AND withdrawn_afterward = false) OR "
            "(support_type <> 'none' AND support_level <> 'none')",
            name="ck_diagnostic_support_coherence",
        ),
    )

    id = Column(Integer, primary_key=True)
    diagnostic_session_id = Column(String, nullable=False)
    activity_id = Column(String, nullable=False)
    production_id = Column(Integer, nullable=False)
    support_type = Column(String, nullable=False)
    support_level = Column(String, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    provided_at = Column(DateTime(timezone=True), nullable=False)
    withdrawn_afterward = Column(Boolean, nullable=False)


class ConversationalDiagnosticObservation(Base):
    """Persist descriptive evidence apart from technical evaluation.

    Persiste evidencia descriptiva separada de la evaluación técnica.
    """

    __tablename__ = "conversational_diagnostic_observations"
    __table_args__ = (
        UniqueConstraint(
            "diagnostic_session_id",
            "observation_id",
            name="uq_diagnostic_observation_session_observation",
        ),
        UniqueConstraint(
            "diagnostic_session_id",
            "observation_id",
            "production_id",
            name="uq_diagnostic_observation_session_observation_production",
        ),
        ForeignKeyConstraint(
            ["diagnostic_session_id", "activity_id", "production_id"],
            [
                "conversational_diagnostic_activity_productions.diagnostic_session_id",
                "conversational_diagnostic_activity_productions.activity_id",
                "conversational_diagnostic_activity_productions.production_id",
            ],
            name="fk_diagnostic_observation_activity_production",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["diagnostic_session_id", "activity_id"],
            [
                "conversational_diagnostic_activities.diagnostic_session_id",
                "conversational_diagnostic_activities.activity_id",
            ],
            name="fk_diagnostic_observation_session_activity",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "(evidence_role = 'context_relevance' "
            "AND dimension = 'motivating_context' "
            "AND context_reference IS NOT NULL) OR "
            "(evidence_role <> 'context_relevance' "
            "AND dimension <> 'motivating_context' "
            "AND context_reference IS NULL)",
            name="ck_diagnostic_observation_context",
        ),
        CheckConstraint(
            "dimension IN ('listening_comprehension', 'response_initiation', "
            "'direct_english_construction', 'oral_production', 'continuity', "
            "'linguistic_retrieval', 'intelligibility', 'support_need', "
            "'transfer', 'motivating_context')",
            name="ck_diagnostic_observation_dimension",
        ),
        CheckConstraint(
            "evidence_role IN ('strength', 'development_need', "
            "'priority_blockage', 'context_relevance')",
            name="ck_diagnostic_observation_evidence_role",
        ),
        CheckConstraint(
            "support_level IN ('none', 'minimal', 'moderate', 'full')",
            name="ck_diagnostic_observation_support_level",
        ),
        CheckConstraint(
            "dimension NOT IN ('response_initiation', "
            "'direct_english_construction', 'oral_production', 'continuity', "
            "'linguistic_retrieval', 'intelligibility', 'support_need', "
            "'transfer') OR production_id IS NOT NULL",
            name="ck_diagnostic_observation_required_production",
        ),
    )

    observation_id = Column(String, primary_key=True)
    diagnostic_session_id = Column(String, nullable=False)
    activity_id = Column(String, nullable=False)
    production_id = Column(Integer, nullable=True)
    dimension = Column(String, nullable=False)
    evidence_role = Column(String, nullable=False)
    context_reference = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    support_level = Column(String, nullable=False)
    observer_id = Column(String, nullable=False)
    observer_version = Column(String, nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)


class ConversationalDiagnosticObservationEvaluation(Base):
    """Link an observation to an evaluation of its own production.

    Vincula una observación con una evaluación de su propia producción.
    """

    __tablename__ = "conversational_diagnostic_observation_evaluations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["diagnostic_session_id", "observation_id", "production_id"],
            [
                "conversational_diagnostic_observations.diagnostic_session_id",
                "conversational_diagnostic_observations.observation_id",
                "conversational_diagnostic_observations.production_id",
            ],
            name="fk_observation_evaluation_observation_production",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["evaluation_result_id", "production_id"],
            [
                "production_evaluation_results.id",
                "production_evaluation_results.production_id",
            ],
            name="fk_observation_evaluation_result_production",
            ondelete="CASCADE",
        ),
    )

    diagnostic_session_id = Column(String, primary_key=True)
    observation_id = Column(String, primary_key=True)
    evaluation_result_id = Column(Integer, primary_key=True)
    production_id = Column(Integer, nullable=False)


class InitialConversationalProfile(Base):
    """Persist an append-only, revisable initial pedagogical hypothesis.

    Persiste una hipótesis pedagógica inicial, acumulativa y revisable.
    """

    __tablename__ = "initial_conversational_profiles"
    __table_args__ = (
        UniqueConstraint(
            "diagnostic_session_id",
            "profile_id",
            name="uq_initial_profile_session_profile",
        ),
        CheckConstraint(
            "status IN ('provisional', 'confirmed')",
            name="ck_initial_profile_status",
        ),
        CheckConstraint(
            "recommended_support_level IN "
            "('none', 'minimal', 'moderate', 'full')",
            name="ck_initial_profile_support_level",
        ),
        CheckConstraint(
            "recommended_method = 'direct-english-construction'",
            name="ck_initial_profile_method",
        ),
    )

    profile_id = Column(String, primary_key=True)
    diagnostic_session_id = Column(
        String,
        ForeignKey(
            "conversational_diagnostic_sessions.diagnostic_session_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    status = Column(String, nullable=False)
    priority_blockage = Column(Text, nullable=False)
    target_capacity = Column(Text, nullable=False)
    recommended_support_level = Column(String, nullable=False)
    relevant_contexts = Column(JSON, nullable=False)
    recommended_method = Column(String, nullable=False)
    first_lesson_id = Column(String, nullable=False)
    review_criterion = Column(Text, nullable=False)
    evidence_summary = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=False)
    generator_id = Column(String, nullable=False)
    generator_version = Column(String, nullable=False)


class InitialConversationalProfileEvidence(Base):
    """Persist a same-session link from a profile to one observation.

    Persiste un vínculo de la misma sesión entre perfil y observación.
    """

    __tablename__ = "initial_conversational_profile_evidences"
    __table_args__ = (
        ForeignKeyConstraint(
            ["diagnostic_session_id", "profile_id"],
            [
                "initial_conversational_profiles.diagnostic_session_id",
                "initial_conversational_profiles.profile_id",
            ],
            name="fk_profile_evidence_session_profile",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["diagnostic_session_id", "observation_id"],
            [
                "conversational_diagnostic_observations.diagnostic_session_id",
                "conversational_diagnostic_observations.observation_id",
            ],
            name="fk_profile_evidence_session_observation",
            ondelete="CASCADE",
        ),
    )

    diagnostic_session_id = Column(String, primary_key=True)
    profile_id = Column(String, primary_key=True)
    observation_id = Column(String, primary_key=True)
