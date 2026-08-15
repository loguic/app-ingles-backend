from dataclasses import FrozenInstanceError, fields
import inspect

import pytest

from app.schemas.content import ContentTreeResponse, Level, Unit
from app.services import content_service
from app.services.pedagogical_complete_from_authoritative_origin import (
    CompleteFromAuthoritativeOrigin,
    CompleteFromAuthoritativeOriginDerivation,
    CompleteFromAuthoritativeOriginError,
    derive_complete_from_authoritative_origin,
)
from app.services.pedagogical_curriculum_context_scope import (
    CurriculumContextScope,
)
from app.services.pedagogical_curriculum_unit_position import (
    CurriculumUnitPosition,
    CurriculumUnitPositionDerivation,
    derive_curriculum_unit_positions,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    OrderedCurriculumCandidateContext,
)


def _tree(*unit_ids: str, level_code: str = "A1") -> ContentTreeResponse:
    return ContentTreeResponse(
        levels=[
            Level(
                code=level_code,
                units=[Unit(id=unit_id, title=unit_id) for unit_id in unit_ids],
            )
        ]
    )


def _authority(monkeypatch, tree: ContentTreeResponse):
    monkeypatch.setattr(content_service, "build_content_tree", lambda: tree)
    return content_service.load_authoritative_curriculum_hierarchy()


def _context(
    positions: tuple[CurriculumUnitPosition, ...],
) -> OrderedCurriculumCandidateContext:
    return OrderedCurriculumCandidateContext(
        scope=CurriculumContextScope(
            start_position=positions[0],
            target_position=positions[-1],
            required_positions=positions,
        ),
        entries=(),
    )


def _equivalent_positions(
    tree: ContentTreeResponse,
) -> tuple[CurriculumUnitPosition, ...]:
    return tuple(
        CurriculumUnitPosition(
            level_code=position.level_code,
            level_index=position.level_index,
            unit_id=position.unit_id,
            unit_index=position.unit_index,
        )
        for position in derive_curriculum_unit_positions(tree).positions
    )


def test_models_are_frozen_and_declare_no_complete_boolean():
    assert all(
        model.__dataclass_params__.frozen
        for model in (
            CompleteFromAuthoritativeOrigin,
            CompleteFromAuthoritativeOriginError,
            CompleteFromAuthoritativeOriginDerivation,
        )
    )
    assert "is_complete" not in {
        field.name
        for model in (
            CompleteFromAuthoritativeOrigin,
            CompleteFromAuthoritativeOriginError,
            CompleteFromAuthoritativeOriginDerivation,
        )
        for field in fields(model)
    }
    error = CompleteFromAuthoritativeOriginError(
        cause="context_origin_mismatch"
    )
    with pytest.raises(FrozenInstanceError):
        error.cause = "authoritative_prefix_mismatch"


def test_api_accepts_only_authority_and_context():
    assert tuple(
        inspect.signature(
            derive_complete_from_authoritative_origin
        ).parameters
    ) == ("authority", "context")


def test_exact_context_produces_proof_and_preserves_inputs(monkeypatch):
    tree = _tree("u1", "u2", "u3")
    authority = _authority(monkeypatch, tree)
    context = _context(_equivalent_positions(tree))

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.errors == ()
    assert derivation.result is not None
    assert derivation.result.authority is authority
    assert derivation.result.context is context
    assert derivation.authority_position_derivation.positions == (
        context.scope.required_positions
    )


def test_intermediate_target_uses_only_authoritative_prefix(monkeypatch):
    tree = _tree("u1", "u2", "u3", "u4")
    authority = _authority(monkeypatch, tree)
    context = _context(_equivalent_positions(tree)[:3])

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.result is not None
    assert derivation.errors == ()


def test_structurally_equal_distinct_positions_are_accepted(monkeypatch):
    tree = _tree("u1", "u2")
    authority = _authority(monkeypatch, tree)
    context_positions = _equivalent_positions(tree)

    derivation = derive_complete_from_authoritative_origin(
        authority,
        _context(context_positions),
    )

    assert derivation.result is not None
    assert all(
        left == right and left is not right
        for left, right in zip(
            derivation.authority_position_derivation.positions,
            context_positions,
        )
    )


def test_position_derivation_is_consumed_and_preserved(monkeypatch):
    tree = _tree("u1")
    authority = _authority(monkeypatch, tree)
    context = _context(_equivalent_positions(tree))
    expected = CurriculumUnitPositionDerivation(
        positions=context.scope.required_positions,
        resolution_errors=(),
    )
    calls = []

    def derive(hierarchy):
        calls.append(hierarchy)
        return expected

    monkeypatch.setattr(
        "app.services.pedagogical_complete_from_authoritative_origin."
        "derive_curriculum_unit_positions",
        derive,
    )

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert len(calls) == 1
    assert calls[0] is authority.hierarchy
    assert derivation.authority_position_derivation is expected


