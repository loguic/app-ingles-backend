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

### B180 — Construcción directa en inglés

Estado: cerrado técnica e integralmente; Incrementos 1–4 publicados.

Capacidad observable: construir oralmente una respuesta desde una intención, ampliarla con información pertinente y transferir el patrón ante una variación inesperada con ayuda mínima, sin copiar una frase completa.

Trazabilidad técnica: `ccafaaa`, `f77f560`, `2f396d3` y `70c3dbf`. Validación final confirmada: suite backend 1191 passed, migraciones PostgreSQL focales y S2 completo correctos, head `a4c8e2f6b901`, estado operativo válido y diff limpio.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no se considera fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación técnica, validación específica, revisión independiente y cierre documental. Las regresiones y suites amplias se ejecutan solo cuando el alcance y riesgo las justifican. Los commits y la publicación permanecen bajo confirmación humana.

No deben repetirse validaciones vigentes si los archivos cubiertos no han cambiado. El estado operativo debe permitir reanudar el trabajo sin repetir inspecciones ya cerradas.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ resultado de evaluación ≠ aprendizaje ≠ mastery;
- `required_stages` y `SkillCoverage` son contratos heredados y no producen `CurriculumPreparationState`;
- no integrar todavía `LessonCapabilityPlan` en `PedagogicalUnitCandidate`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`;
- no modificar `SkillCoverage` ni `required_stages`;
- no implementar todavía ledger, orden curricular, resolución de `artifact_ids`, precedencia ni ciclos;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.

## Bloque activo

### Primera slice estructural del contrato curricular v1

Estado: implementación técnica validada y commiteada mediante `56e7394` (`feat add curriculum capability contracts v1`); pendiente de cierre documental y publicación.

Archivos técnicos commiteados, sin cambios posteriores a la validación:

- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`.

Contratos añadidos:

- `CurriculumPreparationState`;
- `LessonCapabilityClaim`;
- `SkillPrerequisite`;
- `LessonCapabilityPlan`.

Validación vigente, no repetir mientras esos archivos no cambien:

- `.venv/bin/pytest -q tests/test_curriculum_capability_schema.py`: 15 passed;
- regresión seleccionada: 74 passed;
- suite backend completa: 1277 passed;
- revisión independiente Codex: PASS, sin hallazgos;
- `git diff --check`: PASS.

Estado Git: commit técnico local `56e7394`; falta el commit documental, el push y la comprobación final de Git limpio y sincronizado.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Crear el commit documental de esta primera slice estructural, publicar los commits pendientes y comprobar finalmente Git limpio y sincronizado antes de abrir la siguiente.

No corresponde todavía integrar planes en candidatas ni implementar ledger, orden, referencias, precedencia o ciclos.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
