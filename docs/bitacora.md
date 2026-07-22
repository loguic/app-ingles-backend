# Bitácora del proyecto app-ingles-backend

## Estado actual

- Backend: FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy
- Driver: psycopg
- Tests actuales: 12
- Último bloque cerrado: B38

## Historial anterior — B24 a B36

### B24 — Primera prueba automatizada

- Objetivo: instalar/configurar pytest y crear la primera prueba para `/health`.
- Resultado: endpoint `/health` validado con prueba automatizada.

### B25 — Configuración de pytest

- Objetivo: configurar `pytest.ini`.
- Resultado: las pruebas se pueden ejecutar de forma ordenada desde la raíz del proyecto.

### B26 — Prueba de niveles

- Objetivo: probar `/api/v1/levels`.
- Resultado: endpoint de niveles validado.

### B27 — Prueba de lección por ID

- Objetivo: probar `/api/v1/content/lessons/a1-u1-l1`.
- Resultado: recuperación de lección validada.

### B28 — Prueba de ejercicios

- Objetivo: probar `/api/v1/exercises/a1-u1-l1-q1/submit`.
- Resultado: evaluación de respuesta correcta validada.

### B29 — Prueba POST progress

- Objetivo: probar guardado de progreso.
- Resultado: progreso de usuario guardado correctamente.

### B30 — Prueba GET progress

- Objetivo: probar lectura de progreso por usuario.
- Resultado: registros de progreso recuperados correctamente.

### B31 — Prueba de estadísticas

- Objetivo: probar `/api/v1/progress/{user_id}/stats`.
- Resultado: estadísticas de intentos y precisión calculadas correctamente.

### B32 — Limpieza manual de datos de prueba

- Objetivo: eliminar registros `test-user-%` desde PostgreSQL.
- Resultado: base de datos limpia para pruebas.

### B33 — Fixture automático de limpieza

- Objetivo: limpiar registros de prueba antes y después de ejecutar tests.
- Resultado: pruebas más seguras y repetibles.

### B35 — Pruebas faltantes de contenido

- Objetivo: cubrir endpoints faltantes de contenido.
- Endpoints probados:
  - `/api/v1/content/tree`
  - `/api/v1/content/levels/A1`
  - `/api/v1/content/levels/A1/units`
  - `/api/v1/content/units/a1-u1`
  - `/api/v1/content/units/a1-u1/lessons`
- Resultado: cobertura de contenido ampliada.
- Commit: 579f505

### B36 — Verificación general

- Objetivo: verificar estado general del proyecto.
- Resultado:
  - Tests: 12 passed.
  - Git limpio.
  - GitHub sincronizado.

## B37 — Documentación base del proyecto

- Objetivo: crear una estructura profesional de documentación dentro del repositorio.
- Archivos creados:
  - docs/bitacora.md
  - docs/arquitectura.md
  - docs/decisiones-tecnicas.md
  - docs/roadmap.md
- Resultado: documentación base creada y versionada.
- Commit: 2488ce4

## B38 — Revisión arquitectónica inicial

- Objetivo: revisar la estructura actual del backend.
- Hallazgos:
  - La API está organizada bajo app/api/v1/.
  - Los endpoints están separados por dominio funcional.
  - La lógica principal está en services/.
  - Los schemas están en schemas/.
  - La base de datos está en db/.
- Mejora aplicada: se agregó .pytest_cache/ a .gitignore.
- Tests: 12 passed.
- Commit: 37fffbd

## B39 — Documentación de hallazgos arquitectónicos

- Objetivo: registrar en documentación los hallazgos de la revisión arquitectónica.
- Archivos modificados:
  - docs/arquitectura.md
  - docs/bitacora.md
- Resultado: hallazgos de B38 documentados y bitácora reordenada.
- Commit: 8b29402

## B40 — Diseño conceptual de Skill

