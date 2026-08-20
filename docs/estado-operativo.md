# Estado operativo — LOGUIC English

Actualizado: 2026-08-20
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Active candidate membership collection — Slice 35

Estado: cerrada técnicamente de forma local mediante el commit `46a293c` (`feat add active candidate membership collection`); pendiente de commit documental y push. `master` está por delante de `origin/master` únicamente por ese commit técnico.

`ActiveCandidateMembershipCollection` es un value object frozen con exactamente `memberships: tuple[ActiveCandidateMembership, ...]`. `build_active_candidate_membership_collection(memberships: Sequence[ActiveCandidateMembership])` materializa el input una sola vez, acepta vacío, preserva orden e identidades de las memberships y queda aislada de mutaciones posteriores de la sequence original.

La collection exige como máximo una membership por `identity.unit_id` y `admission_id` globalmente único; cualquier duplicado produce `ValueError` que identifica el valor duplicado. No hay dedupe, selección de ganadora, replacement implícito ni regla redundante de identity global.

Fronteras: admission verificada ≠ active membership ≠ membership collection ≠ productive snapshot ≠ representación física. La collection no recalcula gates ni identity, no reconstruye linkage con `AdmissionRecord`, no incorpora transición/replacement, historial, eventos, I/O, manifest, source integrity, loader, orden curricular ni compatibilidad curricular autoritativa.

Validación confirmada: 12 pruebas específicas PASS en 0.18 s; postflight independiente PASS / READY FOR REGRESSION; regresión seleccionada 69 passed en 0.23 s y suite backend completa 1844 passed en 14.51 s (`PYTEST_EXIT=0`); `git diff --check` real PASS. El finding de postflight —ausencia de `isinstance` explícito en el test de shape— es NONBLOCKING y no requiere cambio. A1-U1 sigue pending / non-member; LOADER = BLOCKED.

Primer piloto de routing: preflight arquitectónico `Sol / high` (A=2, I=2, R=2, V=1, C=1; total 8) fue justificado al detectar `logical collection ≠ productive snapshot` con identidad/revisión propia. Implementación `Terra / medium` fue suficiente, sin escalamiento; postflight `Terra / high` fue suficiente y estimó `Terra / medium` razonable una vez cerrada la frontera. No cambian policy, thresholds ni default `Terra / medium`.

## Bloque activo

No hay implementación técnica activa. La slice 35 está cerrada técnicamente y pendiente solo de cierre documental/publicación. No implementar productive snapshot, manifest, source integrity ni loader.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación, validación específica, revisión independiente y cierre documental. No repetir inspecciones ni validaciones ya confirmadas mientras no cambien los archivos cubiertos. Operar con Codex CLI + Bash; si una regresión en Codex queda indeterminada, ejecutarla una sola vez directamente en Bash. La suite backend completa se ejecuta directamente en Bash cuando corresponde.

Antes de cambiar de conversación: actualizar este documento, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar solo con checkpoint válido. Al reanudar: usar `conversation_checkpoint.py resume` antes de proponer comandos, inspecciones o cambios.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ productive snapshot ≠ compatibilidad curricular autoritativa;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Después de cerrar y publicar la slice 35, hacer únicamente el preflight o decisión contractual del productive snapshot: identidad o revisión propia, atomicidad lógica/de lectura y relación con `ActiveCandidateMembershipCollection`. Permanecen pendientes, sin diseñarlas todavía: representación física/manifest, source integrity e integración de carga/loader después de demostrar las capas anteriores.

## Archivos clave

- `docs/estado-operativo.md` y `docs/bitacora.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_validation_service.py`.
