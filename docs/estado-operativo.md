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
- no exigir un plan por lección ni implementar validadores curriculares, ledger, orden curricular, resolución de `artifact_ids`, compatibilidad artefacto/estado, precedencia, ciclos o prerrequisitos interunidad;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.

## Bloque activo

### Contrato curricular v1 — Slice estructural 2

Estado: implementación técnica validada y commiteada mediante `aea6a26` (`feat integrate lesson capability plans`); cierre documental, push y sincronización final pendientes.

Archivos técnicos commiteados y sin cambios posteriores a las validaciones:

- `app/schemas/pedagogical_unit.py`;
- `tests/test_pedagogical_unit_schema.py`.

`PedagogicalUnitCandidate` incorpora `lesson_capability_plans: list[LessonCapabilityPlan] = Field(default_factory=list)`. Los `lesson_id` deben ser únicos y pertenecer a `candidate_unit.lessons`.

Compatibilidad heredada: candidatas que omiten el campo siguen siendo válidas y producen `lesson_capability_plans == []`; el candidato JSON canónico permanece intacto y no se añadió flag o versionado.

Validación vigente, no repetir: 26 pruebas específicas; 17 de regresión directa; suite backend completa 1305 passed; postflight independiente PASS; `git diff --check` PASS. Durante la primera ejecución se corrigió únicamente una aserción nueva sobre `loc` de Pydantic, sin debilitar la validación.

Fronteras conservadas: sin cobertura obligatoria, resolución de artefactos, validación artefacto/estado, ledger, precedencia, orden, ciclos, prerrequisitos interunidad o integración con validadores; `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage` y `required_stages` siguen intactos.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Crear el commit documental, publicar y verificar Git limpio y sincronizado para cerrar la slice 2.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/conversation_checkpoint.py`;
- `tests/test_conversation_checkpoint.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/test_curriculum_capability_schema.py`;
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
