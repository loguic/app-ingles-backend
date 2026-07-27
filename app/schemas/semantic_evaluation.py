import re

from pydantic import BaseModel, Field, model_validator


class SemanticEvaluationRule(BaseModel):
    """Declare one deterministic semantic evaluation rule.

    Declara una regla determinista de evaluación semántica.
    """

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    criterion_id: str
    patterns: list[str] = Field(min_length=1)
    case_sensitive: bool = False

    @model_validator(mode="after")
    def validate_patterns(self) -> "SemanticEvaluationRule":
        """Require unique, non-blank and valid regular expressions.

        Exige expresiones regulares únicas, no vacías y válidas.
        """
        if len(self.patterns) != len(set(self.patterns)):
            raise ValueError("Semantic rule patterns must be unique")

        for pattern in self.patterns:
            if not pattern.strip():
                raise ValueError("Semantic rule patterns cannot be blank")
            try:
                re.compile(pattern)
            except re.error as error:
                raise ValueError(
                    "Semantic rule contains invalid regex: " + str(error)
                ) from error

        return self
