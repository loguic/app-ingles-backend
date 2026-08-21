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

### ActiveCandidateSourceSnapshotManifestV1 — Slice 37

Estado objetivo de cierre: **CERRADO / PUBLICADO / SINCRONIZADO**. Contrato `6306362` (`docs define active candidate source snapshot manifest`), implementación `7b66d4f` (`feat add active candidate source snapshot manifest`) y cierre documental previo `8cdc4ea` (`docs close active candidate source snapshot manifest`) publicados. `8cdc4ea` es el checkpoint sincronizado confirmado inmediatamente anterior a esta actualización documental final (`master == origin/master == 8cdc4ea`); esta actualización no anticipa su propio hash. No hay cambios técnicos pendientes de slice 37.

`ActiveCandidateSourceSnapshotManifestV1` es únicamente el documento físico JSON v1 derivado de `ActiveCandidateSourceSnapshot`: serializa `manifest_schema_version="1.0"`, `snapshot_revision` literal y memberships en su orden representacional. Sus bytes son deterministas (UTF-8 sin BOM, `ensure_ascii=False`, separators compactos, `sort_keys=False`, `allow_nan=False`, newline final), sin hash ni prueba de integrity. El publicador exige `manifest_path: Path` absoluto y explícito, publica con temporal en el mismo parent → write/flush/fsync(file) → close → `os.replace` → fsync(parent), y limita sus garantías a visibilidad física local atómica, no a crash durability.

Si falla antes de replace se conserva S1 y se limpia best-effort solo el temporal no publicado; un fallo de fsync(parent) posterior puede dejar S2 visible con durabilidad no confirmada, sin rollback. No hay domain manifest, PublicationRecord, registry/history, acquisition, source integrity ni loader. Se mantiene: logical snapshot ≠ physical manifest ≠ manifest visible atómicamente ≠ durabilidad ≠ source integrity ≠ acquisition ≠ loader.

Postflight técnico final PASS: se cerraron la prueba real de fsync pre-replace, parent-file, nombre de test de replace y cleanup que preserva la excepción primaria. Validación: 8 específicas PASS en 0.13 s; regresión seleccionada de source/admission/membership/snapshot, 88 passed en 0.27 s; suite backend completa, 1879 passed en 14.59 s; `git diff --check` PASS; `operational_state.py validate` PASS.

Routing: preflight `Sol / high` (8/10) justificó la frontera física; implementación `Terra / medium` y postflight/recheck `Terra / high` fueron suficientes, sin escalamiento. Incidente de transporte: SSH falló con conexión cerrada en puertos 22 y 443; HTTPS respondió HTTP/2 200, se validó con `push --dry-run` y los commits se publicaron explícitamente por HTTPS, actualizando después `origin/master` mediante fetch HTTPS. No se atribuye causa, no se cambiaron remote ni claves y HTTPS no es una decisión arquitectónica permanente. `git_close.py` preservó correctamente el commit local e informó ahead=1/behind=0 ante el fallo inicial.

A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

No hay implementación técnica activa. Slice 37 está completamente cerrada. No implementar source integrity, acquisition ni loader sin un preflight separado.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
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

Preflight separado de acquisition/source integrity: correspondencia demostrable entre manifest/snapshot y candidates/artifacts adquiridos, antes de cualquier loader. No diseñar todavía loader ni compatibilidad curricular autoritativa.

## Archivos clave

- `docs/estado-operativo.md` y `docs/bitacora.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `scripts/engineering/git_close.py`;
- `tests/test_git_close.py`;
- `app/services/pedagogical_candidate_payload_identity.py`;
- `app/services/pedagogical_candidate_admission.py`;
- `app/services/pedagogical_candidate_admission_verification.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_validation_service.py`.
