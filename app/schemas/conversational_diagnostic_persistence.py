from pydantic import BaseModel, Field, model_validator

from app.schemas.conversational_diagnostic import (
    ConversationalDiagnosticActivity,
    ConversationalDiagnosticContext,
    ConversationalDiagnosticSession,
)
from app.services.conversational_diagnostic_validation_service import (
    validate_diagnostic_activity_context,
    validate_diagnostic_activity_sequence,
    validate_diagnostic_session_context,
)


class ConversationalDiagnosticSessionSetup(BaseModel):
    """Group one validated diagnostic session configuration.

    Agrupa una configuración validada de sesión diagnóstica.
    """

    session: ConversationalDiagnosticSession
    context: ConversationalDiagnosticContext
    activities: list[ConversationalDiagnosticActivity] = Field(
        min_length=1
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
        return self
