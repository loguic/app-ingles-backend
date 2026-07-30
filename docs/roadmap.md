# Roadmap del proyecto app-ingles-backend

## Fase 1 — Backend base

Estado: completada a nivel inicial.

- FastAPI modular.
- PostgreSQL activo.
- SQLAlchemy configurado.
- pytest configurado.
- Endpoints principales probados.
- GitHub sincronizado.

## Fase 2 — Modelo pedagógico

Estado: completada a nivel inicial.

Objetivo: pasar de lecciones simples a habilidades medibles.

Bloques completados:

- B40: diseño conceptual de Skill.
- B41: diseño de relación Exercise-Skill.
- B42: registro de intentos reales con contexto pedagógico.
- B43: base para calcular dominio por habilidad mediante skill_ids.
- B44: recomendaciones básicas de progreso.

## Fase 3 — Sistema adaptativo

Estado: completada a nivel inicial.

Objetivo: recomendar repasos y rutas según rendimiento.

Bloques completados:

- B45: revisión del estado actual y orden del modelo adaptativo.
- B46: diseño de mastery_score por habilidad.
- B47: endpoint de dominio por habilidad.
- B48: mejora de recomendaciones usando habilidades débiles.
- B49: sistema básico de repaso por habilidad.
- B50: cierre documental de la fase adaptativa inicial.

Resultado de fase:

- El backend ya puede calcular dominio por habilidad.
- El backend ya puede exponer dominio por habilidad mediante API.
- El backend ya puede recomendar repaso básico por habilidad.
- El backend ya tiene una primera base adaptativa simple.

## Fase 4 — Preparación para frontend

Estado: completada a nivel inicial.

Objetivo: preparar respuestas claras, estables y útiles para una aplicación visual.

Bloques completados:

- B52: dashboard inicial del estudiante.
- B53: endpoint de siguiente acción recomendada.
- B54: contrato API inicial para frontend.
- B55: ejemplos JSON del contrato API para frontend.
- B56: cierre documental de preparación inicial para frontend.

Resultado de fase:

- El backend ya ofrece un dashboard inicial para el frontend.
- El backend ya indica la siguiente acción recomendada.
- El frontend ya cuenta con un contrato API inicial.
- El contrato API ya incluye ejemplos JSON de respuesta.

## Fase 5 — Frontend y práctica conversacional

Estado: en progreso.

Objetivo: conectar el backend con una aplicación visual y desarrollar capacidades pedagógicas completas.

Entorno confirmado:

- Backend FastAPI en Ubuntu local.
- Frontend Flutter en Ubuntu local.
- Comunicación mediante API HTTP.
- App Inglés utiliza el puerto `8001`.
- CNAPP-Lite conserva el puerto `8000`.

Capacidades desarrolladas:

- navegación por niveles, unidades y lecciones;
- ejercicios conectados con el backend;
- progreso persistido;
- reproducción de pronunciaciones regionales;
- grabación temporal de voz;
- repetición guiada;
- autoevaluación de pronunciación;
- resumen local de lección;
- avance persistente por lección.

Capacidades conversacionales desarrolladas:

- conversación guiada mediante conversaciones y turnos con identificadores estables;
- contrato backend para conversaciones ramificadas;
- respuestas alternativas con destinos estables;
- separación, unión y cierre de rutas;
- validación automática de integridad del grafo;
- interfaz Flutter para recorrer conversaciones ramificadas;
- persistencia de intentos conversacionales;
- historial y resumen del progreso conversacional;
- identificadores estables para ejemplos de pronunciación.

Estado pedagógico actual:

- 2 niveles declarados: A1 y A2;
- 1 unidad disponible;
- 2 lecciones, de las cuales una todavía no tiene contenido;
- 2 ejemplos;
- 1 ejercicio;
- 2 conversaciones con 9 turnos;
- el contenido activo todavía no constituye una versión pedagógica suficientemente utilizable;
- existe una primera candidata piloto v2 aislada, no publicada y en estado `pending_approval`.

Constructor Pedagógico de Unidades:

