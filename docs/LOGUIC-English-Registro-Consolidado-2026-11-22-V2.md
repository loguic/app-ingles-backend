# LOGUIC English — Registro consolidado de continuidad y evidencias · 2026-11-22

**Versión:** RECUPERACIÓN V2 · **Estado:** PROPUESTA DOCUMENTAL / NO CANÓNICA / SIN COMMIT.  
**Ámbito:** LOGUIC English, FE y BE.  
**Regla de integridad:** distingue *observado*, *implementado*, *probado*, *publicado* y *pendiente*. No sustituye las autoridades del repositorio hasta ser reconciliado y aprobado. 

## 1. Para qué se redacta ahora

Evitar la pérdida de contexto ocurrida al cambiar de conversación. Reconstruir las pruebas del 21 de noviembre, los avances posteriores del 22 y la situación de A1 v4 sin repetir pruebas, alterar recursos ni introducir nuevas implementaciones. Documentar **antes** de continuar, sin afirmar cierres no demostrados.

## 2. Estado de autoridad y Git observado

| Área | Evidencia observada | Interpretación precisa |
|---|---|---|
| BE | `conversation_checkpoint.py resume --format compact`: `PASS`, `HEAD=fb9b0a9a09510a206c8cd8d67919f44b90d18e63`, `master`, `origin/master`, `AHEAD=0`, `BEHIND=0`, `TREE=CLEAN` | Estado BE al momento de la salida proporcionada el 22/11; no afirma que la semántica `NEXT` esté actualizada. |
| F0 | Plan Operativo Maestro Integral F0–F8 aprobado y cierre Git BE publicado | El texto del checkpoint aún contiene `CHECKPOINT_PENDING` y referencias `NEXT` históricas: reconciliar sin borrar evidencia. |
| FE ISSUE_2 | `c431c3534f34307726ecdf3f4e77da15541befbd` publicado por `git_close.py` en `origin/master` | Cierre Git aislado del defecto de sesiones de audio, **no** aprobación integral de Estación. |
| FE A1 v4 | Tres rutas locales, restauradas y verificadas byte a byte tras publicar ISSUE_2 | Se preservaron deliberadamente, no forman parte del commit ISSUE_2. |
| Currículo | MB1 = `DRAFT / NOT ACTIVE` | Prohibido inferir admisión, activación o publicación curricular. |

## 3. Niveles y prueba oral con IA · 21/11/2026

**Ruta de producto que se estaba explorando:** `FE Niveles → A1 / ejercicio oral → micrófono → Moonshine STT → BE FastAPI → Ollama/Qwen Windows → feedback en Flutter`.

- **Respuesta oral recordada y corregida por el usuario:** «kneed water». Esto **no** es una prueba acústica externa ni equivale por defecto al texto STT.
- **Transcripción automática observada en un registro:** `I knee the water`. No atribuir esta forma exacta a la voz del usuario.
- **Objetivo pedagógico:** `I need water`.
- **Primera prueba:** Flutter devolvió `Feedback is not available right now`.
- **Prueba posterior:** Qwen produjo la indicación `You meant ‘I need water’. Say that next.`; Flutter podía mostrar simultáneamente `Great job!`. Se identificó **incoherencia en la presentación pedagógica**.
- **Decisión posterior:** corregir la continuidad del feedback y ofrecer ayuda de pronunciación respetando el momento pedagógico. No extrapolar esa intención a funcionalidad aprobada en pantalla sin evidencia.
- **Implementación local FE posterior:** cambios en `a1_v4_visible_demo_screen.dart` y su prueba, con referencia histórica a **6 tests PASS**, `flutter analyze PASS` y `git diff --check PASS`. Esas validaciones se hicieron antes de la presente captura; no se han repetido aquí.

### Infraestructura existente — no reinstalar ni revalidar sin motivo

| Servicio | Ubicación documentada | Función |
|---|---|---|
| Flutter | Ubuntu 24.04 en VMware | UI y captura de voz |
| Sherpa-ONNX Moonshine | Ubuntu VMware | STT: transcripción de audio, **no** juicio fonético validado |
| FastAPI | Ubuntu, `127.0.0.1:8001` | Orquestación del ejercicio y evaluación |
| Ollama | Windows 11 anfitrión, observado desde Ubuntu en `192.168.181.1:11434` | Modelos de evaluación y construcción |
| `qwen3:4b-instruct` | Ollama Windows | Modelo anotado para evaluación oral en runbook del 21/11 |
| `qwen3:8b` | Ollama Windows | Constructor pedagógico y otras verificaciones históricas |

