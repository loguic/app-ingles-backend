# Estado operativo — App Inglés

Actualizado: 2026-07-27

## Fase actual

Fase 5 — Frontend y práctica conversacional.

## Último bloque cerrado
B137 — Ingesta y referencia resoluble de audio de producción.
- Commit técnico: `52cf574`.
- Endpoint multipart de WAV separado del envío JSON de producciones.
- Almacenamiento privado backend mediante `PRODUCTION_AUDIO_DIR`.
- Referencias opacas `production-audio://UUID`.
- Resolución interna disponible para futuros analizadores acústicos.
- 11 pruebas específicas B137 superadas.
- Suite backend completa: 368 passed.
- `git diff --check`: correcto.
- No existe todavía un analizador acústico real.

## Bloque activo
Ninguno.

B147 quedó técnicamente cerrado: sobre B140-B146, el backend puede describir de forma robusta la distribución de scores acústicos por etiqueta humana mediante Q25, mediana y Q75, manteniendo separados analizador, versión, rúbrica y etiqueta sin convertir percentiles en umbrales o decisiones pedagógicas. Suite completa: 480 passed. Commit técnico: `1bcdce1`. El corpus humano realmente representativo, la calibración pedagógica basada en evidencia y la comprensión semántica avanzada permanecen pendientes.

## Secuencia vigente de Fase 5

1. Presentación de producciones personales en Flutter — completada.
2. Reconocimiento de voz y palabras — completado con B126–B128.
3. Evaluación semántica y fonética gradual — capacidad actual.
4. Retroalimentación pedagógica adaptativa.
5. Conversación libre.
6. Consolidación y comprobación diferida de retención por Skill.

## Contratos vigentes

- `Skill`: habilidad pedagógica medible del estudiante.
- `LessonExperience 2.0`: contrato pedagógico público vigente.
- `EvidenceDefinition`: definición estática de evidencia.
- `LearnerProduction`: producción capturada, nunca evaluación.
- `LearnerProductionRecord`: producción persistida y trazable.
- `SpeechRecognitionResult`: reconocimiento técnico, no evaluación.
- `contextual_response`: actualmente evidencia por `completion`, no corrección.
- `EvidenceRecord`: diseñado documentalmente, todavía no implementado como schema/runtime.

## Fronteras arquitectónicas

- reconocimiento, evaluación, persistencia e IA permanecen separados;
- `Lesson` y `ConversationTurn` no deben absorber lógica evaluativa;
- una grabación no demuestra pronunciación correcta;
- una transcripción reconocida no demuestra corrección semántica;
- una conversación completada no demuestra fluidez;
- ninguna evaluación implica automáticamente mastery o retention;
- `content/candidates/` permanece aislado del contenido activo hasta aprobación explícita.

## Hueco confirmado para B129

La candidata `a1-u1-l1` tiene tres prompts personales en `c3`:

- `p1`: decir un nombre;
- `p2`: indicar origen;
- `p3`: responder cortésmente.

La misión contiene esos tres criterios como texto, pero actualmente no existe una relación estructurada y estable:
`prompt -> criterio evaluable`.

B129 resolverá esa trazabilidad antes de introducir motores de evaluación.

## Diseño aprobado para B129

Nuevo módulo previsto:
`app/schemas/evaluation.py`

Contrato estático previsto:
`ProductionEvaluationCriterion`

Responsabilidad:
definir qué se evalúa en una producción concreta.

Contrato runtime previsto:
`ProductionEvaluationResult`

Responsabilidad:
representar el resultado de evaluar una producción concreta sin convertirlo en dominio de Skill.

Invariantes previstos:
- referencia explícita a producción/criterio/evidencia;
- compatibilidad con conversación y prompt;
- modalidades compatibles;
- evaluación fonética solo sobre voz;
- score normalizado cuando corresponda;
- sin duplicar `skill_ids`;
- sin modificar `LearnerProduction`;
- sin mastery, retention ni feedback.

## Decisión sobre EvidenceDefinition

`EvidenceDefinition.success_threshold` es el contrato real vigente:
- obligatorio para `measurement_mode=score`;
- rango `0.0–1.0`;
- prohibido para otros modos.

