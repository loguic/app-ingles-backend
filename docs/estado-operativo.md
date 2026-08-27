# Estado operativo — LOGUIC English

Actualizado: 2026-08-27T19:16:43+02:00
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Contrato curricular autoritativo: `docs/curriculum-preparation-prerequisites-contract-v1.md`.
- Método operativo canónico: `docs/loguic-engineering-operating-method-v1.md`.
- Política operativa transversal de routing: `docs/loguic-ai-model-routing-policy-v1.md` (default: `Terra / medium`; por tarea y sin escalamiento automático).
- Git final requerido: limpio y sincronizado con `origin/master`.
- Todo trabajo curricular parte de una capacidad observable del estudiante; `Skill` significa exclusivamente habilidad pedagógica medible.

## Último bloque cerrado

### B51 — Expected-vs-observed resource integrity v1

Estado: **CERRADO / DOCUMENTADO / PUBLICADO / SINCRONIZADO**. Contrato publicado: `409dc4184c58fe8137563cddf3baa067b0fa62cf`. Implementación técnica publicada: `b607bc9a8513792c4001357c175a254f45281756`. Cierre documental publicado: `0577a9204a91517eec479c7250d4408d41e856bd`.

`ActiveCandidateSourceResourceIntegrityVerification` frozen contiene exactamente `observed_resource_identity_collection: ActiveCandidateSourceObservedResourceIdentityCollection`. `verify_active_candidate_source_resource_integrity(...)` consume exclusivamente B50 y conserva ese B50 por identidad; es una verification causal positive-only, sin status, bool, counts, pairs, mismatches persistidos, expected collection duplicada ni segundo input que permita cross-source mixing.

La expected authority se obtiene transitivamente desde B50 mediante `resource_acquisition.resource_binding_collection.expected_resource_coverage_verification.expected_resource_identity_collection`; la observed authority es `B50.entries[*].physical_identity`. El pairing es por `resource_id` literal, nunca por posición, Path ni digest; B45 y B50 pueden tener órdenes diferentes. La comparación es literal y exacta: `expected.content_digest == observed.content_digest`. Se recorre B50 order: todos los matches devuelven verification positiva frozen; uno o más mismatches acumulan IDs en ese orden y producen un único `ValueError` determinista, sin resultado parcial.

La garantía positiva acredita únicamente que, para cada `resource_id` del dominio source-contextual acreditado por B47, el digest observed B50 coincide literalmente con el digest expected B45 correspondiente: `B49 acquired bytes → B44/B50 observed ResourcePhysicalIdentity → B51 comparison == B45 declared expected ResourcePhysicalIdentity`. `resource integrity != expected authenticity != active source integrity != loader readiness`. Same digest/different IDs es válido si cada ID coincide con su expected; digests intercambiados entre IDs fallan aunque el multiset coincida; B50 vacío devuelve verification positiva vacía; un expected digest arbitrario B45 se compara literalmente.

B51 no revalida dominio B47, no reejecuta B39, no llama B44, no recalcula hashes, no relee filesystem ni compara bytes; tampoco acredita expected digest correctness/autenticidad, provenance, active source integrity ni loader readiness. No compone B43 ni activa loader. Validación: 11 directas PASS en 0.15 s; regresión seleccionada, 281 passed en 0.74 s; suite backend completa, 2111 passed en 16.88 s; `git diff --check` técnico, postflight contractual y postflight técnico independiente PASS. Findings BLOCKING: 0. Findings NONBLOCKING: 0. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`.

### B43 — Active candidate current admission gate reevaluation v1

Estado técnico: **CERRADO / PUBLICADO** mediante `7427f2b78b7030883ec3e8b8cfff0d707d2ff0c4` (`feat add active candidate current admission gate reevaluation v1`). Contrato publicado: `287f2fcbfb40cf89c9af05ceb2790773dce17b76`. Este cierre documental queda local y pendiente de su propio commit/publicación.

`reevaluate_active_candidate_current_admission_gates(...)` consume exclusivamente B42 correspondence y, por cada entry alineada B39/B41, reconstruye un candidate efímero solo desde `candidate_bytes`, llama una vez a B33 y conserva `AdmissionGateVerification`. El aggregate frozen existe solo si los cuatro gates actuales verifican: identity, local validation, pending human decisions y decisión admitted. `identity_matches=False` tras B39+B42 es contradicción técnica fail-closed; rejected, pending decisions o validation no passed impiden resultado positivo sin crear resultado parcial. No hay reread de filesystem, manifest, candidate/document paths, red ni recursos.

La garantía es actual, no histórica: current admission gate reevaluation ≠ historical gate execution proof. B39 sigue siendo autoridad de candidate payload integrity y B42 de AdmissionRecord correspondence. B43 no acredita reviewer/decision/timestamp/record authenticity, candidate_revision provenance, recursos, active source integrity ni loader. B31 excluye del digest `validation_report`, `pending_human_decisions` y `proposed_change_summary`; B43 evalúa pending decisions presentes en los bytes completos preservados sin afirmar autenticidad histórica. Validación: 11 directas PASS en 0.21 s; regresión B31–B43 161 PASS en 0.52 s; suite backend 1991 PASS en 18.28 s; `git diff --check`, postflight contractual y postflight técnico PASS, sin findings BLOCKING ni NONBLOCKING materiales.

### B42.1 — Timestamp preciso del estado operativo

Estado técnico: **CERRADO / PUBLICADO** mediante `46020c1e91577dc4929298f3198ce3b91e54143e` (`feat add precise operational state timestamp`); este cierre documental queda local y pendiente de su propio commit/publicación. `Actualizado:` ahora exige fecha, hora y offset ISO 8601 (`YYYY-MM-DDTHH:MM:SS±HH:MM`), con comparación aware por instante; `OperationalStateReport` migró de `updated_on` a `updated_at`.

La validación usa `%cI` y compara contra HEAD, o contra HEAD^ cuando HEAD contiene este documento; un root que lo contiene no tiene baseline Git. Esto evita la autorreferencia del commit de cierre. `conversation_checkpoint.py` reutiliza el validador sin cambio productivo; `block_workflow.py` solo consume/imprime `updated_at`.

B42 permanece cerrado: `AdmissionRecord correspondence verified`; B43 posterior verificó los admission gates actuales sobre la evidencia preservada. Siguen unresolved historical admission gates, reviewer authenticity, candidate_revision provenance, resource integrity y active source integrity. Los postflights B42.1 cerraron dos findings BLOCKING; permanecen solo gaps de cobertura temporal/Git NONBLOCKING, sin fallo funcional observado. Validación: 45 tests de infraestructura PASS en 0.82 s; suite backend completa 1980 PASS en 17.66 s; `git diff --check` y validación real del estado PASS. A1-U1 continúa pending / non-member; `LOADER = BLOCKED`.

## Bloque activo

### B52 — Active source integrity v1

Estado: **IMPLEMENTACIÓN LOCAL VALIDADA / PENDIENTE DE CIERRE TÉCNICO Y DOCUMENTAL**. Contrato publicado mediante `5d318c125acdc7128b0af73abafae0bee8c7b454`. La implementación y sus tests existen únicamente en local; B52 no tiene todavía commit técnico y no está cerrado ni publicado.

Archivos locales: `app/services/pedagogical_active_candidate_source_integrity_verification.py` y `tests/test_pedagogical_active_candidate_source_integrity_verification.py`. B52 compone exclusivamente B43+B51 cuando ambas ramas conservan el mismo B39 por identidad Python; no habilita loader.

Validación confirmada: 7 tests específicos PASS; regresión seleccionada B43+B51+B52, 29 PASS; postflight técnico PASS; findings BLOCKING: 0; findings NONBLOCKING: 0; suite backend completa ejecutada directamente en Bash, 2118 passed en 17.49 s; `git diff --check` PASS. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`.

