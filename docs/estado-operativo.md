# Estado operativo — LOGUIC English

Actualizado: 2026-08-14
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `1578f9d`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 6

Estado: cerrada técnicamente mediante `2a4db09` (`feat validate capability claim state precedence`); documentación, publicación y sincronización final pendientes.

El validador `capability_claim_state_precedence` reutiliza exclusivamente la disponibilidad de slice 5 y exige, para una misma `Skill`, la cadena estricta `EXPOSURE_AVAILABLE < INSTRUCTION_AVAILABLE < PRACTICE_AVAILABLE < EVIDENCE_GATE_AVAILABLE`. Cada estado superior requiere el inmediato anterior, válidamente encadenado, en una posición `(lesson_index, stage_index)` estrictamente menor; el mismo stage no satisface precedencia y los IDs nunca expresan orden.

Los claims equivalentes son independientes y cualquier predecesor válido anterior puede sostener el siguiente; uno inválido no sostiene estados posteriores. Los errores de derivación de slice 5 se omiten sin findings duplicados. Las causas deterministas son `required_state_absent`, `required_state_same_position`, `required_state_only_later` y `required_state_not_validly_chained`, con un finding por claim superior problemático. El estado auxiliar es efímero y local: no existe ledger encubierto. No hubo cambios de schemas, persistencia ni contenido canónico.

Validación vigente, no repetir mientras no cambien archivos técnicos: 24 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 201 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1421 passed in 13.14s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 6

Estado: cerrada técnicamente mediante `2a4db09`; documentación, publicación y sincronización final pendientes. La precedencia estructural y su validación están descritas en «Último bloque cerrado».

Permanecen fuera `CurriculumCapabilityPreparationLedger`, ledger persistido, agregación definitiva por `Skill`, prerrequisitos y `PedagogicalUnitSpecification.prerequisites`, orden interunidad/CEFR, ciclos, orden intra-stage, progreso, ejecución del learner, evidencia real, resultados, mastery, calidad pedagógica, runtime y cambios en `SkillCoverage` o `required_stages`.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular desde el contrato v1 autoritativo y evaluar si ya corresponde construir el ledger curricular derivado o existe una dependencia estructural previa más pequeña, sin abordar prerrequisitos antes de demostrar sus dependencias.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
