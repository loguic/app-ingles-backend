# Estado operativo — LOGUIC English

Actualizado: 2026-08-13
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `6115cfc`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 5

Estado: cerrada técnicamente mediante `6c0871c` (`feat derive capability claim availability`); documentación, publicación y sincronización final pendientes.

El servicio puro `pedagogical_capability_claim_availability.py` deriva local y determinísticamente la disponibilidad efímera e inmutable de cada claim. Los índices proceden solo de `candidate_unit.lessons` y `LessonExperience.stages`; los IDs expresan identidad, se usa el punto curricular más tardío necesario y `Mission` permanece no posicionable sin posición canónica explícita.

La API batch procesa todos los claims en orden determinista, devuelve disponibilidades y errores tipados sin depender de `validation_report`, y el validador traduce cada error en un finding independiente. Omite referencias inválidas de slice 3 y claims incompatibles de slice 4. No hubo cambios de schemas ni persistencia.

Validación vigente, no repetir mientras no cambien archivos técnicos: 20 pruebas específicas PASS; postflight independiente final PASS sin hallazgos; 203 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1397 passed in 13.08s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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
- no exigir un plan por lección ni implementar comparación anterior/simultáneo/posterior, precedencia entre estados, ledger, agregación por `Skill`, orden interunidad o CEFR, ciclos o prerrequisitos;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.
- disponibilidad curricular ≠ recorrido del learner ≠ evidencia real ≠ progreso ≠ mastery.

## Bloque activo

### Contrato curricular v1 — Slice estructural 5

Estado: cerrada técnicamente mediante `6c0871c`; documentación, publicación y sincronización final pendientes. La derivación de disponibilidad y su validación están descritas en «Último bloque cerrado».

Rutas propietarias confirmadas: `ConversationChoice → conversación → stage`; `LearnerProductionPrompt → turn/conversation → stage`; `EvidenceDefinition → stage`; `ProductionEvaluationCriterion → evidence → stage`; `SemanticEvaluationRule → criterion → evidence → stage`. Cada error conserva `lesson_id`, `skill_id`, `preparation_state`, `artifact_ids` y causa.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `tests/test_pedagogical_capability_artifact_state_validation.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular desde el contrato v1 autoritativo y evaluar si corresponde precedencia estructural entre estados reutilizando la derivación de disponibilidad de slice 5, sin asumir ledger ni prerrequisitos antes de confirmar dependencias.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
