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

## Próximo frente pedagógico

Entrada A1 canónica — **HUMAN GATE 1 = APPROVED**. La aprobación define para alumnado con inglés muy bajo o nulo la primera capacidad instructiva de la progresión A1: responder oralmente a una intención comunicativa inmediata con contexto visual claro mediante una construcción propia Persona + Acción, pertinente e inteligible, y reutilizarla en una variación cercana con menos apoyo. Se aprueban método de construcción directa, audio y contexto visual, comprensión guiada, producción oral, pronunciación funcional, microinteracción, retirada progresiva de apoyo, español solo como rescate opcional y evidencia oral propia de pertinencia, construcción e inteligibilidad.

La única autorización siguiente es preparar Puerta 2: definir el marco mínimo de unidad, capacidades existentes reutilizables y brechas técnicas realmente demostradas. No se asigna un identificador nuevo ni se autoriza contenido, implementación, activación, loader o reanudación de B181.
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

Estado: bloque cerrado técnica e integralmente; Hitos A, S1, S2 y B cerrados.

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

S2 añadió un adaptador para crear bajo `/tmp` un clúster PostgreSQL temporal con marcador, socket Unix, puerto dinámico distinto de `5432` y sin utilizar el servicio del sistema o la `DATABASE_URL` real. El flujo ejecuta backup custom, SHA-256, restauración en otra base, verificación determinista, upgrade Alembic desde la frontera histórica `f81a78f8c1c4` hasta el único head resuelto, downgrade y limpieza comprobada. Alembic usa Psycopg 3 explícito mediante `postgresql+psycopg://`.

Codex preparó y revisó el código; la integración real se ejecutó directamente en Kitty para conservar observabilidad externa.

Validación:

- integración aislada: 1 passed in 2.47s; código 0;
- suite backend: 967 passed in 5.56s;
- sin procesos, sockets ni clústeres temporales residuales;
- `operational_state.py validate` correcto;
- `git diff --check` limpio;
- commit técnico `d0efe1e`.

S2 no autoriza migraciones sobre desarrollo, staging o producción reales. Siguiente objetivo funcional de B179: Hito B, persistencia transaccional e historial consultable.

### Hito B — persistencia transaccional incremental

Estado final: Hito B cerrado técnicamente mediante sus incrementos 1–3, 4A y 4B.

Se añadió `ConversationalDiagnosticSessionSetup` y las operaciones públicas `save_conversational_diagnostic_session_setup(setup, db)` y `get_conversational_diagnostic_session_setup(diagnostic_session_id, db)`. El alcance actual cubre sesión, contexto y actividades.

La escritura valida antes del primer `add`, rechaza duplicados sin idempotencia implícita, utiliza tres `flush`, exactamente un `commit` y rollback ante cualquier fallo. La lectura reconstruye Pydantic desde SQLAlchemy, conserva el orden por `sequence_order` y `activity_id`, no ejecuta commit ni usa lazy loading.

Validación: 16 pruebas específicas, 190 de regresión diagnóstica, suite backend 983 passed in 5.55s, `operational_state.py validate` correcto, `git diff --check` limpio, revisión sin defectos accionables y commit `56a3d42`.

El segundo incremento añadió `ConversationalDiagnosticActivityProductionSetup`, `ConversationalDiagnosticProductionSupportsBatch` y `production_supports=[]` al agregado existente. Permite persistir propiedad actividad–producción y apoyos durante la creación o enriquecer después una sesión mediante `save_conversational_diagnostic_production_supports(batch, db)`.

Las producciones deben existir previamente y solo se consultan. La escritura valida sesión, actividad, `prompt_id`, modalidad, propiedad exclusiva, asociaciones existentes y la secuencia histórica de apoyos; rechaza sobrescritura e idempotencia implícita. La creación conserva sus tres `flush` de configuración y añade dos para asociaciones y apoyos; el enriquecimiento usa estos dos últimos. Ambas rutas realizan exactamente un commit y rollback integral. La lectura recupera todo explícitamente, en orden estable, sin lazy loading ni commit.