### B181 — Comprensión contingente y continuidad conversacional breve

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. I1–I4 y correcciones frontend están publicados; la reanudación depende de construcción pedagógica canónica A1 y una nueva validación humana.

## Automatización disponible

- `operational_state.py` valida este checkpoint con `Actualizado:` timezone-aware.
- `conversation_checkpoint.py prepare|resume` prepara y recupera una vista efímera validada al cambiar de conversación.
- `block_close.py` realiza validaciones técnicas y staging controlado.
- `git_close.py` realiza un cierre Git seguro de allowlist explícita, un commit y un push confirmado.
- `block_workflow.py` conserva una deuda de interrupción y no es fiable para cierres desatendidos.

## Método operativo vigente

El método completo y canónico está en `docs/loguic-engineering-operating-method-v1.md`. Este documento conserva únicamente el checkpoint operativo compacto.

Al reanudar, ejecutar primero `python3 scripts/engineering/conversation_checkpoint.py resume` y continuar desde su salida más este checkpoint, sin repetir evidencia vigente. Antes de cambiar de conversación, actualizar y validar este estado y ejecutar `conversation_checkpoint.py prepare`.

## Fronteras obligatorias

- preparación curricular ≠ ejecución del estudiante ≠ evidencia real ≠ evaluación ≠ aprendizaje ≠ mastery;
- admission verificada ≠ publication ≠ active membership ≠ membership collection ≠ active source snapshot ≠ representación física ≠ compatibilidad curricular autoritativa;
- physical AdmissionRecord document ≠ admission record acquired / unverified ≠ AdmissionRecord correspondence ≠ current admission gate reevaluation ≠ historical gate execution proof ≠ admission provenance ≠ active membership proof ≠ candidate payload integrity ≠ resource physical identity ≠ expected resource identity ≠ resource integrity ≠ active source integrity ≠ loader readiness;
- `required_stages` y `SkillCoverage` heredados no producen `CurriculumPreparationState`;
- no modificar todavía `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage`, `required_stages`, runtime, progreso, mastery, fonética, feedback ni B181;
- membership/source state no define orden curricular; hierarchy authority no certifica admission.

## Próximo objetivo

El siguiente paso es cerrar técnica y documentalmente B52 sin ampliar su contrato. B52 permanece local y no publicado; no iniciar loader. `LOADER = BLOCKED`; A1-U1 permanece `pending / non-member`; la compatibilidad curricular autoritativa sigue posterior.

## Archivos clave

- `docs/estado-operativo.md`, `docs/bitacora.md` y `docs/loguic-engineering-operating-method-v1.md`;
- `docs/curriculum-preparation-prerequisites-contract-v1.md`;
- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `scripts/engineering/block_close.py`;
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
- `app/services/pedagogical_active_candidate_source_resource_integrity_verification.py`;
- `app/services/pedagogical_active_candidate_source_integrity_verification.py`;
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
- `tests/test_pedagogical_active_candidate_source_resource_integrity_verification.py`;
- `tests/test_pedagogical_active_candidate_source_integrity_verification.py`;
- `tests/test_pedagogical_expected_resource_identity_collection.py`;
- `tests/test_pedagogical_active_candidate_source_required_resource_inventory.py`;
- `tests/test_pedagogical_active_candidate_source_expected_resource_coverage_verification.py`;
- `app/services/pedagogical_validation_service.py`.