- Objetivo: definir `Skill` como unidad pedagógica medible.
- Archivos modificados:
  - docs/arquitectura.md
  - docs/decisiones-tecnicas.md
  - docs/roadmap.md
- Resultado parcial: `Skill` fue documentada como entidad pedagógica antes de implementarla en código.

## B41 — Diseño conceptual de relación Exercise-Skill

- Objetivo: definir cómo los ejercicios se conectan con habilidades medibles.
- Decisión principal: la relación `Exercise-Skill` será de muchos a muchos.
- Archivos modificados:
  - docs/arquitectura.md
  - docs/decisiones-tecnicas.md
- Resultado parcial: relación pedagógica documentada antes de implementar código.

## B42 — Registro de intentos reales del usuario

- Objetivo: enriquecer el registro de progreso con contexto pedagógico.
- Campos añadidos:
  - level_id
  - unit_id
  - lesson_id
- Archivos modificados:
  - app/db/models.py
  - app/schemas/progress.py
  - app/services/progress_service.py
  - tests/test_progress.py
  - docs/arquitectura.md
- Error encontrado:
  - PostgreSQL no tenía todavía las columnas nuevas.
- Corrección aplicada:
  - Se añadieron las columnas faltantes a la tabla user_progress.
- Resultado:
  - Tests: 12 passed.

## B43 — Base para calcular dominio por habilidad

- Objetivo: preparar el contenido para calcular dominio por habilidad.
- Cambios realizados:
  - Se agregó `skill_ids` al schema `ExerciseMCQ`.
  - Se asociaron habilidades al ejercicio `a1-u1-l1-q1`.
- Skills asociadas:
  - a1_greetings_basic
  - a1_vocabulary_greetings
- Archivos modificados:
  - app/schemas/content.py
  - content/content_tree.json
  - docs/arquitectura.md
- Resultado parcial: los ejercicios ya pueden declarar qué habilidades entrenan.

## B44 — Recomendaciones básicas de progreso

- Objetivo: preparar una recomendación básica basada en la precisión del usuario.
- Endpoint creado:
  - GET /api/v1/progress/{user_id}/recommendation
- Lógica inicial:
  - Sin intentos: recomendar iniciar la primera lección.
  - Accuracy menor a 0.70: recomendar repasar.
  - Accuracy igual o mayor a 0.70: recomendar continuar.
- Archivos modificados:
  - app/api/v1/endpoints/progress.py
  - app/schemas/progress.py
  - app/services/progress_service.py
  - tests/test_progress.py
- Tests: 13 passed.

## B45 — Revisión de estado y orden del modelo adaptativo

- Objetivo: revisar el estado actual del proyecto y ordenar la siguiente fase.
- Resultado:
  - Fase 1 marcada como completada a nivel inicial.
  - Fase 2 marcada como completada a nivel inicial.
  - Fase 3 definida como siguiente fase del sistema adaptativo.
- Próximos bloques:
  - B46: diseñar mastery_score por habilidad.
  - B47: crear endpoint de dominio por habilidad.
  - B48: mejorar recomendaciones usando habilidades débiles.
  - B49: preparar sistema básico de repaso.
  - B50: documentar cierre de fase adaptativa inicial.

## B46 — Diseño y lógica base de mastery_score por habilidad

- Objetivo: diseñar y preparar el cálculo de dominio por habilidad.
- Fórmula inicial:
  - mastery_score = correct_attempts / total_attempts
- Cambios realizados:
  - Se documentó el diseño de mastery_score en arquitectura.
  - Se agregó el schema SkillMastery.
  - Se creó get_skill_ids_by_exercise_id().
  - Se creó get_skill_mastery().
- Resultado parcial:
  - El backend ya puede calcular dominio de una habilidad a nivel de servicio.
- Siguiente paso:
  - B47: exponer el cálculo mediante un endpoint.

## B47 — Endpoint de dominio por habilidad