La antigua referencia documental a `success_condition` fue corregida durante B129 y todavía está pendiente de versionar.

## Archivos clave para B129

Backend:
- `app/schemas/evaluation.py` — nuevo, todavía no creado;
- `app/schemas/content.py`;
- `app/schemas/conversation_production.py`;
- `app/schemas/pedagogical_unit.py`;
- `tests/` — pruebas específicas de B129;
- `docs/lesson-experience-contract.md`;
- `docs/estado-operativo.md`;
- `docs/bitacora.md`;
- `docs/roadmap.md`.

Frontend:
- B128 ya cerrado; no modificar durante el contrato inicial de B129 salvo necesidad demostrada.

## Método operativo desde B129

Al iniciar o retomar un bloque:
1. leer este archivo;
2. inspección agrupada solo si falta información real;
3. diseñar el incremento;
4. construir;
5. prueba específica;
6. integración;
7. suite completa una sola vez al cierre;
8. actualizar documentación y este estado;
9. commit, push y Git limpio.

Si hacen falta varias inspecciones consecutivas sin producir cambio técnico, detener el bloque y revisar el método antes de continuar.

## Resultado técnico B129

- contratos de criterio, resultado y plan evaluativo implementados;
- validación contextual y runtime integrada;
- candidata piloto con tres criterios semánticos trazables;
- pipeline pedagógico integrado;
- 27 pruebas específicas superadas;
- 292 pruebas backend superadas;
- candidata no publicada;
- motor semántico/fonético real todavía pendiente.

## Resultado técnico B130
- `SemanticEvaluationRule` separa reglas pedagógicas del motor.
- `evaluate_semantic_production` ejecuta una regla explícita.
- `evaluate_semantic_production_from_plan` resuelve criterio y regla desde el plan.
- `evaluate_candidate_semantic_production` orquesta candidata → lección → plan → producción → resultado.
- La candidata A1-U1-L1 declara reglas para nombre, procedencia y respuesta cortés.
- 19 pruebas específicas B130 superadas.
- Suite completa backend: 311 passed.

## Resultado técnico B131
- Evaluación y producción permanecen separadas.
- `production_evaluation_results` conserva resultados trazables por `production_id`.
- El historial evaluativo admite múltiples evaluadores/versiones sin sobrescritura.
- B130 y B131 forman el flujo producción → evaluación → persistencia.
- Alembic 1.18.5 pasa a ser el mecanismo oficial de evolución del esquema.
- Baseline histórico: `b1fe71209621`.
- Migración de resultados evaluativos: `98ff29894521`.
- 321 pruebas backend superadas.

## Migraciones desde B131
Todo cambio futuro de esquema debe implementarse mediante una revisión Alembic versionada. No usar `Base.metadata.create_all()` para evolucionar una base existente.

## Resultado técnico B132
- `ProductionFeedbackRule` declara feedback pedagógico fuera del generador.
- `ProductionFeedback` conserva trazabilidad al resultado evaluativo.
- `LessonProductionFeedbackPlan` agrupa reglas por lección.
- `PedagogicalUnitCandidate.feedback_plans` integra el feedback de forma aditiva.
- La candidata A1-U1-L1 contiene reglas para nombre, procedencia y cortesía.
- La integridad feedback → evaluación → criterio se valida antes del runtime.
- 13 pruebas específicas B132 superadas.
- Suite backend completa: 334 passed.

## Resultado técnico B133
- `production_feedbacks` persiste el feedback realmente generado.
- La evaluación permanece como fuente de verdad para producción, criterio y estado.
- El historial de feedback es append-only.
- B132 y B133 forman el flujo generar feedback → persistir feedback.
- Migración: `f81a78f8c1c4`.
- 8 pruebas específicas B133 superadas.
- Suite backend completa: 342 passed.

## Resultado técnico B134
- `ProductionEvaluationOutcome` representa el resultado conjunto.
- `evaluate_production_atomically` centraliza B130-B133.
- Evaluación y feedback participan en una única transacción.
- Un fallo parcial provoca rollback completo del trabajo evaluativo.
- La producción previamente persistida permanece intacta.
- 3 pruebas específicas B134 superadas.
- Suite backend completa: 345 passed.

