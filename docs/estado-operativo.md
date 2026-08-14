# Estado operativo — LOGUIC English

Actualizado: 2026-08-14
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `57f20e3`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 14

Estado: técnicamente cerrada mediante el commit `9c7b238` (`feat add canonical curriculum unit positions`); documentación, publicación y sincronización final pendientes.

La API pura `derive_curriculum_unit_positions(hierarchy)` devuelve posiciones interunidad canónicas tipadas, inmutables y efímeras. `level_index` procede exclusivamente de `cefr_level_index(level.code)`, `unit_index` de la posición real en `Level.units`, y la salida válida se ordena por `(level_index, unit_index)`. Los IDs identifican y nunca ordenan.

Los errores no fail-fast son `unknown_level`, `duplicate_level`, `duplicate_unit` y `ambiguous_unit`. Levels y units ambiguos quedan excluidos de posiciones utilizables, mientras las unidades inequívocas restantes se conservan. Posición curricular ≠ completitud curricular ≠ preparación acumulada ≠ progreso del learner ≠ aprendizaje ≠ mastery. No se implementaron candidates, contexto, completitud, agregación, evaluación global, ledger, findings ni persistencia.

Validación vigente, no repetir mientras no cambien archivos técnicos: 16 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 263 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1555 passed in 12.79s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 14

Estado: técnicamente cerrada mediante el commit `9c7b238`; documentación, publicación y sincronización final pendientes. Las posiciones curriculares canónicas de unidades están descritas en «Último bloque cerrado».

Posición curricular ≠ completitud curricular ≠ preparación acumulada ≠ progreso del learner ≠ aprendizaje ≠ mastery. Permanecen fuera correspondencia `PedagogicalUnitCandidate`–posición canónica, `OrderedCurriculumCandidateContext`, definición y demostración de completitud, target curricular, `context_incomplete`, agregación acumulativa por Skill, evaluación global de `SkillPrerequisite`, conclusión global `unsatisfied`, `CurriculumCapabilityPreparationLedger`, ciclos, findings e integración con `validate_pedagogical_candidate`, progreso, ejecución, evidencia real, resultados, aprendizaje, retention, mastery, calidad pedagógica, runtime, persistencia, selección de cadenas y cambios en `SkillCoverage` o `required_stages`.

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

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice para determinar la dependencia mínima entre posiciones canónicas resueltas y la correspondencia estructural con `PedagogicalUnitCandidate`, antes de introducir completitud curricular y sin asumir todavía un `OrderedCurriculumCandidateContext` completo.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