- Objetivo: exponer por API el cálculo de mastery_score creado en B46.
- Endpoint creado:
  - GET /api/v1/progress/{user_id}/skills/{skill_id}/mastery
- Cambios realizados:
  - Se agregó el endpoint read_skill_mastery().
  - Se agregó una prueba automática para validar el cálculo.
- Resultado:
  - Tests: 14 passed.

## B48 — Mejora inicial de recomendaciones con habilidades débiles

- Objetivo: mejorar el mensaje de recomendación usando lenguaje pedagógico basado en habilidades.
- Cambio realizado:
  - Cuando la precisión general es menor a 0.70, el sistema recomienda revisar habilidades débiles.
- Mensaje actualizado:
  - Review weak skills before moving forward.
- Resultado:
  - Tests: 14 passed.

## B49 — Sistema básico de repaso

- Objetivo: preparar una base simple para recomendar repaso por habilidad.
- Schema creado:
  - ReviewRecommendation
- Servicio creado:
  - get_review_recommendation()
- Endpoint creado:
  - GET /api/v1/progress/{user_id}/skills/{skill_id}/review
- Regla inicial:
  - Si mastery_score < 0.70, la habilidad debe repasarse.
  - Si mastery_score >= 0.70, puede continuar.
- Resultado:
  - Tests: 15 passed.

## B50 — Cierre de fase adaptativa inicial

- Objetivo: cerrar formalmente la fase adaptativa inicial.
- Bloques incluidos:
  - B45: orden del modelo adaptativo.
  - B46: mastery_score por habilidad.
  - B47: endpoint de dominio por habilidad.
  - B48: mejora inicial de recomendaciones usando habilidades débiles.
  - B49: sistema básico de repaso por habilidad.
- Resultado:
  - El backend ya puede calcular dominio por habilidad.
  - El backend ya puede exponer dominio por habilidad mediante API.
  - El backend ya puede recomendar repaso básico por habilidad.
  - La Fase 3 queda completada a nivel inicial.

## B51 — Revisión de estado y decisión de siguiente fase

- Objetivo: revisar el estado posterior al cierre de la fase adaptativa inicial y decidir la siguiente fase.
- Estado confirmado:
  - Fase 1: backend base completado a nivel inicial.
  - Fase 2: modelo pedagógico completado a nivel inicial.
  - Fase 3: sistema adaptativo completado a nivel inicial.
- Decisión:
  - No avanzar todavía a IA controlada.
  - Crear primero una fase de preparación para frontend.
- Motivo:
  - El backend debe entregar respuestas claras, estables y útiles antes de conectar una app visual o agregar IA.
- Siguiente fase:
  - Fase 4: Preparación para frontend.

## B52 — Dashboard inicial del estudiante

- Objetivo: preparar una primera respuesta simple para el frontend.
- Schema creado:
  - StudentDashboard
- Servicio creado:
  - get_student_dashboard()
- Endpoint creado:
  - GET /api/v1/progress/{user_id}/dashboard
- Datos incluidos:
  - user_id
  - total_attempts
  - correct_attempts
  - accuracy
  - recommendation
- Resultado:
  - Tests: 16 passed.

## B53 — Endpoint de siguiente acción recomendada

- Objetivo: indicar al frontend qué debe hacer el estudiante después.
- Schema creado:
  - NextAction
- Servicio creado:
  - get_next_action()
- Endpoint creado:
  - GET /api/v1/progress/{user_id}/next-action
- Acciones iniciales:
  - start_first_lesson
  - review_skill
  - continue_lesson
- Resultado:
  - Tests: 17 passed.

## B54 — Contrato API inicial para frontend

- Objetivo: documentar los endpoints que podrá consumir una aplicación visual.
- Documento creado:
  - docs/api-frontend.md
- Endpoints documentados:
  - POST /progress
  - GET /progress/{user_id}
  - GET /progress/{user_id}/stats
  - GET /progress/{user_id}/recommendation
  - GET /progress/{user_id}/skills/{skill_id}/mastery
  - GET /progress/{user_id}/skills/{skill_id}/review
  - GET /progress/{user_id}/dashboard
  - GET /progress/{user_id}/next-action