## Resultado técnico B135
- `ProductionEvaluationRuntimeConfig` es la nueva frontera neutral de runtime.
- El adaptador desde candidata queda separado del pipeline.
- `evaluate_production_atomically` ya no conoce `PedagogicalUnitCandidate`.
- Una futura fuente de contenido activo podrá proporcionar la misma configuración.
- La prueba de rollback vuelve a demostrar atomicidad real dentro del pipeline.
- 349 pruebas backend superadas.

## Resultado técnico B136
- `PhoneticEvaluationEvidence` representa evidencia acústica normalizada y trazable.
- Producción, evidencia acústica y resultado evaluativo permanecen separados.
- El evaluador fonético verifica producción, criterio y audio antes de aplicar el umbral.
- La salida utiliza el contrato y persistencia evaluativa existentes.
- El transcript reconocido no se interpreta como calidad fonética.
- El análisis acústico real permanece pendiente.
- 357 pruebas backend superadas.

## Resultado técnico B137
- El backend puede recibir WAV mediante multipart y almacenarlos de forma privada.
- `audio_reference` puede ser ahora una referencia opaca administrada por backend.
- Las rutas físicas permanecen ocultas al cliente y a la capa pedagógica.
- `PRODUCTION_AUDIO_DIR` es obligatorio para la ingesta runtime.
- La lectura de bytes queda disponible para futuros analizadores acústicos.
- PostgreSQL continúa almacenando únicamente la referencia, no el binario.
- El contrato JSON previo de producciones permanece intacto.
- No hay todavía medición real de pronunciación.
- 368 pruebas backend superadas.


## Resultado técnico B138
- Se compararon dos enfoques acústicos reales en Ubuntu y CPU.
- `facebook/wav2vec2-lv-60-espeak-cv-ft` produjo observación fonémica y logits CTC, con inferencia aproximada de 0.30 s sobre un WAV de 1.91 s una vez cacheado.
- La pérdida CTC global fue descartada como scorer de pronunciación: en el control `John`/`Joan` no discriminó consistentemente ambas hipótesis.
- Se validó como candidato técnico `Jianshu001/wavlm-phoneme-scorer`, cuya arquitectura combina G2P, alineación CTC, WavLM, GOP y scoring por fonema.
- El checkpoint `wavlm_finetuned.pt` quedó identificado por SHA-256 `7b9485b679d9a1219ac7dbef197b5185ec16e7909632b082b1f0576a963e0040`.
- El checkpoint pudo cargarse con `weights_only=True` usando una allowlist mínima de tipos NumPy; no se aceptó la carga original con `weights_only=False`.
- En el audio control `Hello, I am John.`, el scorer produjo 88.4/100 global y 92.9/100 para `John`.
- Al mantener el objetivo `John` pero usar audio `Joan`, el score de la palabra cayó a 71.1/100 y el fonema objetivo `/aa/` cayó de 83.2 a 19.9 con `pherr=0.95`, localizando el cambio acústico.
- `/hh/` de `Hello` fue marcado como error en ambas muestras, por lo que los scores y umbrales todavía no están calibrados pedagógicamente.
- Las muestras usadas son sintéticas con eSpeak; B138 demuestra viabilidad técnica, no validez pedagógica sobre voces humanas.
- No se modificó código runtime, esquema de base de datos, candidata pedagógica ni contenido activo.