- B105 cerrado: arquitectura profesional, contratos de entrada y salida, matriz de cobertura, revisión humana y preparación futura para MCP.
- B106 cerrado: contratos deterministas para Skills, especificaciones, cobertura, paquetes candidatos e informes de validación.
- B107 cerrado: motor determinista para etapas obligatorias, referencias internas, vínculo entre evaluación y `skill_ids`, y estados de cobertura.
- B116 cerrado: contrato profesional de `LessonExperience` y recorrido pedagógico v2.
- B117 cerrado: schemas aditivos para misión, etapas, apoyos, evidencias y política de finalización.
- B118 cerrado: integridad interna de `LessonExperience`.
- B119 cerrado: integridad externa entre la experiencia y los recursos de `Lesson`.
- B120 cerrado: validación de Skills de `LessonExperience` contra la especificación aprobada.
- B121 cerrado: especificación versionada y candidata piloto `a1-u1-l1` aislada, validada y revisada humanamente.
- B122 cerrado: contratos de producción personal, prompts obligatorios y evidencia `contextual_response` incorporados.
- B123 cerrado: persistencia normalizada y lectura interna estructurada de las producciones personales incorporadas.
- B124 cerrado: exposición API controlada de producciones personales limitada al contenido pedagógico activo.
- Registrar una producción mediante texto o voz no implica todavía que sea correcta.
- La candidata permanece en `pending_approval`: persistencia y exposición backend están disponibles, y B104 frontend completó la presentación y revisión de producciones personales sin publicar la candidata ni introducir evaluación automática.
- El contenido candidato permanece separado del contenido pedagógico activo.
- El agente orquestador y MCP no están implementados y no se incorporarán antes de confirmar una necesidad real.

Evolución prevista:

- presentación de producciones personales en Flutter — completada en B104 frontend;
- reconocimiento de voz y palabras — completado en B126–B128;
- evaluación semántica y fonética gradual — B129 creó contratos trazables, B130 añadió el primer evaluador semántico determinista, B131 incorporó persistencia de resultados, B132 añadió feedback pedagógico, B133 persistió ese feedback, B134 unificó el flujo en un pipeline atómico, B135 desacopló el runtime de la candidata pedagógica, B136 creó la frontera trazable para evidencia fonética, B137 añadió ingesta privada y resolución backend del audio, B138 seleccionó mediante benchmark reproducible una arquitectura WavLM + alineación CTC + GOP + scorer por fonema y B139 integró ese analizador mediante un runtime aislado, configurable y verificable por SHA-256, mientras B140 cerró una base reproducible de calibración técnica con voz humana real y B141 añadió el protocolo, identidad pseudónima por hablante/sesión y medición objetiva de cobertura necesarios para construir un corpus humano representativo, B142 añadió etiquetado humano independiente, trazable y basado en rúbrica versionada, B143 añadió un resumen descriptivo del acuerdo humano separado por muestra y versión de rúbrica, B144 relacionó de forma trazable mediciones acústicas, etiquetas humanas independientes y acuerdo humano preservando múltiples mediciones sin derivar verdad ni decisión pedagógica, B145 añadió observaciones y resúmenes descriptivos versionados de scores técnicos frente a evaluación humana sin establecer correlaciones interpretadas ni umbrales pedagógicos, B146 añadió distribuciones descriptivas de scores por etiqueta humana independiente preservando el desacuerdo y el contexto versionado, y B147 añadió Q25, mediana y Q75 por etiqueta humana como descripción robusta de la distribución sin convertir percentiles en umbrales; la calibración pedagógica con voces humanas representativas y la comprensión semántica avanzada siguen pendientes;
- retroalimentación pedagógica adaptativa;
- conversación libre;
- consolidación y comprobación diferida de retención por Skill.

## Fase 6 — IA controlada

Objetivo: incorporar inteligencia artificial de manera gradual, evaluable y segura.

Capacidades previstas:

- generación contextual de ejercicios;
- respuestas conversacionales dinámicas;
- interlocutores configurables;
- retroalimentación personalizada;
- adaptación según errores;
- recomendaciones pedagógicas;
- control de costes, límites y privacidad.

