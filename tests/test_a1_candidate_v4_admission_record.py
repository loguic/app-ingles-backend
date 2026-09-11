import hashlib
import json
from datetime import datetime
from pathlib import Path

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
RECORD_PATH = ROOT / "content/admissions/a1-u1/adm-a1-u1-002.json"
V4_PATH = ROOT / "content/candidates/a1-u1/pedagogical-unit-candidate-v4.json"
EXPECTED_DIGEST = (
    "sha256:e75a5c9864adb86a3152e67ab9c97951372e11ed5400b70406f033e6f70b9a8d"
)
HISTORICAL_FILE_HASHES = {
    "content/candidates/a1-u1/pedagogical-unit-candidate-v3.json": (
        "1e674bc6d4058f58ec7c6b21252c7aa26b3974e058db5e64aa6e4b4802b6894f"
    ),
    "content/admissions/a1-u1/adm-a1-u1-001.json": (
        "6bc89e19438076c1d31cb22ddd55e21de0ce3d6574cc939a52c377a5bb6885ce"
    ),
    "content/active-source/active-candidate-source-001.json": (
        "c442a6ca85218a2529f1bd0e02f36ddcf4ea7c71a754e0069c0552b2c2e47fab"
    ),
}


def _record() -> AdmissionRecord:
    document = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    return AdmissionRecord(
        admission_id=document["admission_id"],
        identity=CandidatePayloadIdentity(**document["identity"]),
        decision=document["decision"],
        reviewer_id=document["reviewer_id"],
        decided_at=datetime.fromisoformat(document["decided_at"].replace("Z", "+00:00")),
    )


def test_a1_v4_admission_record_is_canonical_and_verifies() -> None:
    candidate = PedagogicalUnitCandidate.model_validate_json(
        V4_PATH.read_text(encoding="utf-8")
    )
    record = _record()

    assert RECORD_PATH == ROOT / "content/admissions/a1-u1/adm-a1-u1-002.json"
    assert record.admission_id == "adm-a1-u1-002"
    assert record.reviewer_id == "reviewer-human-001"
    assert record.decision == "admitted"
    assert record.identity.unit_id == "a1-u1"
    assert record.identity.candidate_revision == "a1-u1-candidate-v4"
    assert record.identity.payload_schema_version == "1.0"
    assert record.identity.content_digest == EXPECTED_DIGEST
    assert RECORD_PATH.read_bytes() == serialize_candidate_admission_record_document(
        record
    )
    assert derive_candidate_payload_identity(
        candidate,
        candidate_revision="a1-u1-candidate-v4",
    ) == record.identity
    assert verify_candidate_admission(candidate, record).verified is True


def test_a1_v3_admission_and_snapshot_history_remain_unchanged() -> None:
    for relative_path, expected_hash in HISTORICAL_FILE_HASHES.items():
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == (
            expected_hash
        )