- Resultado:
  - El frontend ya tiene un contrato API inicial para consultar el backend.

## B55 — Ejemplos JSON del contrato API para frontend

- Objetivo: ampliar el contrato API inicial con ejemplos de respuesta.
- Documento actualizado:
  - docs/api-frontend.md
- Ejemplos agregados:
  - GET /progress/{user_id}/stats
  - GET /progress/{user_id}/recommendation
  - GET /progress/{user_id}/skills/{skill_id}/mastery
  - GET /progress/{user_id}/skills/{skill_id}/review
  - GET /progress/{user_id}/dashboard
  - GET /progress/{user_id}/next-action
- Resultado:
  - El frontend ya tiene ejemplos JSON para construir pantallas iniciales.

## B56 — Cierre de preparación inicial para frontend

- Objetivo: cerrar formalmente la fase de preparación inicial para frontend.
- Bloques incluidos:
  - B52: dashboard inicial del estudiante.
  - B53: endpoint de siguiente acción recomendada.
  - B54: contrato API inicial para frontend.
  - B55: ejemplos JSON del contrato API para frontend.
- Resultado:
  - El backend ya ofrece un dashboard inicial para el frontend.
  - El backend ya indica la siguiente acción recomendada.
  - El frontend ya cuenta con un contrato API inicial.
  - El contrato API ya incluye ejemplos JSON.
  - La Fase 4 queda completada a nivel inicial.

## B57 — Revisión de estado y decisión de inicio de frontend

- Objetivo: revisar el estado del backend y decidir cómo iniciar la fase de frontend.
- Estado confirmado:
  - Backend FastAPI en WSL2.
  - Fase 4 completada a nivel inicial.
  - Contrato API inicial disponible para frontend.
- Decisión:
  - Usar Flutter en Ubuntu VMware.
  - Mantener FastAPI en WSL2.
  - Conectar Flutter con el backend mediante API HTTP.
- Motivo:
  - Flutter ya funciona en Ubuntu VMware.
  - Evita instalar Flutter desde cero en WSL2.
  - Reduce fricción con Android SDK, emuladores, permisos y rutas.

## B58 — Conexión entre Flutter VMware y backend WSL2

- Objetivo: preparar la comunicación entre Ubuntu VMware y FastAPI en WSL2.
- Entornos:
  - Backend FastAPI: WSL2.
  - Frontend Flutter: Ubuntu VMware.
- IP detectadas:
  - WSL2: 172.24.0.128.
  - Windows Wi-Fi: 192.168.1.33.
  - Ubuntu VMware: 192.168.1.41.
- Problema detectado:
  - Ubuntu VMware no podía acceder directamente a 172.24.0.128:8000.
  - Ubuntu VMware tampoco podía acceder inicialmente a 192.168.1.33:8000.
- Correcciones aplicadas:
  - FastAPI se levantó con --host 0.0.0.0 --port 8000.
  - Se creó una regla de firewall en Windows para permitir TCP 8000.
  - Se creó un portproxy de Windows:
    - 192.168.1.33:8000 -> 172.24.0.128:8000.
- Resultado:
  - Ubuntu VMware accede correctamente al backend con:
    - curl http://192.168.1.33:8000/api/v1/health
  - Respuesta confirmada:
    - {"status":"ok"}
## B70 — Migración del backend a Ubuntu VMware

- Objetivo: migrar el backend desde WSL2 hacia Ubuntu VMware para unificar el entorno de desarrollo.
- Ruta nueva:
  - ~/projects/app_ingles_backend/app-ingles-backend
