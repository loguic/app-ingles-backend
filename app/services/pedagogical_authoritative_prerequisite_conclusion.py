"""Derive authoritative negative curriculum prerequisite conclusions.

Deriva conclusiones curriculares negativas autoritativas de prerrequisitos.
"""

from dataclasses import dataclass

from app.services.pedagogical_complete_from_authoritative_origin import (
    CompleteFromAuthoritativeOrigin,
)
from app.services.pedagogical_curriculum_skill_prerequisite_assessment import (
    CurriculumSkillPrerequisiteAssessment,
    CurriculumSkillPrerequisiteAssessmentDerivation,
    derive_curriculum_skill_prerequisite_assessments,
)


@dataclass(frozen=True)
class CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin:
    """Prove missing required curriculum preparation before one consumption.

    Demuestra preparación curricular requerida ausente antes de un consumo.
    """

    proof: CompleteFromAuthoritativeOrigin
    assessment: CurriculumSkillPrerequisiteAssessment


@dataclass(frozen=True)
class CurriculumPrerequisiteAuthoritativeUncertainty:
    """Preserve an unresolved assessment with related precedence uncertainty.

    Conserva un assessment no resuelto con incertidumbre de precedencia relacionada.
    """

    assessment: CurriculumSkillPrerequisiteAssessment


@dataclass(frozen=True)
class CurriculumPrerequisiteAuthoritativeConclusionDerivation:
    """Collect source assessments, conclusions, and conservative uncertainties.

    Reúne assessments fuente, conclusiones e incertidumbres conservadoras.
    """

    assessment_derivation: CurriculumSkillPrerequisiteAssessmentDerivation
    conclusions: tuple[
        CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin, ...
    ]
    uncertainties: tuple[
        CurriculumPrerequisiteAuthoritativeUncertainty, ...
    ]


def derive_authoritative_prerequisite_conclusions(
    proof: CompleteFromAuthoritativeOrigin,
) -> CurriculumPrerequisiteAuthoritativeConclusionDerivation:
    """Derive safe negative conclusions from one authoritative context proof.

    Deriva conclusiones negativas seguras desde una prueba de contexto autoritativo.
    """
    assessment_derivation = derive_curriculum_skill_prerequisite_assessments(
        proof.context
    )
    conclusions: list[
        CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin
    ] = []
    uncertainties: list[
        CurriculumPrerequisiteAuthoritativeUncertainty
    ] = []

    for assessment in assessment_derivation.assessments:
        if assessment.outcome != "unresolved_in_context":
            continue
        if assessment.related_precedence_errors:
            uncertainties.append(
                CurriculumPrerequisiteAuthoritativeUncertainty(
                    assessment=assessment
                )
            )
        else:
            conclusions.append(
                CurriculumPrerequisiteNotPreparedFromAuthoritativeOrigin(
                    proof=proof,
                    assessment=assessment,
                )
            )

    return CurriculumPrerequisiteAuthoritativeConclusionDerivation(
        assessment_derivation=assessment_derivation,
        conclusions=tuple(conclusions),
        uncertainties=tuple(uncertainties),
    )