La IA no sustituirá los contratos pedagógicos, las pruebas automáticas ni las validaciones humanas.

## Fase 7 — Lectura guiada interactiva

Objetivo: reforzar comprensión lectora, fluidez oral, vocabulario y pronunciación mediante documentos segmentados.

Recorrido previsto:

`Abrir texto → Leer o escuchar por segmentos → Resaltar el segmento activo → Consultar palabras → Practicar pronunciación → Guardar dificultades → Repetir`

Capacidades previstas:

- división del documento en segmentos identificados;
- resaltado progresivo del texto leído;
- avance manual, por audio o mediante reconocimiento futuro;
- selección de palabras para consultar significado contextual;
- traducción opcional;
- pronunciación regional `en-US` y `en-GB`;
- ejemplos relacionados con el contexto;
- ocultación del significado para comprobar comprensión;
- vocabulario guardado para repetición inteligente;
- registro de palabras difíciles y segmentos releídos;
- futura detección de omisiones, pausas y errores durante la lectura oral.

La implementación tomará como referencia patrones pedagógicos de herramientas de aprendizaje asistido, pero utilizará un contrato y una experiencia propios de App Inglés.

## B148 — Solapamiento descriptivo entre distribuciones humanas

Estado: cerrado técnicamente.

Se añadió la comparación descriptiva del solapamiento entre IQR Q25–Q75 para pares de etiquetas humanas dentro del mismo contexto versionado de analizador y rúbrica.

Este bloque amplía la evidencia descriptiva disponible, pero no establece separabilidad, umbrales, clasificación automática ni decisiones pedagógicas.

Validación de cierre técnico:
- B148 específico: 11 passed.
- Regresión B142–B148: 63 passed.
- Suite backend completa: 491 passed.
- Commit técnico: `4d7821e`.

## B149 — Informe descriptivo consolidado de calibración modelo-humano

Estado: cerrado técnicamente.

Se añadió un informe consolidado que reúne, dentro del mismo `analyzer_id + analyzer_version + rubric_version`, el resumen modelo-humano, las distribuciones robustas por etiqueta y los solapamientos IQR descriptivos.

Este bloque consolida evidencia existente sin introducir verdad, separabilidad, umbrales, clasificación automática ni decisiones pedagógicas.

Validación de cierre técnico:
- B149 específico: 7 passed.
- Regresión B142–B149: 70 passed.
- Suite backend completa: 498 passed.
- Commit técnico: `e91a011`.

## B150 — Identidad reproducible del informe descriptivo de calibración

Estado: cerrado técnicamente.

Se añadió un artefacto reproducible para el informe descriptivo consolidado mediante `report_version` y SHA-256 determinista sobre su contenido canónico.

Este bloque mejora la trazabilidad y reproducibilidad de la evidencia sin introducir verdad, separabilidad, umbrales, clasificación automática ni decisiones pedagógicas.

Validación de cierre técnico:
- B150 específico: 11 passed.
- Regresión B142–B150: 81 passed.
- Suite backend completa: 509 passed.
- Commit técnico: `1c07f43`.

## B151 — Verificación de integridad del artefacto descriptivo de calibración

Estado: cerrado técnicamente.

Se añadió verificación independiente de integridad para el artefacto descriptivo reproducible de B150, recalculando su SHA-256 canónico y comparándolo con la identidad almacenada.

Este bloque mejora la trazabilidad técnica y permite detectar alteraciones del contenido sin introducir verdad, separabilidad, umbrales, clasificación automática ni decisiones pedagógicas.

Validación de cierre técnico:
- B151 específico: 15 passed.
- Regresión B142–B151: 96 passed.
- Suite backend completa: 524 passed.
- Commit técnico: `6954a58`.

## B152 — Comparación descriptiva reproducible entre artefactos de calibración

Estado: cerrado técnicamente.

Se añadió comparación reproducible entre dos artefactos descriptivos íntegros, preservando sus identidades, versiones de analizador y una `rubric_version` común.