Validación del segundo incremento: 41 pruebas específicas en 0.72 s, 190 de regresión diagnóstica en 1.29 s, suite backend 1008 passed in 5.60s, `operational_state.py validate` correcto, `git diff --check` limpio, revisión sin defectos accionables y commit `719aa74`. No se modificaron modelos ni migraciones.

El tercer incremento añadió `ConversationalDiagnosticObservationsBatch`, `observations=[]` y `save_conversational_diagnostic_observations(batch, db)`. Permite incluir observaciones durante la creación o enriquecer después una sesión, validando antes del primer `add` su sesión, actividad, producción propietaria, apoyos reales, contexto motivador y evaluaciones técnicas preexistentes.

`evaluation_result_ids` se conserva en Pydantic y se convierte en enlaces normalizados; la lectura lo reconstruye en orden ascendente. Las evaluaciones nunca se crean, modifican o eliminan y pueden respaldar varias observaciones compatibles. Observaciones y enlaces usan dos `flush`, exactamente un commit y rollback integral. La lectura es explícita y ordenada, sin lazy loading ni commit.

Validación del tercer incremento: 69 pruebas específicas en 1.28 s, 190 de regresión diagnóstica en 1.35 s, suite backend 1036 passed in 6.10s, `operational_state.py validate` correcto, `git diff --check` limpio, revisión sin defectos accionables y commit `f30887f`. No se modificaron modelos ni migraciones.

El Incremento 4A añadió una máquina de estados explícita mediante `ConversationalDiagnosticSessionTransition` y `transition_conversational_diagnostic_session(command, db)`. Toda sesión nueva comienza `in_progress`; puede pasar a provisional, completed o cancelled, y provisional puede pasar a completed o cancelled. Completed y cancelled son terminales, sin reapertura, repetición ni idempotencia implícita.

El comando aporta estado esperado y timestamp explícitos. La actualización condicional exige coincidencia de sesión y estado, además de `rowcount == 1`; realiza exactamente un commit y rollback integral. Completed exige la cobertura completa compartida con perfiles confirmados. La transición no genera perfiles ni modifica evidencia diagnóstica. `completed_at` representa el cierre actual y no se conserva historial de transiciones.

Validación de 4A: 88 pruebas de validación, 85 de persistencia, 20 de perfiles, 82 de esquemas, 14 de persistencia relacional y suite backend 1066 passed in 6.66s. `operational_state.py validate` correcto, `git diff --check` limpio, revisión sin defectos accionables y commit `94a620e`. No se modificaron modelos ni migraciones.

El Incremento 4B añadió `InitialConversationalProfileSetup`, `ConversationalDiagnosticProfilesBatch`, `profiles=[]` y `save_conversational_diagnostic_profiles(batch, db)`. Los perfiles ya generados se incorporan solo por enriquecimiento posterior: provisional con provisional y completed con confirmed; in_progress y cancelled se rechazan.

La persistencia es append-only, admite varios perfiles históricos con identificadores distintos y rechaza duplicados, sobrescritura e idempotencia implícita. Las evidencias son obligatorias, únicas y apuntan a observaciones preexistentes de la misma sesión; una observación puede reutilizarse entre perfiles sin modificarse. Los perfiles confirmed exigen cobertura completa. `first_lesson_id` se conserva sin consultar contenido.

La escritura valida antes del primer `add`, realiza dos `flush`, exactamente un commit y rollback integral. La lectura reconstruye perfiles por `generated_at` y `profile_id` y sus evidencias por orden diagnóstico, sin lazy loading, commit ni reinterpretación histórica.

Validación de 4B: 105 pruebas de persistencia, 20 de perfiles, 88 de validación, 82 de esquemas y 14 relacionales; 309 relacionadas en 3.17 s, marcador `B179_HITO_B_INCREMENTO_4B_VALIDATED`, revisión sin defectos accionables y commit `c9e3bab`. No se modificaron modelos ni migraciones.

Hito B queda cerrado técnicamente: `get_conversational_diagnostic_session_setup` ofrece el historial interno estructurado y ordenado de configuración, producciones y apoyos, observaciones y evaluaciones, y perfiles con evidencias. No se requiere otro incremento interno para el alcance comprometido.

Límites: sin historial de transiciones, API, Flutter, progreso, mastery, retención ni adaptación. S2 no autoriza bases reales.

