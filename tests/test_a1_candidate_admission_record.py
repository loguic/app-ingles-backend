import json
from datetime import datetime
from pathlib import Path

import pytest

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_candidate_admission import AdmissionRecord
from app.services.pedagogical_candidate_admission_record_document import (
    serialize_candidate_admission_record_document,
)
from app.services.pedagogical_candidate_admission_verification import (
    verify_candidate_admission,
)
from app.services.pedagogical_candidate_payload_identity import (
    CandidatePayloadIdentity,
    derive_candidate_payload_identity,
)


ROOT = Path(__file__).resolve().parents[1]
RELATIVE_DOCUMENT_PATH = Path(
    "content/admissions/a1-u1/adm-a1-u1-001.json"
)
EXPECTED_DIGEST = (
    "sha256:23e0d0e1eba8fb7c6b1c73097f01350abe06c84af30fab49f9e646fd9f095018"
)


def _resolve_document_path(relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("admission document path must stay under repository root")
    document_path = ROOT / relative_path
    if not document_path.is_relative_to(ROOT):
        raise ValueError("admission document path must stay under repository root")
    return document_path


def _load_candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate_json(
        (
            ROOT
            / "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json"
        ).read_text(encoding="utf-8")
    )


def _load_record(document_path: Path) -> AdmissionRecord:
    document = json.loads(document_path.read_text(encoding="utf-8"))
    document_identity = document["identity"]
    identity = CandidatePayloadIdentity(
        unit_id=document_identity["unit_id"],
        candidate_revision=document_identity["candidate_revision"],
        payload_schema_version=document_identity["payload_schema_version"],
        content_digest=document_identity["content_digest"],
    )
    return AdmissionRecord(
        admission_id=document["admission_id"],
        identity=identity,
        decision=document["decision"],
        reviewer_id=document["reviewer_id"],
        decided_at=datetime.fromisoformat(
            document["decided_at"].replace("Z", "+00:00")
        ),
    )


def test_a1_admission_record_is_canonical_and_verifies() -> None:
    document_path = _resolve_document_path(RELATIVE_DOCUMENT_PATH)
    candidate = _load_candidate()
    record = _load_record(document_path)

    assert record.admission_id == "adm-a1-u1-001"
    assert record.reviewer_id == "reviewer-human-001"
    assert record.identity.unit_id == "a1-u1"
    assert record.identity.candidate_revision == "a1-u1-candidate-v3"
    assert record.identity.payload_schema_version == "1.0"
    assert record.identity.content_digest == EXPECTED_DIGEST
    assert record.decision == "admitted"
    assert document_path.read_bytes() == serialize_candidate_admission_record_document(
        record
    )
    assert derive_candidate_payload_identity(
        candidate,
        candidate_revision=record.identity.candidate_revision,
    ) == record.identity

    verification = verify_candidate_admission(candidate, record)

    assert verification.verified is True
    assert verification.local_validation_passed is True
    assert verification.pending_human_decisions_clear is True
    assert verification.human_decision_admitted is True


def test_a1_admission_document_path_rejects_repository_escape() -> None:
    with pytest.raises(ValueError, match="stay under repository root"):
        _resolve_document_path(Path("../outside.json"))
