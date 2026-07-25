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
- B122 en cierre: contratos de producción personal, prompts obligatorios y evidencia `contextual_response` incorporados.
- Registrar una producción mediante texto o voz no implica todavía que sea correcta.
- La candidata permanece en `pending_approval` hasta disponer de persistencia, presentación y revisión de las producciones capturadas.
- El contenido candidato permanece separado del contenido pedagógico activo.
- El agente orquestador y MCP no están implementados y no se incorporarán antes de confirmar una necesidad real.

Evolución prevista:

- persistencia y presentación de producciones personales;
- reconocimiento de voz y palabras;
- evaluación semántica y fonética gradual;
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