### Cierre integral de B179

B179 queda cerrado técnica e integralmente. Hito A aportó el modelo normalizado y la migración `3c4f1a2b7d90` (`40a30b3`); S1, la puerta preventiva fail-closed (`0472093`); S2, el ensayo PostgreSQL aislado y reversible (`d0efe1e`); Hito B, la configuración transaccional (`56a3d42`), producciones y apoyos (`719aa74`), observaciones y evaluaciones (`f30887f`), transición condicional (`94a620e`) y perfiles append-only (`c9e3bab`).

La validación final directa en Kitty registró 1086 pruebas backend superadas en 6.93 s, `operational_state.py validate` correcto, `git diff --check` limpio, Git sincronizado en `master...origin/master` y marcador `B179_INTEGRAL_VALIDATED`.

Permanecen fuera API, Flutter, progreso, mastery, retención, adaptación automática, historial persistente de transiciones y operaciones sobre bases reales. El próximo objetivo es diseñar un bloque desde una capacidad observable del estudiante y el modelo pedagógico maestro; el historial técnico no selecciona automáticamente dicho bloque.

## B180 — Construcción directa en inglés

Estado: bloque cerrado técnica e integralmente; Incrementos 1, 2, 3 y 4 cerrados, documentados y publicados.

La capacidad observable de B180 es construir oralmente una respuesta directamente en inglés desde una intención comunicativa, ampliarla con información pertinente y transferir el patrón ante una variación inesperada con ayuda mínima, sin copiar una frase completa.

### Incremento 1 — primera lección

`a1-u1-l1` mantiene su identificador y adopta el título `Introduce yourself directly`. Reutiliza la Skill `a1_introduce_yourself`, la situación de conocer a una persona y el andamio Persona + Verbo. La experiencia queda organizada en cinco etapas: modelo consciente con refuerzo fonético, construcción guiada, ampliación, transferencia inesperada y cierre.

Las tres evidencias son `guided`, `expanded` y `transfer`. Voz es la modalidad principal y texto solo respaldo. La ayuda disminuye de `anchors` a `initial_word` y `none`; ampliación y transferencia no admiten un modelo completo. Un banco validable aporta cuatro preguntas relacionadas de transferencia, sin implementar todavía su selección en runtime.

La política de corrección limita cada producción a una orientación y ordena las prioridades como pertinencia, construcción directa, inteligibilidad y precisión secundaria. El incremento representa y valida esta política, pero no selecciona automáticamente una corrección.

El refuerzo fonético reutiliza audio e IPA en-US/en-GB para escucha breve, seguimiento de ritmo, shadowing y el objetivo `/iː/` cuando aparece naturalmente. Es preparatorio y no cuenta como transferencia independiente. El Karaoke Fonético permanece pospuesto, no descartado: una capacidad futura aislada podrá incorporar audio sincronizado, texto, fonemas, colores, shadowing, dictado y grabación, sin que B180 implemente ahora ese motor o su interfaz.

Los contratos retrocompatibles incorporan función pedagógica, modalidad principal y de respaldo, nivel de apoyo, permiso de modelo completo, banco de variantes, política de corrección y refuerzo de pronunciación. Un validador puro comprueba estructura, secuencia, evidencias, retirada de apoyos, modalidades, transferencia y finalización sin clasificar significado libre, progreso o mastery.

Validación final: suite backend 1104 passed in 9.20s, `operational_state.py validate` correcto, `git diff --check` limpio, revisión sin defectos accionables y commit técnico `ccafaaa`.

Al cierre del Incremento 1 permanecían fuera la selección runtime de variantes, comprobación semántica de ampliación y transferencia, captura efectiva de modalidad y apoyo, selección real de la corrección, persistencia adicional no demostrada, API, Flutter, progreso, mastery y adaptación automática.

El siguiente incremento entonces recomendado fue una ejecución pedagógica interna mínima que seleccionara una variante de transferencia y registrara modalidad y apoyo realmente utilizados, manteniendo separada cualquier futura evaluación semántica.

### Incremento 2 — ejecución pedagógica interna