La IP procede de una observación de red VMware, **no** debe tratarse como configuración permanente. La ejecución de evaluación con Qwen no prueba que exista evaluación fonética GOP/WavLM en el ejercicio FE.

## 4. Niveles — evidencia FE ↔ BE del 22/11

La salida explícita del usuario confirmó:

```text
GET http://127.0.0.1:8001/api/v1/levels
HTTP_STATUS=200
{"levels":["A1","A2","B1","B2","C1","C2"]}
```

El selector y la navegación por nivel/unidad/lección existen históricamente en Flutter. **HTTP 200 no demuestra** por sí solo un recorrido completo desde Niveles hasta una evaluación del estudiante. Tampoco añade `Pre-A1` al contrato ni activa MB1.

## 5. FE — A1 v4: evidencia fresca suministrada hoy

**Comando ejecutado:** inspección read-only de `git status --short`, `git diff --stat` y contenido de `docs/a1-v4-continuidad-pedagogica-pendientes.md`.

```text
 M lib/screens/a1_v4_visible_demo_screen.dart
 M test/a1_v4_visible_demo_screen_test.dart
?? docs/a1-v4-continuidad-pedagogica-pendientes.md

lib/screens/a1_v4_visible_demo_screen.dart | 131 ++++++++++++++++++++++--------------------------------
test/a1_v4_visible_demo_screen_test.dart   |  76 ++++++++++++++++++++++++++++++-
2 files changed, 128 insertions(+), 79 deletions(-)
```

El documento FE **ya existe** y declara literalmente: `Estado: implementación local pendiente de revisión humana. A1 v4 no está pedagógicamente completa.`

Según ese documento:

- La pantalla **reutiliza grabación, transcripción disponible, evaluación semántica y audio británico aprobado de «I need water»**.
- La referencia se ofrece **después de la primera escucha y la evaluación**, no antes; se preserva el enfoque audio-first.
- El feedback conversacional se presenta como **orientación pedagógica**, **no** como corrección gramatical estructurada.
- La referencia de voz **no** constituye prueba de evaluación de pronunciación.

**Pendientes explícitos del documento FE:**

1. **IPA y explicaciones para hispanohablantes:** determinar recurso aprobado por objetivo y momento de revelación; IPA curricular no equivale a aprobación de uso FE.
2. **Audio lento:** reproducción validada o adaptación autorizada del controlador y plataformas.
3. **GOP/WavLM:** integración autorizada audio + referencia + contratos fonéticos; interpretar, validar y manejar disponibilidad. El contrato actual de evaluación del turno hablado **no devuelve** esa evidencia.
4. **Corrección gramatical estructurada:** evidencia o campos específicos distintos del feedback conversacional general.
5. **Revisión humana:** diseño, accesibilidad, secuencia audio-first y decisiones adaptativas de cuatro etapas antes del cierre.

**Límite de observación:** se vio `git diff --stat`, **no el diff completo**. Por eso el alcance interno de las 131/76 líneas modificadas requiere lectura focal antes de declarar que toda la implementación cumple el documento.

## 6. ISSUE_2 V3 — sesiones de reproducción FE

La especificación previa compartida por el usuario tenía estado `DRAFT`, sin autorización inicial de commits ni cambios BE/Ollama/Sherpa/A1 v4. Definía sesiones independientes por reproducción (`AudioPlayer`, identificador, suscripciones y validez), protección de `onPlayerComplete`, cancelación inmediata y concurrencia segura.

**Evolución posterior verificada:** se implementó, se probaron condiciones de concurrencia/interrupción y se obtuvo postflight focalizado PASS. El cierre Git FE se completó en `c431c3534f34307726ecdf3f4e77da15541befbd` para exactamente cuatro rutas:

```text
lib/services/pronunciation_audio_service.dart
test/pronunciation_audio_event_order_test.dart
lib/screens/station_journey_screen.dart
test/station_journey_screen_test.dart
```

La salida del usuario dio `FE_SCOPE_PRECHECK_PASS`, `Git close completed: c431c353...`, `A1_V4_RESTORED_PASS` e `ISSUE2_GIT_PUBLISHED_A1_PRESERVED_PASS`. Los tres archivos A1 fueron contrastados por SHA-256 y recuperados. Respaldo local observado: `~/Downloads/LOGUIC-ISSUE2-A1V4-20261122-015429`.

