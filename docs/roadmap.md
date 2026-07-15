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

Capacidad actual:

- conversación guiada mediante conversaciones y turnos con identificadores estables.

Evolución prevista:

- conversaciones ramificadas;
- respuestas alternativas;
- persistencia de sesiones conversacionales;
- reconocimiento de voz y palabras;
- puntuación automática;
- retroalimentación pedagógica;
- conversación libre.

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