Se incorporaron `DirectEnglishConstructionAttempt` y `DirectEnglishConstructionAttemptProduction`, con la revisión Alembic lineal `7d8e9f0a1b2c`. Las operaciones internas permiten iniciar, finalizar y recuperar un intento completo sin crear una representación paralela de la producción: `LearnerProduction` continúa siendo la única producción real y su `modality`, la fuente de modalidad utilizada.

La transferencia se selecciona de forma determinista mediante SHA-256 sobre `selector_version + attempt_id + lesson_id + transfer_bank_id`. El intento conserva el snapshot exacto de banco, variante, prompt y versión `sha256-v1`; no usa azar ni vuelve a seleccionar una variante histórica. Cada enlace registra por separado el apoyo configurado y el realmente utilizado.

`completion_requirements_met` se calcula al reconstruir el intento. Solo expresa si existen guided, expanded y transfer, las tres son de voz, no exceden el apoyo previsto y transfer se realizó sin apoyo. El texto y el apoyo adicional se conservan como hechos, pero producen `false`; este resultado no evalúa significado, aprendizaje, progreso o mastery.

La escritura reutiliza un helper transaccional sin commit de la persistencia de conversación, mantiene exactamente un commit público y rollback integral. Permanecen fuera evaluación semántica, pertinencia, literalidad, corrección automática, API, Flutter, progreso, mastery, adaptación y Karaoke Fonético.

Validación: 34 pruebas específicas; 148 relacionadas y 1 omitida; suite backend 1149 passed in 9.59s; migración focal PostgreSQL 1 passed in 2.30s; ensayo S2 completo reversible hasta el head; revisión sin defectos accionables; commit `f77f560`.

Al cierre del Incremento 2 se recomendó registrar y recuperar una única orientación pedagógica prioritaria por producción, aportada explícitamente y sin selección automática, evaluación semántica, API o Flutter.

### Incremento 3 — orientación pedagógica prioritaria

Se añadió `DirectEnglishConstructionProductionOrientation` y la revisión `a4c8e2f6b901`, enlazando cada orientación exclusivamente con `DirectEnglishConstructionAttemptProduction`. La tabla no duplica intento, producción, función, modalidad o apoyo. Admite cero o una orientación por enlace y rechaza toda segunda escritura, actualización, borrado, sobrescritura o idempotencia implícita.

`DirectEnglishConstructionOrientationCreate`, su record y `save_direct_english_construction_orientation` conservan una decisión ya tomada: prioridad, guidance exacta de hasta 2000 caracteres, fuente no secreta y timestamp. `human` permite versión opcional; `external` exige versión. La lectura incorpora la orientación opcional a guided, expanded y transfer sin inferir ausencias ni recalcular decisiones.

La prioridad debe pertenecer a la `CorrectionGuidancePolicy` activa, pero el backend no decide cuál es correcta. `ProductionFeedback` no se reutiliza porque depende de evaluación técnica y representa otro historial. Se preservan orientación ≠ evaluación semántica o técnica ≠ verdad pedagógica ≠ progreso o mastery.

Validación: PostgreSQL focal 1 passed in 2.48s para `7d8e9f0a1b2c → a4c8e2f6b901 → 7d8e9f0a1b2c`; S2 completo 1 passed in 2.38s desde el límite histórico `f81a78f8c1c4`; suite backend 1171 passed in 10.30s; revisión sin defectos; commit `2f396d3`.

La infraestructura interna quedó suficiente para dejar de añadir persistencia por defecto: contenido validado, intento completo, producciones reales, modalidad, apoyo, transferencia y orientación trazable. El Incremento 4 posterior asumió la brecha pedagógica restante: presentar una sola orientación antes de una nueva producción y retirar otra vez el apoyo, sin selección automática, evaluación, API o Flutter.

### Incremento 4 — preparación de reintento guiado

`DirectEnglishConstructionRetryPreparationRequest`, `DirectEnglishConstructionRetryPreparation` y `prepare_direct_english_construction_retry` preparan, mediante lectura explícita, un nuevo intento completo a partir de una producción guided, expanded o transfer de un intento finalizado y de su única orientación registrada. La operación devuelve conversación, prompt, apoyo configurado y usado y el foco de orientación, pero no crea `attempt_id`, escribe datos ni modifica intento, producción u orientación.

