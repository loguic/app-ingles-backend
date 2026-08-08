# Estado operativo — LOGUIC English

Actualizado: 2026-08-08
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Documento rector: `docs/modelo-pedagogico-maestro.md`.
- Horizonte pedagógico: 3 meses como meta y 6 meses como máximo.
- Todo bloque nuevo debe partir de una capacidad observable del estudiante.
- `Skill` significa exclusivamente habilidad pedagógica medible.

## Bloques cerrados recientes

### B179 — Diagnóstico conversacional persistente y consultable

Estado: cerrado técnica e integralmente.

Hito A — modelos persistentes y migración Alembic: cerrado.

Hito S1 — contrato ejecutable de seguridad DevSecOps: cerrado.

Hito S2 — adaptador PostgreSQL seguro: cerrado mediante integración aislada ejecutada en Kitty.

Hito B — persistencia transaccional e historial consultable: cerrado.

Capacidades completadas:

- persistencia de las siete entidades diagnósticas principales;
- propiedad exclusiva actividad–producción;
- coincidencia relacional de sesión, actividad, `prompt_id` y producción;
- observaciones transaccionales y enlaces normalizados con evaluaciones técnicas inmutables;
- perfiles iniciales append-only, evidencias y su historial interno estructurado y ordenado;
- máquina de estados explícita y concurrentemente segura, sin reapertura ni historial de transiciones;
- producción obligatoria para las ocho dimensiones dependientes;
- revisión Alembic `3c4f1a2b7d90` con `upgrade` y `downgrade` validados aisladamente.
- puerta preventiva fail-closed con entorno e identidad explícitos;
- evidencias verificables de backup, restauración, ensayo y rollback;
- producción rechazada incondicionalmente en S1.
- clúster PostgreSQL temporal por socket Unix bajo `/tmp`, sin servicio del sistema, puerto `5432` ni `DATABASE_URL` real;
- backup, SHA-256, restauración separada, verificación determinista y ensayo Alembic reversible;
- limpieza protegida por workspace administrado y marcador.
- round-trip de sesión, contexto, actividades, propiedad actividad–producción y apoyos;
- enriquecimiento atómico sobre producciones preexistentes, sin sobrescritura ni idempotencia implícita.

Validación final directa en Kitty:

- pruebas específicas: 14 passed in 1.13s;
- regresión relacionada: 7 passed in 0.31s;
- suite backend: 937 passed in 2.91s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión final de Codex: sin defectos accionables;
- commit técnico: `40a30b3`.

Validación de S1:

- pruebas específicas: 17 passed;
- regresión de ingeniería: 27 passed;
- suite backend: 954 passed in 2.89s;
- revisión de Codex: sin defectos accionables;
- `operational_state.py validate` y `git diff --check`: correctos;
- commit técnico: `0472093`.

Validación de S2:

- integración real aislada: 1 passed in 2.47s; código 0;
- suite backend: 967 passed in 5.56s;
- sin procesos, sockets ni clústeres temporales residuales;
- URL Alembic explícita `postgresql+psycopg://`;
- Codex preparó y revisó; Kitty conservó la observabilidad de la integración;
- `operational_state.py validate` y `git diff --check`: correctos;
- commit técnico: `d0efe1e`.

Validación del primer incremento de Hito B: 16 específicas, 190 de regresión, suite backend 983 passed in 5.55s, revisión sin defectos y commit `56a3d42`.
Validación del segundo incremento: 41 específicas en 0.72 s, 190 de regresión en 1.29 s, suite backend 1008 passed in 5.60s, revisión sin defectos y commit `719aa74`.
Validación del tercero: 69 específicas, suite backend 1036 passed; 4A: suite backend 1066 passed in 6.66s, commit `94a620e`; 4B: 309 relacionadas en 3.17s, marcador `B179_HITO_B_INCREMENTO_4B_VALIDATED`, commit `c9e3bab`; revisiones sin defectos.

Validación integral directa en Kitty: suite backend 1086 passed in 6.93s; `operational_state.py validate` correcto; `git diff --check` limpio; Git sincronizado `master...origin/master`; marcador `B179_INTEGRAL_VALIDATED`.

Límites vigentes:

- sin API ni Flutter;
- sin progreso, mastery, retención, adaptación automática ni historial de transiciones;
- S2 no autoriza migraciones en desarrollo, staging o producción reales.

## Último bloque cerrado

### B180 — Construcción directa en inglés

Estado: cerrado técnica e integralmente; Incrementos 1, 2, 3 y 4 cerrados y publicados.
Capacidad observable: construir oralmente una respuesta desde una intención, ampliarla con información pertinente y transferir el patrón ante una variación inesperada con ayuda mínima, sin copiar una frase completa.
`a1-u1-l1` conserva su identificador y pasa a `Introduce yourself directly`, con la Skill `a1_introduce_yourself`, patrón Persona + Verbo y cinco etapas: modelo con refuerzo fonético, construcción guiada, ampliación, transferencia y cierre. Las evidencias `guided`, `expanded` y `transfer` retiran apoyo de `anchors` a `initial_word` y `none`; voz es principal y texto, respaldo.
La corrección admite como máximo una orientación y prioriza pertinencia, construcción directa, inteligibilidad y precisión secundaria. El refuerzo reutiliza audio e IPA regionales para escucha, ritmo, shadowing y `/iː/`; no constituye evidencia independiente.
Validación: suite backend 1104 passed in 9.20s; `operational_state.py validate` correcto; `git diff --check` limpio; revisión sin defectos accionables; commit `ccafaaa`.

