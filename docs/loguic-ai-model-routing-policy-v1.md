# LOGUIC AI Model Routing Policy v1.1 — Astra Extension

Estado: v1.1 vigente, cerrada, publicada y sincronizada. Se conserva la ruta `docs/loguic-ai-model-routing-policy-v1.md` para mantener una única autoridad y sus referencias existentes; Git conserva la v1 histórica.

## 1. Propósito

Seleccionar de forma objetiva y reproducible la herramienta o el modelo mínimo fiable para cada tarea de ingeniería LOGUIC.

Objetivos simultáneos:

- preservar calidad;
- evitar consumo innecesario de cuota;
- reservar modelos superiores para tareas que realmente los necesiten;
- hacer explícitas y auditables las decisiones de routing;
- preparar la futura integración con IA local y LOGUIC OS.

## 2. Alcance

Esta es una política transversal de ingeniería LOGUIC. Este repositorio alberga la política como piloto operativo y versionado; la extensión v1.1 incorpora GPT-6 Astra como nivel superior excepcional. No es una regla específica del dominio App Inglés.

No es un contrato pedagógico, no pertenece al contrato curricular y no define comportamiento del estudiante.

Regula únicamente:

- selección de herramientas;
- selección de modelos de IA;
- reasoning effort;
- escalamiento y degradación operacionales.

No define currículo, `Skill`, prerrequisitos, evaluación del estudiante, mastery ni decisiones pedagógicas.

En LOGUIC, `Skill` significa exclusivamente una habilidad pedagógica medible del estudiante. Esta política no usa ese término para capacidades de IA, agentes o herramientas.

## 3. Principio rector

Primero preguntar: ¿la tarea necesita IA?

Si una herramienta determinista puede resolverla correctamente, se usará herramienta o Bash. Solo si la IA aporta razonamiento o transformación útil se seleccionará un modelo.

> Usar el modelo menos costoso que pueda resolver de forma fiable la tarea actual.

Si el riesgo o la ambigüedad son altos, se escala antes de ejecutar.

La selección ocurre por tarea, no por conversación, sesión, slice completa ni por el modelo usado anteriormente.

## 4. Bandas base y orden operativo v1.1

Las bandas base de scoring se preservan de v1 y se definen en la sección 5: `0–3 Luna / 4–7 Terra / 8–10 Sol`. Son una recomendación inicial, no una jerarquía completa ni una cuarta banda para Astra.

El orden operativo completo es:

1. herramientas deterministas o Bash cuando bastan;
2. Luna;
3. Terra;
4. Sol;
5. Astra únicamente como override de la sección 10.1.

Astra está por encima de Sol como override excepcional, fuera de las bandas numéricas. No se activa por 10/10 ni exige recorrer todos los modelos antes de seleccionarlo. `Terra / medium` sigue siendo el default operativo.

La futura IA local, cuando forme parte operativa, se situará después de herramientas deterministas/Bash y antes de Luna. No altera las bandas base ni el override Astra.

## 5. Scoring LOGUIC v1

Evaluar cinco dimensiones de 0 a 2:

| Dimensión | 0 | 1 | 2 |
| --- | --- | --- | --- |
| A — Ambigüedad | Resultado completamente definido. | Alguna decisión local. | Problema abierto o varias soluciones válidas. |
| I — Impacto | Aislado y fácilmente reversible. | Afecta varios componentes relacionados. | Transversal, arquitectónico o difícil de revertir. |
| R — Razonamiento | Mecánico. | Varios pasos relacionados. | Trade-offs, arquitectura o inferencia profunda. |
| V — Verificabilidad | Resultado determinista o fácilmente comprobable. | Requiere varias comprobaciones. | Difícil de demostrar automáticamente. |
| C — Contexto/acoplamiento | Un archivo, acción o contexto pequeño. | Varios contratos o componentes relacionados. | Muchas capas, dependencias o contexto extenso. |

