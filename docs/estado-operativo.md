# Estado operativo — LOGUIC English

Actualizado: 2026-08-27T12:11:59+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B50 — Observed ResourcePhysicalIdentity from acquired resource bytes v1

Estado técnico: **CERRADO / PUBLICADO** mediante `8ed695d3d59ab44f33ec11ef3dd47f7085b0f345`. Contrato publicado: `6934def64d2d9a12bcac712252eaf0c6cfcf557a`. Este cierre documental queda local y pendiente de su propio commit/publicación; no existe todavía commit documental B50.

`ObservedResourcePhysicalIdentity` frozen contiene exactamente `acquired_resource: AcquiredResource` y `physical_identity: ResourcePhysicalIdentity`. `ActiveCandidateSourceObservedResourceIdentityCollection` frozen contiene exactamente `resource_acquisition: ActiveCandidateSourceResourceAcquisition` y `entries: tuple[ObservedResourcePhysicalIdentity, ...]`. `derive_active_candidate_source_observed_resource_identities(...)` acepta exclusivamente B49 mediante `isinstance`, conserva B49 y cada `AcquiredResource` por identidad, no revalida B49/B48/B47/B46/B45 y produce una entry por cada entry B49 en el mismo orden B49/B48/B46.

Por cada `AcquiredResource`, B50 llama exactamente una vez a B44: `derive_resource_physical_identity(acquired_resource.resource_bytes, resource_id=acquired_resource.binding.resource_id)`. Los bytes y el ID son literales y autoritativos; el retorno B44 se conserva directamente. No hay `hashlib`, hash/digest manual, reconstrucción de `ResourcePhysicalIdentity`, Path derivation, cache, sorting, grouping ni deduplicación. Same bytes/different IDs produce dos llamadas, dos entries, IDs distintos y digest igual permitido; `same digest != same logical resource`.

La garantía positiva se limita a observed identity desde evidencia adquirida: `acquired bytes != observed ResourcePhysicalIdentity != expected-vs-observed equality != resource integrity != active source integrity != loader readiness`. B50 es in-memory y funciona aunque el Path original desaparezca tras B49; no usa filesystem I/O, network, DB, persistence, clock ni randomness. Expected identities accesibles B50 → B49 → B48 → B47 → B45 no influyen: no hay consulta B45, expected digest, match, status ni integrity. ResourcePhysicalIdentity permanece neutral; observedness procede del wrapper B50.