El Incremento 2 añade intentos completos append-only, selección SHA-256 reproducible y snapshot de banco, variante, prompt y `sha256-v1`. `LearnerProduction` sigue siendo la producción real y aporta `modality`; el enlace separa apoyo configurado y usado. `start`, `finalize` y `get` comparten una transacción sin commits parciales. `completion_requirements_met` se calcula: solo confirma las tres funciones con voz y retirada estructural; `false` no implica fracaso, progreso ni mastery.
La revisión `7d8e9f0a1b2c` fue validada en PostgreSQL `3c4f1a2b7d90 → 7d8e9f0a1b2c → 3c4f1a2b7d90` y mediante S2 completo desde `f81a78f8c1c4` al head y vuelta. S2 conserva esa frontera histórica, resuelve un único head antes de crear recursos, rechaza grafos o revisiones incompatibles y congela hashes concretos. Validación: 34 específicas; 148 relacionadas y 1 omitida; suite backend 1149 passed in 9.59s; commit `f77f560`.
El Incremento 3 añade una orientación append-only opcional por producción B180, enlazada solo a `DirectEnglishConstructionAttemptProduction`. Conserva prioridad, guidance exacta (máximo 2000), fuente `human|external` y trazabilidad, sin modificar intento o producción ni reutilizar feedback evaluativo. El backend valida la prioridad contra la política activa, pero no la selecciona ni la declara verdadera.
La revisión `a4c8e2f6b901` es el nuevo head. PostgreSQL focal validó `7d8e9f0a1b2c → a4c8e2f6b901 → 7d8e9f0a1b2c` en 2.48s; S2 completo validó desde y hacia `f81a78f8c1c4` en 2.38s. Suite backend: 1171 passed in 10.30s; commit `2f396d3`.
El Incremento 4 añade `prepare_direct_english_construction_retry`, una lectura que recupera el intento finalizado, la producción y orientación exactas y prepara menor apoyo sin escribir ni afirmar mejora. Retira un peldaño desde el apoyo usado y nunca supera el configurado; transfer queda en `none` y conserva su contexto previo, mientras el nuevo intento aplicará el selector existente con un `attempt_id` nuevo. Suite backend: 1191 passed in 10.33s; commit `70c3dbf`.
El ciclo interno `contenido → producción → orientación → reintento con menor apoyo` satisface la capacidad comprometida. B180 queda cerrado sin Incremento 5; trazabilidad técnica: `ccafaaa`, `f77f560`, `2f396d3` y `70c3dbf`. Validación final: suite backend 1191 passed in 10.33s, migraciones PostgreSQL focales y S2 completo correctos, head `a4c8e2f6b901`, estado operativo válido y diff limpio.

## Deuda operativa separada

El cierre mediante `block_workflow.py` no terminó correctamente. La herramienta puede perder la salida final o dejar procesos hijos al interrumpirse; esta deuda permanece separada de B179.

## Automatización disponible

- `operational_state.py` valida y resume este checkpoint.
- `block_close.py` ejecuta validaciones técnicas y staging controlado.
- `block_workflow.py` requiere resolver la deuda de interrupción antes de considerarse fiable para cierres desatendidos.

## Método operativo vigente

Cada hito pasa por definición, implementación técnica, validación específica, regresión relacionada, suite completa y cierre documental. Los commits y la publicación permanecen bajo confirmación humana.

## Fronteras obligatorias

- producción ≠ evaluación técnica;
- evaluación técnica ≠ observación diagnóstica;
- observación diagnóstica ≠ decisión pedagógica;
- perfil inicial ≠ progreso;
- progreso ≠ mastery.

## Bloque activo
B181 — Comprensión contingente y continuidad conversacional breve. El Incremento 1, cerrado y publicado, define `a1-u1-l2`, `Keep the conversation going`, como conversación audio-first de siete turnos, tres respuestas por voz, apoyo `anchors → initial_word → none`, seguimiento inesperado y cierre natural; trazabilidad: backend `c246876`, checkpoint `2c7fa20` y audios frontend `8235449`. El Incremento 2 está cerrado técnica, documental y operativamente: Flutter ejecuta el flujo audio-first, conserva y sube tres WAV y envía una única `ConversationProductionSubmission`, reutilizando el backend sin cambios; commits frontend publicados `8baf7a6` y `4fe98ad`. B181 permanece abierto y no está cerrado integralmente.

## Próximo objetivo
Ya existen tres producciones reales persistidas tras recorrer la conversación con transcript contingente y apoyo decreciente. La brecha observable restante es realizar y registrar separadamente la revisión efectiva de `intention_understanding` y `contingent_response` sobre esas producciones. Producción persistida, reconocimiento técnico y finalización no demuestran comprensión, pertinencia, aprendizaje, progreso, mastery ni fluidez; no se prescribe todavía solución, infraestructura ni otro incremento.

El Karaoke Fonético queda pospuesto, no descartado, como capacidad aislada posterior; B181 tampoco implementa sincronización, timestamps, colores, dictado, grabación guiada ni UI específica.

Toda futura aplicación sobre entornos reales requerirá una autorización y controles adicionales fuera de S2.

## Archivos clave

- `docs/estado-operativo.md`;
- `docs/modelo-pedagogico-maestro.md`, `docs/conversational-diagnostic-contract.md`, `docs/devsecops-gate.md`, `docs/roadmap.md` y `docs/bitacora.md`.
