# Estado operativo — LOGUIC English

Actualizado: 2026-08-15
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `d860d54`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 27

Estado técnico: cerrado mediante `35e1396` (`feat add authoritative prerequisite report findings`); cierre documental y publicación pendientes.

`derive_authoritative_prerequisite_report_findings(...)` consume únicamente `AuthoritativePrerequisiteValidationStatusDerivation`, conserva esa fuente por identidad y traduce estados ya derivados a findings de representación sin recalcular failed/pending/passed.

Los findings existentes de slice 24 se preservan directamente. Context, proof y errores de consumo/preparación usan respectivamente `authoritative_prerequisite_context_integrity`, `authoritative_prerequisite_origin_integrity` y `authoritative_prerequisite_resolution` con severidad error; cada uncertainty produce un único warning `authoritative_prerequisite_uncertainty`. La política evita duplicar wrappers estructurales, ignora errores externos al scope cuando existe context válido y conserva un orden determinista por familias.

Report finding ≠ verdad curricular; cannot derive ≠ prerequisite not prepared. Failed/pending/passed describe la resolución de esta validación curricular autoritativa, no learner state ni mastery. `ValidationReport` queda fuera de esta slice y requiere preflight separado; `validate_pedagogical_candidate` permanece bloqueado.

Validación vigente, no repetir mientras no cambie código técnico: 17 específicas PASS; postflight independiente PASS sin findings; 133 de regresión PASS; suite backend completa, 1752 passed in 13.43s, `PYTEST_EXIT=0`; `git diff --check` PASS.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada para cambiar de conversación.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no se considera fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación técnica, validación específica, revisión independiente y cierre documental. Las regresiones y suites amplias se ejecutan solo cuando el alcance y riesgo las justifican. Los commits y la publicación permanecen bajo confirmación humana.

El protocolo operativo conserva Codex CLI + Bash y `docs/estado-operativo.md` como fuente canónica para cambiar de conversación. No deben repetirse inspecciones ni validaciones vigentes si los archivos cubiertos no han cambiado.

Antes de cambiar: actualizar `docs/estado-operativo.md`, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar únicamente si genera un checkpoint válido. Al reanudar: ejecutar `conversation_checkpoint.py resume`, recuperar ese estado antes de proponer comandos, inspecciones o cambios, y no repetir validaciones vigentes.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ resultado de evaluación ≠ aprendizaje ≠ mastery;
- `required_stages` y `SkillCoverage` son contratos heredados y no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`;
- no modificar `SkillCoverage` ni `required_stages`;
- no exigir un plan por lección ni implementar ledger, agregación curricular definitiva por `Skill`, orden interunidad o CEFR, ciclos, orden intra-stage o prerrequisitos;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.
- disponibilidad curricular ≠ recorrido del learner ≠ evidencia real ≠ progreso ≠ mastery.

## Bloque activo

### Contrato curricular v1 — Slice estructural 27

Estado técnico cerrado mediante `35e1396`; cierre documental y publicación pendientes. La derivación pura de report findings está descrita en «Último bloque cerrado».

Permanecen fuera `ValidationReport`, su wrapper trazable y la integración con validadores, además de learner state, mastery, runtime y persistencia.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos de la slice: `app/services/pedagogical_authoritative_prerequisite_report_findings.py` y `tests/test_pedagogical_authoritative_prerequisite_report_findings.py`. El inventario histórico completo permanece en `docs/bitacora.md`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer un preflight separado para evaluar `AuthoritativePrerequisiteValidationReport`, conservando `status_derivation` como fuente canónica y `ValidationReport` como representación serializable, sin reconstruir status o causas desde findings.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_conversation_checkpoint.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `app/services/pedagogical_capability_artifact_reference_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `tests/test_pedagogical_capability_artifact_reference_validation.py`;
- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `tests/test_pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_capability_claim_availability.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`;
- `app/services/pedagogical_capability_preparation_snapshot.py`;
- `tests/test_pedagogical_capability_preparation_snapshot.py`;
- `app/services/pedagogical_local_capability_preparation_view.py`;
- `tests/test_pedagogical_local_capability_preparation_view.py`;
- `app/services/pedagogical_local_skill_prerequisite_consumption.py`;
- `tests/test_pedagogical_local_skill_prerequisite_consumption.py`;
- `app/services/pedagogical_local_skill_prerequisite_assessment.py`;
- `tests/test_pedagogical_local_skill_prerequisite_assessment.py`;
- `app/services/pedagogical_curriculum_order.py`;
- `tests/test_pedagogical_curriculum_order.py`;
- `app/services/pedagogical_curriculum_unit_position.py`;
- `tests/test_pedagogical_curriculum_unit_position.py`;
- `app/services/pedagogical_curriculum_candidate_correspondence.py`;
- `tests/test_pedagogical_curriculum_candidate_correspondence.py`;
- `app/services/pedagogical_curriculum_context_scope.py`;
- `tests/test_pedagogical_curriculum_context_scope.py`;
- `app/services/pedagogical_ordered_curriculum_candidate_context.py`;
- `tests/test_pedagogical_ordered_curriculum_candidate_context.py`;
- `app/services/pedagogical_accumulated_curriculum_preparation.py`;
- `tests/test_pedagogical_accumulated_curriculum_preparation.py`;
- `app/services/pedagogical_curriculum_skill_prerequisite_assessment.py` y `tests/test_pedagogical_curriculum_skill_prerequisite_assessment.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
