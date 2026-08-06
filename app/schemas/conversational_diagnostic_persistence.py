from pydantic import BaseModel, Field, model_validator

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticObservation,
    ConversationalDiagnosticSession,
    DiagnosticSupportUsage,
)
from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_activity_context,
    validate_diagnostic_activity_sequence,
    validate_diagnostic_context_references,
    validate_diagnostic_observation,
    validate_diagnostic_session_context,
)


def _validate_observation_collection(
    diagnostic_session_id: str,
    observations: list[ConversationalDiagnosticObservation],
) -> None:
    observation_ids: set[str] = set()
    session_reference = ConversationalDiagnosticSession.model_construct(
        diagnostic_session_id=diagnostic_session_id
    )
    for observation in observations:
        if observation.observation_id in observation_ids:
            raise ValueError(
                "Diagnostic observations must have unique identifiers"
            )
        observation_ids.add(observation.observation_id)
        activity_reference = ConversationalDiagnosticActivity.model_construct(
            diagnostic_session_id=diagnostic_session_id,
            activity_id=observation.activity_id,
        )
        validate_diagnostic_observation(
            session_reference,
            activity_reference,
            observation,
        )


class ConversationalDiagnosticObservationsBatch(BaseModel):
    """Group new diagnostic observations for one atomic enrichment.

    Agrupa nuevas observaciones diagnósticas para un enriquecimiento atómico.
    """

    diagnostic_session_id: str
    observations: list[ConversationalDiagnosticObservation] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_observations(
        self,
    ) -> "ConversationalDiagnosticObservationsBatch":
        _validate_observation_collection(
            self.diagnostic_session_id,
            self.observations,
        )
        return self


class ConversationalDiagnosticActivityProductionSetup(BaseModel):
    """Reference one owned production and its diagnostic supports.

    Referencia una producción propia y sus apoyos diagnósticos.
    """

    diagnostic_session_id: str
    activity_id: str
    production_id: int = Field(gt=0)
    support_usages: list[DiagnosticSupportUsage] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_support_references(
        self,
    ) -> "ConversationalDiagnosticActivityProductionSetup":
        sequence_orders: list[int] = []
        for usage in self.support_usages:
            if usage.diagnostic_session_id != self.diagnostic_session_id:
                raise ValueError(
                    "Diagnostic support must belong to the association session"
                )
            if usage.activity_id != self.activity_id:
                raise ValueError(
                    "Diagnostic support must belong to the association activity"
                )
            if usage.production_id != self.production_id:
                raise ValueError(
                    "Diagnostic support must belong to the association production"
                )
            sequence_orders.append(usage.sequence_order)

        if len(sequence_orders) != len(set(sequence_orders)):
            raise ValueError(
                "Diagnostic supports must have unique sequence orders "
                "within an association"
            )
        if sequence_orders != sorted(sequence_orders):
            raise ValueError(
                "Diagnostic supports must follow sequence order"
            )
        return self


def _validate_association_collection(
    diagnostic_session_id: str,
    associations: list[ConversationalDiagnosticActivityProductionSetup],
) -> None:
    association_keys: set[tuple[str, int]] = set()
    production_ids: set[int] = set()
    for association in associations:
        if association.diagnostic_session_id != diagnostic_session_id:
            raise ValueError(
                "Diagnostic production must belong to the aggregate session"
            )
        key = (association.activity_id, association.production_id)
        if key in association_keys:
            raise ValueError(
                "Diagnostic activity-production associations must be unique"
            )
        if association.production_id in production_ids:
            raise ValueError(
                "A diagnostic production cannot belong to multiple activities"
            )
        association_keys.add(key)
        production_ids.add(association.production_id)


class ConversationalDiagnosticProductionSupportsBatch(BaseModel):
    """Group new production ownership and support evidence atomically.

    Agrupa de forma atómica nueva propiedad de producciones y sus apoyos.
    """

    diagnostic_session_id: str
    associations: list[ConversationalDiagnosticActivityProductionSetup] = Field(
        min_length=1
    )

    @model_validator(mode="after")
    def validate_associations(
        self,
    ) -> "ConversationalDiagnosticProductionSupportsBatch":
        _validate_association_collection(
            self.diagnostic_session_id,
            self.associations,
        )
        return self


class ConversationalDiagnosticSessionSetup(BaseModel):
    """Group one validated diagnostic session configuration.

    Agrupa una configuración validada de sesión diagnóstica.
    """

    session: ConversationalDiagnosticSession
    context: ConversationalDiagnosticContext
    activities: list[ConversationalDiagnosticActivity] = Field(
        min_length=1
    )
    production_supports: list[
        ConversationalDiagnosticActivityProductionSetup
    ] = Field(default_factory=list)
    observations: list[ConversationalDiagnosticObservation] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_setup(self) -> "ConversationalDiagnosticSessionSetup":
        """Reuse canonical cross-contract diagnostic validators.

        Reutiliza los validadores canónicos entre contratos diagnósticos.
        """
        validate_diagnostic_session_context(self.session, self.context)
        validate_diagnostic_activity_sequence(
            self.session,
            self.activities,
        )
        for activity in self.activities:
            validate_diagnostic_activity_context(
                self.session,
                self.context,
                activity,
            )
        _validate_association_collection(
            self.session.diagnostic_session_id,
            self.production_supports,
        )
        activity_ids = {activity.activity_id for activity in self.activities}
        if any(
            association.activity_id not in activity_ids
            for association in self.production_supports
        ):
            raise ValueError(
                "Diagnostic production must reference an aggregate activity"
            )
        _validate_observation_collection(
            self.session.diagnostic_session_id,
            self.observations,
        )
        activity_by_id = {
            activity.activity_id: activity for activity in self.activities
        }
        for observation in self.observations:
            activity = activity_by_id.get(observation.activity_id)
            if activity is None:
                raise ValueError(
                    "Diagnostic observation must reference an aggregate activity"
                )
            validate_diagnostic_observation(
                self.session,
                activity,
                observation,
            )
        validate_diagnostic_context_references(
            self.context,
            self.observations,
        )
        return self
