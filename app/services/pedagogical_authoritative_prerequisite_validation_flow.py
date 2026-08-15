"""Compose the complete authoritative prerequisite validation flow.

Compone el flujo completo de validación autoritativa de prerequisites.
"""

from collections.abc import Sequence

from app.schemas.pedagogical_unit import PedagogicalUnitCandidate
from app.services.pedagogical_authoritative_curriculum_hierarchy import (
    AuthoritativeCurriculumHierarchy,
)
from app.services.pedagogical_authoritative_prerequisite_orchestration import (
    derive_authoritative_prerequisite_validation,
)
from app.services.pedagogical_authoritative_prerequisite_report_findings import (
    derive_authoritative_prerequisite_report_findings,
)
from app.services.pedagogical_authoritative_prerequisite_validation_report import (
    AuthoritativePrerequisiteValidationReport,
    derive_authoritative_prerequisite_validation_report,
)
from app.services.pedagogical_authoritative_prerequisite_validation_status import (
    derive_authoritative_prerequisite_validation_status,
)


def derive_authoritative_prerequisite_validation_flow(
    authority: AuthoritativeCurriculumHierarchy,
    candidates: Sequence[PedagogicalUnitCandidate],
    *,
    target_level_code: str,
    target_unit_id: str,
) -> AuthoritativePrerequisiteValidationReport:
    """Compose authoritative prerequisite stages into the traceable report.

    Compone las etapas autoritativas de prerequisites en el reporte trazable.
    """
    orchestration = derive_authoritative_prerequisite_validation(
        authority,
        candidates,
        target_level_code=target_level_code,
        target_unit_id=target_unit_id,
    )
    status_derivation = derive_authoritative_prerequisite_validation_status(
        orchestration
    )
    finding_derivation = derive_authoritative_prerequisite_report_findings(
        status_derivation
    )
    report = derive_authoritative_prerequisite_validation_report(
        finding_derivation
    )
    return report
