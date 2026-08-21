# Estado operativo — LOGUIC English

Actualizado: 2026-08-21
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### Active candidate source snapshot — Slice 36

Estado: cerrada técnicamente de forma local mediante el contrato `9bb3a13` (`docs define active candidate source snapshot`) y el commit técnico `deeb99a` (`feat add active candidate source snapshot`); pendiente de cierre documental y push. `master` está por delante de `origin/master` únicamente por esos dos commits.

`ActiveCandidateSourceSnapshot` es un value object frozen con exactamente `snapshot_revision: str` y `collection: ActiveCandidateMembershipCollection`. `build_active_candidate_source_snapshot(collection, *, snapshot_revision)` valida solo una revision `str` non-blank y una collection conforme, preservando ambas instancias literalmente y sin reconstruir memberships.

`candidate_revision` identifica una unit candidata y `snapshot_revision` el conjunto activo completo; no se derivan entre sí. El snapshot compone la collection ya conforme, por lo que hereda vacío válido, orden solo representacional y sus unicidades sin recalcularlas. Misma revision y collection estructural son iguales; misma revision con collection distinta puede construirse localmente y su conflicto pertenece a una futura consistencia global de source/publication.

Fronteras: admission verificada ≠ active membership ≠ membership collection ≠ active source snapshot ≠ publication event ≠ representación física. Snapshot declarado ≠ publicación física completada; tampoco equivale a source integrity, loader, orden curricular o compatibilidad curricular autoritativa. No introduce snapshot ID, digest, source ID, timestamps, schema version, replacement, historial, eventos, I/O, manifest ni validación/reconstrucción de capas anteriores.

Validación confirmada: 11 pruebas específicas PASS en 0.11 s; postflight independiente PASS / READY FOR REGRESSION; regresión seleccionada 80 passed en 0.25 s y suite backend completa 1855 passed en 13.88 s (`PYTEST_EXIT=0`); `git diff --check` real PASS. A1-U1 sigue pending / non-member; LOADER = BLOCKED.

Segundo piloto de routing: preflight contractual `Sol / high` fue justificado por la identidad, publication y atomicidad del snapshot. Implementación `Terra / medium` fue suficiente sin escalamiento; postflight `Terra / high` fue suficiente y `Terra / medium` habría sido razonable con el contrato cerrado. No cambian policy, thresholds ni default `Terra / medium`.

## Bloque activo

No hay implementación técnica activa. La slice 36 está cerrada técnicamente y pendiente solo de cierre documental/publicación. No implementar representación física, source integrity ni loader.

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
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ active source snapshot ≠ representación física ≠ compatibilidad curricular autoritativa;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Después de cerrar y publicar la slice 36, hacer únicamente el preflight de la representación física explícita de `ActiveCandidateSourceSnapshot`: cómo expresará revision y memberships, con lectura/publicación física atómica, sin diseñar todavía source integrity, adquisición ni loader. Permanecen pendientes source integrity, correspondencia con candidates adquiridos e integración de carga/loader.

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
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_validation_service.py`.
