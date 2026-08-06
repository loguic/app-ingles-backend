# Roadmap del proyecto app-ingles-backend
## Dirección canónica vigente desde B176

Desde B176, la dirección del producto está definida por:

`docs/modelo-pedagogico-maestro.md`

Ese documento establece:

- el puerto de llegada de fluidez conversacional funcional;
- las cuatro fases pedagógicas;
- el diagnóstico conversacional;
- el ciclo diario;
- los métodos y principios aprobados;
- la pronunciación funcional transversal;
- el sistema de macrobloques pedagógicos;
- las tres puertas humanas de control.

El historial técnico conservado en este roadmap continúa siendo válido como trazabilidad de lo construido, pero ya no determina automáticamente el siguiente bloque.

Todo trabajo nuevo deberá partir de una capacidad observable del estudiante y justificar su contribución directa al puerto de llegada.


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

## B164 — Comparación reproducible entre artefactos técnicos verificados

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison` junto con `compare_phonetic_calibration_technical_distribution_comparison_report_artifacts`.

La comparación exige artefactos B162 íntegros según B163, conserva `artifact_version` y `content_sha256` de ambos lados y registra los analizadores y versiones presentes en cada informe técnico.

Ambos artefactos deben utilizar exactamente la misma `rubric_version`.

Este bloque establece identidad y trazabilidad reproducible entre informes técnicos versionados. Todavía no compara sus diferencias internas ni determina mejora, degradación, superioridad de analizadores o decisiones pedagógicas.

Validación de cierre técnico:
- B164 específico: 7 passed.
- Regresión B142–B164: 212 passed.
- Suite backend completa: 640 passed.
- Commit técnico: `5a18bcd`.

## B165 — Deltas descriptivos entre comparaciones técnicas

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDelta` junto con `compare_phonetic_calibration_technical_distribution_comparison_deltas`.

B165 compara dos comparaciones robustas B160 dentro de una comparación reproducible B164 válida. Cada lado debe corresponder exactamente a los analizadores, versiones y rúbrica de su artefacto, y ambas comparaciones deben representar la misma etiqueta humana.

El resultado conserva las diferencias técnicas de Q25, mediana y Q75 de ambos informes y calcula sus deltas reproducibles `right - left`.

Este bloque sigue siendo descriptivo: no interpreta signo ni magnitud de los deltas como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B165 específico: 8 passed.
- Regresión B142–B165: 220 passed.
- Suite backend completa: 648 passed.
- Commit técnico: `9964241`.

## B166 — Informe consolidado de deltas técnicos por etiqueta

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReport` junto con `build_phonetic_calibration_technical_distribution_comparison_delta_report`.

B166 consolida deltas descriptivos B165 por etiqueta humana dentro de una comparación reproducible B164 válida.

Todos los deltas deben compartir la misma `rubric_version` del contexto y cada etiqueta humana debe aparecer una sola vez. El servicio exige etiquetas únicas en ambos lados, exactamente el mismo conjunto de etiquetas y genera los resultados en orden determinista.

Este bloque sigue siendo descriptivo: no interpreta signo ni magnitud de los deltas como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B166 específico: 7 passed.
- Regresión B142–B166: 227 passed.
- Suite backend completa: 655 passed.
- Commit técnico: `403306f`.

## B167 — Sistematización del cierre de bloques

Estado: cerrado técnicamente.

Se añadió `scripts/engineering/block_close.py` para reducir pasos repetitivos del cierre técnico manteniendo controles explícitos y trazabilidad.

Automatiza validación de raíz, `git diff --check`, pruebas específicas, regresión fonética, suite completa, preflight técnico y staging restringido a las rutas técnicas validadas.

Los commits, la documentación, el push y las decisiones arquitectónicas permanecen manuales y requieren confirmación humana.

Validación de cierre técnico:
- B167 específico: 19 passed.
- Regresión fonética automática: 246 passed en 53 archivos.
- Suite backend completa: 674 passed.
- Commit técnico: `5f249d4`.

## B168 — Artefacto reproducible del informe de deltas técnicos

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact` junto con `build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact`.

B168 convierte el informe consolidado B166 en un artefacto versionado con identidad SHA-256 reproducible calculada sobre su representación JSON canónica.

El bloque sigue siendo estrictamente descriptivo: no interpreta los deltas como mejora, degradación o superioridad del analizador y no introduce decisiones pedagógicas.

Validación de cierre técnico:
- B168 específico: 6 passed.
- Regresión fonética automática: 252 passed en 55 archivos.
- Suite backend completa: 680 passed.
- Commit técnico: `89d1fec`.

