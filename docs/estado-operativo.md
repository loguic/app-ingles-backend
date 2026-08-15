# Estado operativo — LOGUIC English

Actualizado: 2026-08-15
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `241e77c`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 20

Estado: cerrada, publicada y sincronizada mediante los commits contractual `530e910` (`docs define authoritative curriculum hierarchy contract`) y documental `241e77c`; primer push confirmado hasta `241e77c` en `origin/master`.

El preflight detectó que no existía una fuente autoritativa contractual. La decisión aprobada sitúa la autoridad en un proveedor curricular designado, no en archivo, ruta, `ContentTreeResponse`, IDs, booleanos del caller ni representación física subyacente.

El origen es la primera `CurriculumUnitPosition` derivada de la hierarchy autoritativa y el proveedor garantiza continuidad sin omisiones hasta target. `origin present` ≠ complete from origin; `complete_within_hierarchy` ≠ `complete_from_authoritative_origin` ≠ `globally_complete`.

`unresolved_in_context` ≠ `unsatisfied`. Autoridad/completitud curricular estructural ≠ ejecución ≠ evidencia real ≠ aprendizaje ≠ retention ≠ mastery.

Validación vigente, no repetir mientras no cambie el contrato: postflight contractual PASS sin findings críticos; `git diff --check` PASS; sin cambios de código ni necesidad de pytest.

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

### Contrato curricular v1 — Slice estructural 20

Estado: cerrada, publicada y sincronizada mediante los commits contractual `530e910` y documental `241e77c`; primer push confirmado hasta `241e77c` en `origin/master`. La autoridad curricular está descrita en «Último bloque cerrado».

Permanecen fuera el tipo emitido exclusivamente por el proveedor autoritativo, la prueba estructural de `complete_from_authoritative_origin`, `unsatisfied` curricular, ciclos, ledger, findings, progreso, ejecución, evidencia, aprendizaje, retention, mastery, runtime y persistencia.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`.
- `app/services/pedagogical_capability_preparation_snapshot.py`;
- `tests/test_pedagogical_capability_preparation_snapshot.py`.
- `app/services/pedagogical_local_capability_preparation_view.py`;
- `tests/test_pedagogical_local_capability_preparation_view.py`.
- `app/services/pedagogical_local_skill_prerequisite_consumption.py`;
- `tests/test_pedagogical_local_skill_prerequisite_consumption.py`.
- `app/services/pedagogical_local_skill_prerequisite_assessment.py`;
- `tests/test_pedagogical_local_skill_prerequisite_assessment.py`.
- `app/services/pedagogical_curriculum_order.py`;
- `tests/test_pedagogical_curriculum_order.py`.
- `app/services/pedagogical_curriculum_unit_position.py`;
- `tests/test_pedagogical_curriculum_unit_position.py`.
- `app/services/pedagogical_curriculum_candidate_correspondence.py`;
- `tests/test_pedagogical_curriculum_candidate_correspondence.py`.
- `app/services/pedagogical_curriculum_context_scope.py`;
- `tests/test_pedagogical_curriculum_context_scope.py`.
- `app/services/pedagogical_ordered_curriculum_candidate_context.py`;
- `tests/test_pedagogical_ordered_curriculum_candidate_context.py`.
- `app/services/pedagogical_accumulated_curriculum_preparation.py`;
- `tests/test_pedagogical_accumulated_curriculum_preparation.py`.
- `app/services/pedagogical_curriculum_skill_prerequisite_assessment.py` y `tests/test_pedagogical_curriculum_skill_prerequisite_assessment.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight técnico de la siguiente slice para diseñar un tipo emitido solo por el proveedor curricular autoritativo y la prueba estructural de `complete_from_authoritative_origin`, sin implementar todavía `unsatisfied`.

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
