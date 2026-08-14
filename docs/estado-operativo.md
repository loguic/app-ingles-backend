# Estado operativo — LOGUIC English

Actualizado: 2026-08-14
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `56e2098`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 11

Estado: cerrada, publicada y sincronizada mediante los commits técnico `bf92641` (`feat add local skill prerequisite consumption`) y documental `56e2098`; primer push confirmado hasta `56e2098` en `origin/master`.

La API pura `derive_local_skill_prerequisite_consumptions(candidate)` resuelve de forma tipada, inmutable y efímera el punto local de consumo de cada `SkillPrerequisite`. Cada prerequisite pertenece al `LessonCapabilityPlan` propietario y toma de él su `lesson_id`. Un `before_stage_id` explícito solo se resuelve dentro de los stages reales de esa lección; si está ausente, se usa su primer stage real (`stage_index == 0`), sin `lesson_start`, posiciones sintéticas, stages artificiales ni índices negativos.

`lesson_index` procede de `candidate_unit.lessons` y `stage_index` de `LessonExperience.stages`; los IDs identifican y nunca ordenan. Las causas derivativas son `unknown_lesson`, `ambiguous_lesson`, `lesson_without_experience` y `unknown_stage_for_lesson`. Cada prerequisite produce `consumption` XOR `resolution_error`, sin fail-fast y conservando el orden declarativo. `reason` se preserva sin ejecutar lógica. No se evalúa satisfacción, estado actual ni comparación de estados; no hubo findings, integración con el validador general, ledger ni persistencia.

Validación vigente, no repetir mientras no cambien archivos técnicos: 19 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 277 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1500 passed in 13.05s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 11

Estado: cerrada, publicada y sincronizada mediante los commits técnico `bf92641` y documental `56e2098`; primer push confirmado hasta `56e2098` en `origin/master`. La resolución local del punto de consumo está descrita en «Último bloque cerrado».

Resolución del punto de consumo ≠ satisfacción del prerequisite ≠ progreso del learner ≠ aprendizaje ≠ mastery. Permanecen fuera evaluación de satisfacción de `SkillPrerequisite`, contexto interunidad/CEFR, `CurriculumCapabilityPreparationLedger` completo, comparación `actual_state` frente a `required_state`, estado no resuelto en contexto local, ciclos, progreso, ejecución del learner, evidencia real, resultados, aprendizaje, mastery, calidad pedagógica, runtime, persistencia, selección de cadenas y cambios en `SkillCoverage` o `required_stages`.

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

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular para determinar la dependencia mínima necesaria para evaluar `SkillPrerequisite` sin declarar incorrectamente `unsatisfied` usando solo contexto local y sin asumir todavía que corresponde construir el ledger completo.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