El apoyo usado retrocede un peldaño (`model → anchors → initial_word → none`) y el resultado se limita al nivel que ofrezca menos ayuda frente al apoyo configurado. Transfer siempre queda en `none`; conserva banco, variante y prompt anteriores solo como trazabilidad e indica `new_attempt_selector`, de modo que el nuevo `attempt_id` usará el selector SHA-256 existente y puede seleccionar de nuevo la misma variante sin lógica adaptativa.

Presentar la orientación no demuestra que se aplicó ni que hubo mejora. El nuevo intento continúa siendo completo y append-only mediante `start` y `finalize` existentes. No se añadieron persistencia, modelos, Alembic o S2. Validación: 71 pruebas focales, 50 de regresión pura/SQLite, suite backend 1191 passed in 10.33s, validaciones operativas correctas, revisión sin defectos y commit `70c3dbf`.

Con este incremento, el ciclo interno `contenido → producción → orientación → preparación con menor apoyo → nuevo intento` cubre el objetivo técnico y pedagógico interno de B180. No queda una capacidad observable imprescindible que justifique un Incremento 5. API, Flutter, evaluación semántica, progreso, mastery, adaptación y Karaoke Fonético permanecen fuera.

### Cierre integral de B180

B180 queda cerrado técnica e integralmente. El Incremento 1 aportó contenido y validación (`ccafaaa`); el 2, ejecución, trazabilidad y la migración `7d8e9f0a1b2c` (`f77f560`); el 3, orientación prioritaria append-only y el head `a4c8e2f6b901` (`2f396d3`); y el 4, preparación read-only del reintento con menor apoyo (`70c3dbf`).

La validación final registra suite backend 1191 passed in 10.33s, migraciones focales PostgreSQL y S2 completo validados, `operational_state.py validate` correcto y `git diff --check` limpio. `completion_requirements_met`, la orientación y la preparación preservan sus fronteras: estructura no es mastery, orientación presentada no es aplicación demostrada y reintento preparado no es mejora.

La siguiente brecha observable recomendada, todavía sin número, es comprender la intención principal de una intervención oral nueva, responder de manera contingente y mantener un intercambio breve con ayuda reducida. Debe preceder a más infraestructura porque conecta la construcción directa ya lograda con escucha, reacción y continuidad conversacional. Quedan fuera persistencia no demostrada, API, Flutter, progreso, mastery, adaptación automática y Karaoke Fonético completo.

## B181 — Comprensión contingente y continuidad conversacional breve

Estado: Incrementos 1, 2, 3 y 4 cerrados y publicados; B181 integral permanece **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**.

La capacidad observable es escuchar tres intervenciones breves relacionadas de una persona recién conocida, identificar suficientemente su intención comunicativa, responder oralmente con palabras propias y mantener tres intercambios conectados hasta una reacción o cierre natural, con apoyo visible decreciente.

### Incremento 1 — conversación breve conectada

`a1-u1-l2` adopta el título `Keep the conversation going` y la nueva Skill `a1_maintain_short_connected_exchange`; `a1-u1-l1` permanece sin cambios. `a1-u1-l2-c1` contiene siete turnos, tres producciones propias y cuatro intervenciones del interlocutor: pregunta de procedencia, pregunta por intereses, seguimiento inesperado relacionado y reacción/cierre natural.

La experiencia prioriza voz y presenta el audio antes del transcript. El transcript comienza oculto y solo actúa como contingencia o accesibilidad; cuando se usa, la comprensión es asistida y no exclusivamente auditiva. Los apoyos visibles disminuyen `anchors → initial_word → none`; la tercera producción es `unexpected_contingent_response`, el seguimiento inesperado y el cierre quedan marcados explícitamente y ninguna producción permite copiar un modelo completo.

Las evidencias `a1-u1-l2-ev-place-response`, `a1-u1-l2-ev-interest-response` y `a1-u1-l2-ev-unexpected-followup-response` se asocian una a una con los prompts. Cada una declara revisión humana o externa estática de `intention_understanding` y `contingent_response`, con estados `positive | negative | pending`. Ambas dimensiones necesitan `positive`; `negative` o `pending` impiden considerar satisfecha la revisión, sin crear progreso o mastery automático.