## B169 — Verificación de integridad del artefacto de deltas técnicos

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification` junto con `verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact`.

B169 verifica reproduciblemente el artefacto B168 reconstruyendo su identidad canónica y comparando el SHA-256 almacenado con el SHA-256 calculado desde su contenido actual.

El bloque sigue siendo estrictamente técnico y descriptivo: verifica integridad, pero no interpreta los deltas ni introduce decisiones pedagógicas.

Validación de cierre técnico:
- B169 específico: 5 passed.
- Regresión fonética automática: 257 passed en 57 archivos.
- Suite backend completa: 685 passed.
- Commit técnico: `140ea14`.

## B170 — Comparación reproducible entre artefactos de deltas técnicos

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison` junto con `compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts`.

B170 permite comparar dos artefactos B168 íntegros preservando su identidad reproducible y sus contextos técnicos, con `rubric_version` común obligatoria.

El bloque sigue siendo estrictamente descriptivo: establece comparabilidad reproducible entre artefactos de deltas, pero no interpreta cuál analizador mejora, empeora o es superior.

Validación de cierre técnico:
- B170 específico: 7 passed.
- Regresión fonética automática: 264 passed en 59 archivos.
- Suite backend completa: 692 passed.
- Commit técnico: `e34d18d`.

## B171 — Distancia descriptiva entre IQR por etiqueta humana

Estado: cerrado técnicamente.

Se añadió `PhoneticCalibrationHumanLabelScoreIqrGap` junto con `describe_phonetic_calibration_human_label_score_iqr_gaps`.

B171 cubre el vacío descriptivo dejado por B148 para distribuciones no solapadas: conserva cuánto espacio existe entre sus IQR mediante `gap_width`, manteniendo `0.0` cuando se solapan o se tocan.

El bloque no convierte esta distancia en separabilidad pedagógica ni introduce umbrales, clasificación automática o decisiones pedagógicas.

Validación de cierre técnico:
- B171 específico: 7 passed.
- Regresión fonética automática: 271 passed en 61 archivos.
- Suite backend completa: 699 passed.
- Commit técnico: `094571a`.

## B172 — Relación descriptiva unificada de evidencia IQR

Estado: cerrado técnicamente.

Se añadió una relación explícita entre la evidencia de solapamiento B148 y la distancia IQR B171 para el mismo contexto versionado y par de etiquetas.

La integración se realiza en una capa independiente, sin modificar B149–B151.

El bloque mantiene carácter exclusivamente descriptivo: no define separabilidad pedagógica, umbrales ni clasificación automática.

Validación:
- B172 específico: 10 passed.
- Regresión fonética: 281 passed en 63 archivos.
- Suite backend completa: 716 passed.
- Commit técnico: `bb0dcdd`.

## B173 — Cobertura regional de referencia del corpus fonético humano

Estado: cerrado técnicamente.

Se añadió una extensión compatible del corpus representativo B141 que registra explícitamente la variante de pronunciación utilizada como referencia mediante `reference_locale`, limitada actualmente a `en-US` y `en-GB`.

La cobertura regional observa por locale el número de muestras, hablantes pseudónimos y sesiones, sin alterar los contratos ni manifiestos históricos de B141.

Los audios históricos sin locale permanecen sin clasificación regional retrospectiva.

Este bloque prepara una futura construcción trazable del corpus humano real, pero no demuestra representatividad, no establece mínimos de suficiencia ni introduce umbrales o decisiones pedagógicas.

Validación:
- B173 específico: 16 passed.
- Regresión fonética automática: 297 passed en 67 archivos.
- Suite backend completa: 725 passed.
- Commit técnico: `dbefa49`.

## B174 — Cobertura regional de evidencia humana del corpus fonético

Estado: cerrado técnicamente.

Se añadió una cobertura descriptiva de la evidencia humana revisada por `reference_locale + rubric_version`, relacionando las muestras regionales B173 con acuerdos humanos B143 y etiquetas independientes B142.

La cobertura conserva muestras, hablantes, sesiones, cantidad y distribución de etiquetas, evaluadores pseudónimos distintos y muestras con acuerdo unánime, sin convertir el desacuerdo humano en mayoría o verdad.

B174 mejora la observabilidad necesaria para construir posteriormente un corpus humano realmente representativo, pero no establece mínimos de suficiencia ni demuestra representatividad y no introduce umbrales o decisiones pedagógicas.

Validación:
- B174 específico: 14 passed.
- Regresión fonética: 311 pruebas en 69 archivos.
- Suite backend completa: 746 pruebas.
- Commit técnico: `a7cdac4`.

