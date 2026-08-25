# Estado operativo — LOGUIC English

Actualizado: 2026-08-24T21:27:21+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B42.1 — Timestamp preciso del estado operativo

Estado técnico: **CERRADO / PUBLICADO** mediante `46020c1e91577dc4929298f3198ce3b91e54143e` (`feat add precise operational state timestamp`); este cierre documental queda local y pendiente de su propio commit/publicación. `Actualizado:` ahora exige fecha, hora y offset ISO 8601 (`YYYY-MM-DDTHH:MM:SS±HH:MM`), con comparación aware por instante; `OperationalStateReport` migró de `updated_on` a `updated_at`.

La validación usa `%cI` y compara contra HEAD, o contra HEAD^ cuando HEAD contiene este documento; un root que lo contiene no tiene baseline Git. Esto evita la autorreferencia del commit de cierre. `conversation_checkpoint.py` reutiliza el validador sin cambio productivo; `block_workflow.py` solo consume/imprime `updated_at`.

B42 permanece cerrado: `AdmissionRecord correspondence verified`. Siguen unresolved admitted decision, current/historical admission gates, reviewer authenticity, candidate_revision provenance, resource integrity y active source integrity. Los postflights B42.1 cerraron dos findings BLOCKING; permanecen solo gaps de cobertura temporal/Git NONBLOCKING, sin fallo funcional observado. Validación: 45 tests de infraestructura PASS en 0.82 s; suite backend completa 1980 PASS en 17.66 s; `git diff --check` y validación real del estado PASS. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

### Cierre documental B42.1

Estado: preparación local de este cierre documental; no hay bloque funcional/técnico adicional activo. El microbloque tooling `git_close.py --publish-url` v1 permanece cerrado y publicado, sin relación con admission, source integrity o loader.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint con `Actualizado:` timezone-aware.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

Cada slice pasa por definición, implementación, validación específica, revisión independiente y cierre documental. No repetir inspecciones ni validaciones ya confirmadas mientras no cambien los archivos cubiertos. Operar con Codex CLI + Bash; si una regresión en Codex queda indeterminada, ejecutarla una sola vez directamente en Bash. La suite backend completa se ejecuta directamente en Bash cuando corresponde.

Antes de cambiar de conversación: actualizar este documento con timestamp local aware, validarlo con `operational_state.py`, ejecutar `conversation_checkpoint.py prepare` y cambiar solo con checkpoint válido. Al reanudar: usar `conversation_checkpoint.py resume` antes de proponer comandos, inspecciones o cambios.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ active source snapshot ≠ representación física ≠ compatibilidad curricular autoritativa;
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ AdmissionRecord correspondence ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B42.1, reevaluar las reglas actuales de admission gates usando exclusivamente candidate bytes B39 preservados, AdmissionRecord adquirido/correspondido B41/B42 y contratos B33/validation. Current gate reevaluation ≠ historical gate execution proof. No se diseña ni numera aquí ese bloque posterior; después seguirán pendientes recursos físicos, active source integrity y loader. `LOADER = BLOCKED` y la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_candidate_admission_record_document.py`;
- `app/services/pedagogical_active_candidate_admission_record_acquisition.py`;
- `app/services/pedagogical_active_candidate_admission_record_correspondence.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `tests/test_pedagogical_active_candidate_admission_record_acquisition.py`;
- `tests/test_pedagogical_active_candidate_admission_record_correspondence.py`;
- `app/services/pedagogical_validation_service.py`.
