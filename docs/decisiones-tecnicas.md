# Decisiones técnicas del proyecto app-ingles-backend

## DT-001 — Backend modular con FastAPI

Se usa FastAPI como framework principal por su claridad, rendimiento y facilidad para construir APIs modernas.

## DT-002 — PostgreSQL como base de datos principal

Se usa PostgreSQL para persistencia relacional, escalabilidad y compatibilidad con una arquitectura profesional.

## DT-003 — SQLAlchemy como ORM

Se usa SQLAlchemy para separar la lógica Python del acceso directo a la base de datos.

## DT-004 — pytest como sistema de pruebas

Se usa pytest para validar endpoints y evitar regresiones conforme crece el backend.

## DT-005 — Documentación dentro del repositorio

La documentación se mantiene en la carpeta docs/ para que pueda versionarse con Git y abrirse desde Obsidian.

## DT-006 — Skill como unidad pedagógica medible

Se define `Skill` como una habilidad concreta que el estudiante debe desarrollar y que podrá medirse con ejercicios, intentos y estadísticas.

Esta decisión permite que el sistema evolucione desde una app basada solo en lecciones hacia una plataforma adaptativa capaz de identificar fortalezas, debilidades y recomendaciones personalizadas.

Inicialmente `Skill` se documenta a nivel conceptual. En bloques posteriores se implementará como schema, modelo de base de datos y endpoint.

## DT-007 — Relación Exercise-Skill muchos a muchos

Se define que la relación entre `Exercise` y `Skill` será de muchos a muchos.

Un ejercicio podrá entrenar o evaluar varias habilidades, y una habilidad podrá estar asociada a varios ejercicios.

Esta decisión permite calcular progreso por habilidad, detectar debilidades específicas y preparar futuras recomendaciones personalizadas.

La implementación podrá iniciar de forma simple con `skill_ids` dentro del contenido JSON y evolucionar más adelante hacia una tabla relacional `exercise_skills` en PostgreSQL.

## DT-008 — Contrato escalable para prácticas conversacionales

Las prácticas conversacionales se incorporan al contenido pedagógico mediante una lista opcional `conversations` dentro de cada lección.

Cada conversación contiene:

- un identificador estable;
- título y contexto;
- un modo de interacción;
- una secuencia ordenada de turnos.

Cada turno contiene:

- un identificador estable;
- el rol `partner` o `learner`;
- texto en inglés;
- traducción opcional;
- pronunciaciones regionales opcionales.

La primera implementación utiliza el modo `guided`.

B100 activa el modo `branching` mediante un contrato aditivo y compatible con las conversaciones guiadas existentes. El modo `free` continúa reservado para una evolución posterior y no incorpora todavía conversación libre ni inteligencia artificial.

Una conversación ramificada puede declarar:

- `start_turn_id` como punto de entrada estable;
- `next_turn_id` para transiciones deterministas;
- `ConversationChoice` para respuestas alternativas del estudiante;
- destinos diferentes, unión posterior de ramas y cierre explícito.

La integridad del grafo se valida al cargar el contenido con Pydantic. Se rechazan identificadores duplicados, referencias inexistentes, turnos inaccesibles, opciones en turnos que no pertenecen al estudiante, ramas con una sola opción, combinaciones ambiguas de `next_turn_id` y `choices`, y ciclos alcanzables.

Los identificadores estables permitirán asociar posteriormente:

- progreso conversacional;
- sesiones persistidas;
- reconocimiento de voz y palabras;
- puntuación automática;
- evaluación pedagógica;
- analítica;
- respuestas alternativas;
- generación dinámica mediante IA.

La lógica futura de reconocimiento, evaluación, persistencia e IA se mantendrá separada del contenido base. Se añadirá mediante contratos y servicios específicos, evitando convertir `Lesson` o `ConversationTurn` en modelos con responsabilidades mezcladas.

Esta decisión permite comenzar con conversación guiada determinista y evolucionar de forma aditiva sin reescribir las lecciones existentes.