## B175 — Auditoría de reutilización tecnológica y extensibilidad multilingüe

Estado: auditoría cerrada.

B175 estableció la política `open-source/local first`: reutilizar software, modelos y runtimes abiertos antes de desarrollar capacidades propias. Los servicios de pago quedan como adaptadores opcionales futuros.

La auditoría confirmó:
- conservación de los contratos y el runtime fonético desacoplado;
- WavLM como proveedor local experimental de inglés;
- reutilización de Sherpa-ONNX y Moonshine para STT;
- conservación de la capa local de reproducción y grabación de audio;
- evaluación semántica determinista para actividades cerradas;
- ausencia actual de integración real con OpenAI;
- conversación libre todavía pendiente de contratos de sesión y mensajes dinámicos;
- Qwen3.5-4B únicamente como candidato para benchmark local futuro;
- necesidad futura de separar LOGUIC Core, capacidades compartidas y módulos específicos por idioma.

Hallazgo corregido posteriormente en B176:

La diferencia entre `EvidenceDefinition.measurement_mode` y `ProductionEvaluationCriterion.measurement_mode` no constituye por sí sola una incoherencia.

Una evidencia pedagógica `contextual_response` puede registrar `completion`, mientras sus producciones concretas son evaluadas mediante criterios semánticos `binary` o fonéticos `score`. Ambos contratos representan responsabilidades diferentes.

B175 no modificó código, contratos, dependencias ni base de datos y no requirió ejecutar pruebas.

## B176 — Reorientación estratégica y pedagógica

Estado: en documentación.

B176 canceló su alcance técnico original después de comprobar que la supuesta igualdad obligatoria entre evidencia pedagógica y criterio evaluativo era incorrecta.

El bloque definió y aprobó:

- el puerto de llegada de LOGUIC English;
- la fluidez conversacional funcional como resultado final;
- un horizonte orientativo de tres a seis meses;
- cuatro fases pedagógicas basadas en desempeño;
- diagnóstico y plan conversacional inicial;
- práctica diaria centrada en tiempo real hablando;
- construcción directa en inglés;
- pronunciación funcional transversal;
- el triángulo vocálico `/iː/–/ɪ/–/e/`;
- macrobloques pedagógicos completos;
- tres puertas humanas de aprobación;
- incorporación futura y controlada de Codex.

La fuente canónica de estas decisiones es:

`docs/modelo-pedagogico-maestro.md`

## Próximo macrobloque

Todavía no está seleccionado.

No se asignará automáticamente B177 a una deuda técnica ni a una capacidad futura ya listada.

El próximo macrobloque deberá superar primero la Puerta 1 y definir:

- problema del estudiante;
- fase pedagógica;
- capacidad objetivo;
- método;
- experiencia;
- evidencia observable;
- transferencia;
- criterios de aceptación.
## B177 — Diagnóstico conversacional contextual

Estado: en desarrollo.

Puerta 1 — Definición de la capacidad: cerrada.

Puerta 2 — Plan de implementación: cerrada.

Etapa A — contratos puros: completada.

Etapa B — validaciones cruzadas: completada.

Etapa C — generación trazable y revisable del Perfil Conversacional Inicial: implementación técnica completada y validada.

Validación de la Etapa C:

- 915 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `d0004fd`.

Pendiente para cerrar B177: documentación, publicación y verificación final de Git.

Etapa A — Contratos puros: implementada y validada.

Etapa B — Validaciones cruzadas: implementada y validada.

Capacidad objetivo: generar un Perfil Conversacional Inicial contextual, trazable y revisable para los perfiles de 6–8 años, 9–12 años, 13–17 años y adultos.

Piloto funcional previsto: niños de 9–12 años.

Siguiente etapa: generación trazable y revisable del Perfil Conversacional Inicial a partir de las evidencias diagnósticas validadas.

Límites vigentes: sin persistencia, migraciones, API, contenido piloto ni integración Flutter.

Commit técnico de la Etapa A: `6d4a52b`.

Commit técnico de la Etapa B: `e4e287c`.

## B178 — Sistematización profesional del método de trabajo

Estado: implementación técnica y documentación completadas.

B178 reduce el trabajo manual y repetitivo mediante dos herramientas:

- `scripts/engineering/operational_state.py`;
- `scripts/engineering/block_workflow.py`.

Capacidades incorporadas:

- validación estructural, temporal y de tamaño del checkpoint;
- detección de estado operativo anterior al último commit;
- resumen corto de último bloque, bloque activo y siguiente objetivo;
- orquestación sobre `block_close.py`;
- delegación de pruebas específicas, preflight y staging técnico;
- interrupción temprana cuando el contexto operativo es inválido.