**Distinción:** el helper comprobó limpieza/sincronía para publicar ISSUE_2 y **después** se restauró A1 v4, quedando FE deliberadamente con cambios locales. No repetir postflight de audio sin causa técnica nueva.

## 7. Diseño y Estación: no rehacer aprobaciones

- Skill UI/UX repo-local `frontend/.agents/skills/loguic-uiux-design-review/SKILL.md` aprobada el **16/11/2026**.
- Estación escritorio: revisión humana aprobada el **17/11/2026**, ajuste FE publicado `2c100be...`, ocho pruebas focales PASS.
- Ventana estrecha **~850 px**, aprobada para ese tamaño el **19/11/2026**; documentación FE publicada `1094812...`.
- Las aprobaciones se limitan a los alcances revisados. No constituyen aceptación integral de WCAG AA, ventanas menores o recorrido E2E.
- En vez de repetir capturas, preservar la evidencia y verificar solo brechas nuevas al retomar ese hito.

## 8. Estado del producto y límites de cierre

| Trabajo | Estado sostenible |
|---|---|
| F0, plan operativo maestro | Aprobado / publicado en BE. `NEXT` semántico histórico requiere reconciliación. |
| ISSUE_2 V3 | Implementación + postflight focalizado + Git publicado/sincronizado. |
| A1 v4, cambios pedagógicos posteriores | **IMPLEMENTED LOCAL / TESTS PREVIOS PASS / HUMAN REVIEW PENDING / NOT PUBLISHED**. |
| Niveles BE | Endpoint HTTP 200, A1–C2. |
| Prueba oral STT + Qwen | Ejecución anterior observada; feedback contradictorio detectado, cambios FE posteriores. |
| Evaluación de pronunciación GOP/WavLM **en este ejercicio** | **NO ACREDITADA**. No presentar STT ni Qwen como medidor de pronunciación. |
| Ayuda gramatical estructurada **en este ejercicio** | **NO ACREDITADA**; solo orientación conversacional registrada. |
| MB1 | **DRAFT / NOT ACTIVE**. |
| MVP integral | **NOT CLOSED / NO MEDIBLE**; no inferir aprobación del alumno. |

## 9. Reglas de continuidad y siguiente paso documental

**Reglas:** no repetir audio ni Ollama; un paso por turno; instrucciones rotuladas BE/FE + TERMINAL/CODEX; sin `rg`, heredocs ni Codex para tareas deterministas; conservar archivos locales, no mezclar scopes ni publicar sin autorización explícita; resumir en cada cierre hechos, evidencia, diferencias y NEXT.

**Siguiente paso correcto (DOCUMENTACIÓN):** cotejar este registro con los `docs/estado-operativo.md`, `docs/bitacora.md` y `docs/roadmap.md` actuales de BE, y con `docs/bitacora-frontend.md` + `docs/a1-v4-continuidad-pedagogica-pendientes.md` de FE. Incorporar el avance del 21–22/11 como **anotaciones históricas de evidencia y estado**, sin borrar contenidos ni atribuir cierres ficticios. Antes de cualquier commit: revisión humana, validación documental y control explícito de alcance. Este documento **no se ha escrito dentro de la VM ni publicado por Git**.

**Siguiente paso de producto después de documentar:** revisar solo el diff FE de A1 v4 preservado, decidir su aceptación y cierre; luego comprobar el recorrido real `Niveles → A1 → ejercicio oral → feedback`, sin inventar integración fonética o gramatical estructurada.

## 10. Procedencia

1. Resultados de `conversation_checkpoint.py resume` y `GET /api/v1/levels` pegados por el usuario el 22/11.
2. Salida FE `git status`, `git diff --stat` y texto íntegro del documento `a1-v4-continuidad-pedagogica-pendientes.md` compartidos el 22/11.
3. Log de cierre ISSUE_2: `git_close.py` commit `c431c353...`, stash restaurado y hashes SHA-256 PASS.
4. Documento histórico `LOGUIC-English-Ollama-Windows-VMware-Runbook-2026-11-21.md` y otros fragmentos recuperados del proyecto.
5. Corrección explícita del usuario sobre su respuesta «kneed water», diferenciada de la transcripción automática `I knee the water`.

> **Advertencia de autoridad:** este informe reúne evidencias disponibles, no inspecciona en vivo los repositorios del usuario, no valida retrospectivamente cada test, ni autoriza activación curricular, cambios de código, publicación o cierre del MVP.