- Cambios realizados:
  - Se clonó el backend desde GitHub.
  - Se creó el entorno virtual .venv.
  - Se instalaron dependencias desde requirements.txt.
  - Se instaló PostgreSQL local en Ubuntu VMware.
  - Se creó la base de datos app_ingles_db.
  - Se creó el usuario PostgreSQL appIngles.
  - Se creó el archivo .env local con DATABASE_URL.
  - Se ejecutó app.db.create_tables para crear la tabla user_progress.
  - Se agregó .venv/ al .gitignore.
- Validaciones realizadas:
  - pytest: 17 tests passed.
  - Backend levantado con Uvicorn.
  - Endpoint /api/v1/health respondió {"status":"ok"}.
- Decisión técnica:
  - Ubuntu VMware local queda como entorno principal del proyecto.
  - WSL2 deja de ser el entorno principal para app-ingles.

## B93 — Contrato backend para pronunciaciones regionales

- Objetivo:
  - ampliar el contenido pedagógico para que cada frase pueda ofrecer pronunciaciones regionales con IPA y audio.
- Cambios realizados:
  - se creó el modelo `Pronunciation` en `app/schemas/content.py`;
  - cada pronunciación contiene `locale`, `ipa` y `audio_asset`;
  - las variantes actuales están limitadas a `en-US` y `en-GB`;
  - `Example` ahora admite una lista opcional `pronunciations`;
  - se añadió a `content/content_tree.json` la pronunciación estadounidense y británica de `Hello, I am John.`;
  - se actualizaron las pruebas de detalle de lección para validar ambas variantes, sus IPA y sus rutas de audio.
- Decisión técnica:
  - se utiliza una lista escalable de pronunciaciones en lugar de campos independientes como `ipa_us` o `ipa_uk`;
  - esta estructura permite incorporar futuras variantes regionales sin rediseñar el contrato;
  - las referencias de audio apuntan a recursos locales administrados por el frontend.
- Validaciones realizadas:
  - `pytest tests/test_content_lessons.py -q` → prueba superada;
  - `pytest -q` → 17 pruebas superadas en 0.64 segundos;
  - `GET http://127.0.0.1:8001/api/v1/health` → `{"status":"ok"}`.
- Entorno local:
  - CNAPP-Lite conserva el puerto `8000`;
  - App Inglés utiliza el puerto `8001` para evitar conflictos.

## Continuidad B94–B98 — Capacidades desarrolladas en frontend

Los bloques B94 a B98 corresponden al repositorio frontend y están documentados en `docs/bitacora-frontend.md`.

Resumen:

- B94 — Escuchar, grabar y comparar.
- B95 — Repetición guiada de una frase.
- B96 — Autoevaluación guiada de pronunciación.
- B97 — Resumen local de finalización de una lección.
- B98 — Indicador persistente de avance por lección.

Estos bloques no requirieron cambios funcionales en el backend.

La numeración de bloques es global para App Inglés, aunque la documentación se distribuya entre los repositorios backend y frontend.


## B99 — Contrato backend escalable para práctica conversacional

### Objetivo

Preparar el contenido pedagógico para incorporar prácticas conversacionales guiadas sin reescribir posteriormente el modelo de lecciones.

### Implementación realizada

- Se añadió `ConversationTurn` en `app/schemas/content.py`.
- Cada turno contiene:
  - identificador estable;
  - rol `partner` o `learner`;
  - texto en inglés;
  - traducción opcional;
  - pronunciaciones regionales opcionales.
- Se añadió `Conversation` con:
  - identificador estable;
  - título;
  - contexto opcional;
  - modo de interacción;
  - lista ordenada de turnos.
- El contrato admite los modos `guided`, `branching` y `free`.
- Solo `guided` tiene contenido implementado actualmente.
- `Lesson` incorpora una lista opcional `conversations`.
- Las lecciones antiguas siguen siendo compatibles y devuelven una lista vacía.

### Contenido inicial