Uso principal:

`python scripts/engineering/operational_state.py summary`

`python scripts/engineering/block_workflow.py --technical-preflight --specific-test <ruta>`

Validación:

- 8 pruebas específicas superadas;
- 923 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `c08196d`.

Los commits y el push continúan bajo confirmación humana.

## B179 — Diagnóstico conversacional persistente y consultable

Estado: bloque activo; Hito A cerrado técnicamente.

El Hito A incorporó modelos SQLAlchemy y la revisión Alembic `3c4f1a2b7d90` para las siete entidades principales del diagnóstico. Añadió las tablas normalizadas `conversational_diagnostic_activity_productions` y `conversational_diagnostic_observation_evaluations` para proteger:

- propiedad exclusiva actividad–producción;
- coincidencia de sesión, actividad, `prompt_id` y producción;
- integridad observación–evaluación–producción;
- perfiles iniciales históricos sin sobrescritura destructiva;
- producción obligatoria en las ocho dimensiones dependientes mediante `ck_diagnostic_observation_required_production`.

Validación técnica directa de respaldo:

- 14 pruebas específicas superadas;
- 7 pruebas de regresión relacionada superadas;
- 937 pruebas del backend superadas;
- migración validada mediante `upgrade` y `downgrade` aislados;
- `operational_state.py validate` correcto;
- `git diff --check` limpio;
- revisión final de Codex sin defectos accionables;
- commit técnico `40a30b3`.

El cierre mediante `block_workflow.py` no terminó correctamente: la interrupción perdió la salida final y dejó un proceso hijo que requirió detención manual. La validación final se ejecutó directamente en Kitty. Esta deuda operativa se tratará fuera de B179 Hito A.

Siguiente objetivo: Hito B, persistencia transaccional e historial consultable, incluida la conversión entre contratos Pydantic y tablas normalizadas.

Límites: sin API, Flutter, progreso ni mastery.

### Hito S1 — contrato ejecutable de seguridad DevSecOps

Estado: cerrado técnicamente.

S1 añadió una puerta preventiva y fail-closed que impide avanzar una operación potencialmente destructiva sin evidencia verificable de recuperación. Valida entorno e identidad no secreta del objetivo, backup regular y no vacío con SHA-256 correcto, restauración satisfactoria del backup exacto con antigüedad configurable, ensayo aislado con upgrade y downgrade, compatibilidad de revisiones y rollback explícito. Producción permanece siempre rechazada.

El núcleo no conecta a bases, ejecuta Alembic, crea o restaura backups, inicia procesos externos, accede a red ni sustituye una prueba real de restauración.

Validación:

- 17 pruebas específicas;
- 27 pruebas de regresión de ingeniería;
- suite backend: 954 passed in 2.89s;
- revisión de Codex sin defectos accionables;
- `operational_state.py validate` válido;
- `git diff --check` limpio;
- commit técnico `0472093`.

Estrategia transversal: LOGUIC English será el piloto. Tras validar backup y restauración reales en un entorno aislado, el núcleo común se extraerá a un repositorio independiente versionado y cada proyecto incorporará un adaptador propio; no se copiarán scripts manualmente. Proyectos previstos: CNAPP-Lite, AutoRadar ES, AgencyForge y otros.

Siguiente objetivo: diseñar S2, adaptador PostgreSQL seguro para backup y restauración aislada, sin aplicarlo todavía a datos reales.

### Hito S2 — adaptador PostgreSQL seguro

Estado: cerrado técnicamente mediante integración real aislada.

S2 añadió un adaptador para crear bajo `/tmp` un clúster PostgreSQL temporal con marcador, socket Unix, puerto dinámico distinto de `5432` y sin utilizar el servicio del sistema o la `DATABASE_URL` real. El flujo ejecuta backup custom, SHA-256, restauración en otra base, verificación determinista, upgrade Alembic hasta `3c4f1a2b7d90`, downgrade a la revisión inicial y limpieza comprobada. Alembic usa Psycopg 3 explícito mediante `postgresql+psycopg://`.

Codex preparó y revisó el código; la integración real se ejecutó directamente en Kitty para conservar observabilidad externa.

Validación:

- integración aislada: 1 passed in 2.47s; código 0;
- suite backend: 967 passed in 5.56s;
- sin procesos, sockets ni clústeres temporales residuales;
- `operational_state.py validate` correcto;
- `git diff --check` limpio;
- commit técnico `d0efe1e`.

S2 no autoriza migraciones sobre desarrollo, staging o producción reales. Siguiente objetivo funcional de B179: Hito B, persistencia transaccional e historial consultable.
