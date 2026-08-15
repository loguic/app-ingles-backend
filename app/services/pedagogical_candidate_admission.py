"""Represent final human admission decisions for candidate payload identities."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


AdmissionDecision = Literal["admitted", "rejected"]


@dataclass(frozen=True)
class AdmissionRecord:
    """Record one final human decision about an exact payload identity."""

    admission_id: str
    identity: CandidatePayloadIdentity
    decision: AdmissionDecision
    reviewer_id: str
    decided_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.admission_id, str) or not self.admission_id.strip():
            raise ValueError("admission_id must be a non-blank string")
        if not isinstance(self.identity, CandidatePayloadIdentity):
            raise ValueError("identity must be a CandidatePayloadIdentity")
        if not isinstance(self.decision, str):
            raise ValueError("decision must be a string")
        if self.decision not in ("admitted", "rejected"):
            raise ValueError("decision must be 'admitted' or 'rejected'")
        if not isinstance(self.reviewer_id, str) or not self.reviewer_id.strip():
            raise ValueError("reviewer_id must be a non-blank string")
        if not isinstance(self.decided_at, datetime):
            raise ValueError("decided_at must be a datetime")
        if (
            self.decided_at.tzinfo is None
            or self.decided_at.utcoffset() is None
            or self.decided_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("decided_at must be timezone-aware UTC")
