"""Tests for the pure A1 runtime projection constructor v1."""

from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import app.services.pedagogical_runtime_projection_builder as builder
from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
    CandidatePayloadIntegrityVerification,
)
from app.services.pedagogical_active_candidate_membership import (
    ActiveCandidateMembership,
)
from app.services.pedagogical_active_candidate_membership_collection import (
    build_active_candidate_membership_collection,
)
from app.services.pedagogical_active_candidate_source_integrity_verification import (
    ActiveCandidateSourceIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_resource_integrity_verification import (
    ActiveCandidateSourceResourceIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_snapshot import (
    build_active_candidate_source_snapshot,
)
from app.services.pedagogical_active_candidate_source_snapshot_manifest import (
    serialize_active_candidate_source_snapshot_manifest,
)
from app.services.pedagogical_candidate_payload_identity import (
    derive_candidate_payload_identity,
)
from app.services.pedagogical_runtime_activation_documents import (
    serialize_runtime_content_tree,
)


def _candidate() -> PedagogicalUnitCandidate:
    return PedagogicalUnitCandidate.model_validate_json(
        Path("content/candidates/a1-u1/pedagogical-unit-candidate-v4.json").read_bytes()
    )


def _b39(
    *,
    candidate_bytes: bytes | None = None,
    membership: ActiveCandidateMembership | None = None,
) -> ActiveCandidateSourceCandidateIntegrityVerification:
    candidate = _candidate()
    identity = derive_candidate_payload_identity(candidate, candidate_revision="candidate-v4")
    membership = membership or ActiveCandidateMembership(
        identity=identity,
        admission_id="adm-a1-u1-002",
    )
    snapshot = build_active_candidate_source_snapshot(
        build_active_candidate_membership_collection((membership,)),
        snapshot_revision="active-candidate-source-002",
    )
    entry = CandidatePayloadIntegrityVerification(
        membership=membership,
        candidate_path=Path("/not-read/candidate.json"),
        candidate_bytes=candidate_bytes or json.dumps(
            candidate.model_dump(mode="json"),
            ensure_ascii=False,
        ).encode("utf-8"),
        derived_identity=identity,
    )
    return ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=snapshot,
        entries=(entry,),
    )


def _b52(
    b43_b39: ActiveCandidateSourceCandidateIntegrityVerification,
    *,
    b51_b39: ActiveCandidateSourceCandidateIntegrityVerification | None = None,
) -> ActiveCandidateSourceIntegrityVerification:
    b51_b39 = b51_b39 or b43_b39
    b43 = ActiveCandidateSourceCurrentAdmissionGateReevaluation(
        admission_record_correspondence_verification=cast(
            Any,
            SimpleNamespace(
                admission_record_acquisition=SimpleNamespace(
                    candidate_integrity_verification=b43_b39
                )
            ),
        ),
        entries=(),
    )
    b51 = ActiveCandidateSourceResourceIntegrityVerification(
        observed_resource_identity_collection=cast(
            Any,
            SimpleNamespace(
                resource_acquisition=SimpleNamespace(
                    resource_binding_collection=SimpleNamespace(
                        expected_resource_coverage_verification=SimpleNamespace(
                            required_resource_inventory=SimpleNamespace(
                                candidate_integrity_verification=b51_b39
                            )
                        )
                    )
                )
            ),
        )
    )
    return ActiveCandidateSourceIntegrityVerification(
        current_admission_gate_reevaluation=b43,
        resource_integrity_verification=b51,
    )


def test_builds_one_canonical_projection_from_one_shared_b52_source() -> None:
    b39 = _b39()
    result = builder.build_eligible_runtime_content_projection(_b52(b39))
    candidate = _candidate()

    assert result.source_snapshot_revision == "active-candidate-source-002"
    assert result.source_snapshot_manifest_digest == "sha256:" + hashlib.sha256(
        serialize_active_candidate_source_snapshot_manifest(b39.snapshot)
    ).hexdigest()
    assert result.content_tree.levels[0].code == candidate.specification.level
    assert result.content_tree.levels[0].units == [candidate.candidate_unit]
    assert result.runtime_projection_digest == "sha256:" + hashlib.sha256(
        serialize_runtime_content_tree(result.content_tree)
    ).hexdigest()


def test_rejects_invalid_input_and_causally_mismatched_b39() -> None:
    with pytest.raises(ValueError, match="ActiveCandidateSourceIntegrityVerification"):
        builder.build_eligible_runtime_content_projection(cast(Any, object()))

    first = _b39()
    second = _b39()
    with pytest.raises(ValueError, match="causal source mismatch"):
        builder.build_eligible_runtime_content_projection(_b52(first, b51_b39=second))


def test_rejects_invalid_bytes_and_candidate_membership_mismatch() -> None:
    invalid_b39 = _b39(candidate_bytes=b"not json")
    with pytest.raises(ValueError, match="candidate bytes are invalid"):
        builder.build_eligible_runtime_content_projection(_b52(invalid_b39))

    identity = derive_candidate_payload_identity(_candidate(), candidate_revision="candidate-v4")
    mismatched_membership = ActiveCandidateMembership(
        identity=replace(identity, unit_id="a1-u99"),
        admission_id="adm-a1-u1-002",
    )
    mismatched_b39 = _b39(membership=mismatched_membership)
    with pytest.raises(ValueError, match="candidate unit does not match membership"):
        builder.build_eligible_runtime_content_projection(_b52(mismatched_b39))


def test_rejects_empty_or_multiple_active_candidates() -> None:
    b39 = _b39()
    empty = replace(b39, entries=())
    with pytest.raises(ValueError, match="exactly one active candidate"):
        builder.build_eligible_runtime_content_projection(_b52(empty))

    multiple = replace(b39, entries=(b39.entries[0], b39.entries[0]))
    with pytest.raises(ValueError, match="exactly one active candidate"):
        builder.build_eligible_runtime_content_projection(_b52(multiple))


def test_constructor_has_no_io_publication_or_runtime_authority_dependencies() -> None:
    source = inspect.getsource(builder)
    for forbidden in (
        "Path",
        "open(",
        "read_bytes",
        "os.",
        "tempfile",
        "publish_",
        "ActiveRuntimePointer",
        "content_service",
        "CONTENT_TREE_PATH",
        "verify_active_candidate_source_integrity",
    ):
        assert forbidden not in source