Este bloque permite comparar contextos técnicos versionados sin decidir cuál es mejor ni introducir verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B152 específico: 22 passed.
- Regresión B142–B152: 118 passed.
- Suite backend completa: 546 passed.
- Commit técnico: `858d36b`.

## B153 — Identidad reproducible de evidencia humana para comparación

Estado: cerrado técnicamente.

Se añadió una identidad reproducible de la evidencia humana basada en `rubric_version`, número de muestras distintas y SHA-256 canónico de los acuerdos compatibles.

Este bloque permite comprobar posteriormente si dos calibraciones utilizan la misma base humana, sin comparar todavía diferencias de score ni introducir verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B153 específico: 13 passed.
- Regresión B142–B153: 131 passed.
- Suite backend completa: 559 passed.
- Commit técnico: `75dae4c`.

## B154 — Compatibilidad reproducible de evidencia humana entre calibraciones

Estado: cerrado técnicamente.

Se añadió compatibilidad reproducible entre dos identidades B153 de evidencia humana. `same_evidence` solo es verdadero cuando coinciden exactamente `rubric_version`, `sample_count` y `evidence_sha256`.

Este bloque permite comprobar que dos calibraciones parten de la misma base humana antes de interpretar diferencias técnicas, sin determinar qué analizador es mejor ni introducir verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B154 específico: 6 passed.
- Regresión B142–B154: 137 passed.
- Suite backend completa: 565 passed.
- Commit técnico: `66b8b39`.

## B155 — Contexto reproducible de calibración comparable

Estado: cerrado técnicamente.

Se añadió un contexto reproducible que combina la comparación de artefactos B152 con la compatibilidad de evidencia humana B154.

El contexto solo existe cuando los artefactos son comparables, comparten `rubric_version` y utilizan exactamente la misma evidencia humana reproducible.

Este bloque prepara análisis técnicos posteriores sin calcular todavía diferencias de score ni determinar qué analizador es mejor. Tampoco introduce verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B155 específico: 6 passed.
- Regresión B142–B155: 143 passed.
- Suite backend completa: 571 passed.
- Commit técnico: `3927ebb`.

## B156 — Identidad reproducible de cobertura técnica de calibración

Estado: cerrado técnicamente.

Se añadió una identidad reproducible de cobertura técnica basada en `analyzer_id`, `analyzer_version`, `rubric_version`, número de muestras distintas y SHA-256 del conjunto canónico de `sample_id`.

Este bloque permite comprobar posteriormente que dos analizadores fueron evaluados sobre la misma cobertura efectiva de muestras, sin calcular todavía diferencias de score ni introducir verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B156 específico: 16 passed.
- Regresión B142–B156: 159 passed.
- Suite backend completa: 587 passed.
- Commit técnico: `45189b8`.

## B157 — Compatibilidad reproducible de cobertura técnica entre calibraciones

Estado: cerrado técnicamente.

Se añadió compatibilidad reproducible entre dos identidades B156 de cobertura técnica. `same_coverage` solo es verdadero cuando coinciden exactamente `rubric_version`, `sample_count` y `sample_ids_sha256`.

Este bloque permite comprobar que dos analizadores distintos fueron evaluados sobre exactamente el mismo conjunto efectivo de muestras antes de cualquier comparación posterior de scores.

Límites: B157 no calcula diferencias de score, no determina qué analizador es mejor y no introduce verdad, separabilidad, umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B157 específico: 6 passed.
- Regresión B142–B157: 165 passed.
- Suite backend completa: 593 passed.
- Commit técnico: `437723a`.

## B158 — Contexto reproducible de comparación técnica completa

Estado: cerrado técnicamente.

Se añadió un contexto que combina la comparabilidad de artefactos, la compatibilidad de evidencia humana y la compatibilidad de cobertura técnica.

El contexto solo existe cuando ambas calibraciones comparten exactamente la misma evidencia humana reproducible, exactamente la misma cobertura efectiva de muestras y cada cobertura corresponde al analizador, versión y rúbrica correctos de su lado.

Este bloque prepara comparaciones técnicas posteriores bajo condiciones controladas, sin calcular todavía diferencias de score, mejoras, degradaciones ni decidir qué analizador es mejor.