- Se añadió `a1-u1-l1-c1` a la lección `a1-u1-l1`.
- La conversación contiene cuatro turnos alternados entre interlocutor y estudiante.
- Todos los turnos tienen identificadores estables.
- `Hello, I am John.` reutiliza las pronunciaciones `en-US` y `en-GB`.

### Escalabilidad

El contrato permitirá incorporar progresivamente:

- conversaciones ramificadas;
- respuestas alternativas;
- conversación libre;
- reconocimiento de voz y palabras;
- puntuación automática;
- retroalimentación pedagógica;
- persistencia de sesiones;
- analítica;
- interlocutores con inteligencia artificial;
- generación dinámica de respuestas.

La evaluación, persistencia, inteligencia artificial y reconocimiento permanecerán separados del contenido pedagógico base.

### Documentación

- Se añadió `DT-008 — Contrato escalable para prácticas conversacionales`.
- Se actualizó `docs/roadmap.md` con:
  - el entorno Ubuntu local;
  - conversación guiada y libre;
  - IA controlada;
  - lectura guiada interactiva.

### Pruebas y validaciones

- Se amplió `tests/test_content_lessons.py`.
- Se validan conversación, modo, roles, pronunciaciones y compatibilidad.
- Prueba específica → `2 passed`.
- Suite completa backend → `18 passed`.
- `git diff --check` → sin errores.

### Estado

El contrato backend está implementado y validado.

Pendiente:

- commit y push del backend;
- modelo e interfaz conversacional en Flutter;
- implementación visual basada en el prototipo maestro de `LOGUIC English`.

### Cierre backend de B99

- Commit funcional: `08e4070`.
- Mensaje funcional: `B99 añadir contrato backend para práctica conversacional`.
- Documentación técnica completada en `docs/bitacora.md`, `docs/decisiones-tecnicas.md` y `docs/roadmap.md`.
- Cierre documental y sincronización registrados mediante Git.

### Ajuste de soporte auditivo para B99 frontend

Durante la preparación de la interfaz conversacional se detectó que el recorrido pedagógico aprobado exige escuchar al interlocutor, pero los turnos `partner` no incluían referencias de audio.

Cambios realizados:

- Se añadieron pronunciaciones `en-US` y `en-GB` a los turnos `a1-u1-l1-c1-t1` y `a1-u1-l1-c1-t3`.
- Cada pronunciación incorpora IPA normalizado y una ruta estable de `audio_asset`.
- Se generaron cuatro audios WAV provisionales en el repositorio frontend mediante voces masculinas `en-us` y `en-gb` de eSpeak NG, con velocidad `145`.
- eSpeak NG continúa limitado a prototipo local y respaldo offline.
- Se amplió `tests/test_content_lessons.py` para validar variantes, rutas de audio e IPA no vacíos en ambos turnos `partner`.

Validaciones:

- Prueba específica backend → `2 passed`.
- Suite completa backend → `18 passed`.
- `git diff --check` → sin errores.

Estado:

- Ajuste funcional y documental pendiente de commit y push.
- La implementación visual de B99 continúa en el frontend.

## B100 — Contrato backend profesional para conversaciones ramificadas

### Objetivo

Ampliar el contrato conversacional de forma aditiva para soportar conversaciones ramificadas reales, sin romper B99 ni mezclar persistencia, reconocimiento de voz, puntuación o inteligencia artificial con el contenido pedagógico base.

### Implementación realizada

- Se añadió `ConversationChoice` con:
  - identificador estable;
  - texto en inglés;
  - traducción opcional;
  - pronunciaciones regionales opcionales;
  - `next_turn_id` opcional.
- `ConversationTurn` admite:
  - `next_turn_id` para transiciones deterministas;
  - `choices` para respuestas alternativas.
- `Conversation` admite `start_turn_id`.
- Se añadió `validate_conversation_graph` mediante `model_validator` de Pydantic.
- La validación se ejecuta al cargar `content_tree.json` mediante `ContentTreeResponse.model_validate`.
- Las conversaciones `guided` existentes continúan siendo compatibles sin declarar grafo explícito.

