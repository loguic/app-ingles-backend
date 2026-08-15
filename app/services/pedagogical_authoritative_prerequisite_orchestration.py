"""Orchestrate authoritative curriculum prerequisite validation.

Orquesta la validación autoritativa de prerrequisitos curriculares.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.schemas.pedagogical_unit import (
    PedagogicalUnitCandidate,
    ValidationFinding,
)
from app.services.pedagogical_authoritative_curriculum_hierarchy import (
    AuthoritativeCurriculumHierarchy,
)
from app.services.pedagogical_authoritative_prerequisite_conclusion import (
    CurriculumPrerequisiteAuthoritativeConclusionDerivation,
    derive_authoritative_prerequisite_conclusions,
)
from app.services.pedagogical_authoritative_prerequisite_validation import (
    validate_authoritative_prerequisite_conclusions,
)
from app.services.pedagogical_complete_from_authoritative_origin import (
    CompleteFromAuthoritativeOriginDerivation,
    derive_complete_from_authoritative_origin,
)
from app.services.pedagogical_ordered_curriculum_candidate_context import (
    CurriculumCandidateContextDerivation,
    derive_ordered_curriculum_candidate_context,
)


@dataclass(frozen=True)
class AuthoritativePrerequisiteValidationDerivation:
    """Preserve every reached stage of authoritative validation.

    Conserva cada etapa alcanzada de la validación autoritativa.
    """

    authority: AuthoritativeCurriculumHierarchy
    context_derivation: CurriculumCandidateContextDerivation
    proof_derivation: CompleteFromAuthoritativeOriginDerivation | None
    conclusion_derivation: (
        CurriculumPrerequisiteAuthoritativeConclusionDerivation | None
    )
    findings: tuple[ValidationFinding, ...]


def derive_authoritative_prerequisite_validation(
    authority: AuthoritativeCurriculumHierarchy,
    candidates: Sequence[PedagogicalUnitCandidate],
    *,
    target_level_code: str,
    target_unit_id: str,
) -> AuthoritativePrerequisiteValidationDerivation:
    """Run the pure authoritative prerequisite validation pipeline.

    Ejecuta el pipeline puro de validación autoritativa de prerrequisitos.
    """
    context_derivation = derive_ordered_curriculum_candidate_context(
        authority.hierarchy,
        candidates,
        target_level_code=target_level_code,
        target_unit_id=target_unit_id,
    )
    if context_derivation.context is None:
        return AuthoritativePrerequisiteValidationDerivation(
            authority=authority,
            context_derivation=context_derivation,
            proof_derivation=None,
            conclusion_derivation=None,
            findings=(),
        )

    proof_derivation = derive_complete_from_authoritative_origin(
        authority,
        context_derivation.context,
    )
    if proof_derivation.result is None:
        return AuthoritativePrerequisiteValidationDerivation(
            authority=authority,
            context_derivation=context_derivation,
            proof_derivation=proof_derivation,
            conclusion_derivation=None,
            findings=(),
        )

    conclusion_derivation = derive_authoritative_prerequisite_conclusions(
        proof_derivation.result
    )
    findings = validate_authoritative_prerequisite_conclusions(
        conclusion_derivation
    )
    return AuthoritativePrerequisiteValidationDerivation(
        authority=authority,
        context_derivation=context_derivation,
        proof_derivation=proof_derivation,
        conclusion_derivation=conclusion_derivation,
        findings=tuple(findings),
    )
