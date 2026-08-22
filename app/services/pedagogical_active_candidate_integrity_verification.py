"""Verify active candidate payload identities from acquired bytes.

Verifica identidades de payload de candidates activos desde bytes adquiridos.
"""

from dataclasses import dataclass
import json
from pathlib import Path

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_source_acquisition import (
    ActiveCandidateSourceAcquisition,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    ActiveCandidateSourceSnapshot,
)
from app.services.pedagogical_candidate_payload_identity import (
    PAYLOAD_SCHEMA_VERSION,
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)


@dataclass(frozen=True)
class CandidatePayloadIntegrityVerification:
    """Preserve one candidate payload identity verified from acquired bytes.

    Conserva una identidad de payload candidate verificada desde bytes adquiridos.
    """

    membership: ActiveCandidateMembership
    candidate_path: Path
    candidate_bytes: bytes
    derived_identity: CandidatePayloadIdentity


@dataclass(frozen=True)
class ActiveCandidateSourceCandidateIntegrityVerification:
    """Represent one source whose acquired candidate payloads all match identity.

    Representa una source cuyos payloads candidate adquiridos coinciden con
    su identidad.
    """

    snapshot: ActiveCandidateSourceSnapshot
    entries: tuple[CandidatePayloadIntegrityVerification, ...]


def verify_active_candidate_source_candidate_integrity(
    acquisition: ActiveCandidateSourceAcquisition,
) -> ActiveCandidateSourceCandidateIntegrityVerification:
    """Verify every acquired candidate payload without reopening its source path.

    Verifica cada payload candidate adquirido sin reabrir su path de source.
    """

    if not isinstance(acquisition, ActiveCandidateSourceAcquisition):
        raise ValueError("acquisition must be an ActiveCandidateSourceAcquisition")

    verifications: list[CandidatePayloadIntegrityVerification] = []
    for entry in acquisition.entries:
        declared_identity = entry.membership.identity
        if declared_identity.payload_schema_version != PAYLOAD_SCHEMA_VERSION:
            raise ValueError("unsupported payload schema version")

        reconstructed_candidate = _reconstruct_candidate(entry.candidate_bytes)
        derived_identity = derive_candidate_payload_identity(
            reconstructed_candidate,
            candidate_revision=declared_identity.candidate_revision,
        )
        if derived_identity != declared_identity:
            raise ValueError("candidate payload identity mismatch")

        verifications.append(
            CandidatePayloadIntegrityVerification(
                membership=entry.membership,
                candidate_path=entry.candidate_path,
                candidate_bytes=entry.candidate_bytes,
                derived_identity=derived_identity,
            )
        )

    return ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=acquisition.snapshot,
        entries=tuple(verifications),
    )


def _reconstruct_candidate(candidate_bytes: bytes) -> PedagogicalUnitCandidate:
    if not isinstance(candidate_bytes, bytes):
        raise ValueError("candidate_bytes must be bytes")

    try:
        text = candidate_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("candidate bytes must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("candidate bytes must not contain a UTF-8 BOM")

    try:
        document = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (TypeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("candidate bytes must be valid JSON") from error

    try:
        return PedagogicalUnitCandidate.model_validate(document)
    except ValueError as error:
        raise ValueError(
            "candidate bytes must reconstruct a valid PedagogicalUnitCandidate"
        ) from error


def _reject_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def _reject_nonstandard_json_constant(value: str) -> object:
    raise ValueError(f"nonstandard JSON constant: {value}")