### Reglas de integridad

El contrato rechaza:

- identificadores duplicados de turnos u opciones;
- `start_turn_id` inexistente;
- transiciones hacia turnos inexistentes;
- turnos inaccesibles;
- opciones definidas en turnos que no pertenecen al estudiante;
- una sola opción en un punto de ramificación;
- uso simultáneo de `next_turn_id` y `choices`;
- conversaciones ramificadas sin punto de inicio;
- conversaciones ramificadas sin opciones;
- ciclos alcanzables, incluso cuando otra rama sí puede terminar.

### Contenido ramificado

- Se añadió `a1-u1-l1-c2`.
- La conversación comienza en `a1-u1-l1-c2-t1`.
- El estudiante dispone de dos respuestas alternativas.
- Cada respuesta conduce a una reacción diferente del interlocutor.
- Las rutas se unen posteriormente en `a1-u1-l1-c2-t5`.
- El último turno finaliza sin transición adicional.

### Pruebas y validaciones

- `tests/test_content_lessons.py` valida el contrato expuesto por la API.
- `tests/test_conversation_schema.py` valida grafos correctos e incorrectos.
- Prueba específica de contenido y esquema → `5 passed`.
- Suite completa backend → `28 passed`.
- `git diff --check` → sin errores.

### Límites del bloque

B100 no incorpora todavía:

- interfaz Flutter para recorrer las ramas;
- persistencia de sesiones conversacionales;
- reconocimiento de voz o palabras;
- puntuación automática;
- analítica;
- inteligencia artificial.

Estas capacidades se mantendrán en contratos y servicios separados para conservar responsabilidades claras.

### Estado

Implementación backend, pruebas y documentación completadas.

Pendiente:

- validación final después de documentar;
- revisión de `git status`;
- commit y push;
- implementación frontend de las conversaciones ramificadas.

## B101 — Persistencia del progreso conversacional

### Objetivo

Guardar cada conversación completada como un intento persistente e independiente del progreso de ejercicios, conservando el recorrido real, las opciones elegidas y la fecha de finalización.

### Diseño de persistencia

- Se creó la tabla independiente `conversation_attempts`.
- No se modificó la tabla `user_progress`.
- Cada intento almacena:
  - usuario, nivel, unidad y lección;
  - identificador de conversación;
  - modo `guided` o `branching`;
  - identificadores de los turnos recorridos;
  - identificadores de las opciones seleccionadas;
  - fecha de finalización.
- Las listas se almacenan mediante columnas SQLAlchemy `JSON`.
- No se guardan grabaciones, rutas de archivos de audio ni contenido sensible.
- Repetir una conversación crea un intento nuevo y no sobrescribe el anterior.

### Contrato y servicios

- Se añadieron `ConversationAttemptCreate` y `ConversationAttemptRecord`.
- `visited_turn_ids` exige al menos un turno.
- El modo queda limitado actualmente a `guided` y `branching`.
- Se añadió búsqueda contextual de conversaciones mediante nivel, unidad y lección.
- Se creó un servicio independiente para:
  - validar recorridos completados;
  - guardar intentos;
  - recuperar intentos por usuario en orden cronológico.

### Validación de recorridos

El backend rechaza:

- conversaciones inexistentes;
- jerarquías de nivel, unidad o lección incorrectas;
- modos que no coinciden con la conversación;
- conversaciones guiadas incompletas o fuera de orden;
- opciones dentro de conversaciones guiadas;
- rutas ramificadas sin la opción requerida;
- opciones que no pertenecen al turno activo;
- turnos que no coinciden con la rama seleccionada;
- opciones adicionales o inventadas;
- recorridos que no alcanzan el cierre real de la ruta.

### API

- `POST /api/v1/conversation-attempts` guarda un intento completado y validado.
- `GET /api/v1/conversation-attempts/{user_id}` recupera los intentos del usuario.
- Los recorridos inválidos devuelven estado HTTP `400` con el motivo correspondiente.

