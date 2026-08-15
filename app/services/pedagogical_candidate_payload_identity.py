"""Derive the canonical identity of one pedagogical candidate payload."""

from dataclasses import dataclass
import hashlib
import json

from pydantic import BaseModel

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate


PAYLOAD_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class CandidatePayloadIdentity:
    """Identify one exact canonical pedagogical candidate payload."""

    unit_id: str
    candidate_revision: str
    payload_schema_version: str
    content_digest: str


def _dump_model(model: BaseModel) -> dict[str, object]:
    return model.model_dump(
        mode="json",
        by_alias=False,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
        round_trip=False,
        serialize_as_any=False,
    )


def _canonical_payload(
    candidate: PedagogicalUnitCandidate,
) -> dict[str, object]:
    return {
        "specification": _dump_model(candidate.specification),
        "candidate_unit": _dump_model(candidate.candidate_unit),
        "evaluation_plans": [
            _dump_model(plan)
            for plan in candidate.evaluation_plans
        ],
        "feedback_plans": [
            _dump_model(plan)
            for plan in candidate.feedback_plans
        ],
        "lesson_capability_plans": [
            _dump_model(plan)
            for plan in candidate.lesson_capability_plans
        ],
        "skill_coverage": [
            _dump_model(coverage)
            for coverage in candidate.skill_coverage
        ],
        "required_resource_ids": list(candidate.required_resource_ids),
    }


def _canonical_bytes(candidate: PedagogicalUnitCandidate) -> bytes:
    canonical_json = json.dumps(
        _canonical_payload(candidate),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return canonical_json.encode("utf-8")


def derive_candidate_payload_identity(
    candidate: PedagogicalUnitCandidate,
    *,
    candidate_revision: str,
) -> CandidatePayloadIdentity:
    """Derive the immutable identity of the canonical admission payload."""

    if not isinstance(candidate_revision, str) or not candidate_revision.strip():
        raise ValueError("candidate_revision must be a non-blank string")

    digest = hashlib.sha256(_canonical_bytes(candidate)).hexdigest()
    return CandidatePayloadIdentity(
        unit_id=candidate.specification.unit_id,
        candidate_revision=candidate_revision,
        payload_schema_version=PAYLOAD_SCHEMA_VERSION,
        content_digest="sha256:" + digest,
    )
