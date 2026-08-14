# Estado operativo — LOGUIC English

Actualizado: 2026-08-14
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `a3e9237`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 9

Estado: cerrada, publicada y sincronizada mediante los commits técnico `20e0f85` (`refactor expose curriculum preparation state order`) y documental `a3e9237`; push confirmado hasta `a3e9237` en `origin/master`.

La API pública y pura expone `CURRICULUM_PREPARATION_STATE_ORDER` como fuente única e inmutable de `EXPOSURE_AVAILABLE < INSTRUCTION_AVAILABLE < PRACTICE_AVAILABLE < EVIDENCE_GATE_AVAILABLE`, y `curriculum_preparation_state_index(state)` devuelve respectivamente `0..3`. Un estado desconocido produce `ValueError`, sin fallback ni `ValidationFinding`.

Se eliminaron `_STATE_ORDER` y `_state_index`; la precedencia interna reutiliza exclusivamente la API pública, sin representación paralela ni mapping mutable. La semántica de slices 6–7 permanece intacta. No se implementaron agregación por `Skill`, `highest_preparation_state`, selección de cadena, ledger, snapshot agregado ni persistencia.

Validación vigente, no repetir mientras no cambien archivos técnicos: 41 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 118 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1459 passed in 13.21s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 9

Estado: cerrada, publicada y sincronizada mediante los commits técnico `20e0f85` y documental `a3e9237`; push confirmado hasta `a3e9237` en `origin/master`. El orden canónico público está descrito en «Último bloque cerrado».

Permanecen fuera agregación local por `skill_id`, `highest_preparation_state`, selección de cadena máxima, `CurriculumCapabilityPreparationLedger`, `SkillPrerequisite`, `PedagogicalUnitSpecification.prerequisites`, contexto interunidad/CEFR, ciclos, progreso, ejecución del learner, evidencia real, resultados, mastery, calidad pedagógica, runtime, persistencia y cambios en `SkillCoverage` o `required_stages`.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`.
- `app/services/pedagogical_capability_preparation_snapshot.py`;
- `tests/test_pedagogical_capability_preparation_snapshot.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular para determinar si ya corresponde derivar una vista local agregada por `Skill` y `highest_preparation_state` desde el snapshot de slice 8 y el orden público de slice 9.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
