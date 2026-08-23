"""Acquire local admission record documents without provenance verification.

Adquiere documentos locales de admission record sin verificar todavía provenance.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Sequence

from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION,
    serialize_candidate_admission_record_document,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
)


_DECIDED_AT_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
)


@dataclass(frozen=True)
class ActiveCandidateAdmissionRecordBinding:
    """Associate one declared admission with one explicit local document path.

    Asocia una admisión declarada con un path local explícito de documento.
    """

    admission_id: str
    document_path: Path


@dataclass(frozen=True)
class AcquiredActiveCandidateAdmissionRecordEntry:
    """Keep one acquired, still-unverified admission record document.

    Conserva un documento de admission record adquirido y aún no verificado.
    """

    membership: ActiveCandidateMembership
    document_path: Path
    admission_record_bytes: bytes
    admission_record: AdmissionRecord


@dataclass(frozen=True)
class ActiveCandidateSourceAdmissionRecordAcquisition:
    """Represent acquired, unverified admission records for one B39 source.

    Representa admission records adquiridos y no verificados para una source B39.
    """

    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    )
    entries: tuple[AcquiredActiveCandidateAdmissionRecordEntry, ...]


def acquire_active_candidate_admission_records(
    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    ),
    *,
    admission_record_bindings: Sequence[ActiveCandidateAdmissionRecordBinding],
) -> ActiveCandidateSourceAdmissionRecordAcquisition:
    """Acquire every declared admission record without correspondence checks.

    Adquiere cada admission record declarado sin comprobar correspondencia.
    """

    if not isinstance(
        candidate_integrity_verification,
        ActiveCandidateSourceCandidateIntegrityVerification,
    ):
        raise ValueError(
            "candidate_integrity_verification must be an "
            "ActiveCandidateSourceCandidateIntegrityVerification"
        )

    bindings = tuple(admission_record_bindings)
    bindings_by_admission_id = _index_bindings(bindings)
    memberships = tuple(
        entry.membership
        for entry in candidate_integrity_verification.entries
    )
    declared_admission_ids = {
        membership.admission_id for membership in memberships
    }

    for binding in bindings:
        if binding.admission_id not in declared_admission_ids:
            raise ValueError(
                "unexpected active candidate admission record binding admission_id: "
                + binding.admission_id
            )

    for membership in memberships:
        if membership.admission_id not in bindings_by_admission_id:
            raise ValueError(
                "missing active candidate admission record binding admission_id: "
                + membership.admission_id
            )

    entries: list[AcquiredActiveCandidateAdmissionRecordEntry] = []
    for membership in memberships:
        binding = bindings_by_admission_id.get(membership.admission_id)
        assert binding is not None

        _validate_document_path(binding.document_path)
        admission_record_bytes = _read_file_once(binding.document_path)
        admission_record = _reconstruct_admission_record(admission_record_bytes)
        _require_byte_conformant_document(
            admission_record,
            admission_record_bytes,
        )
        entries.append(
            AcquiredActiveCandidateAdmissionRecordEntry(
                membership=membership,
                document_path=binding.document_path,
                admission_record_bytes=admission_record_bytes,
                admission_record=admission_record,
            )
        )

    return ActiveCandidateSourceAdmissionRecordAcquisition(
        candidate_integrity_verification=candidate_integrity_verification,
        entries=tuple(entries),
    )


def _index_bindings(
    bindings: tuple[ActiveCandidateAdmissionRecordBinding, ...],
) -> dict[str, ActiveCandidateAdmissionRecordBinding]:
    bindings_by_admission_id: dict[str, ActiveCandidateAdmissionRecordBinding] = {}
    document_paths: set[Path] = set()
    for binding in bindings:
        if not isinstance(binding, ActiveCandidateAdmissionRecordBinding):
            raise ValueError(
                "admission_record_bindings must contain "
                "ActiveCandidateAdmissionRecordBinding"
            )
        if type(binding.admission_id) is not str:
            raise ValueError("admission record binding admission_id must be a string")
        if binding.admission_id in bindings_by_admission_id:
            raise ValueError(
                "duplicate active candidate admission record binding admission_id: "
                + binding.admission_id
            )
        if not isinstance(binding.document_path, Path):
            raise ValueError("document_path must be a Path")
        if binding.document_path in document_paths:
            raise ValueError(
                "duplicate active candidate admission record binding document_path"
            )
        bindings_by_admission_id[binding.admission_id] = binding
        document_paths.add(binding.document_path)
    return bindings_by_admission_id


def _validate_document_path(document_path: Path) -> None:
    if not isinstance(document_path, Path):
        raise ValueError("document_path must be a Path")
    if not document_path.is_absolute():
        raise ValueError("document_path must be absolute")
    if document_path.is_symlink():
        raise ValueError("document_path must not be a symlink")
    if not document_path.exists():
        raise ValueError("document_path must exist")
    if not document_path.is_file():
        raise ValueError("document_path must be a regular file")


def _read_file_once(document_path: Path) -> bytes:
    with document_path.open("rb") as document_file:
        return document_file.read()


def _reconstruct_admission_record(admission_record_bytes: bytes) -> AdmissionRecord:
    document = _parse_json_document(admission_record_bytes)
    if type(document) is not dict:
        raise ValueError("admission record document must be an object")
    _require_exact_keys(
        document,
        {
            "document_schema_version",
            "admission_id",
            "identity",
            "decision",
            "reviewer_id",
            "decided_at",
        },
        "admission record document",
    )

    if document["document_schema_version"] != ADMISSION_RECORD_DOCUMENT_SCHEMA_VERSION:
        raise ValueError("unsupported admission record document schema")
    if type(document["document_schema_version"]) is not str:
        raise ValueError("admission record document schema version must be a string")
    if type(document["admission_id"]) is not str:
        raise ValueError("admission record document admission_id must be a string")
    if type(document["decision"]) is not str:
        raise ValueError("admission record document decision must be a string")
    if type(document["reviewer_id"]) is not str:
        raise ValueError("admission record document reviewer_id must be a string")
    if type(document["decided_at"]) is not str:
        raise ValueError("admission record document decided_at must be a string")

    identity = _reconstruct_identity(document["identity"])
    decided_at = _parse_decided_at(document["decided_at"])
    try:
        return AdmissionRecord(
            admission_id=document["admission_id"],
            identity=identity,
            decision=document["decision"],
            reviewer_id=document["reviewer_id"],
            decided_at=decided_at,
        )
    except ValueError as error:
        raise ValueError(
            "admission record document must reconstruct a valid AdmissionRecord"
        ) from error


def _parse_json_document(admission_record_bytes: bytes) -> object:
    if not isinstance(admission_record_bytes, bytes):
        raise ValueError("admission_record_bytes must be bytes")
    try:
        text = admission_record_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("admission record document must be valid UTF-8") from error
    if text.startswith("\ufeff"):
        raise ValueError("admission record document must not contain a UTF-8 BOM")

    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_json_constant,
        )
    except (TypeError, json.JSONDecodeError, ValueError) as error:
        raise ValueError("admission record document must be valid JSON") from error


def _reconstruct_identity(document: object) -> CandidatePayloadIdentity:
    if type(document) is not dict:
        raise ValueError("admission record document identity must be an object")
    _require_exact_keys(
        document,
        {
            "unit_id",
            "candidate_revision",
            "payload_schema_version",
            "content_digest",
        },
        "admission record document identity",
    )
    values = {
        key: document[key]
        for key in (
            "unit_id",
            "candidate_revision",
            "payload_schema_version",
            "content_digest",
        )
    }
    if any(type(value) is not str for value in values.values()):
        raise ValueError("admission record document identity values must be strings")
    return CandidatePayloadIdentity(**values)


def _parse_decided_at(value: str) -> datetime:
    if not _DECIDED_AT_PATTERN.fullmatch(value):
        raise ValueError(
            "admission record document decided_at must use "
            "YYYY-MM-DDTHH:MM:SS.ffffffZ"
        )
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError as error:
        raise ValueError("admission record document decided_at must be valid") from error


def _require_exact_keys(
    document: dict[str, object],
    expected_keys: set[str],
    name: str,
) -> None:
    if set(document) != expected_keys:
        raise ValueError(f"{name} must contain exactly its contractual fields")


def _require_byte_conformant_document(
    admission_record: AdmissionRecord,
    admission_record_bytes: bytes,
) -> None:
    expected_bytes = serialize_candidate_admission_record_document(admission_record)
    if admission_record_bytes != expected_bytes:
        raise ValueError(
            "admission record document physical format is not byte-conformant "
            "with v1"
        )


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
