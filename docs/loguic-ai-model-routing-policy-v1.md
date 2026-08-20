# LOGUIC AI Model Routing Policy v1

## 1. Propósito

Seleccionar de forma objetiva y reproducible la herramienta o el modelo mínimo fiable para cada tarea de ingeniería LOGUIC.

Objetivos simultáneos:

- preservar calidad;
- evitar consumo innecesario de cuota;
- reservar modelos superiores para tareas que realmente los necesiten;
- hacer explícitas y auditables las decisiones de routing;
- preparar la futura integración con IA local y LOGUIC OS.

## 2. Alcance

Esta es una política transversal de ingeniería LOGUIC. Este repositorio alberga la v1 como política operativa piloto y versionada; no es una regla específica del dominio App Inglés.

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

## 4. Routing base v1

Orden conceptual actual:

1. Bash o herramienta determinista.
2. Luna.
3. Terra.
4. Sol.

Extensión futura prevista:

1. Bash o herramienta determinista.
2. IA local.
3. Luna.
4. Terra.
5. Sol.

La IA local todavía no forma parte operativa de v1.

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

El scoring da una recomendación inicial. Los escaladores obligatorios prevalecen.

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

Escalar a Sol independientemente del score cuando exista:

- riesgo real de pérdida de datos;
- seguridad crítica;
- cambio arquitectónico transversal;
- decisión fundacional difícil de revertir;
- contradicción contractual importante;
- resultado difícil de verificar objetivamente;
- dos intentos razonables fallidos por insuficiencia de razonamiento.

Regla:

`2 intentos razonables fallidos por capacidad o razonamiento → STOP → reevaluar con Sol.`

No aplicar esta regla si el fallo real fue un prompt, ruta, estado o comando incorrecto, o una precondición inexistente. Primero se determina la causa del fallo; no existe escalamiento automático Luna → Terra → Sol.

## 11. Degradadores

Puede reducirse el modelo cuando la incertidumbre ya fue eliminada, por ejemplo si existe contrato aprobado, procedimiento cerrado, archivos exactos conocidos, output esperado definido, tests ya definidos o rollback sencillo.

Transiciones válidas:

`Sol → Terra → Luna → Bash`

No mantener un modelo caro por inercia.

## 12. Modelo y reasoning effort

Modelo y reasoning effort son decisiones independientes.

| Modelo / effort | Orientación v1 |
| --- | --- |
| Luna / low | Trabajo mecánico. |
| Luna / medium | Trabajo mecánico con varias comprobaciones. |
| Terra / medium | Default LOGUIC. |
| Terra / high | Preflight, debugging o revisión con trade-offs. |
| Sol / medium | Problema complejo pero bien delimitado. |
| Sol / high | Arquitectura, contratos difíciles o debugging profundo. |
| extra-high | Uso excepcional. |

No usar `high` ni `extra-high` por defecto.

## 13. Routing dentro de una slice

Una misma slice puede cambiar de modelo según la tarea:

`arquitectura o preflight crítico → Sol`

`contrato ya decidido → Terra`

`implementación acotada → Terra`

`ejecución de pruebas ya definidas → Bash o Luna`

`git status, diff-check, push o suite completa ya especificada → Bash`

`finding complejo → escalar según evidencia`

## 14. Regla de cuota

- Cuota baja y tarea mecánica: Bash o Luna.
- Cuota baja y tarea normal: Terra.
- Cuota baja y tarea crítica: Sol o aplazar.
- Nunca degradar una tarea crítica solo para ahorrar cuota.

## 15. Carácter empírico y revisión

Esta v1 es una política operativa inicialmente empírica. No afirma que sus umbrales, ejemplos o esfuerzos sean definitivos; se revisará con evidencia de uso en slices reales.

La evidencia mínima por tarea deberá registrar:

- tipo de tarea, score y ruta elegida;
- modelo y reasoning effort usados;
- resultado y validación aplicada;
- reintentos y causa clasificada: razonamiento insuficiente o error de prompt, estado, ruta, comando o precondición;
- escalamiento o degradación y su evidencia;
- tiempo o iteraciones hasta un resultado verificable;
- falsos positivos o negativos de routing e incidencias de calidad posteriores.

La revisión se realizará después de slices representativas, no a partir de una única tarea. Hasta entonces, la política no autoriza un router automático, telemetría obligatoria ni integración de IA local.
