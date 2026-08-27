"""Tests for active candidate source integrity composition v1."""

from dataclasses import FrozenInstanceError, fields
import inspect
from types import SimpleNamespace
from typing import Any, cast

import pytest

import app.services.pedagogical_active_candidate_source_integrity_verification as integrity
from app.services.pedagogical_active_candidate_current_admission_gate_reevaluation import (
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
)
from app.services.pedagogical_active_candidate_integrity_verification import (
    ActiveCandidateSourceCandidateIntegrityVerification,
)
from app.services.pedagogical_active_candidate_source_resource_integrity_verification import (
    ActiveCandidateSourceResourceIntegrityVerification,
)


def _candidate_integrity(
    *,
    snapshot: object | None = None,
) -> ActiveCandidateSourceCandidateIntegrityVerification:
    return ActiveCandidateSourceCandidateIntegrityVerification(
        snapshot=cast(Any, snapshot or SimpleNamespace(snapshot_revision="source-r1")),
        entries=(),
    )


def _positive_branches(
    candidate_integrity_verification: (
        ActiveCandidateSourceCandidateIntegrityVerification
    ),
    *,
    admission_entries: tuple[object, ...] = (),
    observed_entries: tuple[object, ...] = (),
) -> tuple[
    ActiveCandidateSourceCurrentAdmissionGateReevaluation,
    ActiveCandidateSourceResourceIntegrityVerification,
]:
    admission_record_acquisition = SimpleNamespace(
        candidate_integrity_verification=candidate_integrity_verification
    )
    current_admission_gate_reevaluation = (
        ActiveCandidateSourceCurrentAdmissionGateReevaluation(
            admission_record_correspondence_verification=cast(
                Any,
                SimpleNamespace(
                    admission_record_acquisition=admission_record_acquisition
                ),
            ),
            entries=cast(Any, admission_entries),
        )
    )

    expected_resource_coverage_verification = SimpleNamespace(
        required_resource_inventory=SimpleNamespace(
            candidate_integrity_verification=candidate_integrity_verification
        )
    )
    observed_resource_identity_collection = SimpleNamespace(
        resource_acquisition=SimpleNamespace(
            resource_binding_collection=SimpleNamespace(
                expected_resource_coverage_verification=(
                    expected_resource_coverage_verification
                )
            )
        ),
        entries=observed_entries,
    )
    resource_integrity_verification = (
        ActiveCandidateSourceResourceIntegrityVerification(
            observed_resource_identity_collection=cast(
                Any,
                observed_resource_identity_collection,
            )
        )
    )
    return current_admission_gate_reevaluation, resource_integrity_verification


def test_public_shape_api_and_input_identity_preservation() -> None:
    b39 = _candidate_integrity()
    b43, b51 = _positive_branches(b39)

    result = integrity.verify_active_candidate_source_integrity(b43, b51)

    assert [
        field.name
        for field in fields(integrity.ActiveCandidateSourceIntegrityVerification)
    ] == [
        "current_admission_gate_reevaluation",
        "resource_integrity_verification",
    ]
    assert list(
        inspect.signature(
            integrity.verify_active_candidate_source_integrity
        ).parameters
    ) == [
        "current_admission_gate_reevaluation",
        "resource_integrity_verification",
    ]
    assert result.current_admission_gate_reevaluation is b43
    assert result.resource_integrity_verification is b51
    with pytest.raises(FrozenInstanceError):
        result.resource_integrity_verification = b51  # type: ignore[misc]


def test_rejects_invalid_aggregate_inputs_without_duck_typing() -> None:
    b43, b51 = _positive_branches(_candidate_integrity())
    duck_b43 = SimpleNamespace(
        admission_record_correspondence_verification=(
            b43.admission_record_correspondence_verification
        )
    )
    duck_b51 = SimpleNamespace(
        observed_resource_identity_collection=(
            b51.observed_resource_identity_collection
        )
    )

    for invalid in (object(), duck_b43, {}, (), []):
        with pytest.raises(
            ValueError,
            match="ActiveCandidateSourceCurrentAdmissionGateReevaluation",
        ):
            integrity.verify_active_candidate_source_integrity(
                cast(ActiveCandidateSourceCurrentAdmissionGateReevaluation, invalid),
                b51,
            )

    for invalid in (object(), duck_b51, {}, (), []):
        with pytest.raises(
            ValueError,
            match="ActiveCandidateSourceResourceIntegrityVerification",
        ):
            integrity.verify_active_candidate_source_integrity(
                b43,
                cast(ActiveCandidateSourceResourceIntegrityVerification, invalid),
            )


def test_requires_same_b39_identity_not_structural_equality() -> None:
    shared_snapshot = SimpleNamespace(snapshot_revision="source-r1")
    b43_b39 = _candidate_integrity(snapshot=shared_snapshot)
    b51_b39 = _candidate_integrity(snapshot=shared_snapshot)
    b43, _ = _positive_branches(b43_b39)
    _, b51 = _positive_branches(b51_b39)

    assert b43_b39 == b51_b39
    assert b43_b39 is not b51_b39
    with pytest.raises(
        ValueError,
        match="^active source integrity causal source mismatch$",
    ):
        integrity.verify_active_candidate_source_integrity(b43, b51)


def test_causal_mismatch_is_all_or_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    b43, _ = _positive_branches(_candidate_integrity())
    _, b51 = _positive_branches(_candidate_integrity())
    constructions: list[dict[str, object]] = []

    def track_result(**kwargs: object) -> object:
        constructions.append(kwargs)
        return object()

    monkeypatch.setattr(
        integrity,
        "ActiveCandidateSourceIntegrityVerification",
        track_result,
    )

    with pytest.raises(
        ValueError,
        match="^active source integrity causal source mismatch$",
    ):
        integrity.verify_active_candidate_source_integrity(b43, b51)

    assert constructions == []


def test_common_empty_source_is_positive() -> None:
    empty_b39 = _candidate_integrity()
    b43, b51 = _positive_branches(empty_b39)

    result = integrity.verify_active_candidate_source_integrity(b43, b51)

    assert result.current_admission_gate_reevaluation is b43
    assert result.resource_integrity_verification is b51


def test_does_not_pair_or_compare_branch_entries() -> None:
    b39 = _candidate_integrity()
    b43, b51 = _positive_branches(
        b39,
        admission_entries=(object(), object()),
        observed_entries=(object(),),
    )

    result = integrity.verify_active_candidate_source_integrity(b43, b51)

    assert result.current_admission_gate_reevaluation is b43
    assert result.resource_integrity_verification is b51


def test_module_has_no_upstream_rerun_or_io_dependencies() -> None:
    source = inspect.getsource(integrity)

    for forbidden_reference in (
        "hashlib",
        "Path",
        "open(",
        "read_bytes",
        "candidate_bytes",
        "resource_bytes",
        "model_validate",
        "zip(",
        ".entries",
        "verify_candidate_admission",
        "verify_active_candidate_source_candidate_integrity",
        "reevaluate_active_candidate_current_admission_gates",
        "verify_active_candidate_source_resource_integrity",
        "derive_resource_physical_identity",
        "verify_active_candidate_source_expected_resource_coverage",
        "loader",
    ):
        assert forbidden_reference not in source