Fórmula:

`LOGUIC_AI_SCORE = A + I + R + V + C`

Routing inicial:

| Score | Modelo |
| --- | --- |
| 0–3 | Luna |
| 4–7 | Terra |
| 8–10 | Sol |

El scoring da una recomendación inicial. Los escaladores obligatorios prevalecen. Una tarea 8–10 permanece en Sol salvo que cumpla y documente el override Astra de la sección 10.1; ni siquiera 10/10 lo activa por sí solo.

## 6. Bash y herramientas deterministas

Preferir Bash o una herramienta determinista cuando la IA no añade valor real.

Ejemplos:

- pytest con selección ya definida;
- suite completa ya decidida;
- `git status`;
- `git diff --check`;
- `git push`;
- `operational_state.py validate`;
- comandos deterministas y verificaciones exactas.

No consumir IA únicamente para ejecutar un comando cuya semántica ya está cerrada.

## 7. Luna

Usar Luna para trabajo mecánico, claro, repetible, fácilmente verificable y de bajo riesgo.

Ejemplos:

- documentación mecánica;
- transformación de texto con reglas cerradas;
- resumen de logs;
- actualización de hashes confirmados;
- ejecución o revisión de procedimientos ya especificados;
- clasificación sencilla;
- cambios triviales bajo contrato cerrado.

Luna no debe tomar decisiones arquitectónicas nuevas.

## 8. Terra

Terra es el default operativo LOGUIC: `Terra / medium`.

Usar Terra para:

- implementación de contrato cerrado;
- preflight técnico acotado;
- creación de tests;
- debugging localizado;
- inspección de varios archivos relacionados;
- revisión normal de diff;
- refactorización controlada;
- documentación técnica que requiere comprensión;
- postflight técnico ordinario.

## 9. Sol

Escalar a Sol para:

- nueva arquitectura;
- contratos fundacionales;
- alta ambigüedad;
- decisiones con varias estrategias razonables;
- cambios transversales;
- contradicciones entre capas;
- debugging complejo o persistente;
- seguridad crítica;
- migraciones difíciles de revertir;
- revisión especialmente crítica;
- contexto grande con fuerte interdependencia.

Sol no es el default.

## 10. Escaladores obligatorios

Escalar como mínimo a Sol independientemente del score cuando exista:

- riesgo real de pérdida de datos;
- seguridad crítica;
- cambio arquitectónico transversal;
- decisión fundacional difícil de revertir;
- contradicción contractual importante;
- resultado difícil de verificar objetivamente;
- dos intentos razonables fallidos por insuficiencia de razonamiento.

Regla:

`2 intentos razonables fallidos por capacidad o razonamiento en un nivel inferior → STOP → reevaluar con Sol.`

No aplicar esta regla si el fallo real fue un prompt, ruta, estado o comando incorrecto, o una precondición inexistente. Primero se determina la causa del fallo; no existe escalamiento automático Luna → Terra → Sol → Astra. Si los dos intentos razonables fallidos fueron con Sol, aplica la sección 10.1.

### 10.1. Override Astra

Astra se selecciona cuando la tarea requiere IA, existe al menos una de las condiciones concretas siguientes y el orquestador documenta la evidencia, la cuestión no resuelta y por qué el análisis acotado con Sol no basta. Esta justificación puede establecerse en preflight; no es necesario provocar fallos previos. El override prevalece también sobre un score inferior cuando el riesgo lo justifique.