B49 vacío produce B50 positivo vacío sin llamadas B44. Si B44 falla, no hay aggregate ni tuple parcial pública, findings, status o resultado negativo; el error se propaga. B50 no duplica bytes, IDs, Paths, digest map, índices, counts, expected identities ni metadata. No prueba expected-vs-observed equality, expected digest correctness, integrity, intended-resource correctness, autenticidad, provenance, snapshot, path safety, media validity, corrección semántica/pedagógica, active source integrity ni loader readiness. Validación: 12 directas PASS en 0.14 s; regresión B31–B50, 196 passed en 0.54 s; suite backend completa, 2100 passed en 16.99 s; `git diff --check` técnico, postflight contractual y postflight técnico PASS. Findings BLOCKING: ninguno. Findings NONBLOCKING: ninguno. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`.

### B43 — Active candidate current admission gate reevaluation v1

Estado técnico: **CERRADO / PUBLICADO** mediante `7427f2b78b7030883ec3e8b8cfff0d707d2ff0c4` (`feat add active candidate current admission gate reevaluation v1`). Contrato publicado: `287f2fcbfb40cf89c9af05ceb2790773dce17b76`. Este cierre documental queda local y pendiente de su propio commit/publicación.

`reevaluate_active_candidate_current_admission_gates(...)` consume exclusivamente B42 correspondence y, por cada entry alineada B39/B41, reconstruye un candidate efímero solo desde `candidate_bytes`, llama una vez a B33 y conserva `AdmissionGateVerification`. El aggregate frozen existe solo si los cuatro gates actuales verifican: identity, local validation, pending human decisions y decisión admitted. `identity_matches=False` tras B39+B42 es contradicción técnica fail-closed; rejected, pending decisions o validation no passed impiden resultado positivo sin crear resultado parcial. No hay reread de filesystem, manifest, candidate/document paths, red ni recursos.

La garantía es actual, no histórica: current admission gate reevaluation ≠ historical gate execution proof. B39 sigue siendo autoridad de candidate payload integrity y B42 de AdmissionRecord correspondence. B43 no acredita reviewer/decision/timestamp/record authenticity, candidate_revision provenance, recursos, active source integrity ni loader. B31 excluye del digest `validation_report`, `pending_human_decisions` y `proposed_change_summary`; B43 evalúa pending decisions presentes en los bytes completos preservados sin afirmar autenticidad histórica. Validación: 11 directas PASS en 0.21 s; regresión B31–B43 161 PASS en 0.52 s; suite backend 1991 PASS en 18.28 s; `git diff --check`, postflight contractual y postflight técnico PASS, sin findings BLOCKING ni NONBLOCKING materiales.

### B42.1 — Timestamp preciso del estado operativo

Estado técnico: **CERRADO / PUBLICADO** mediante `46020c1e91577dc4929298f3198ce3b91e54143e` (`feat add precise operational state timestamp`); este cierre documental queda local y pendiente de su propio commit/publicación. `Actualizado:` ahora exige fecha, hora y offset ISO 8601 (`YYYY-MM-DDTHH:MM:SS±HH:MM`), con comparación aware por instante; `OperationalStateReport` migró de `updated_on` a `updated_at`.

La validación usa `%cI` y compara contra HEAD, o contra HEAD^ cuando HEAD contiene este documento; un root que lo contiene no tiene baseline Git. Esto evita la autorreferencia del commit de cierre. `conversation_checkpoint.py` reutiliza el validador sin cambio productivo; `block_workflow.py` solo consume/imprime `updated_at`.

B42 permanece cerrado: `AdmissionRecord correspondence verified`; B43 posterior verificó los admission gates actuales sobre la evidencia preservada. Siguen unresolved historical admission gates, reviewer authenticity, candidate_revision provenance, resource integrity y active source integrity. Los postflights B42.1 cerraron dos findings BLOCKING; permanecen solo gaps de cobertura temporal/Git NONBLOCKING, sin fallo funcional observado. Validación: 45 tests de infraestructura PASS en 0.82 s; suite backend completa 1980 PASS en 17.66 s; `git diff --check` y validación real del estado PASS. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

### Cierre documental local B50

Estado: preparación local de este cierre documental hasta su publicación; no hay bloque funcional/técnico adicional activo. B50, B49, B48, B47, B46, B45, B44, B43 y B42.1 permanecen cerrados. B42.1 conserva su trazabilidad como mejora de timestamp operativo. El microbloque tooling `git_close.py --publish-url` v1 también permanece cerrado y publicado, sin relación con admission, source integrity o loader.

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
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ AdmissionRecord correspondence ≠ current admission gate reevaluation ≠ historical gate execution proof ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource physical identity ≠ expected resource identity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

Tras publicar este cierre documental de B50, la siguiente frontera es expected-vs-observed resource integrity. Conceptualmente comparará de forma independiente las observed identities B50 con expected identities accesibles transitivamente por `resource_id`/digest; no se diseña todavía API, result shape, diagnostics ni objeto success/failure. Después podrán seguir active source integrity y loader. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`; la compatibilidad curricular autoritativa sigue posterior.

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
- `app/services/pedagogical_active_candidate_current_admission_gate_reevaluation.py`;
- `app/services/pedagogical_resource_physical_identity.py`;
- `app/services/pedagogical_active_candidate_source_resource_acquisition.py`;
- `app/services/pedagogical_active_candidate_source_observed_resource_identity_collection.py`;
- `app/services/pedagogical_expected_resource_identity_collection.py`;
- `app/services/pedagogical_active_candidate_source_required_resource_inventory.py`;
- `app/services/pedagogical_active_candidate_source_expected_resource_coverage_verification.py`;
- `app/services/pedagogical_active_candidate_membership.py`;
- `app/services/pedagogical_active_candidate_membership_collection.py`;
- `app/services/pedagogical_active_candidate_source_snapshot.py`;
- `app/services/pedagogical_active_candidate_source_acquisition.py`;
- `app/services/pedagogical_active_candidate_integrity_verification.py`;
- `tests/test_pedagogical_candidate_admission_record_document.py`;
- `tests/test_pedagogical_active_candidate_admission_record_acquisition.py`;
- `tests/test_pedagogical_active_candidate_admission_record_correspondence.py`;
- `tests/test_pedagogical_active_candidate_current_admission_gate_reevaluation.py`;
- `tests/test_pedagogical_resource_physical_identity.py`;
- `tests/test_pedagogical_active_candidate_source_resource_acquisition.py`;
- `tests/test_pedagogical_active_candidate_source_observed_resource_identity_collection.py`;
- `tests/test_pedagogical_expected_resource_identity_collection.py`;
- `tests/test_pedagogical_active_candidate_source_required_resource_inventory.py`;
- `tests/test_pedagogical_active_candidate_source_expected_resource_coverage_verification.py`;
- `app/services/pedagogical_validation_service.py`.
