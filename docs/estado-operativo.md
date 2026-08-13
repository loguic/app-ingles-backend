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

### Contrato curricular v1 — Slice estructural 3

Estado: cerrada, publicada y sincronizada mediante los commits técnico `779f770` y documental `83e830a`.

El validador `capability_artifact_reference_integrity` resuelve local y tipadamente `LessonCapabilityClaim.artifact_ids`, rechazando referencias desconocidas, externas o ambiguas sin prioridad implícita. Las candidatas heredadas conservan su comportamiento.

Validación final vigente: 21 pruebas específicas; 82 de regresión directa; suite backend completa con código 0; postflight independiente PASS; `git diff --check` PASS.

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
- no exigir un plan por lección ni implementar secuencia de estados, ledger, orden curricular, precedencia, ciclos o prerrequisitos interunidad;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.

## Bloque activo

### Contrato curricular v1 — Slice estructural 4

Estado: cerrada, publicada y sincronizada mediante los commits técnico `b95c53c` (`feat validate capability artifact state compatibility`) y documental `6115cfc`; push confirmado hasta `6115cfc` en `origin/master`.

El validador independiente `capability_artifact_state_compatibility`, integrado en `validate_pedagogical_candidate`, reutiliza la resolución tipada de la slice 3 y valida combinaciones completas y relaciones reales entre los artefactos de un claim y su `CurriculumPreparationState`, no una tabla simple tipo → estado. Omite claims con referencias inválidas o ambiguas y emite un único finding determinista por claim incompatible.

Soporta las combinaciones estructurales de `EXPOSURE_AVAILABLE`, `INSTRUCTION_AVAILABLE`, `PRACTICE_AVAILABLE` y `EVIDENCE_GATE_AVAILABLE`. La puerta de evidencia admite rutas mediante `LearnerProductionPrompt` o mediante `ConversationChoice` sin prompt cuando existe una valoración compatible; una choice sin valoración sigue siendo inválida. `PronunciationReinforcement` y `ExternalReviewRequirement` participan indirectamente sin IDs inventados. No se modificaron schemas ni contenido canónico.

Validación vigente, no repetir mientras no cambien los archivos técnicos: 51 pruebas específicas PASS; postflight independiente final PASS sin hallazgos; 154 pruebas de regresión directa PASS; suite backend completa ejecutada directamente en Bash, 1377 passed in 13.32s y código 0; `git diff --check` PASS. Si el terminal background de Codex vuelve a detenerse alrededor de las primeras pruebas, ejecutar la suite directamente en Bash; no existe evidencia de regresión del backend.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `tests/test_pedagogical_capability_artifact_state_validation.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Definir mediante preflight la siguiente slice curricular desde el contrato v1 autoritativo, comprobando dependencias reales antes de asumir ledger o precedencia como siguiente paso.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