Validación de cierre técnico:
- B158 específico: 7 passed.
- Regresión B142–B158: 172 passed.
- Suite backend completa: 600 passed.
- Commit técnico: `6fc5e7a`.

## B159 — Comparación descriptiva de scores por etiqueta humana

Estado: cerrado técnicamente.

Se añadió una comparación reproducible de medianas por etiqueta humana entre dos calibraciones que ya cumplen el contexto técnico completo B158.

Cada distribución debe pertenecer exactamente al analizador, versión y rúbrica de su lado y ambas deben usar la misma etiqueta humana.

El resultado conserva conteos y medianas y calcula:

`median_difference = right_median - left_median`

Este bloque sigue siendo descriptivo: no interpreta signo o magnitud como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B159 específico: 7 passed.
- Regresión B142–B159: 179 passed.
- Suite backend completa: 607 passed.
- Commit técnico: `cb70582`.

## B160 — Comparación robusta de distribuciones por etiqueta humana

Estado: cerrado técnicamente.

Se añadió una comparación reproducible de distribuciones robustas por etiqueta humana entre dos calibraciones que ya cumplen el contexto técnico completo B158.

Cada distribución debe pertenecer exactamente al analizador, versión y rúbrica de su lado y ambas deben usar la misma etiqueta humana.

El resultado conserva `sample_count`, Q25, mediana y Q75 de ambos lados y calcula las diferencias reproducibles `right - left` para los tres puntos robustos.

Este bloque sigue siendo descriptivo: no interpreta signo, magnitud ni forma como mejora, degradación, superioridad del analizador ni decisión pedagógica.

Validación de cierre técnico:
- B160 específico: 8 passed.
- Regresión B142–B160: 187 passed.
- Suite backend completa: 615 passed.
- Commit técnico: `a64bec7`.

## B161 — Informe consolidado de comparación técnica por etiquetas

Estado: cerrado técnicamente.

Se añadió un informe consolidado reproducible que agrupa comparaciones robustas B160 por etiqueta humana dentro de un único contexto técnico completo B158.

Cada comparación debe corresponder exactamente a los analizadores, versiones y rúbrica del contexto. Las etiquetas deben ser únicas y ambos lados deben utilizar exactamente el mismo conjunto de etiquetas. El resultado se genera en orden determinista.

Este bloque continúa siendo descriptivo: no interpreta diferencias de Q25, mediana o Q75 como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B161 específico: 7 passed.
- Regresión B142–B161: 194 passed.
- Suite backend completa: 622 passed.
- Commit técnico: `58b95d2`.

## B162 — Artefacto reproducible del informe de comparación técnica

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonReportArtifact`, que encapsula un informe B161 completo junto con una `artifact_version` explícita y una identidad `content_sha256` reproducible.

El hash se calcula sobre una representación JSON canónica que incluye la versión del artefacto y todo el contenido del informe. La identidad permanece estable para entradas idénticas y cambia ante modificaciones de versión o contenido.

Este bloque añade identidad reproducible al informe consolidado, pero todavía no verifica su integridad posterior ni interpreta las diferencias técnicas como mejora, degradación, superioridad del analizador o decisión pedagógica.

Validación de cierre técnico:
- B162 específico: 6 passed.
- Regresión B142–B162: 200 passed.
- Suite backend completa: 628 passed.
- Commit técnico: `51e85f0`.

## B163 — Verificación de integridad del artefacto de comparación técnica

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification`, que permite verificar reproduciblemente la integridad de un artefacto B162 frente a su contenido actual.

La verificación reconstruye el artefacto mediante el constructor canónico B162 y conserva `artifact_version`, `expected_sha256`, `computed_sha256` y `matches_content`, permitiendo detectar cualquier discrepancia entre la identidad almacenada y el contenido actual.

Este bloque verifica integridad técnica únicamente. No interpreta las diferencias de Q25, mediana o Q75 como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B163 específico: 5 passed.
- Regresión B142–B163: 205 passed.
- Suite backend completa: 633 passed.
- Commit técnico: `953ba52`.
