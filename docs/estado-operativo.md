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

### Safe deterministic Git close helper v1

Estado: cerrado, documentado y publicado mediante `bf16407` (`feat add deterministic git close helper`) y `f36bd1f` (`docs close deterministic git close helper`); push confirmado en `origin/master` desde `681f790` hasta `f36bd1f`.

`scripts/engineering/git_close.py` sustituye el tramo repetitivo `git add` exacto → verificación → commit → push → sync por una orden explícita con `--branch`, `--upstream`, `--message` y `--file` repetible. Automatizar comprobaciones ≠ eliminarlas: antes de efectos exige root/repo, branch y upstream exactos, HEAD no detached, ausencia de operaciones Git, index vacío, cambios totales exactamente iguales a la allowlist, paths seguros y ahead/behind `0/0`.

Tras `git add -- <allowlist>` verifica staged scope exacto y ausencia de cambios unstaged/untracked; hace un único commit normal, confirma estructuralmente sus paths y limpieza, push normal explícito al remote/ref confirmado y éxito solo con branch/upstream esperados, porcelain vacío y ahead/behind `0/0`. No ejecuta pytest, `diff --check` u `operational_state`; tampoco descubre archivos, genera mensajes, hace force, retry, rollback, configuración Git, múltiples commits o I/O ajeno a Git.

Validación: 16 pruebas específicas PASS en 1.61 s; postflight independiente recheck PASS / READY FOR REGRESSION; regresión seleccionada de tooling (`tests/test_block_close.py`, `tests/test_conversation_checkpoint.py`, `tests/test_operational_state.py`, `tests/test_git_close.py`), 63 passed en 2.11 s (`PYTEST_EXIT=0`); suite backend completa, 1871 passed en 15.20 s (`PYTEST_EXIT=0`); `git diff --check` PASS. Las pruebas usan repos temporales y bare remotes locales: cubren cierre correcto, scope múltiple, staging previo, allowlist/path/message inválidos, branch/upstream, precheck ahead/behind, fallo de push que preserva commit ahead y worktree sucio tras hook. Permanecen fuera de scope la simulación directa de carrera stage→commit y hardening de remote names que empiecen por `-`.

Primer uso real preparado, todavía pendiente de ejecución: desde Bash se invocará `git_close.py` con allowlist exacta `docs/estado-operativo.md` y `docs/bitacora.md`, y mensaje `docs finalize deterministic git close helper`. Solo un éxito demostrará operativamente precheck → stage exacto → verify → commit → push → final sync verify. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

No hay implementación técnica activa. El helper Git está cerrado y publicado; su primer uso real está preparado y pendiente. No implementar representación física, source integrity ni loader.

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

Después de completar el primer uso real del helper Git, retomar App Inglés en la slice 37: únicamente el preflight de la representación física explícita de `ActiveCandidateSourceSnapshot`/source y atomicidad física, sin diseñar todavía source integrity, adquisición ni loader. Permanecen pendientes source integrity, correspondencia con candidates adquiridos e integración de carga/loader.

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