El backend solo valida la estructura prevista. No persiste juicios ni infiere comprensión real, pertinencia semántica, contingencia real, no literalidad, progreso, aprendizaje, mastery o fluidez; finalización estructural no equivale a éxito pedagógico. No se añadieron persistencia, modelos SQLAlchemy, Alembic, S2, API ni Flutter runtime. Karaoke Fonético continúa pospuesto, no descartado.

Trazabilidad backend: `c246876`. La suite backend completa posterior al cambio terminó correctamente y `git diff --check` pasó, sin un número de tests disponible que deba reconstruirse. Trazabilidad frontend de audios: `8235449`, ya publicado; `flutter analyze` correcto, 37 tests passed en `flutter test` y `git diff --check` limpio.

Los ocho WAV en-US/en-GB correspondientes a t1, t3, t5 y t7 fueron escuchados y aprobados humanamente. Todos cumplen PCM s16le, 22050 Hz, mono y 16-bit, y las ocho rutas backend coinciden exactamente con los ocho assets físicos del frontend.

### Incremento 2 — ejecución audio-first y persistencia de producciones

Flutter ejecuta `a1-u1-l2-c1` completa: cada transcript comienza oculto, solo puede revelarse tras escuchar al menos una vez y el audio puede repetirse. El transcript continúa siendo contingencia o accesibilidad y comprensión asistida. Los tres prompts muestran exactamente `anchors → initial_word → none`, sin reconstruir respuestas completas.

Las tres grabaciones se conservan por `prompt_id` y `turn_id` hasta el envío. La infraestructura backend existente recibe tres uploads mediante `/conversation-production-audio` y una única `ConversationProductionSubmission` mediante `/conversation-productions`; no hubo cambios backend ni almacenamiento paralelo. B181 `free` no utiliza `conversation-attempts`, mientras `guided` y `branching` conservan su persistencia anterior.

Trazabilidad frontend publicada: implementación `8baf7a6` y documentación `4fe98ad`; Git final `## master...origin/master`. Validación: 9 pruebas focales finales, `flutter analyze` correcto, 36 pruebas de regresión relacionada, suite frontend completa 39 passed, `git diff --check` limpio y Postflight de compatibilidad superado.

Persistir las tres respuestas y completar el recorrido no demuestra comprensión, pertinencia, progreso, mastery o fluidez; el reconocimiento técnico tampoco es evaluación pedagógica. Permanecen fuera uso persistido del transcript, fallback textual, resultados efectivos de revisión, rollback remoto de WAV parciales, scoring, semántica automática, adaptación y Karaoke Fonético.

### Incremento 3 — revisión efectiva independiente

`ShortConnectedExchangeProductionReview` registra historiales append-only de `intention_understanding` y `contingent_response` con resultados `positive | negative | pending`, fuente humana o externa y trazabilidad temporal. Cada fila enlaza directamente con `LearnerProduction.id`; no duplica identidad derivable. Múltiples revisiones pueden coexistir para una producción y dimensión, sin update, overwrite, consenso, mayoría o resultado vigente.

La escritura valida referencias, las tres producciones canónicas y la rúbrica activa antes de insertar hasta las seis decisiones en un batch con un commit y rollback integral. La lectura recupera las tres producciones y todo el historial ordenado, sin agregar, priorizar ni transformar resultados.

La revisión `b181c3e4f5a6` sucede linealmente a `a4c8e2f6b901` y añade PK, FK con cascade, checks e índices de producción e historial, deliberadamente sin unicidad `production_id + dimension`. S2 descubrió el nuevo head sin cambios de adaptador o frontera. Validación: 22 focales; regresiones 122 y 149 passed con 1 deselected en el Postflight; PostgreSQL focal 1 passed in 2.31s; S2 unitario 22 passed y 1 deselected; S2 completo 1 passed in 2.33s; suite backend final 1230 passed in 13.38s; `git diff --check` limpio. Commit técnico `21d34e5`.

