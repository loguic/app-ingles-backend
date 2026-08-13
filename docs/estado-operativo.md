# Estado operativo — LOGUIC English

Actualizado: 2026-08-13
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado anterior a la slice activa: `56f2081`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 2

Estado: cerrada, publicada y sincronizada mediante los commits técnico `aea6a26` y documental `297d8a3`.

`PedagogicalUnitCandidate` incorpora `lesson_capability_plans` con `default_factory=list`, unicidad por `lesson_id` y pertenencia a `candidate_unit.lessons`. Las candidatas heredadas siguen siendo válidas con lista vacía y el candidato JSON canónico permanece intacto.

Validación final vigente: 26 pruebas específicas; 17 de regresión directa; suite backend completa 1305 passed; postflight independiente PASS; `git diff --check` PASS.

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
- no exigir un plan por lección ni implementar compatibilidad artefacto/estado, secuencia de estados, ledger, orden curricular, precedencia, ciclos o prerrequisitos interunidad;
- no modificar runtime individual, progreso, mastery, fonética, feedback ni B181.

## Bloque activo

### Contrato curricular v1 — Slice estructural 3

Estado: cerrada técnicamente mediante `779f770` (`feat validate capability artifact references`); cierre documental, publicación y sincronización final pendientes.

El validador independiente `capability_artifact_reference_integrity`, integrado en `validate_pedagogical_candidate`, resuelve localmente cada `LessonCapabilityClaim.artifact_ids` dentro de la lección propietaria con identidad, tipo real, propietario y objeto original. Rechaza referencias desconocidas, pertenecientes a otra lección o ambiguas, sin prioridad implícita ante colisiones.

Solo indexa los tipos autorizados con identidad propia. `ProductionEvaluationCriterion` y `SemanticEvaluationRule` proceden exclusivamente del plan cuyo `lesson_id` coincide. No inventa IDs para `PronunciationReinforcement`, `ExternalReviewRequirement`, `Pronunciation` ni `audio_asset`. Las candidatas heredadas sin planes conservan su comportamiento.

Validación vigente, no repetir mientras no cambien los archivos técnicos: 21 pruebas específicas PASS; postflight independiente PASS sin hallazgos; 82 pruebas de regresión directa PASS; suite backend completa posterior al incidente alcanzó 100 % y terminó con código 0; `git diff --check` PASS.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_reference_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `tests/test_pedagogical_capability_artifact_reference_validation.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Completar el cierre documental, publicación y sincronización de la slice 3. Después, diseñar la slice 4 de compatibilidad tipada artefacto ↔ `CurriculumPreparationState`, reutilizando el índice y la resolución existentes.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
