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

### Contrato curricular v1 — Slice estructural 10

Estado: cerrada técnicamente mediante `0ace21a` (`feat add local skill preparation view`); documentación, publicación y sincronización final pendientes.

La API pura `derive_local_capability_preparation_view(...)` devuelve una `LocalCapabilityPreparationView` efímera e inmutable, agrupando por `skill_id` exclusivamente los `available_claims` del snapshot de slice 8. Cada `LocalSkillPreparation` conserva todos sus claims originales y deriva `highest_preparation_state` únicamente mediante el orden público de slice 9.

`highest_preparation_state` es solo el máximo curricular estructural antes del punto: no equivale a recorrido, ejecución, evidencia real, resultado, progreso, aprendizaje ni mastery. Se conservan todas las alternativas, no se selecciona cadena y las Skills sin claims quedan ausentes. `before_point` y los errores proceden directamente de slice 8; el orden por `skill_id` solo estabiliza la salida. No hubo findings ni integración con el validador general.

Validación vigente, no repetir mientras no cambien archivos técnicos: 22 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 159 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1481 passed in 13.06s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 10

Estado: cerrada técnicamente mediante `0ace21a`; documentación, publicación y sincronización final pendientes. La vista local agregada por Skill está descrita en «Último bloque cerrado».

Permanecen fuera `CurriculumCapabilityPreparationLedger` completo, selección de cadena máxima, supporting IDs agregados, `SkillPrerequisite`, `PedagogicalUnitSpecification.prerequisites`, contexto interunidad/CEFR, ciclos, progreso, ejecución del learner, evidencia real, resultados, mastery, calidad pedagógica, runtime, persistencia y cambios en `SkillCoverage` o `required_stages`.

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

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular para determinar la dependencia mínima posterior a la vista local agregada por Skill, sin asumir todavía que corresponde construir el ledger completo.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