### Separación del progreso de ejercicios

- Los intentos conversacionales no se incluyen en `UserProgress`.
- No modifican `total_attempts`, `correct_attempts` ni `accuracy`.
- No afectan dominio por habilidad, recomendaciones ni siguiente acción.
- La evaluación oral futura permanecerá separada del registro básico de finalización.

### Base de datos

- El proyecto todavía no utiliza Alembic.
- La tabla fue creada mediante `python3 -m app.db.create_tables`, siguiendo el mecanismo actual.
- `create_all()` permite añadir esta tabla independiente sin alterar las existentes.
- La incorporación futura de migraciones versionadas continúa siendo una mejora pendiente del sistema.

### Pruebas y validaciones

- Se creó `tests/test_conversation_attempts.py`.
- Las siete pruebas específicas validan:
  - guardado y lectura de conversación guiada;
  - guardado de una ruta ramificada válida;
  - rechazo de una ruta incompatible con la opción elegida;
  - rechazo y ausencia de persistencia de un intento incompleto;
  - rechazo de jerarquía incorrecta;
  - separación respecto a estadísticas de ejercicios;
  - intentos repetidos independientes.
- Pruebas específicas B101 → `7 passed`.
- Suite completa backend → `35 passed`.
- `git diff --check` → sin errores.

### Archivos principales

- `app/db/models.py`
- `app/schemas/conversation_attempt.py`
- `app/services/content_service.py`
- `app/services/conversation_attempt_service.py`
- `app/api/v1/endpoints/conversation_attempts.py`
- `app/api/v1/router.py`
- `tests/test_conversation_attempts.py`

### Cierre de B101

- Validación backend completa: `35 passed`.
- Commit backend: `0f66c68` — `B101 añadir persistencia conversacional`.
- Push completado a `origin/master`.
- Integración y validación manual desde Flutter completadas posteriormente.
- Backend confirmado limpio y sincronizado al cerrar B101.

## B103 — Identificadores estables para ejemplos de pronunciación

### Objetivo

Incorporar identificadores persistentes y estables a las frases de ejemplo antes de guardar autoevaluaciones de pronunciación, analítica o repetición inteligente.

### Decisión técnica

- No se utilizarán índices como identificadores persistentes.
- Un índice como `example:0` puede cambiar si el contenido pedagógico se reordena.
- Cada ejemplo debe declarar un `id` estable dentro del contrato de contenido.
- Este cambio crea una base segura para futuras evaluaciones `good`, `almost` y `repeat`.
- B103 todavía no persiste autoevaluaciones ni grabaciones.

### Implementación backend

- El esquema Pydantic `Example` requiere ahora el campo `id`.
- Se añadieron identificadores estables a los ejemplos actuales:
  - `a1-u1-l1-e1` para `Hello, I am John.`;
  - `a1-u1-l1-e2` para `Goodbye! See you later.`.
- El cambio es aditivo respecto al contenido funcional existente.
- No se modificaron conversaciones, ejercicios ni progreso persistido.

### Pruebas y validaciones

- `tests/test_content_lessons.py` valida los dos identificadores.
- Pruebas específicas de contenido: `5 passed`.
- Suite backend completa: `35 passed`.
- `git diff --check`: sin errores.

### Archivos principales

- `app/schemas/content.py`
- `content/content_tree.json`
- `tests/test_content_lessons.py`

### Cierre de B103

- Validación backend completa: `35 passed`.
- Revisión de código y seguridad completada sin cambios inesperados ni datos sensibles.
- Commit backend principal: `b8b6b36` — `B103 añadir identificadores estables a ejemplos`.
- Push del cambio técnico completado a `origin/master`.
- Adaptación compatible del modelo Flutter completada y validada.
- Backend confirmado limpio y sincronizado después del commit documental.
