# Estado operativo — LOGUIC English

Actualizado: 2026-08-13
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último checkpoint estable publicado: contrato curricular v1 de prerrequisitos, commit `d6b6e7f`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 1

Estado: cerrada, publicada y sincronizada.

Sobre el contrato autoritativo `d6b6e7f`, el commit técnico `56e7394` añadió `CurriculumPreparationState`, `LessonCapabilityClaim`, `SkillPrerequisite` y `LessonCapabilityPlan`; el commit documental es `c74e259`.

Validación final: revisión independiente PASS; 15 pruebas específicas; 74 de regresión seleccionada; suite backend completa 1277 passed; `git diff --check` PASS. Git confirmado limpio y sincronizado: `## master...origin/master` hasta `c74e259`.

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

### Checkpoint de cambio de conversación

Estado: siguiente objetivo identificado; diseño e implementación todavía no abiertos.

Objetivo: diseñar e implementar una herramienta de ingeniería determinista que automatice la preparación y recuperación de contexto entre conversaciones, conservando `docs/estado-operativo.md` como fuente canónica y el protocolo Codex CLI + Bash.

No se abre todavía su implementación ni se repiten inspecciones o validaciones cerradas.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Diseñar e implementar el «Checkpoint de cambio de conversación», una herramienta de ingeniería determinista para preparar y recuperar contexto entre conversaciones. Este checkpoint no está abierto todavía.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
