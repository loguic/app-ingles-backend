from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PhoneticCalibrationSample(BaseModel):
    """Describe one controlled human calibration sample.

    Describe una muestra humana controlada para calibración.
    """

    sample_id: str = Field(min_length=1)
    reference_text: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    audio_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_class: Literal["unlabeled", "acceptable", "variant", "known_error"]


class RepresentativePhoneticCalibrationSample(PhoneticCalibrationSample):
    """Identify a calibration sample by pseudonymous speaker and session.

    Identifica una muestra de calibración por hablante y sesión pseudónimos.
    """

    speaker_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


class PhoneticCalibrationHumanLabel(BaseModel):
    """Record one independent human judgment for a calibration sample.

    Registra un juicio humano independiente para una muestra de calibración.
    """

    sample_id: str = Field(min_length=1)
    labeler_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label: Literal["acceptable", "variant", "known_error"]


class PhoneticCalibrationMeasurement(BaseModel):
    """Represent one reproducible analyzer result for calibration.

    Representa un resultado reproducible del analizador para calibración.
    """

    sample_id: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    analyzed_at: datetime


class RepresentativePhoneticCalibrationCoverage(BaseModel):
    """Describe observable coverage of a representative calibration corpus.

    Describe la cobertura observable de un corpus representativo de calibración.
    """

    sample_count: int = Field(ge=0)
    speaker_count: int = Field(ge=0)
    session_count: int = Field(ge=0)


class RepresentativePhoneticCalibrationObservation(BaseModel):
    """Link a representative human sample to its acoustic measurement.

    Vincula una muestra humana representativa con su medición acústica.
    """

    sample: RepresentativePhoneticCalibrationSample
    measurement: PhoneticCalibrationMeasurement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.sample.sample_id != self.measurement.sample_id:
            raise ValueError("Calibration sample and measurement must share sample_id")
        return self


class PhoneticCalibrationObservation(BaseModel):
    """Link one controlled sample to its acoustic measurement.

    Vincula una muestra controlada con su medición acústica.
    """

    sample: PhoneticCalibrationSample
    measurement: PhoneticCalibrationMeasurement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.sample.sample_id != self.measurement.sample_id:
            raise ValueError("Calibration sample and measurement must share sample_id")
        return self

class PhoneticCalibrationHumanAgreement(BaseModel):
    """Summarize observed human-label agreement without deriving truth.

    Resume el acuerdo observado entre etiquetas humanas sin derivar verdad.
    """

    sample_id: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    label_count: int = Field(ge=1)
    labeler_count: int = Field(ge=1)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous: bool


class PhoneticCalibrationHumanRelationship(BaseModel):
    """Relate technical measurement to descriptive human agreement.

    Relaciona medición técnica con acuerdo humano descriptivo.
    """

    measurement: PhoneticCalibrationMeasurement
    human_labels: list[PhoneticCalibrationHumanLabel] = Field(default_factory=list)
    human_agreement: PhoneticCalibrationHumanAgreement

    @model_validator(mode="after")
    def validate_sample_identity(self):
        if self.measurement.sample_id != self.human_agreement.sample_id:
            raise ValueError("Calibration measurement and human agreement must share sample_id")

        for label in self.human_labels:
            if (
                label.sample_id != self.human_agreement.sample_id
                or label.rubric_version != self.human_agreement.rubric_version
            ):
                raise ValueError(
                    "Human labels and human agreement must share sample_id and rubric_version"
                )

        return self


class PhoneticCalibrationModelHumanObservation(BaseModel):
    """Describe one technical measurement beside human agreement.

    Describe una medición técnica junto al acuerdo humano observado.
    """

    sample_id: str = Field(min_length=1)
    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    label_count: int = Field(ge=1)
    labeler_count: int = Field(ge=1)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous: bool


class PhoneticCalibrationModelHumanSummary(BaseModel):
    """Summarize descriptive model-human observations by versioned context.

    Resume observaciones descriptivas modelo-humano por contexto versionado.
    """

    analyzer_id: str = Field(min_length=1)
    analyzer_version: str = Field(min_length=1)
    rubric_version: str = Field(min_length=1)
    observation_count: int = Field(ge=1)
    sample_count: int = Field(ge=1)
    score_min: float = Field(ge=0.0, le=1.0)
    score_max: float = Field(ge=0.0, le=1.0)
    score_mean: float = Field(ge=0.0, le=1.0)
    label_counts: dict[Literal["acceptable", "variant", "known_error"], int]
    unanimous_count: int = Field(ge=0)
