# Estado operativo — LOGUIC English

Actualizado: 2026-08-14
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Último commit publicado y sincronizado: `787561e`.
- Todo trabajo curricular parte de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Contrato curricular v1 — Slice estructural 7

Estado: cerrada, publicada y sincronizada mediante los commits técnico `f1eb2ba` (`refactor expose capability claim precedence derivation`) y documental `787561e`; push confirmado hasta `787561e` en `origin/master`.

La API pura `derive_capability_claim_state_precedence(candidate)` consume la derivación de slice 5 y devuelve `CapabilityClaimPrecedenceDerivation`, separando inmutablemente cada `CapabilityClaimAvailability` posicionable en `valid_claims` o un `CapabilityClaimPrecedenceError` en `precedence_errors`. Los claims excluidos por slice 5 quedan fuera de ambas colecciones y no generan errores duplicados.

Conserva la precedencia estricta y acumulativa de slice 6, el aislamiento por `Skill`, el rechazo del mismo stage y las cuatro causas existentes. No colapsa claims ni calcula estado máximo, posición elegida, snapshot o ledger. El validador es solo adaptador de errores a findings. `_STATE_ORDER` es una tuple inmutable y `_state_index()` la consulta sin estado global mutable. No hubo cambios de schemas, persistencia ni contenido canónico.

Validación vigente, no repetir mientras no cambien archivos técnicos: 35 pruebas específicas PASS; postflight independiente final PASS sin hallazgos; 201 pruebas de regresión directa PASS; suite backend completa directa en Bash, 1432 passed in 13.30s, `PYTEST_EXIT=0`; `git diff --check` PASS.

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

### Contrato curricular v1 — Slice estructural 7

Estado: cerrada, publicada y sincronizada mediante los commits técnico `f1eb2ba` y documental `787561e`; push confirmado hasta `787561e` en `origin/master`. La derivación pura de precedencia está descrita en «Último bloque cerrado».

Permanecen fuera `CurriculumCapabilityPreparationLedger`, snapshot curricular, agregación por `Skill`, `highest_preparation_state`, elección de primera/última posición, prerrequisitos y `PedagogicalUnitSpecification.prerequisites`, contexto interunidad/CEFR, ciclos, progreso, ejecución del learner, evidencia real, resultados, mastery, calidad pedagógica, runtime, persistencia y cambios en `SkillCoverage` o `required_stages`.

Si el background de Codex vuelve a interrumpirse, conservar Codex CLI + Bash y ejecutar la suite backend completa directamente en Bash. No repetir las validaciones vigentes mientras no cambien los archivos técnicos.

Archivos técnicos commiteados:

- `app/services/pedagogical_capability_artifact_state_validation.py`;
- `app/services/pedagogical_validation_service.py`;
- `app/services/pedagogical_capability_claim_precedence_validation.py`;
- `tests/test_pedagogical_capability_claim_precedence_validation.py`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

I1–I4 y las correcciones frontend están publicados. No existe un fallo técnico pendiente. Su reanudación depende de la construcción pedagógica canónica A1 y de generar después un candidato adecuado para repetir la validación humana. La segunda validación humana permanece pausada, no completada.

## Próximo objetivo

Hacer preflight de la siguiente slice curricular desde el contrato v1 autoritativo y reevaluar si ya corresponde construir una vista o ledger curricular derivado o todavía falta una dependencia estructural previa, sin iniciar prerrequisitos antes de demostrar sus dependencias.

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
- `docs/modelo-pedagogico-maestro.md`;
- `docs/roadmap.md` y `docs/bitacora.md`.