| Señal | Condición adicional exigida para Astra |
| --- | --- |
| Contradicción entre autoridades canónicas | Dos autoridades vigentes y aplicables al mismo alcance exigen resultados incompatibles; la precedencia documental no lo resuelve y la decisión afecta invariantes de varios subsistemas. |
| Impacto transversal muy alto o decisión fundacional difícilmente reversible | La decisión afecta conjuntamente contratos, persistencia o consumidores y su reversión no está acotada o verificada; dividirla en tareas independientes perdería invariantes necesarias para valorar sus consecuencias. |
| Contexto extremadamente largo o altamente acoplado; reconciliación agentic compleja | Tras recuperar el checkpoint, filtrar historia y acotar la tarea, sigue siendo necesario razonar conjuntamente sobre autoridades, dependencias y evidencia causal de varios subsistemas; los análisis separados no permiten verificar su consistencia global. |
| Pérdida de datos o seguridad crítica | Existe riesgo concreto y quedan incertidumbres sobre integridad, autorización, aislamiento o recuperación que cruzan subsistemas y no pueden resolverse con un procedimiento verificado o una revisión acotada con Sol. |
| Debugging complejo tras dos intentos razonables fallidos con Sol | Ambos intentos abordaron la misma cuestión pendiente con hipótesis justificadas, incorporaron la evidencia anterior y tuvieron criterios de validación explícitos; persiste un fallo atribuible a capacidad o razonamiento, tras descartar causas operativas. |

Verificada la condición y registrada la justificación, se escala a Astra antes de continuar la parte afectada. Un fallo de red, entorno/harness, permisos, cuota, herramienta, datos ausentes o autoridad humana pendiente no cuenta como intento fallido por razonamiento. Repetir el mismo intento sin nueva hipótesis tampoco cuenta. Si Astra no resuelve la cuestión, registrar lo pendiente y reevaluar evidencia o autoridad; no encadenar reintentos ni inventar otro nivel.

No bastan por sí solos: score alto, número de archivos, longitud de conversación, varios repositorios, la etiqueta «seguridad», una tarea agentic ordinaria ni la novedad del modelo. Una discrepancia resuelta por la autoridad vigente o un checkpoint obsoleto corregible con hechos confirmados permanece en el nivel mínimo fiable.

Cada override deja en la evidencia de tarea existente: score base, condición aplicable y fuentes, límite concreto de Sol, modelo/effort seleccionados y realmente usados, resultado verificable esperado y frontera para degradar. No requiere nueva telemetría ni un router automático. La selección no prueba superioridad empírica de Astra en LOGUIC; se revisará con resultados reales.

Si varias condiciones aplican, se registra una señal principal y las demás como evidencia de apoyo; su solapamiento no crea una banda, un escalamiento adicional ni una presunción de Astra.

Astra no decide prioridades humanas ni puede aprobar su propia propuesta, sustituir autoridad ausente, ampliar el alcance, saltar gates, activar currículo o autorizar operaciones sensibles. La reconciliación agentic no autoriza delegación ni nuevos agentes. Ante autoridades irreconciliables, prepara las alternativas y eleva la decisión humana pendiente.

Regla final: herramientas deterministas si bastan; en otro caso score `0–3 Luna / 4–7 Terra / 8–10 Sol`, con Sol como mínimo ante los escaladores de la sección 10 y Astra solo ante el override documentado de esta sección. Selección por tarea, nunca por inercia de conversación.

## 11. Degradadores

Puede reducirse el modelo cuando la incertidumbre ya fue eliminada, por ejemplo si existe contrato aprobado, procedimiento cerrado, archivos exactos conocidos, output esperado definido, tests ya definidos o rollback sencillo.

Transiciones válidas:

`Astra → Sol → Terra → Luna → Bash`

Reevaluar al cerrar la contradicción, reducir ambigüedad, impacto o acoplamiento, o disponer de contrato y validación acotados. Puede saltarse directamente al mínimo fiable; no es obligatorio recorrer la cadena. No mantener un modelo caro por inercia.

## 12. Modelo y reasoning effort

Modelo y reasoning effort son decisiones independientes.