def test_authority_position_errors_fail_closed_and_remain_original(monkeypatch):
    tree = ContentTreeResponse(
        levels=[Level(code="A1", units=[]), Level(code="A1", units=[])]
    )
    authority = _authority(monkeypatch, tree)
    position_derivation = derive_curriculum_unit_positions(tree)
    context = _context(
        (CurriculumUnitPosition("A1", 0, "u1", 0),)
    )
    monkeypatch.setattr(
        "app.services.pedagogical_complete_from_authoritative_origin."
        "derive_curriculum_unit_positions",
        lambda hierarchy: position_derivation,
    )

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.result is None
    assert [error.cause for error in derivation.errors] == [
        "authoritative_hierarchy_position_unresolved"
    ]
    assert derivation.authority_position_derivation is position_derivation
    assert all(
        actual is expected
        for actual, expected in zip(
            derivation.authority_position_derivation.resolution_errors,
            position_derivation.resolution_errors,
        )
    )


def test_empty_authority_has_no_synthetic_origin(monkeypatch):
    authority = _authority(monkeypatch, ContentTreeResponse(levels=[]))
    context = _context(
        (CurriculumUnitPosition("A1", 0, "invented", 0),)
    )

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.result is None
    assert derivation.authority_position_derivation.positions == ()
    assert [error.cause for error in derivation.errors] == [
        "authoritative_hierarchy_position_unresolved"
    ]


def test_a1_authority_rejects_b1_context_origin(monkeypatch):
    authority = _authority(monkeypatch, _tree("a1-unit", level_code="A1"))
    context = _context(
        _equivalent_positions(_tree("b1-unit", level_code="B1"))
    )

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.result is None
    assert [error.cause for error in derivation.errors] == [
        "context_origin_mismatch"
    ]


def test_b1_authority_accepts_b1_origin(monkeypatch):
    tree = _tree("b1-unit", level_code="B1")
    authority = _authority(monkeypatch, tree)

    derivation = derive_complete_from_authoritative_origin(
        authority,
        _context(_equivalent_positions(tree)),
    )

    assert derivation.result is not None


def test_structurally_absent_target_fails(monkeypatch):
    tree = _tree("u1", "u2")
    authority = _authority(monkeypatch, tree)
    positions = _equivalent_positions(tree)
    foreign_target = CurriculumUnitPosition("A1", 0, "u3", 2)
    context = OrderedCurriculumCandidateContext(
        scope=CurriculumContextScope(
            start_position=positions[0],
            target_position=foreign_target,
            required_positions=(positions[0], foreign_target),
        ),
        entries=(),
    )

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert derivation.result is None
    assert [error.cause for error in derivation.errors] == [
        "context_target_outside_authority"
    ]


@pytest.mark.parametrize(
    "context_positions",
    [
        lambda positions: (positions[0], positions[2]),
        lambda positions: (
            positions[0],
            positions[1],
            CurriculumUnitPosition("A1", 0, "extra", 99),
            positions[2],
        ),
        lambda positions: (
            positions[0],
            positions[2],
            positions[1],
            positions[3],
        ),
    ],
    ids=["missing-intermediate", "extra-position", "wrong-order"],
)
def test_non_exact_prefix_fails(monkeypatch, context_positions):
    tree = _tree("u1", "u2", "u3", "u4")
    authority = _authority(monkeypatch, tree)
    positions = _equivalent_positions(tree)

    derivation = derive_complete_from_authoritative_origin(
        authority,
        _context(context_positions(positions)),
    )

    assert derivation.result is None
    assert [error.cause for error in derivation.errors] == [
        "authoritative_prefix_mismatch"
    ]


def test_ordinary_content_tree_is_not_an_authority_argument():
    tree = _tree("u1")
    context = _context(_equivalent_positions(tree))

    with pytest.raises(AttributeError):
        derive_complete_from_authoritative_origin(tree, context)  # type: ignore[arg-type]


def test_failure_priority_stops_after_origin_mismatch(monkeypatch):
    authority = _authority(monkeypatch, _tree("a1", level_code="A1"))
    foreign = CurriculumUnitPosition("B1", 2, "outside", 0)
    context = _context((foreign,))

    derivation = derive_complete_from_authoritative_origin(authority, context)

    assert [error.cause for error in derivation.errors] == [
        "context_origin_mismatch"
    ]


def test_derivation_does_not_mutate_inputs(monkeypatch):
    tree = _tree("u1", "u2")
    authority = _authority(monkeypatch, tree)
    context = _context(_equivalent_positions(tree))
    before_tree = tree.model_dump()
    before_scope = context.scope

    derive_complete_from_authoritative_origin(authority, context)

    assert tree.model_dump() == before_tree
    assert context.scope is before_scope
