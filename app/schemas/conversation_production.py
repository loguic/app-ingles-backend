from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class LearnerProductionItem(BaseModel):
    """Represent one captured learner production without evaluating it.

    Representa una producción capturada sin evaluarla.
    """

    prompt_id: str
    turn_id: str
    modality: Literal["text", "voice"]
    response_text: Optional[str] = None
    audio_reference: Optional[str] = None

    @model_validator(mode="after")
    def validate_modality_content(self) -> "LearnerProductionItem":
        """Match the captured content with exactly one modality.

        Vincula el contenido capturado con una sola modalidad.
        """
        if self.modality == "text":
            if (
                self.response_text is None
                or not self.response_text.strip()
            ):
                raise ValueError(
                    "Text production requires non-blank response_text"
                )

            if self.audio_reference is not None:
                raise ValueError(
                    "Text production cannot define audio_reference"
                )

            return self

        if (
            self.audio_reference is None
            or not self.audio_reference.strip()
        ):
            raise ValueError(
                "Voice production requires non-blank audio_reference"
            )

        if self.response_text is not None:
            raise ValueError(
                "Voice production cannot define response_text"
            )

        return self


class ConversationProductionSubmission(BaseModel):
    """Group captured productions from one conversation.

    Agrupa las producciones capturadas de una conversación.
    """

    user_id: str
    level_id: str
    unit_id: str
    lesson_id: str
    conversation_id: str
    productions: list[LearnerProductionItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_prompt_ids(
        self,
    ) -> "ConversationProductionSubmission":
        """Keep one captured result per production prompt.

        Mantiene un resultado capturado por prompt de producción.
        """
        prompt_ids = [
            production.prompt_id
            for production in self.productions
        ]

        if len(prompt_ids) != len(set(prompt_ids)):
            raise ValueError(
                "Conversation production prompt IDs must be unique"
            )

        return self
