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