| Modelo / effort | Orientación v1.1 |
| --- | --- |
| Luna / low | Trabajo mecánico. |
| Luna / medium | Trabajo mecánico con varias comprobaciones. |
| Terra / medium | Default LOGUIC. |
| Terra / high | Preflight, debugging o revisión con trade-offs. |
| Sol / medium | Problema complejo pero bien delimitado. |
| Sol / high | Arquitectura, contratos difíciles o debugging profundo. |
| Astra / medium | Override justificado con pregunta y entregable acotados. |
| Astra / high | Override justificado que exige comparar hipótesis o consecuencias fuertemente acopladas. |
| extra-high | Uso excepcional. |

No usar `high` ni `extra-high` por defecto.

Elegir Astra no eleva automáticamente el effort; aumentar el effort de Sol tampoco sustituye un override Astra justificado. Para esta extensión se proponen `medium` y `high`, compatibles con los niveles publicados para [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) (consulta: 2026-09-05). Son orientaciones LOGUIC, no recomendaciones universales del proveedor ni garantías de rendimiento. La disponibilidad en Codex parte del hecho confirmado para este entorno; usar únicamente combinaciones expuestas por la herramienta y registrar cualquier diferencia entre selección y ejecución. No se normalizan esfuerzos adicionales en v1.1; `extra-high` conserva su carácter excepcional y no implica activar un parámetro automáticamente.

## 13. Routing dentro de una slice

Una misma slice puede cambiar de modelo según la tarea:

`arquitectura o preflight crítico → Sol`

`override de la sección 10.1 documentado → Astra → reevaluar al cerrar esa frontera`

`contrato ya decidido → Terra`

`implementación acotada → Terra`

`ejecución de pruebas ya definidas → Bash o Luna`

`git status, diff-check, push o suite completa ya especificada → Bash`

`finding complejo → escalar según evidencia`

Ejemplos LOGUIC de clasificación; no autorizan abrir trabajo:

| Modelo | Tarea ilustrativa |
| --- | --- |
| Luna | Registrar el hash frontend confirmado de B184.4 y sus validaciones, con alcance y texto ya decididos. |
| Terra | Revisar documentación y referencias de una enmienda de timing con contrato cerrado y diff acotado. |
| Sol | Analizar la frontera active source integrity B52 ≠ loader readiness, con autoridades compatibles y pregunta contractual acotada. |
| Astra | Reconciliar, si apareciera, una contradicción irresuelta entre contratos vigentes de evidencia, persistencia y consumidores que requiera una decisión conjunta; o investigar una carrera transaccional tras dos intentos razonables fallidos con Sol conforme a 10.1. |

## 14. Regla de cuota

- Cuota baja y tarea mecánica: Bash o Luna.
- Cuota baja y tarea normal: Terra.
- Cuota baja y tarea crítica: Sol, o Astra si aplica 10.1; aplazar la parte que requiere ese nivel si no está disponible.
- Nunca degradar una tarea crítica solo para ahorrar cuota.

Indisponibilidad de Astra no demuestra que Sol sea suficiente. Solo se degrada por reducción documentada del riesgo o alcance conforme a la sección 11; las tareas independientes ya autorizadas pueden continuar en su nivel adecuado.

## 15. Carácter empírico y revisión

La política y su extensión v1.1 mantienen carácter empírico. No afirman que sus umbrales, ejemplos o esfuerzos sean definitivos; se revisarán con evidencia de uso en slices reales.

La evidencia mínima por tarea deberá registrar:

- tipo de tarea, score y ruta elegida;
- modelo y reasoning effort usados;
- resultado y validación aplicada;
- reintentos y causa clasificada: razonamiento insuficiente o error de prompt, estado, ruta, comando o precondición;
- escalamiento o degradación y su evidencia;
- tiempo o iteraciones hasta un resultado verificable;
- falsos positivos o negativos de routing e incidencias de calidad posteriores.

La revisión se realizará después de slices representativas, no a partir de una única tarea. Hasta entonces, la política no autoriza un router automático, telemetría obligatoria ni integración de IA local.