Revisión no es evaluación técnica, diagnóstico u orientación B180; ningún resultado crea consenso, fracaso global, progreso o mastery. Permanecen fuera API, Flutter, transcript persistido, fallback textual, rollback remoto de WAV, scoring, semántica o comprensión automáticas, aprendizaje, fluidez, adaptación y Karaoke Fonético. B180 y el contenido y rúbrica B181 permanecen intactos.

### Incremento 4 — revisión humana local controlada

La CLI `scripts/review/short_connected_exchange_review.py` y el servicio read-only asociado permiten a un revisor humano local, identificado mediante una etiqueta declarada pero no autenticada, seleccionar una submission real de `a1-u1-l2-c1`. La preparación exige sus tres producciones canónicas de voz y deriva del contenido activo las intervenciones, evidencias, preguntas y resultados permitidos, sin duplicar la rúbrica.

Los tres WAV se resuelven mediante `resolve_production_audio_path`, conservando URI opaca, UUID, directorio privado, confinamiento y existencia. La consola muestra la ruta local para reproducción externa, pero no la persiste ni incorpora reproductor. Tampoco muestra o usa `recognized_text`, scoring, evaluación técnica, feedback, diagnóstico, progreso o mastery.

La CLI recoge en memoria las seis decisiones de `intention_understanding` y `contingent_response`, presenta el lote y exige confirmación. Una única llamada persiste el `ShortConnectedExchangeProductionReviewBatch`; después se recupera todo el historial append-only, sin consenso, mayoría o resultado vigente. Cancelar antes de confirmar no escribe y no existe retry automático. Commit técnico `6a67763`.

La corrección transversal DevSecOps `687e394` añadió un wrapper que ejecuta pytest contra un PostgreSQL efímero: workspace S2 marcado, socket confinado, puerto dinámico distinto de 5432, base `isolated_pytest`, `alembic upgrade head` y `DATABASE_URL` inyectada antes de colección. Rechaza `app_ingles_db`, usa subprocess con `shell=False`, propaga el exit code y limpia en `finally`, sin modificar el adaptador S2 o su frontera histórica.

Validación: 50 pruebas focales y dependencias SQLite; 21 relacionadas con contenido y producciones; PostgreSQL aislado 8 passed in 0.32s; wrapper 12 passed in 0.19s; suite backend completa aislada 1262 passed in 12.38s; `git diff --check` limpio y EOF correcto. No cambiaron modelos, migraciones, endpoints, contenido B181, B180, persistencia I3, Flutter ni S2.

Revisión local no es identidad autenticada, reconocimiento, evaluación técnica, consenso o resultado vigente; `positive`, `negative` y `pending` no crean progreso, mastery o fracaso global. API, HTTP, Flutter, panel administrativo, autenticación, integración externa, reproductor, semántica automática, adaptación, fallback textual, transcript persistido, rollback remoto de WAV y Karaoke Fonético permanecen fuera.

B181 ya demostró una revisión humana real mediante la CLI sobre la submission `555`, las producciones `1663`–`1665` y tres WAV reales. La primera validación no superó la rúbrica y reveló un defecto UX posteriormente corregido de forma local; una segunda validación confirmó la comprensión de la nueva microcopy y se pausó antes de completarse al detectarse una carencia pedagógica más profunda.

La pausa no responde a un fallo técnico pendiente. `a1-u1-l1` debe entenderse en este recorrido como prototipo/candidato histórico utilizado para desarrollar y validar infraestructura pedagógica, contratos y runtime, no como la futura entrada A1 canónica ni como una L1 definitiva fallida. Por ello no se planifica un parche manual L1→L2 para hacer pasar B181.

La dirección inmediata, sin abrir ni numerar un nuevo bloque, es revisar el Constructor Pedagógico existente y determinar cómo deberá generar y validar progresiones reales y mapas de prerrequisitos. Después deberán construirse canónicamente la entrada A1 y el candidato pedagógico necesario para B181 antes de reanudar su validación humana.

El retry de persistencia B181 y la corrección UX consigna ≠ respuesta están versionados y publicados en frontend mediante el commit técnico `aabe4a4`; el commit documental frontend es `505549f`. Las validaciones asociadas permanecen: test focal PASS, `flutter analyze` PASS, `git diff --check` PASS y suite frontend completa 44 passed. Esta publicación no modifica la pausa pedagógica ni su condición de reanudación.