## Resultado técnico B139
- `PhoneticAnalyzer` establece una frontera neutral entre runtime y motor acústico.
- La evaluación fonética desde plan convive con la evaluación semántica dentro del pipeline atómico.
- `AcousticPhoneticMeasurement` separa la medición técnica de `PhoneticEvaluationEvidence`.
- `ProductionAudioPhoneticAnalyzer` resuelve referencias privadas B137 antes de invocar el scorer.
- `CommandAcousticPhoneticScorer` ejecuta el motor aislado sin `shell=True`, con timeout, código de salida y JSON controlados.
- `wavlm_gop_runner.py` adapta el resultado WavLM/GOP de escala 0-100 al contrato normalizado 0.0-1.0.
- El runner verifica SHA-256 tanto del pipeline acústico como del checkpoint antes de ejecutar el modelo.
- La configuración runtime usa variables `PHONETIC_ANALYZER_*`; no existen rutas experimentales `/tmp` hardcodeadas en el backend.
- Torch, TorchAudio, WavLM y sus modelos permanecen fuera de `.venv` del backend.
- Smoke test real B137 → runtime B139 → WavLM/GOP → B136 produjo score 0.884 para la muestra controlada.
- Pipeline SHA-256 validado: `e09e2403e9f75fa23bfed65cc5e8e7fe90872328e0b351753e08a94a78437909`.
- Checkpoint SHA-256 validado: `7b9485b679d9a1219ac7dbef197b5185ec16e7909632b082b1f0576a963e0040`.
- 21 pruebas nuevas respecto a B138.
- Suite backend completa: 389 passed.
- Commit técnico: `f692f0f`.
- B139 no calibra todavía los scores con voces humanas, no introduce feedback fonético pedagógico, mastery ni retention.

## Resultado técnico B140
- Se definieron contratos separados para muestras, mediciones y observaciones de calibración fonética.
- `unlabeled` preserva la separación entre medición acústica y juicio pedagógico.
- Los manifiestos se validan antes de ejecutar el scorer y cada WAV se verifica mediante SHA-256.
- El mismo `CommandAcousticPhoneticScorer` configurable y verificable de B139 puede reutilizarse directamente para corpus de calibración.
- El runtime pesado persistente permanece fuera de `.venv` y reprodujo la ejecución humana previamente obtenida.
- El corpus inicial controlado contiene cuatro repeticiones válidas del mismo hablante y misma frase; scores técnicos: 0.574, 0.582, 0.626 y 0.606.
- Audio humano, manifiesto local, configuración runtime y mediciones locales están excluidos de Git.
- Validación específica: 20 passed.
- Suite backend completa: 407 passed.
- `git diff --check`: correcto.
- Commit técnico: `77ce27e`.
- B140 todavía no establece calidad de pronunciación, umbrales pedagógicos, feedback fonético, mastery ni retention.

## B148 — Solapamiento descriptivo entre distribuciones humanas

Estado: implementación técnica cerrada y validada.

Se incorporó la descripción del solapamiento IQR Q25–Q75 entre pares de etiquetas humanas compatibles dentro del mismo `analyzer_id + analyzer_version + rubric_version`.

Cadena vigente:
`audio humano → medición acústica técnica → etiqueta humana independiente → acuerdo humano descriptivo → relación técnica-humana → resúmenes descriptivos → distribución por etiqueta → distribución robusta → solapamiento IQR descriptivo`

Separación obligatoria:
`score técnico ≠ juicio humano ≠ decisión pedagógica`

B148 no introduce verdad, mayoría automática, umbrales, clasificación, feedback pedagógico, mastery ni retention.

Validación técnica:
- B148 específico: 11 passed.
- Regresión B142–B148: 63 passed.
- Suite backend completa: 491 passed.
- `git diff --check`: limpio.
- Commit técnico: `4d7821e`.

## B149 — Informe descriptivo consolidado de calibración modelo-humano

Estado: implementación técnica cerrada y validada.

Se incorporó `PhoneticCalibrationDescriptiveReport`, que consolida por `analyzer_id + analyzer_version + rubric_version` el resumen modelo-humano, las distribuciones robustas por etiqueta y los solapamientos IQR descriptivos.

El contrato y el servicio preservan estrictamente el contexto versionado y no mezclan evidencia incompatible.

Cadena vigente:
`audio humano → medición acústica técnica → etiqueta humana independiente → acuerdo humano descriptivo → relación técnica-humana → resúmenes descriptivos → distribución por etiqueta → distribución robusta → solapamiento IQR descriptivo → informe descriptivo consolidado`

Separación obligatoria:
`score técnico ≠ juicio humano ≠ decisión pedagógica`

B149 no introduce verdad, separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación técnica:
- B149 específico: 7 passed.
- Regresión B142–B149: 70 passed.
- Suite backend completa: 498 passed.
- `git diff --check`: limpio.
- Commit técnico: `e91a011`.
