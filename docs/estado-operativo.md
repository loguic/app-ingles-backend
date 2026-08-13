# Estado operativo — LOGUIC English

Actualizado: 2026-08-13
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `af47bb6`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 1

Estado: cerrada, publicada y sincronizada.

Sobre el contrato autoritativo `d6b6e7f`, el commit técnico `56e7394` añadió `CurriculumPreparationState`, `LessonCapabilityClaim`, `SkillPrerequisite` y `LessonCapabilityPlan`; el commit documental es `c74e259`.

Validación final: revisión independiente PASS; 15 pruebas específicas; 74 de regresión seleccionada; suite backend completa 1277 passed; `git diff --check` PASS. Git quedó publicado y sincronizado; el cierre documental posterior alcanzó `af47bb6`.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no se considera fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación técnica, validación específica, revisión independiente y cierre documental. Las regresiones y suites amplias se ejecutan solo cuando el alcance y riesgo las justifican. Los commits y la publicación permanecen bajo confirmación humana.

El protocolo operativo conserva Codex CLI + Bash y `docs/estado-operativo.md` como fuente canónica para cambiar de conversación. No deben repetirse inspecciones ni validaciones vigentes si los archivos cubiertos no han cambiado.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ resultado de evaluación ≠ aprendizaje ≠ mastery;
- `required_stages` y `SkillCoverage` son contratos heredados y no producen `CurriculumPreparationState`;
- no integrar todavía `LessonCapabilityPlan` en `PedagogicalUnitCandidate`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`;
- no modificar `SkillCoverage` ni `required_stages`;
- no implementar todavía ledger, orden curricular, resolución de `artifact_ids`, precedencia ni ciclos;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.

## Bloque activo

### Checkpoint de cambio de conversación — Slice estructural 1

Estado: implementación técnica validada y commiteada mediante `bc288fc` (`feat add conversation checkpoint tool`); cierre documental, publicación y sincronización final pendientes.

Archivos técnicos commiteados y sin cambios posteriores a las validaciones:

- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_conversation_checkpoint.py`.

Capacidades: `prepare` y `resume` read-only; reutilización de `operational_state.py`; inspección Git local de HEAD, branch o detached, upstream, ahead/behind, staged, unstaged, untracked y rename; Markdown efímero; fail-closed; representación segura y reversible de rutas; y correspondencia exacta entre cambios locales y rutas documentadas.

Validación vigente, no repetir mientras esos dos archivos no cambien: 23 pruebas específicas PASS; regresión directa `tests/test_operational_state.py` + `tests/test_block_workflow.py`, 8 passed; `git diff --check` PASS; postflight final PASS. No se ejecutó la suite backend completa porque la herramienta es read-only, no modifica código productivo y la validación focal, regresión directa y pruebas funcionales cubren su alcance.

Pruebas funcionales reales: `prepare` rechazó el estado canónico que omitía cambios locales; después generó correctamente el checkpoint con el estado actualizado; `resume` reconstruyó el mismo contexto actual.

Limitación no bloqueante: una ruta que contenga backticks requerirá otra convención documental si alguna vez aparece en el proyecto.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Crear el commit documental, publicar, ejecutar la prueba final de `prepare` y `resume` con el estado publicado y Git limpio, y verificar la sincronización final.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_conversation_checkpoint.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
