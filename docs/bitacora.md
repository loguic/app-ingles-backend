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

## B104 — Punto de control y sincronización de la Fase 5

Fecha: 2026-07-22

### Objetivo

- Confirmar el rumbo real del producto sin desviarse del roadmap aprobado.
- Sincronizar la Fase 5 con las capacidades ya terminadas.
- Medir el contenido pedagógico disponible antes de iniciar otro bloque técnico.

### Estado confirmado

- La infraestructura de práctica oral y conversacional está avanzada.
- La interfaz conversacional ramificada, la persistencia de intentos y el historial ya están completados.
- El contenido actual contiene 2 niveles declarados, 1 unidad, 2 lecciones, 2 ejemplos, 1 ejercicio, 2 conversaciones y 9 turnos.
- `a1-u1-l2` existe únicamente como marcador de contenido.
- A2 todavía no contiene unidades.
- El contenido pedagógico actual aún no constituye una versión suficientemente utilizable.

### Cambio realizado

- Se actualizó `docs/roadmap.md`.
- No se añadieron nuevas fases ni se modificó el orden del roadmap.
- Las capacidades B100–B103 se trasladaron al estado desarrollado.
- Reconocimiento de voz, puntuación automática, retroalimentación pedagógica y conversación libre permanecen como evolución prevista.

### Cierre de B104

- Commit principal: `dbf99c0` — `B104 sincronizar roadmap de fase 5`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado antes del commit documental.
- No se modificó código ni contenido pedagógico.

## B105 — Arquitectura del Constructor Pedagógico de Unidades

Fecha: 2026-07-22

### Objetivo

- Sustituir el trabajo pedagógico fragmentado por la construcción controlada de unidades completas.
- Diseñar una capacidad reutilizable desde A1 hasta C2 sin alterar el roadmap aprobado.
- Mantener los Skills medibles como núcleo de la progresión y la evaluación.

### Diseño aprobado

- Se creó `docs/pedagogical-unit-builder.md`.
- Se definieron contratos versionables de entrada y salida.
- El constructor producirá paquetes candidatos aislados del contenido activo.
- Cada unidad deberá incluir una matriz de cobertura de Skills.
- Las validaciones deterministas se ejecutarán antes de la revisión mediante agentes o personas.
- Se utilizará inicialmente un único agente orquestador controlado.
- El agente no podrá modificar contenido activo, aprobar su propio resultado ni omitir validaciones.
- MCP queda preparado como evolución futura, pero no se implementa en B105.
- Toda integración requerirá aprobación humana, pruebas y revisión visual.

### Alcance y límites

- B105 aprueba únicamente la arquitectura del constructor.
- La implementación determinista pertenecerá a un bloque posterior.
- El agente orquestador se incorporará después de validar el núcleo determinista.
- La especificación y construcción de `A1-U1` se realizarán en bloques separados.
- No se modificó código ni contenido pedagógico activo.

### Cierre técnico principal

- Documento revisado mediante diff completo.
- `git diff --check`: sin errores.
- Commit principal: `248e5cd` — `B105 diseñar constructor pedagogico de unidades`.
- Push del documento arquitectónico completado a `origin/master`.

### Cierre final de B105

- Entrada documental validada.
- Commit documental: `f2127cb` — `docs cerrar B105 en bitacora`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado.

## B106 — Núcleo determinista del Constructor Pedagógico

Fecha: 2026-07-22

### Objetivo

- Implementar los contratos deterministas definidos por la arquitectura de B105.
- Separar las especificaciones y paquetes candidatos del contenido pedagógico activo.
- Validar automáticamente Skills, cobertura, unidades candidatas e informes antes de cualquier agente o revisión humana.

### Implementación

- Se creó `app/schemas/pedagogical_unit.py`.
- Se definió `SkillSpecification` con identificador estable, descripción observable y etapas pedagógicas.
- Se definió `SkillCoverage` con introducción, práctica, aplicación, evaluación, consolidación y modalidades.
- Se creó `PedagogicalUnitSpecification` como contrato obligatorio de entrada.
- Se validó la coherencia entre `unit_id` y nivel CEFR.
- Se añadieron `ValidationFinding` y `ValidationReport` con estados y severidades coherentes.
- Se creó `PedagogicalUnitCandidate` reutilizando el contrato vigente `Unit`.
- El paquete candidato valida identidad de unidad, cobertura única, Skills ausentes y Skills desconocidos.
- No se modificó el contenido pedagógico activo ni se implementaron agentes o MCP.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_unit_schema.py`.
- Pruebas contractuales nuevas: `21 passed`.
- Suite backend completa: `56 passed`.
- `git diff --check`: sin errores después de normalizar los finales de archivo.

### Cierre técnico principal

- Commit técnico: `42db89c` — `B106 implementar contratos pedagogicos deterministas`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Cierre final de B106

- La entrada documental y la corrección final de B105 fueron revisadas.
- Commit documental: `35b1c99` — `docs cerrar B106 en bitacora`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado.

## B107 — Motor determinista de validación pedagógica

Fecha: 2026-07-23

### Objetivo

- Implementar validadores pedagógicos automáticos y reproducibles sobre paquetes candidatos.
- Reutilizar los contratos de B106 sin duplicar las validaciones estructurales de Pydantic.
- Rechazar o dejar pendiente cualquier candidato con cobertura, referencias o evidencias incoherentes.

### Implementación

- Se creó `app/services/pedagogical_validation_service.py` siguiendo el patrón funcional de `app/services/`.
- Se implementó la validación de etapas obligatorias por Skill: introducción, práctica, aplicación, evaluación y consolidación.
- Se implementó la validación de referencias internas contra lecciones, ejemplos, conversaciones y ejercicios del candidato.
- Se comprobó que cada ejercicio usado como evidencia incluya el Skill evaluado en `skill_ids`.
- Se evitó duplicar hallazgos cuando una evidencia de evaluación referencia un elemento inexistente.
- Se validaron los estados de cobertura `complete`, `incomplete` y `pending_approval`.
- El informe global devuelve `passed`, `pending` o `failed`, dando prioridad a los errores sobre las advertencias.
- El servicio no lee ni escribe archivos y no modifica el contenido pedagógico activo.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_validation_service.py`.
- Pruebas específicas del motor: `17 passed`.
- Suite backend completa: `73 passed`.
- Compilación Python de servicio y pruebas: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Commits técnicos

- `39b51b9` — `B107 validar cobertura de etapas pedagogicas`.
- `58a00ea` — `B107 validar referencias internas pedagogicas`.
- `bd278ad` — `B107 validar vinculo entre evaluacion y Skill`.
- `507e86f` — `B107 validar estado de cobertura pedagogica`.
- Todos los commits fueron publicados en `origin/master`.

### Límites respetados

- No se modificó `content/content_tree.json`.
- No se generó ni integró contenido para A1-U1.
- No se implementaron agentes, MCP ni acceso a herramientas externas.
- Los validadores adicionales de recursos, duplicados y límites de contenido quedan para bloques posteriores separados.

### Cierre de B107

- El motor determinista quedó implementado, probado y publicado.
- Esta entrada constituye el cierre documental de B107.
- La publicación de esta documentación y la verificación de Git limpio forman parte del cierre operativo del bloque.

## B108 — Validación determinista del inventario de recursos

Fecha: 2026-07-23

### Objetivo

- Validar de forma determinista el inventario lógico de recursos de los paquetes candidatos.
- Mantener desacopladas las referencias del backend y los archivos físicos administrados por Flutter.
- Impedir que un candidato omita audios referenciados o declare identificadores duplicados.

### Decisiones técnicas

- El backend conserva rutas lógicas como `audio/a1_u1_l1_hello_us.wav`.
- Flutter recibe esas rutas sin transformación y las reproduce mediante `AssetSource(audioAsset)`.
- Los archivos físicos permanecen en `assets/audio/` del frontend.
- El backend no accede al sistema de archivos del frontend ni utiliza rutas absolutas.
- `required_resource_ids` representa el inventario lógico del paquete candidato.

### Implementación

- Se amplió `app/services/pedagogical_validation_service.py`.
- Se recopilan los `audio_asset` de ejemplos, turnos y elecciones conversacionales.
- Se detectan audios referenciados ausentes de `required_resource_ids`.
- Se detectan identificadores duplicados dentro del inventario.
- Los recursos adicionales no utilizados no se rechazan todavía porque el contrato podrá incluir otros tipos de recurso.
- Se actualizó la fixture candidata con audios inventariados de ejemplo y conversación.

### Pruebas y validaciones

- Pruebas específicas del motor ampliadas: `20 passed`.
- Suite backend completa: `76 passed`.
- Compilación Python de servicio y pruebas: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Cierre técnico

- Commit técnico: `d23d396` — `B108 validar inventario logico de recursos`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado.

### Límites respetados

- No se modificó el contenido pedagógico activo.
- No se comprobaron archivos físicos desde el backend.
- No se implementaron generación de audios, agentes ni MCP.
- La validación física entre repositorios requerirá un flujo posterior explícito y desacoplado.

### Cierre de B108

- El inventario lógico de recursos quedó implementado, probado y publicado.
- Esta entrada constituye el cierre documental de B108.
- La publicación de esta documentación y la verificación de Git limpio forman parte del cierre operativo del bloque.

## B109 — Detección determinista de duplicados exactos

Fecha: 2026-07-23

### Objetivo

- Detectar opciones equivalentes dentro de un mismo ejercicio de selección.
- Aplicar una comparación determinista sin modificar el paquete candidato.
- Evitar falsos positivos entre ejercicios distintos y entre contextos pedagógicos diferentes.

### Decisiones técnicas

- El primer incremento de B109 se limita a duplicados inequívocos dentro del mismo ejercicio.
- No se detecta todavía similitud semántica porque no existe un umbral aprobado.
- Una frase repetida entre ejemplos y conversaciones no se considera automáticamente duplicada.
- La normalización utiliza `casefold()` y la reducción de espacios adicionales.
- El validador se implementó en un módulo aislado para no ampliar innecesariamente el servicio principal.

### Implementación

- Se creó `app/services/pedagogical_duplicate_validation.py`.
- Se implementó `normalize_candidate_text(value)`.
- Se implementó `validate_duplicate_exercise_options(candidate)`.
- Cada grupo equivalente genera un único hallazgo con los índices de las opciones afectadas.
- El hallazgo utiliza `validator_id="duplicate_exercise_options"`, severidad `error` y referencia al ejercicio.
- El nuevo validador se integró en `validate_pedagogical_candidate`.
- El candidato no se modifica durante la validación.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_duplicate_validation.py`.
- Pruebas específicas de B109: `8 passed`.
- Pruebas conjuntas del motor pedagógico: `27 passed`.
- Suite backend completa: `84 passed`.
- Compilación Python de módulos y pruebas: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Cierre técnico

- Commit técnico: `90a2311` — `B109 detectar opciones duplicadas exactas`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Límites respetados

- No se modificó el contenido pedagógico activo.
- No se implementó detección de similitud semántica.
- No se compararon automáticamente ejemplos y conversaciones.
- No se reformaron ni movieron los validadores anteriores.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre de B109

- La detección determinista de opciones equivalentes quedó implementada, probada y publicada.
- Esta entrada constituye el cierre documental de B109.
- La publicación de esta documentación y la verificación de Git limpio forman parte del cierre operativo del bloque.

## B110 — Validación determinista de límites cuantitativos de contenido

Fecha: 2026-07-23

### Objetivo

- Representar límites cuantitativos aprobados mediante un contrato estructurado.
- Validar de forma determinista las cantidades del contenido candidato.
- Aplicar únicamente los límites declarados por cada especificación pedagógica.

### Decisiones técnicas

- Se creó `ContentLimits` con campos opcionales para mínimos y máximos.
- No existen umbrales universales codificados por nivel CEFR.
- Cada mínimo declarado debe ser menor o igual que su máximo correspondiente.
- Los límites narrativos de dificultad continúan en `content_constraints` y no se interpretan automáticamente.
- El validador cuantitativo se implementó en un módulo aislado.

### Implementación

- Se amplió `PedagogicalUnitSpecification` con `content_limits` y un valor vacío compatible con especificaciones anteriores.
- Se validan cantidades mínimas y máximas de lecciones por unidad.
- Se validan ejemplos, conversaciones y ejercicios por lección.
- Se validan opciones por ejercicio y turnos por conversación.
- Cada incumplimiento genera un hallazgo `content_limits` con severidad `error` y referencia al elemento afectado.
- El validador se integró en `validate_pedagogical_candidate`.
- El candidato no se modifica durante la validación.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_content_limits_schema.py`.
- Se creó `tests/test_pedagogical_content_limits_validation.py`.
- Pruebas del contrato: `21 passed`.
- Pruebas del contrato y esquema pedagógico: `42 passed`.
- Pruebas específicas e integradas de B110: `56 passed`.
- Suite backend completa: `120 passed`.
- Compilación Python de esquemas, servicios y pruebas: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Cierre técnico

- Commit técnico: `8c8f1dc` — `B110 validar limites cuantitativos de contenido`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Límites respetados

- No se implementó análisis de dificultad lingüística.
- No se validó longitud de frases ni cantidad de palabras.
- No se añadió similitud semántica ni repetición entre contextos pedagógicos.
- No se definieron umbrales universales por nivel CEFR.
- No se modificó el contenido pedagógico activo.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre de B110

- El contrato y la validación determinista de límites cuantitativos quedaron implementados, probados y publicados.
- Esta entrada constituye el cierre documental de B110.
- La publicación de esta documentación y la verificación de Git limpio forman parte del cierre operativo del bloque.

## B111 — Integridad determinista de identificadores de contenido

Fecha: 2026-07-23

### Objetivo

- Validar formatos jerárquicos y unicidad de los identificadores del contenido candidato.
- Impedir identificadores incoherentes con sus unidades, lecciones o conversaciones padre.
- Mantener esta validación separada de los esquemas generales y de la integridad de grafos.

### Implementación

- Se creó `app/services/pedagogical_identifier_validation.py`.
- Se validan identificadores de lecciones, ejemplos, conversaciones y ejercicios.
- Se validan identificadores de turnos y elecciones conversacionales.
- Se comprueba el prefijo jerárquico exacto del elemento padre.
- Se comprueba la unicidad de lecciones, ejemplos, conversaciones y ejercicios.
- Los números comienzan en `1`, pero no se exige que sean consecutivos.
- Los incumplimientos generan `content_identifier_integrity` con severidad `error`.
- El validador se integró en `validate_pedagogical_candidate`.
- El candidato no se modifica durante la validación.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_identifier_validation.py`.
- Pruebas específicas de B111: `13 passed`.
- Pruebas del motor pedagógico: `56 passed`.
- Suite backend completa: `133 passed`.
- Compilación Python de servicios y pruebas: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Cierre técnico

- Commit técnico: `fbddef2` — `B111 validar integridad de identificadores`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Límites respetados

- No se modificaron los esquemas generales de `content.py`.
- No se reformaron los validadores anteriores.
- No se duplicaron las validaciones de grafos ni referencias internas.
- No se exigieron numeraciones consecutivas.
- No se modificó el contenido pedagógico activo.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre de B111

- La integridad determinista de identificadores quedó implementada, probada y publicada.
- Esta entrada constituye el cierre documental de B111.
- La publicación de esta documentación y la verificación de Git limpio forman parte del cierre operativo del bloque.

## B112 — Integridad determinista de ejercicios

Fecha: 2026-07-23

### Objetivo

- Validar que cada ejercicio de opción múltiple sea utilizable, resoluble y esté vinculado con Skills declarados.

### Implementación

- Se creó `app/services/pedagogical_exercise_integrity_validation.py`.
- Se implementó `validate_exercise_integrity(candidate)` sin modificar el candidato.
- El `prompt` no puede estar vacío ni contener únicamente espacios.
- Cada ejercicio debe contener al menos dos opciones.
- Ninguna opción puede estar vacía ni contener únicamente espacios.
- `answer_index` debe pertenecer al rango real de `options`.
- `skill_ids` debe contener al menos un Skill.
- No se permiten `skill_ids` duplicados dentro del mismo ejercicio.
- Todos los `skill_ids` deben existir en `candidate.specification.skills`.
- Los hallazgos usan `validator_id="exercise_integrity"`, severidad `error` y referencia al ejercicio.
- El validador se integró en `validate_pedagogical_candidate`.

### Pruebas y compatibilidad

- Se creó `tests/test_pedagogical_exercise_integrity_validation.py` con 11 pruebas.
- Se cubrieron ejercicios válidos, prompts vacíos, opciones insuficientes o vacías, índices inválidos y relaciones con Skills.
- Se comprobó que la validación no modifica el candidato.
- Se añadió una prueba de integración con el agregador principal.
- Se adaptó una prueba anterior para filtrar su hallazgo `evaluation_skill_link` sin asumir que el informe completo contiene un único error.
- Suite backend completa: `144 passed`.
- Compilación Python: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Límites respetados

- B109 conserva la responsabilidad sobre opciones textualmente equivalentes.
- B110 conserva la responsabilidad sobre límites cuantitativos configurables.
- No se modificaron los esquemas generales de contenido.
- No se modificó el contenido pedagógico activo.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre técnico

- Commit técnico: `7f82778` — `B112 validar integridad de ejercicios`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Cierre de B112

- La integridad determinista de ejercicios quedó implementada, probada y publicada.
- La publicación de esta documentación y la verificación final de Git forman parte del cierre operativo.

## B113 — Integridad determinista textual y de pronunciaciones

Fecha: 2026-07-23

### Objetivo

- Validar la integridad mínima de los textos pedagógicos y de las pronunciaciones del contenido candidato.

### Implementación

- Se creó `app/services/pedagogical_content_text_integrity_validation.py`.
- Se implementó `validate_content_text_integrity(candidate)` sin modificar el candidato.
- `Example.en` no puede estar vacío ni contener únicamente espacios.
- `Conversation.title` no puede estar vacío ni contener únicamente espacios.
- `ConversationTurn.en` no puede estar vacío ni contener únicamente espacios.
- `ConversationChoice.en` no puede estar vacío ni contener únicamente espacios.
- Toda pronunciación debe contener `ipa` y `audio_asset` no vacíos.
- No puede repetirse un mismo `locale` dentro de las pronunciaciones de un ejemplo, turno o elección.
- Los hallazgos usan `validator_id="content_text_integrity"`, severidad `error` y referencia al elemento propietario.
- El validador se integró en `validate_pedagogical_candidate`.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_content_text_integrity_validation.py` con 12 pruebas.
- Se cubrieron ejemplos, conversaciones, turnos, elecciones y pronunciaciones válidas e inválidas.
- Se validaron `ipa`, `audio_asset` y locales duplicados.
- Se comprobó que la validación no modifica el candidato.
- Se añadió una prueba de integración con el agregador principal.
- Suite backend completa: `156 passed`.
- Compilación Python: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Límites respetados

- El esquema conversacional conserva la responsabilidad sobre rutas, ciclos, destinos y estructura del grafo.
- B108 conserva la responsabilidad sobre la existencia de recursos de audio.
- B111 conserva la responsabilidad sobre formatos y jerarquía de identificadores.
- No se validaron todavía traducciones opcionales `es` ni `context`.
- No se modificaron los esquemas generales de contenido.
- No se modificó el contenido pedagógico activo.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre técnico

- Commit técnico: `abc4455` — `B113 validar integridad textual y pronunciaciones`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Cierre de B113

- La integridad determinista textual y de pronunciaciones quedó implementada, probada y publicada.
- La publicación de esta documentación y la verificación final de Git forman parte del cierre operativo.

## B114 — Integridad estructural de unidad y lecciones

Fecha: 2026-07-23

### Objetivo

- Detectar de forma determinista estructuras inválidas en la unidad candidata y sus lecciones.

### Implementación

- Se creó `app/services/pedagogical_unit_lesson_structure_validation.py`.
- Se implementó `validate_unit_lesson_structure(candidate)` sin modificar el candidato.
- `Unit.title` no puede estar vacío ni contener únicamente espacios.
- La unidad candidata debe contener al menos una lección.
- `Lesson.title` no puede estar vacío ni contener únicamente espacios.
- Los hallazgos usan `validator_id="unit_lesson_structure_integrity"`, severidad `error` y referencias a la unidad o lección afectada.
- El validador se integró en `validate_pedagogical_candidate`.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_unit_lesson_structure_validation.py` con 6 pruebas.
- Se cubrieron unidad válida, título de unidad vacío, unidad sin lecciones y título de lección vacío.
- Se comprobó que la validación no modifica el candidato.
- Se añadió una prueba de integración con el agregador principal.
- Pruebas específicas B114: `6 passed`.
- Suite backend completa: `162 passed`.
- Compilación Python: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Límites respetados

- No se hizo obligatorio `Lesson.objective`.
- No se exigió contenido en `vocabulary` ni `grammar`.
- No se implementó validación semántica de `learner_outcome` ni de los campos `*_scope`.
- No se modificaron los esquemas Pydantic.
- No se modificó el contenido pedagógico activo.
- Los hallazgos existentes de referencias internas se conservaron.
- No se incorporaron agentes, MCP ni herramientas externas.

### Cierre técnico

- Commit técnico: `1db6c6e` — `B114 validar estructura de unidad y lecciones`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Cierre de B114

- La integridad estructural determinista de unidad y lecciones quedó implementada, probada y publicada.
- La publicación de esta documentación y la verificación final de Git forman parte del cierre operativo.

## B115 — Integridad de metadatos de lección

Fecha: 2026-07-23

### Objetivo

- Validar de forma determinista la integridad de `objective`, `vocabulary` y `grammar` en cada lección candidata.

### Implementación

- Se creó `app/services/pedagogical_lesson_metadata_validation.py`.
- Se implementó `validate_lesson_metadata_integrity(candidate)` sin modificar el candidato.
- `Lesson.objective` continúa siendo opcional.
- Si `objective` está presente, no puede estar vacío ni contener únicamente espacios.
- `vocabulary` y `grammar` pueden continuar como listas vacías.
- Sus entradas no pueden estar vacías ni contener únicamente espacios.
- No se permiten entradas equivalentes duplicadas dentro de cada lista.
- La comparación reutiliza `normalize_candidate_text`, ignorando mayúsculas, espacios exteriores y espacios internos repetidos.
- Los hallazgos usan `validator_id="lesson_metadata_integrity"`, severidad `error` y referencia a la lección afectada.
- El validador se integró en `validate_pedagogical_candidate`.

### Pruebas y validaciones

- Se creó `tests/test_pedagogical_lesson_metadata_validation.py`.
- Se añadieron 9 pruebas específicas.
- Se cubrieron objetivo ausente, objetivo vacío, entradas vacías y duplicadas de vocabulario y gramática.
- Se comprobó que la validación no modifica el candidato.
- Se añadió una prueba de integración con el agregador principal.
- Pruebas específicas B115: `9 passed`.
- Suite backend completa: `171 passed`.
- Compilación Python: correcta.
- Control de separaciones excesivas: correcto.
- `git diff --check`: sin errores.

### Límites respetados

- No se hizo obligatorio `Lesson.objective`.
- No se exigió que `vocabulary` ni `grammar` tengan elementos.
- No se evaluó la corrección lingüística o pedagógica de sus textos.
- No se implementó comparación semántica.
- No se modificaron los esquemas Pydantic.
- No se modificó el contenido pedagógico activo.
- No se incorporaron agentes, inteligencia artificial ni MCP.

### Cierre técnico

- Commit técnico: `d3d6e3f` — `B115 validar metadatos de lecciones`.
- Push completado a `origin/master`.
- Repositorio técnico confirmado limpio y sincronizado antes del cierre documental.

### Cierre de B115

- La integridad determinista de metadatos de lección quedó implementada, probada y publicada.
- La publicación de esta documentación y la verificación final de Git forman parte del cierre operativo.

## B116 — Diseño profesional de la experiencia de lección

### Problema detectado

- El contrato público `Lesson` y `LessonDetailCard` organizaban la experiencia mediante una secuencia tradicional fija.
- `vocabulary`, `grammar` y `examples` actuaban como bloques principales.
- La finalización de la lección dependía exclusivamente de completar ejercicios.
- La experiencia pedagógica, las evidencias y la política de finalización no habían sido formalizadas antes de reforzar el flujo provisional.
- Se reconoció el riesgo real de retrabajo, coste y pérdida de tiempo en un producto profesional.

### Corrección del método

- Se pausó cualquier cambio técnico de B116.
- Se volvió al último estado estable confirmado.
- Se realizó una auditoría arquitectónica de impacto en backend y Flutter.
- Se prohibió ampliar `Example` o convertir progresivamente el flujo heredado en el núcleo definitivo.
- Se aprobó construir un reemplazo profesional en paralelo.
- Se adoptó un método compacto: agrupar trabajo siempre que existan precondiciones, pruebas, reversibilidad y validación suficientes.

### Contrato profesional aprobado

Se creó `docs/lesson-experience-contract.md` como fuente canónica para:

- `LessonExperience`;
- `Mission`;
- `LessonStage`;
- `LanguageSupportItem`;
- `EvidenceDefinition`;
- `CompletionPolicy`;
- responsabilidades de entidades;
- evidencias y finalización;
- sustitución paralela;
- auditoría de impacto;
- automatización controlada;
- riesgos y medidas preventivas;
- criterios de aceptación;
- Definition of Done.

### Flujo pedagógico objetivo

La experiencia de lección v2 seguirá esta secuencia:

1. misión comunicativa;
2. encuentro inicial;
3. comprensión guiada;
4. lenguaje útil en contexto;
5. escucha y producción guiada;
6. respuesta asistida;
7. conversación aplicada;
8. retroalimentación y repetición adaptativa;
9. evidencia observable;
10. cierre y siguiente acción.

Vocabulario, gramática, traducción y frases de referencia quedarán subordinados a la misión comunicativa.

### Decisión sobre el legado

- `Example` queda congelado como compatibilidad heredada.
- No recibirá nuevas capacidades.
- No pertenecerá al contrato v2.
- `LessonDetailCard` permanecerá temporalmente como renderizador heredado.
- Flutter incorporará posteriormente un renderizador independiente para `LessonExperience`.
- La selección entre ambos recorridos será explícita y verificable.
- El legado solo podrá retirarse después de migración completa, pruebas y reversión comprobada.

### Evidencias y aprendizaje

- Se diferenciaron práctica, aplicación, evidencia, finalización y dominio.
- Completar una conversación no demostrará automáticamente fluidez.
- Grabar una frase no demostrará automáticamente pronunciación correcta.
- El dominio actual basado únicamente en ejercicios queda clasificado como cálculo heredado.
- La finalización v2 dependerá de evidencias obligatorias declaradas.

### Automatización e innovación con IA

- La IA generará candidatos, pruebas, informes, documentación y propuestas de migración.
- Los scripts críticos serán deterministas, con precondiciones y resultados revisables.
- Ningún agente o herramienta podrá publicar contenido activo, elegir Skills, aprobar sus propios resultados o cambiar identificadores silenciosamente.
- Se priorizará la máxima reducción de tiempo compatible con estabilidad, trazabilidad y revisión humana.
- La innovación deberá mejorar de manera demostrable velocidad, calidad, seguridad, aprendizaje o capacidad del producto.

### Documentación didáctica

- El manual técnico comenzará como documentación modular versionada.
- Cada concepto nuevo explicará propósito, problema resuelto, ubicación, relaciones, ejemplo aplicado, alternativas, riesgos y límites.
- Se diferenciarán claramente contratos, clases, patrones, Skills, agentes, herramientas, adaptadores y MCP.
- El manual de usuario se elaborará a partir de la primera experiencia v2 estable y se validará mediante un recorrido real.

### Validaciones

- Documento canónico completo: validado.
- Secciones obligatorias: 11 de 11.
- Sin secciones pendientes.
- Sin encabezados duplicados.
- Sin separaciones excesivas.
- Sin espacios finales.
- `git diff --check`: correcto durante su construcción.

### Límites respetados

- No se modificó código backend.
- No se modificó Flutter.
- No se modificó la API.
- No se modificó `content_tree.json`.
- No se migró contenido activo.
- No se alteró persistencia ni progreso.
- No se implementaron todavía las entidades v2.

### Estado de B116

- Diseño arquitectónico aprobado.
- Auditoría de impacto completada.
- Estrategia de sustitución paralela aprobada.
- Contrato canónico preparado para revisión final y versionado.
- El cierre operativo requiere revisar el diff, realizar commit y push y confirmar Git limpio y sincronizado.

## B117 — Contrato backend aditivo `LessonExperience` v2

### Objetivo

Crear el contrato público inicial de la experiencia profesional de lección sin eliminar ni modificar todavía el flujo heredado.

### Implementación

Se añadieron a `app/schemas/content.py` los siguientes esquemas Pydantic:

- `Mission`;
- `LanguageSupportItem`;
- `LessonStage`;
- `EvidenceDefinition`;
- `CompletionPolicy`;
- `LessonExperience`.

`Lesson` recibió el campo aditivo:

`experience: Optional[LessonExperience] = None`

Las lecciones heredadas continúan siendo válidas cuando no incluyen `experience`.

### Contrato inicial

`LessonExperience` declara:

- versión de contrato `2.0`;
- misión comunicativa;
- referencias a Skills;
- etapas pedagógicas ordenadas;
- apoyos lingüísticos contextuales;
- definiciones de evidencia;
- política de práctica, finalización y refuerzo.

### Validaciones iniciales

- Solo se admite la versión `2.0`.
- Una evidencia con medición `score` exige `success_threshold`.
- El umbral debe encontrarse entre `0.0` y `1.0`.
- Las evidencias no basadas en puntuación no pueden declarar umbral.
- Las listas pedagógicas obligatorias utilizan límites mínimos Pydantic.
- Todavía no se implementaron referencias cruzadas entre etapas, actividades, Skills y evidencias.

### Explicación técnica didáctica

Estas clases son principalmente esquemas o contratos de datos Pydantic.

Un contrato de datos define:

- qué campos existen;
- qué tipos acepta cada campo;
- qué información es obligatoria;
- qué valores son válidos;
- qué estructuras puede recibir o devolver la API.

No constituyen por sí solas un patrón de diseño.

La ampliación es aditiva porque incorpora `experience` sin eliminar los campos heredados. Esta estrategia permite construir el núcleo v2 en paralelo, conservar compatibilidad y reducir el riesgo de regresiones.

### Pruebas

Se creó `tests/test_lesson_experience_schema.py` con cinco pruebas:

- compatibilidad de una lección heredada sin `experience`;
- deserialización correcta del contrato v2;
- rechazo de versiones no soportadas;
- obligación de umbral para medición por puntuación;
- rechazo de umbral en otros modos de medición.

### Incidencia controlada

La primera automatización ejecutó pytest mediante `/usr/bin/python3` en lugar del entorno virtual.

El mecanismo de reversión restauró automáticamente todos los cambios.

Se confirmó después:

- `.venv/bin/python3`;
- Pydantic `2.12.5`;
- pytest `9.0.3`;
- repositorio limpio.

La implementación se repitió utilizando explícitamente el entorno virtual del proyecto.

### Validaciones finales

- Cinco pruebas específicas: correctas.
- Suite backend completa: `176 passed`.
- Compilación Python: correcta.
- Validación estructural AST: correcta.
- Se confirmaron seis clases v2.
- `Lesson` conserva nueve campos con `experience` aditivo.
- `git diff --check`: correcto.
- Control de separaciones excesivas: correcto.

### Límites respetados

- No se modificó `content_tree.json`.
- No se publicó una lección v2.
- No se modificó Flutter.
- No se modificaron endpoints.
- No se modificó persistencia.
- No se eliminaron `Example`, `vocabulary`, `grammar` ni `LessonDetailCard`.
- No se implementaron todavía referencias cruzadas ni progreso v2.

### Cierre técnico

- Commit técnico: `d2c4f60` — `B117 añadir contrato LessonExperience v2`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado después de la publicación.

### Estado de B117

El contrato backend aditivo inicial quedó implementado, probado y publicado.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B118 — Integridad interna de `LessonExperience`

### Objetivo

Proteger las relaciones internas del contrato `LessonExperience` para impedir que una experiencia incoherente llegue a la API o a Flutter.

### Implementación

- Se añadió `validate_internal_integrity` como `model_validator` de `LessonExperience`.
- Se validan identificadores duplicados de Skills, etapas, apoyos lingüísticos y evidencias.
- Los apoyos lingüísticos solo pueden referenciar etapas existentes.
- Las evidencias solo pueden referenciar Skills declaradas por la experiencia.
- Cada evidencia debe referenciar una etapa existente.
- La actividad de cada evidencia debe estar declarada por su etapa.
- La política de finalización solo puede referenciar etapas y evidencias existentes.
- Las evidencias obligatorias deben coincidir exactamente con `required_evidence_ids`.
- Las condiciones de finalización basadas en actividad exigen al menos una actividad.

### Explicación técnica didáctica

`LessonExperience` actúa como responsable de las reglas que relacionan sus componentes internos.

La validación de tipo confirma, por ejemplo, que `stage_id` es texto.

La validación de integridad confirma que ese `stage_id` corresponde realmente a una etapa declarada.

Este comportamiento se aproxima al principio de raíz de agregado: una entidad principal protege la coherencia de los elementos que administra. No implica todavía una adopción completa de Domain-Driven Design.

### Pruebas

- Se creó `tests/test_lesson_experience_integrity.py`.
- Se añadieron 19 casos específicos mediante pruebas parametrizadas.
- Las cinco pruebas de contrato de B117 continúan correctas.
- Pruebas específicas combinadas: `24 passed`.
- Suite backend completa: `195 passed`.

### Corrección del método

- Dos intentos de transportar código extenso dentro de `python3 -c` fallaron por delimitadores y comillas anidadas.
- Un comando posterior de diagnóstico también falló por escape incorrecto.
- Ninguno de esos errores modificó el repositorio.
- Se volvió al último estado estable confirmado.
- Se abandonó el transporte de bloques extensos mediante cadenas anidadas.
- La implementación se dividió en un validador pequeño y un archivo de pruebas aislado.
- El script temporal fue eliminado después de confirmar la implementación.

### Validaciones finales

- Compilación Python: correcta.
- Suite backend completa: `195 passed`.
- `git diff --check`: correcto.
- Control de separaciones excesivas y espacios finales: correcto.

### Límites respetados

- No se modificó `content_tree.json`.
- No se modificó Flutter.
- No se modificaron endpoints ni persistencia.
- No se validó todavía la existencia externa de conversaciones, ejercicios o Skills.
- No se impuso todavía un orden obligatorio de tipos de etapa.
- No se evaluó calidad pedagógica o lingüística.

### Cierre técnico

- Commit técnico: `e2b9307` — `B118 validar integridad interna LessonExperience`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado después de la publicación.

### Estado de B118

La integridad interna de `LessonExperience` quedó implementada, probada y publicada.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B119 — Integridad externa de `LessonExperience`

### Objetivo

Proteger las referencias entre `LessonExperience` y los recursos reales declarados por `Lesson`, sin sustituir las validaciones del Constructor Pedagógico.

### Implementación

- Se añadió `validate_external_experience_integrity` como `model_validator` de `Lesson`.
- Los identificadores de conversaciones deben ser únicos en una lección v2.
- Los identificadores de ejercicios deben ser únicos en una lección v2.
- Una conversación y un ejercicio no pueden compartir el mismo identificador.
- Una evidencia `exercise_result` debe referenciar un ejercicio existente.
- Las Skills declaradas por una evidencia `exercise_result` deben pertenecer al ejercicio relacionado.
- Una evidencia `conversation_completion` debe referenciar una conversación existente.
- Las lecciones heredadas sin `experience` conservan su comportamiento anterior.

### Explicación técnica didáctica

B118 validó las relaciones internas del agregado `LessonExperience`.

B119 valida su frontera externa: comprueba que determinadas referencias internas correspondan realmente a recursos disponibles en la lección.

El validador está situado en `Lesson` porque allí están disponibles simultáneamente la experiencia, las conversaciones y los ejercicios.

Los tipos `comprehension_result`, `contextual_response` y `guided_production` no se resuelven todavía contra un modelo concreto, porque el contrato B116 no define aún un registro general de actividades.

### Separación de responsabilidades

El contrato público v2 rechaza referencias externas incoherentes cuando una lección contiene `LessonExperience`.

Las lecciones candidatas heredadas sin `experience` continúan llegando al sistema de validadores pedagógicos, que genera `findings` en lugar de ser detenido por Pydantic.

Esta separación evita que el contrato público sustituya prematuramente al proceso controlado de autoría y revisión.

### Pruebas

- Se creó `tests/test_lesson_experience_external_integrity.py`.
- Se añadió un caso externo coherente.
- Se añadieron seis casos negativos para duplicados, colisiones, recursos inexistentes y Skills incompatibles.
- La fase roja confirmó `6 failed, 1 passed` antes de implementar el validador.
- Las pruebas específicas de B119 quedaron en `7 passed`.
- Las pruebas seleccionadas de regresión quedaron en `44 passed`.
- La suite backend completa quedó en `202 passed`.

### Regresiones detectadas y corregidas

- El fixture válido de B117 contenía una evidencia `exercise_result`, pero no incluía el ejercicio referenciado.
- Se completó ese fixture con un ejercicio coherente y con la Skill declarada por la evidencia.
- La primera versión del validador comprobaba duplicados antes de detectar que una lección no tenía `experience`.
- Esto detenía pruebas del Constructor Pedagógico que introducen duplicados deliberadamente para generar `findings`.
- El retorno para lecciones heredadas se movió al inicio del validador.
- Después de la corrección, la suite completa pasó sin regresiones.

### Corrección del método

- Un comando extenso mediante `python3 -c` volvió a deformarse antes de ejecutarse.
- El error no modificó `content.py`.
- Se confirmó el último estado estable antes de continuar.
- El validador se preparó como fragmento temporal plano, se inspeccionó y después se aplicó con restauración automática.
- El fragmento temporal se eliminó tras superar las pruebas.

### Validaciones finales

- Compilación Python: correcta.
- Pruebas específicas B119: `7 passed`.
- Pruebas seleccionadas de contrato y regresión: `44 passed`.
- Suite backend completa: `202 passed`.
- `git diff --check`: correcto.

### Límites respetados

- No se modificó `content_tree.json`.
- No se modificó Flutter.
- No se modificaron endpoints ni persistencia.
- No se validó todavía el catálogo global de Skills.
- No se resolvieron todos los `stage.activity_ids` contra un registro general.
- No se impuso un tipo concreto de actividad para cada tipo de etapa.
- No se evaluó calidad pedagógica o lingüística.

### Cierre técnico

- Commit técnico: `c1e1af9` — `B119 validar referencias externas LessonExperience`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado después de la publicación.

### Estado de B119

La integridad externa inicial de `LessonExperience` quedó implementada, probada y publicada.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B120 — Validación de Skills de `LessonExperience`

### Objetivo

Validar que las Skills declaradas por `LessonExperience` existan en la especificación pedagógica aprobada de la unidad.

### Fuente de verdad

La fuente de verdad es `PedagogicalUnitSpecification.skills`.

`Lesson`, los ejercicios y `LessonExperience` solo almacenan referencias mediante `skill_ids`; no poseen por sí mismos el catálogo aprobado.

### Implementación

- Se creó `pedagogical_lesson_experience_skill_validation.py`.
- Se añadió `validate_lesson_experience_skills(candidate)`.
- El validador recorre las lecciones candidatas que contienen `LessonExperience`.
- Cada `experience.skill_id` se compara con las Skills declaradas en la especificación.
- Cada Skill desconocida genera un `ValidationFinding` reproducible de severidad `error`.
- El hallazgo usa `validator_id="lesson_experience_skills"`.
- `reference_ids` incluye el identificador de la lección y la Skill desconocida.
- El validador quedó integrado en `validate_pedagogical_candidate`.

### Explicación técnica didáctica

Esta regla pertenece al Constructor Pedagógico y no al modelo público `Lesson`.

El modelo `Lesson` no dispone de la especificación completa y no puede confirmar por sí solo si una Skill existe en el catálogo aprobado.

Los validadores deterministas comparan el contenido candidato con su especificación y producen `findings` que pueden revisarse antes de aprobar el contenido.

B118 ya garantiza que las Skills de cada evidencia pertenezcan a `LessonExperience.skill_ids`.

Por ello, validar nuevamente cada evidencia contra la especificación produciría hallazgos duplicados sin añadir detección nueva.

### Pruebas

- Candidato heredado sin experiencia: sin hallazgos.
- Experiencia con Skills válidas: sin hallazgos.
- Experiencia con Skill desconocida: un hallazgo de error.
- Integración en el orquestador principal: informe con estado `failed`.
- La fase roja confirmó `2 failed, 2 passed`.
- Las pruebas específicas finales quedaron en `4 passed`.
- La suite backend completa quedó en `206 passed`.

### Validaciones finales

- Compilación Python: correcta.
- Pruebas específicas B120: `4 passed`.
- Suite backend completa: `206 passed`.
- `git diff --check`: correcto.

### Límites respetados

- No se modificó `Lesson` ni sus validadores Pydantic.
- No se modificó `SkillSpecification`.
- No se modificó `content_tree.json`.
- No se modificó Flutter.
- No se modificaron endpoints, progreso ni persistencia.
- No se duplicó la validación de Skills de las evidencias.

### Cierre técnico

- Commit técnico: `1a25fda` — `B120 validar Skills de LessonExperience`.
- Push completado a `origin/master`.
- Repositorio confirmado limpio y sincronizado después de la publicación.

### Estado de B120

La validación de Skills de `LessonExperience` contra su fuente de verdad quedó implementada, probada y publicada.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B121 — Primera lección piloto v2 candidata

### Objetivo

Construir la primera lección piloto basada en `LessonExperience`, mantenerla físicamente separada del contenido activo y someterla a validaciones deterministas y revisión humana antes de cualquier integración.

### Especificación pedagógica aprobada

- Unidad: `a1-u1`.
- Lección piloto: `a1-u1-l1`.
- Skill: `a1_introduce_yourself`.
- Resultado observable: decir el nombre y el lugar de origen durante un intercambio breve.
- Etapas obligatorias: introducir, practicar, aplicar, evaluar y consolidar.
- Completar la lección no equivale a dominar ni retener la Skill.
- La cobertura debe permanecer en `pending_approval` hasta superar la revisión pedagógica humana.

### Infraestructura candidata

- Se creó `content/candidates/` como espacio aislado y versionado.
- La API y Flutter continúan leyendo exclusivamente `content/content_tree.json`.
- Se añadió `content/candidates/README.md` con las reglas del ciclo de vida.
- Se versionó `pedagogical-unit-specification-v2.json` como especificación aprobada independiente.
- Ningún mecanismo copia o promociona automáticamente candidatos al contenido activo.

### Validaciones ampliadas

- `validate_content_identifiers` valida ahora identificadores jerárquicos v2.
- Convenciones aprobadas: `-m<n>`, `-s<n>`, `-ls<n>` y `-ev<n>`.
- Los identificadores de misión, etapas, apoyos y evidencias deben ser únicos en toda la unidad candidata.
- `evaluation_evidence_ids` admite ejercicios heredados y `EvidenceDefinition` v2.
- Una evidencia v2 debe declarar la misma Skill que pretende evaluar.
- Las referencias desconocidas siguen produciendo un único hallazgo determinista.
- La compatibilidad con candidatos y ejercicios heredados se conserva.

### Candidata piloto creada

- Archivo: `content/candidates/a1-u1/pedagogical-unit-candidate-v2.json`.
- Contiene una lección, nueve etapas, tres conversaciones, dos ejercicios y tres evidencias.
- Evidencias obligatorias: `a1-u1-l1-ev2` y `a1-u1-l1-ev3`.
- Estado de validación almacenado: `pending`.
- Único hallazgo: advertencia `skill_coverage_status` por cobertura `pending_approval`.
- El informe almacenado coincide con una validación recalculada.
- `content/content_tree.json` permaneció idéntico al contenido publicado.

### Revisión humana

- La misión y la progresión pedagógica son adecuadas para A1.
- La comprensión, los apoyos lingüísticos y la práctica guiada son coherentes.
- `a1-u1-l1-c3` todavía no captura una producción personal real.
- Completar `c2` demuestra práctica, pero no producción autónoma.
- `conversation_completion` demuestra recorrido, no corrección semántica o fonética.
- La retroalimentación adaptativa no debe convertirse automáticamente en requisito obligatorio.
- Faltan referencias revisadas de pronunciación en-US y en-GB.
- Las traducciones de cortesía requieren revisión lingüística neutral.

### Decisión pedagógica

- B121 no declara demostrada, dominada ni retenida la Skill.
- La candidata permanece aislada y en `pending_approval`.
- La aprobación futura requiere capturar una respuesta personal mediante texto o voz.
- La evidencia deberá diferenciar completar una actividad de producir correctamente el resultado observable.
- El dominio y la retención requerirán evidencias múltiples y revisión diferida en bloques posteriores.

### Protección automática del artefacto

- Se creó `tests/test_pedagogical_candidate_artifact.py`.
- La prueba carga el JSON real mediante `PedagogicalUnitCandidate`.
- Comprueba que la candidata coincide exactamente con la especificación aprobada.
- Recalcula el informe y rechaza informes obsoletos o inventados.
- Protege el estado `pending_approval` y las dos evidencias obligatorias.

### Validaciones finales

- Compilación Python: correcta.
- Pruebas de identificadores y evidencias ampliadas: `43 passed`.
- Pruebas del artefacto real: `3 passed`.
- Suite backend completa: `219 passed`.
- `git diff --check`: correcto.

### Commits técnicos

- `4154989` — `B121 preparar infraestructura para candidata v2`.
- `135a07c` — `B121 separar finalizacion de dominio de Skill`.
- `1e08ad3` — `B121 crear candidata piloto v2 pendiente de aprobacion`.
- Los tres commits fueron publicados en `origin/master`.

### Límites respetados

- No se modificó `content_tree.json`.
- No se modificó Flutter.
- No se modificaron endpoints, progreso ni persistencia.
- No se implementó evaluación semántica o fonética.
- No se generaron ni sustituyeron audios.
- No se implementó promoción automática de candidatos.
- No se declaró dominio ni retención de la Skill.

### Estado de B121

La primera lección piloto v2 quedó especificada, construida, aislada, validada, protegida mediante pruebas y revisada humanamente.

La candidata permanece en `pending_approval` porque todavía falta una capacidad real para capturar y representar la producción personal del estudiante.

El cierre operativo requiere incorporar esta documentación, versionar el roadmap actualizado y confirmar nuevamente Git limpio y sincronizado.

## B122 — Captura de producción personal observable

### Objetivo

Representar una producción personal real del estudiante mediante contratos explícitos, sin confundir captura, recorrido, evaluación, dominio ni retención de una Skill.

### Contratos incorporados

- `LearnerProductionPrompt` declara qué turnos requieren producción.
- Cada prompt define modalidades aceptadas: `text` o `voice`.
- `LearnerProductionItem` representa una respuesta capturada.
- `ConversationProductionSubmission` agrupa las producciones de una conversación.
- La validación comprueba conversación, prompt, turno, modalidad y obligatoriedad.
- Los contratos no contienen puntuación, corrección semántica, evaluación fonética, dominio ni retención.

### Integridad pedagógica

- Un `production_prompt` solo puede pertenecer a un turno `learner`.
- Sus identificadores siguen `<conversation_id>-p<n>`.
- Los identificadores deben ser únicos dentro de la unidad candidata.
- `contextual_response` requiere una conversación existente con al menos un prompt.
- Su `measurement_mode` continúa siendo `completion`.
- Una producción registrada no se considera automáticamente correcta.

### Aplicación a la candidata

- `a1-u1-l1-c3-t2` requiere `a1-u1-l1-c3-p1` para el nombre.
- `a1-u1-l1-c3-t4` requiere `a1-u1-l1-c3-p2` para el origen.
- `a1-u1-l1-c3-t6` requiere `a1-u1-l1-c3-p3` para la respuesta de cortesía.
- Los tres prompts admiten texto y voz y son obligatorios.
- `a1-u1-l1-ev3` cambió de `conversation_completion` a `contextual_response`.
- El informe recalculado permanece en `pending` con una advertencia `skill_coverage_status`.
- La cobertura continúa en `pending_approval`.

### Revisión humana actualizada

- B122 resuelve el contrato de captura y evidencia contextual.
- Persistencia y presentación en Flutter continúan pendientes.
- No existe todavía evaluación semántica o fonética.
- También siguen pendientes la adaptación condicional, pronunciaciones revisadas y traducciones neutrales.
- La candidata permanece aislada del contenido activo.

### Protección automática

- `tests/test_pedagogical_candidate_artifact.py` protege los tres prompts.
- La prueba verifica modalidades, obligatoriedad y `contextual_response`.
- El informe almacenado debe coincidir con la validación recalculada.
- `content/content_tree.json` permanece sin modificaciones.

### Validaciones finales

- Validación específica de candidata y contratos: `62 passed`.
- Suite backend completa: `250 passed`.
- `git diff --check`: correcto.
- Git quedó limpio y sincronizado después del commit técnico.

### Commits técnicos

- `4829318` — `B122 definir contratos de produccion personal`.
- `b2dccd6` — `B122 aplicar produccion personal a candidata`.
- Ambos commits fueron publicados en `origin/master`.

### Límites respetados

- No se añadieron tablas, migraciones ni endpoints.
- No se implementó persistencia de producciones.
- No se modificó Flutter.
- No se implementó evaluación semántica ni fonética.
- No se modificó el contenido pedagógico activo.
- No se declaró demostrada, dominada ni retenida la Skill.

### Estado de B122

La captura de producción personal quedó definida, validada y aplicada a la candidata aislada.

La candidata continúa en `pending_approval` hasta disponer de persistencia, presentación y revisión de las producciones capturadas.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B123 — Persistencia de producción personal

### Objetivo

Persistir de forma estructurada y trazable las producciones personales capturadas por los contratos de B122, sin convertir su almacenamiento en evaluación, dominio ni retención de una Skill.

### Persistencia incorporada

- `conversation_production_submissions` representa cada entrega completa de una conversación.
- `learner_productions` almacena las producciones individuales asociadas a la entrega.
- Cada producción conserva `prompt_id`, `turn_id`, modalidad, texto y referencia de audio cuando corresponda.
- La relación hija usa clave foránea con borrado en cascada.
- La unicidad por entrega y prompt evita duplicar una misma producción requerida.
- Las tablas fueron creadas mediante el mecanismo actual `Base.metadata.create_all` y su estructura fue comprobada en PostgreSQL.

### Contratos de lectura persistida

- `LearnerProductionRecord` incorpora el identificador persistido de cada producción.
- `ConversationProductionSubmissionRecord` incorpora identificador de entrega, fecha de envío y producciones persistidas.
- Los contratos continúan sin puntuación, corrección, dominio, retención ni evaluación fonética.

### Servicio interno

- `save_conversation_production_submission` valida la entrega antes de iniciar escrituras.
- La entrega y sus producciones se guardan dentro de una única transacción.
- Ante `SQLAlchemyError`, el servicio ejecuta `rollback` y no conserva datos parciales.
- `get_conversation_production_submissions_by_user` reconstruye las entregas persistidas en orden cronológico.
- El servicio recibe explícitamente la `Conversation`; no carga ni publica contenido candidato.

### Protección automática

- La prueba de guardado y lectura verifica persistencia y reconstrucción completas.
- La prueba de entrega inválida confirma que la validación ocurre antes de escribir.
- La prueba de fallo de `commit` confirma rollback de entrega y producciones.
- Los datos de prueba se aíslan mediante usuarios `test-user-b123-*`.

### Validaciones finales

- Contratos y persistencia relacionados: `23 passed`.
- Suite backend completa: `256 passed`.
- `git diff --check`: correcto.
- El cambio técnico quedó publicado y Git limpio antes de documentar el cierre.

### Commits técnicos

- `76ddb52` — `B123 definir persistencia de producciones`.
- `00b9269` — `B123 definir registros de producciones persistidas`.
- `f31e533` — `B123 persistir producciones capturadas`.
- Los commits fueron publicados en `origin/master`.

### Límites respetados

- No se añadió ningún endpoint para estas producciones.
- No se modificó Flutter.
- No se expuso la candidata al contenido activo.
- No se implementó evaluación semántica ni fonética.
- No se declaró demostrada, dominada ni retenida ninguna Skill.

### Estado de B123

La persistencia y lectura interna de las producciones personales quedaron implementadas, validadas y protegidas automáticamente.

La candidata continúa en `pending_approval`: todavía falta presentar y revisar estas producciones dentro de la experiencia de usuario.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B124 — Exposición controlada de producciones personales

### Objetivo

Exponer mediante API las producciones personales persistidas, manteniendo una frontera estricta entre contenido activo y contenido candidato.

### Frontera de contenido activo

- `save_active_conversation_production_submission` resuelve la conversación exclusivamente desde `content/content_tree.json`.
- Una conversación inexistente en contenido activo es rechazada antes de persistir.
- `level_id`, `unit_id` y `lesson_id` deben coincidir con la jerarquía publicada.
- La validación de prompts, turnos, modalidades y obligatoriedad continúa delegada a los contratos de B122.
- La persistencia atómica y el rollback continúan delegados a B123.

### Lectura controlada

- `get_active_conversation_production_submissions_by_user` parte de la persistencia interna existente.
- Solo devuelve entregas cuya conversación continúa presente en contenido activo.
- También exige coincidencia de la jerarquía persistida con la publicada.
- Una producción histórica puede permanecer en base de datos sin quedar expuesta por la API.

### API incorporada

- `POST /api/v1/conversation-productions` guarda una entrega válida perteneciente a contenido activo.
- `GET /api/v1/conversation-productions/{user_id}` devuelve únicamente producciones asociadas a contenido activo.
- Los errores de validación contextual se traducen a HTTP `400`.
- El router quedó registrado en la API v1.

### Aislamiento de candidata

- `content/candidates/` continúa sin ser consumido por la API.
- `a1-u1-l1-c3` sigue fuera de `content/content_tree.json`.
- Las pruebas positivas utilizan contenido sintético mediante `monkeypatch`; no publican la candidata.
- La API rechaza actualmente `a1-u1-l1-c3` cuando se intenta usar como contenido activo real.
- La revisión humana continúa en `pending_approval`.

### Protección automática

- La frontera de servicio rechaza conversación inexistente y jerarquía incorrecta.
- La frontera de servicio valida guardado y lectura cuando el contenido se resuelve como activo.
- La lectura controlada oculta persistencia perteneciente a contenido no activo.
- Las pruebas HTTP verifican aislamiento, guardado/lectura, jerarquía y filtrado.
- Servicio y API relacionados: `12 passed`.

### Validaciones finales

- Suite backend completa: `265 passed`.
- `git diff --check`: correcto.
- El cambio técnico quedó publicado y Git limpio antes del cierre documental.

### Commit técnico

- `b26bcf3` — `B124 exponer producciones de contenido activo`.
- El commit fue publicado en `origin/master`.

### Límites respetados

- No se modificó `content/content_tree.json`.
- No se publicó ni promocionó la candidata.
- No se modificó Flutter.
- No se implementó evaluación semántica ni fonética.
- No se almacenó ninguna conclusión de corrección, dominio o retención de Skills.
- No se añadió preview de contenido candidato mediante API.

### Estado de B124

La exposición backend de producciones personales quedó implementada y limitada al contenido pedagógico activo.

La candidata continúa en `pending_approval`; la siguiente capacidad necesaria es presentar y revisar las producciones personales en Flutter sin asumir todavía evaluación automática.

El cierre operativo requiere versionar esta documentación y confirmar nuevamente Git limpio y sincronizado.

## B125 — Sincronización del roadmap tras B104 frontend

### Objetivo

Sincronizar la planificación backend con el cierre real de B104 frontend antes de abrir una nueva capacidad técnica.

### Actualización realizada

- El roadmap reconoce que B104 frontend completó la presentación y revisión de producciones personales persistidas.
- La candidata `a1-u1-l1` continúa aislada y en `pending_approval`.
- B104 frontend no publicó contenido candidato.
- Presentar una producción no implica evaluarla ni demostrar dominio o retención de ninguna Skill.
- `presentación de producciones personales en Flutter` queda marcada como completada dentro de la evolución prevista de Fase 5.
- El orden restante de Fase 5 no fue modificado.

### Límites respetados

- No se modificó código backend.
- No se modificó Flutter.
- No se publicó `content/candidates/`.
- No se inició reconocimiento de voz.
- No se implementó evaluación semántica ni fonética.
- No se abrió Fase 6.
- No se introdujeron agentes ni MCP.

### Estado de B125

La planificación queda sincronizada con el estado real del producto.

La siguiente capacidad técnica deberá definirse explícitamente a partir del roadmap actualizado; no se asume automáticamente que el siguiente bloque sea reconocimiento de voz.

## B129 — Contrato trazable de evaluación de producciones personales

Fecha: 2026-07-27

### Objetivo

Establecer la arquitectura trazable necesaria para evaluar producciones personales sin mezclar captura, reconocimiento de voz, evaluación, dominio ni retención de Skills.

### Contratos implementados

Se creó `app/schemas/evaluation.py` con:

- `ProductionEvaluationCriterion`;
- `ProductionEvaluationResult`;
- `LessonProductionEvaluationPlan`.

`ProductionEvaluationCriterion` declara qué producción será evaluada, su evidencia pedagógica, conversación, prompt, dimensión, modalidad y modo de medición.

Dimensiones iniciales:

- `semantic`;
- `phonetic`.

Modos iniciales:

- `binary`;
- `score`.

Los scores permanecen normalizados entre `0.0` y `1.0`.

Una evaluación fonética solo puede aplicarse a modalidad `voice`.

`ProductionEvaluationResult` representa el resultado runtime de evaluar una producción concreta y conserva trazabilidad mediante:

- `production_id`;
- `criterion_id`;
- estado;
- score opcional;
- identificador y versión del evaluador;
- fecha de evaluación.

No representa mastery ni retention.

### Separación de responsabilidades

B129 preserva las fronteras existentes:

- `LearnerProduction` continúa representando únicamente lo producido por el estudiante;
- `SpeechRecognitionResult` continúa representando únicamente lo reconocido técnicamente;
- `EvidenceDefinition` continúa declarando evidencia pedagógica estática;
- los criterios evaluativos viven en un contrato específico;
- los resultados evaluativos viven separados de la producción capturada;
- `Lesson` y `ConversationTurn` no recibieron lógica evaluativa;
- `LessonExperience.contract_version` continúa siendo `2.0`.

### Integridad contextual

Se creó `production_evaluation_validation_service.py`.

La validación comprueba:

- IDs de criterios únicos;
- existencia de `LessonExperience`;
- existencia de `EvidenceDefinition`;
- correspondencia entre evidencia y conversación;
- existencia del `production_prompt`;
- compatibilidad de modalidades entre criterio y prompt;
- correspondencia entre resultado, producción y criterio;
- compatibilidad entre producción y modalidad evaluable;
- reglas de score y `success_threshold`;
- coherencia entre score y estado `passed` o `failed`.

### Integración con candidatas

`PedagogicalUnitCandidate` recibió de forma aditiva:

`evaluation_plans: list[LessonProductionEvaluationPlan]`

Las candidatas existentes continúan siendo válidas sin planes evaluativos.

Se protege:

- un único plan por lección;
- rechazo de referencias a lecciones inexistentes.

La validación evaluativa quedó integrada en `validate_pedagogical_candidate()` mediante el hallazgo determinista:

`production_evaluation_integrity`.

### Candidata piloto

La candidata aislada `a1-u1-l1` recibió un plan semántico para la conversación aplicada `c3`.

Relaciones explícitas:

- `p1` → el estudiante declara un nombre;
- `p2` → el estudiante declara un origen;
- `p3` → el estudiante responde cortésmente.

Los tres criterios:

- referencian `a1-u1-l1-ev3`;
- pertenecen a `a1-u1-l1-c3`;
- usan dimensión `semantic`;
- usan medición `binary`;
- admiten texto y voz;
- no realizan todavía evaluación automática.

La candidata continúa aislada del contenido activo.

### Corrección documental

El contrato canónico fue alineado con la implementación de B117:

- `success_threshold` es el concepto vigente;
- solo se utiliza con `measurement_mode=score`;
- rango permitido `0.0–1.0`.

La antigua referencia documental a `success_condition` fue retirada.

### Pruebas

Se añadieron pruebas para:

- schemas de evaluación;
- integridad contextual;
- resultados runtime;
- compatibilidad de `PedagogicalUnitCandidate`;
- candidata piloto real;
- integración con el pipeline pedagógico.

Resultado específico B129:

`27 passed`

Suite backend completa:

`292 passed`

`git diff --check`: correcto.

### Límites respetados

B129 no implementa todavía:

- algoritmo de similitud semántica;
- evaluación fonética real;
- puntuación automática de pronunciación;
- feedback adaptativo;
- `EvidenceRecord` persistido;
- mastery;
- retention;
- conversación libre;
- inteligencia artificial generativa;
- publicación de la candidata.

### Estado de B129

La infraestructura trazable de evaluación queda implementada e integrada.

La siguiente evolución podrá construir un primer evaluador real sobre estos contratos sin volver a mezclar reconocimiento, producción y evaluación.## B130 — Primer evaluador semántico determinista

Fecha: 2026-07-27

Objetivo:
Convertir una producción personal de texto o un transcript STT en resultados evaluativos trazables usando los contratos creados en B129.

Resultado:
- Se añadió `SemanticEvaluationRule` como contrato declarativo de reglas.
- Se implementó `evaluate_semantic_production` para producir `ProductionEvaluationResult`.
- El motor acepta texto escrito o transcript reconocido de una producción de voz.
- Las reglas se declaran en `LessonProductionEvaluationPlan.semantic_rules`; el motor no contiene lógica específica por `criterion_id`.
- La candidata A1-U1-L1 incorpora reglas para nombre, procedencia y respuesta cortés.
- Se añadió resolución automática producción → prompt → criterio → regla → resultado.
- Se añadió orquestación candidata → lesson → plan → producción → resultado.
- Las reglas y criterios mantienen trazabilidad con los contratos de B129.
- Se validaron 19 pruebas específicas de B130.
- Suite completa backend: 311 passed.
- `git diff --check`: correcto.
- Commit técnico: `4109b98`.

Límite técnico:
Este primer evaluador ejecuta patrones lingüísticos deterministas configurables. Evalúa criterios clasificados como semánticos, pero no constituye todavía un motor de comprensión semántica profunda. No se implementaron API, persistencia del resultado, evaluación fonética, feedback adaptativo, mastery, retention ni IA.

## B131 — Persistencia trazable de resultados evaluativos

Fecha: 2026-07-27

Objetivo:
Persistir los resultados generados por la evaluación de producciones personales sin mezclar evaluación con la producción capturada.

Resultado:
- Se creó `production_evaluation_results` como entidad persistente separada de `learner_productions`.
- Cada resultado mantiene `production_id`, `criterion_id`, `status`, `score`, `evaluator_id`, `evaluator_version` y `evaluated_at`.
- `ProductionEvaluationResultRecord` incorpora `evaluation_result_id` como identidad persistente.
- La FK `production_id -> learner_productions.id` usa `ON DELETE CASCADE`.
- Se implementó persistencia por lotes y consulta del historial evaluativo por producción.
- El historial es append-only: nuevas evaluaciones/versiones no sobrescriben resultados anteriores.
- Se integró producción persistida → evaluación semántica B130 → persistencia B131.
- Los errores previos a la evaluación no generan resultados persistidos.
- Se introdujo Alembic 1.18.5 como mecanismo versionado de evolución del esquema.
- Baseline histórico: `b1fe71209621`.
- Migración B131: `98ff29894521`.
- PostgreSQL fue migrado y verificado en `98ff29894521 (head)`.
- `alembic check`: sin nuevas operaciones detectadas.
- 10 pruebas específicas B131 superadas.
- Suite completa backend: 321 passed.
- `git diff --check`: correcto.
- Commit técnico: `66d348b`.

Decisión de infraestructura:
Desde B131, los cambios de esquema deben expresarse mediante migraciones Alembic versionadas. `Base.metadata.create_all()` no se considera mecanismo de evolución de una base existente.

Límites:
B131 no añade API pública de resultados, feedback adaptativo, mastery, retention, evaluación fonética ni comprensión semántica avanzada.

## B132 — Feedback pedagógico determinista y trazable

Fecha: 2026-07-27

Objetivo:
Transformar un resultado evaluativo concreto en orientación pedagógica útil y trazable sin confundir feedback con dominio de una Skill.

Resultado:
- Se creó `ProductionFeedbackRule` como contrato declarativo de feedback.
- Se creó `ProductionFeedback` con trazabilidad a `evaluation_result_id`, `production_id` y `criterion_id`.
- Se implementó `generate_pedagogical_feedback`.
- El feedback diferencia resultados `passed` y `failed`.
- Cada salida conserva la descripción pedagógica del criterio y una orientación accionable.
- Se añadió `LessonProductionFeedbackPlan`.
- `PedagogicalUnitCandidate` admite `feedback_plans` de forma aditiva.
- La candidata A1-U1-L1 declara reglas de feedback para nombre, procedencia y respuesta cortés.
- Se implementó resolución candidata → criterio → regla → feedback.
- Se validó la integridad feedback plan → evaluation plan → criterion.
- El feedback no modifica `LearnerProduction` ni `ProductionEvaluationResult`.
- 13 pruebas específicas B132 superadas.
- Suite completa backend: 334 passed.
- `git diff --check`: correcto.
- Commit técnico: `bb5c331`.

Límites:
B132 no persiste todavía el feedback, no expone API pública y no implementa mastery, retention, evaluación fonética, comprensión semántica avanzada ni IA generativa.

## B133 — Persistencia trazable del feedback pedagógico

Fecha: 2026-07-27

Objetivo:
Conservar exactamente el feedback pedagógico generado para un resultado evaluativo, manteniendo separadas producción, evaluación y orientación.

Resultado:
- Se creó la tabla `production_feedbacks`.
- Cada feedback persiste `evaluation_result_id`, descripción del criterio, mensaje, orientación, `generator_id`, `generator_version` y `generated_at`.
- La FK `evaluation_result_id -> production_evaluation_results.id` usa `ON DELETE CASCADE`.
- `ProductionFeedbackRecord` expone `feedback_id` y fecha de generación.
- `production_id`, `criterion_id` y estado evaluativo se reconstruyen desde el resultado enlazado y no se duplican como autoridad persistente.
- Se implementó persistencia append-only del historial de feedback.
- Se implementó generación B132 → persistencia B133 de extremo a extremo.
- Se rechazan inconsistencias de producción, criterio, estado o resultado evaluativo inexistente.
- Migración Alembic B133: `f81a78f8c1c4`.
- PostgreSQL verificado en `f81a78f8c1c4 (head)`.
- `alembic check`: sin nuevas operaciones detectadas.
- 8 pruebas específicas B133 superadas.
- Suite completa backend: 342 passed.
- `git diff --check`: correcto.
- Commit técnico: `f07d4d5`.

Límites:
B133 no añade API pública de feedback, mastery, retention, evaluación fonética, adaptación automática ni IA generativa.

## B134 — Pipeline evaluativo completo de una producción

Fecha: 2026-07-27

Objetivo:
Coordinar evaluación, persistencia del resultado, generación de feedback y persistencia del feedback como una única capacidad runtime consistente.

Resultado:
- Se creó `ProductionEvaluationOutcome`.
- Se implementó `evaluate_production_atomically`.
- El pipeline coordina producción persistida → evaluación semántica → resultado persistido → feedback pedagógico → feedback persistido.
- La persistencia evaluativa y la persistencia de feedback admiten `commit_transaction=False` para participar en una transacción externa.
- El comportamiento previo se mantiene con `commit_transaction=True` por defecto.
- El pipeline realiza un único `commit()` cuando toda la cadena finaliza correctamente.
- Ante cualquier fallo se ejecuta `rollback()` de toda la operación.
- Se verificó que un fallo durante el feedback elimina la evaluación temporal pero conserva la producción que existía antes del pipeline.
- El flujo soporta transcript STT para producciones de voz.
- 3 pruebas específicas B134 superadas.
- Suite completa backend: 345 passed.
- `git diff --check`: correcto.
- Commit técnico: `955ef49`.

Límites:
B134 no añade API pública, cambios de esquema, mastery, retention, evaluación fonética, feedback adaptativo ni IA generativa.

## B135 — Desacoplar evaluación runtime de la candidata pedagógica

Fecha: 2026-07-27

Objetivo:
Eliminar la dependencia directa del pipeline evaluativo runtime respecto a `PedagogicalUnitCandidate`, manteniendo la candidata aislada hasta una aprobación explícita.

Resultado:
- Se creó `ProductionEvaluationRuntimeConfig` como contrato neutral de configuración runtime.
- El contrato reúne `lesson_id`, plan evaluativo y plan de feedback.
- Se valida coherencia de lección y referencias feedback → criterio.
- Se creó `build_runtime_evaluation_config_from_candidate` como adaptador explícito desde una candidata.
- `evaluate_production_atomically` ya no importa ni recibe `PedagogicalUnitCandidate`.
- El pipeline consume únicamente `ProductionEvaluationRuntimeConfig`.
- Evaluación semántica, persistencia evaluativa, generación de feedback, persistencia de feedback y atomicidad permanecen intactas.
- La candidata A1-U1-L1 sigue aislada y no se publica como contenido runtime.
- Una futura fuente de contenido activo podrá construir el mismo contrato sin modificar el pipeline.
- Se corrigió la prueba de rollback de B134 para garantizar que el fallo ocurre dentro del pipeline después del `flush()` evaluativo.
- 7 pruebas del alcance B135 superadas, 4 de ellas nuevas.
- Suite completa backend: 349 passed.
- `git diff --check`: correcto.
- Commit técnico: `9795b2f`.

Límites:
B135 no publica la candidata, no añade API pública, no cambia reglas pedagógicas y no implementa mastery, retention, fonética ni IA.

## B136 — Frontera de evidencia fonética trazable

Fecha: 2026-07-27

Objetivo:
Crear una frontera neutral y trazable para evaluación fonética sin confundir reconocimiento de palabras con calidad de pronunciación.

Resultado:
- Se creó `PhoneticEvaluationEvidence` para representar evidencia acústica normalizada.
- La evidencia conserva `production_id`, `criterion_id`, `audio_reference`, puntuación, analizador, versión y fecha de análisis.
- Se creó `evaluate_phonetic_production_from_evidence`.
- El evaluador exige producción de voz, criterio fonético y medición `score`.
- Se valida la correspondencia producción → criterio → audio → evidencia antes de evaluar.
- El resultado `passed` o `failed` se determina con el `success_threshold` del criterio.
- La salida reutiliza `ProductionEvaluationResult` y la persistencia introducida en B131.
- `learner_productions` continúa sin almacenar `phonetic_score`.
- El transcript reconocido no se usa como medida de pronunciación.
- La integración de persistencia fue comprobada con una producción de voz real en SQLite aislado.
- 8 pruebas específicas B136 superadas.
- Suite completa backend: 357 passed.
- `git diff --check`: correcto.
- Commit técnico: `616d43d`.

Límites:
B136 no analiza audio todavía, no selecciona un motor acústico, no añade criterios fonéticos a la candidata, no publica contenido, no añade API pública y no introduce mastery, retention ni IA.

## B137 — Ingesta y referencia resoluble de audio de producción

Fecha: 2026-07-27

Objetivo:
Hacer que las grabaciones del estudiante puedan entrar realmente al backend y quedar disponibles mediante referencias opacas y resolubles para futuros analizadores acústicos.

Resultado:
- Se añadió `python-multipart==0.0.32`.
- Se creó `POST /conversation-production-audio` para recibir WAV mediante multipart.
- La subida binaria permanece separada del contrato JSON existente de `POST /conversation-productions`.
- Se creó `ProductionAudioUploadRecord`.
- El backend almacena el audio fuera de PostgreSQL en un directorio privado configurable mediante `PRODUCTION_AUDIO_DIR`.
- El nombre físico del archivo se genera mediante UUID y nunca procede del nombre enviado por el cliente.
- La referencia persistible tiene formato `production-audio://UUID` y no expone rutas del servidor.
- Se añadieron almacenamiento, resolución y lectura interna de audio para futuros analizadores.
- Se limita cada audio a 10 MiB.
- Se comprueba cabecera RIFF/WAVE antes del almacenamiento.
- El directorio se protege con permisos `0700` y los archivos con `0600`.
- Se rechazan referencias con esquema no soportado, UUID inválido y audios inexistentes.
- La frontera permite sustituir posteriormente almacenamiento local por object storage sin cambiar la evaluación pedagógica.
- 11 pruebas específicas B137 superadas.
- Suite completa backend: 368 passed.
- `git diff --check`: correcto.
- Commit técnico: `52cf574`.

Configuración runtime:
`PRODUCTION_AUDIO_DIR` debe apuntar al directorio privado administrado por backend donde se almacenarán los WAV de producción.

Límites:
B137 no integra todavía un analizador acústico, no produce puntuaciones fonéticas, no modifica la candidata pedagógica, no cambia el esquema de base de datos y no introduce mastery, retention ni IA.

## B138 — Selección y validación del analizador fonético real

Fecha de cierre: 2026-07-28

Objetivo:
Seleccionar mediante pruebas reproducibles una arquitectura acústica real capaz de producir evidencia fonética trazable para la frontera definida en B136.

Resultado:
- Se trabajó en entornos experimentales aislados bajo `/tmp`, sin contaminar `.venv` ni `requirements.txt` del backend.
- El primer candidato fue `facebook/wav2vec2-lv-60-espeak-cv-ft`.
- El modelo produjo fonemas, logits CTC y una inferencia cacheada aproximada de 0.30 s para un WAV de 1.91 s en CPU.
- Se descartó la pérdida CTC global como puntuación de pronunciación: el experimento controlado `John` frente a `Joan` no discriminó consistentemente ambas hipótesis.
- El segundo candidato fue `Jianshu001/wavlm-phoneme-scorer`, basado en G2P, alineación CTC, WavLM, GOP y scorer por fonema.
- Se inspeccionó el pipeline antes de ejecutarlo y se detectó que el código original cargaba el checkpoint mediante `torch.load(..., weights_only=False)`.
- No se ejecutó esa carga insegura. Se creó una copia experimental que conserva `weights_only=True`, `mmap=True` y una allowlist mínima de tipos NumPy.
- El checkpoint `wavlm_finetuned.pt` tiene SHA-256 `7b9485b679d9a1219ac7dbef197b5185ec16e7909632b082b1f0576a963e0040`.
- La carga restringida confirmó `model_state` como `OrderedDict` con 517 entradas.
- El pipeline completo ejecutó en CPU: WAV → G2P → alineación CTC → WavLM → GOP → scoring por fonema.
- Para `Hello, I am John.` obtuvo 88.4/100 global y 92.9/100 en `John`.
- En el control donde el audio decía `Joan` manteniendo como objetivo `John`, la palabra cayó a 71.1/100.
- El fonema objetivo `/aa/` pasó de score 83.2 y `pherr=0.25` a score 19.9 y `pherr=0.95`, quedando marcado como error.
- El fonema `/hh/` de `Hello` fue marcado como error en ambas muestras, lo que demuestra que la calibración pedagógica todavía está pendiente.
- Se selecciona WavLM + alineación CTC + GOP + scorer por fonema como arquitectura técnicamente viable para continuar.
- B138 no integra todavía el analizador en producción y no convierte sus scores en evidencia pedagógica aprobada, mastery ni retention.

Límites:
Las pruebas B138 usaron audio sintético eSpeak. La integración futura deberá conservar la frontera neutral de B136, una carga segura y trazable del modelo, y validar posteriormente el comportamiento con voces humanas y criterios pedagógicos antes de fijar umbrales de producción.

## B139 — Integración runtime del analizador fonético real

Fecha de cierre: 2026-07-28

Objetivo:
Integrar la arquitectura fonética seleccionada en B138 detrás de las fronteras neutrales B136-B137, manteniendo sus dependencias pesadas fuera del proceso FastAPI.

Resultado:
- Se creó `PhoneticAnalyzer` como protocolo neutral de análisis.
- Se añadió ejecución fonética desde `LessonProductionEvaluationPlan`.
- El pipeline atómico puede combinar resultados semánticos y fonéticos en una misma transacción.
- La ausencia temporal de feedback fonético no relaja la obligación de feedback para resultados semánticos.
- `AcousticPhoneticMeasurement` representa la medición acústica previa a la trazabilidad de dominio.
- `ProductionAudioPhoneticAnalyzer` resuelve `production-audio://UUID` y entrega al scorer únicamente WAV resuelto y texto de referencia explícito.
- `CommandAcousticPhoneticScorer` ejecuta analizadores externos con `shell=False`, timeout y contrato JSON validado.
- Se versionó `scripts/phonetic/wavlm_gop_runner.py` para normalizar `overall_score` de 0-100 a 0.0-1.0.
- El runner verifica SHA-256 del pipeline acústico y del checkpoint antes de ejecutar el modelo.
- La identidad persistida del analizador incluye versión del runner y hashes verificados.
- `build_runtime_phonetic_analyzer` construye el runtime mediante variables `PHONETIC_ANALYZER_*`.
- Las dependencias Torch/WavLM permanecen aisladas de `.venv`.
- El smoke test real produjo `PhoneticEvaluationEvidence` con score 0.884 y trazabilidad completa.
- Suite completa backend: 389 passed.
- `git diff --check`: correcto.
- Commit técnico: `f692f0f`.

Límites:
B139 demuestra integración técnica real, no validez pedagógica. Los scores y umbrales deberán validarse posteriormente con voces humanas representativas antes de utilizarse como criterio pedagógico de producción. No se añade todavía feedback fonético al estudiante, mastery ni retention.

## B140 — Calibración técnica humana reproducible del analizador fonético

Fecha de cierre: 2026-07-29

Objetivo:
Introducir una base reproducible para estudiar el comportamiento del analizador fonético B139 con voz humana real antes de establecer cualquier criterio pedagógico.

Resultado:
- Se añadieron contratos `PhoneticCalibrationSample`, `PhoneticCalibrationMeasurement` y `PhoneticCalibrationObservation`.
- Las muestras admiten `unlabeled` para impedir atribuir calidad pedagógica sin evaluación humana independiente.
- Se añadió carga y validación de manifiestos de calibración.
- El servicio de calibración verifica existencia, confinamiento de ruta y SHA-256 del WAV antes de medirlo.
- Se desacopló `build_runtime_acoustic_phonetic_scorer` para reutilizar el mismo runtime verificable de B139 en calibración.
- El runtime pesado se reconstruyó fuera de `.venv` bajo `~/.local/share/app-ingles/phonetic-runtime/` y reprodujo el primer score humano técnico `0.625`.
- Audio humano, manifiesto real, configuración runtime y mediciones permanecen locales e ignorados por Git; solo `manifest.example.json` es versionable.
- Tras corregir una incidencia de captura VMware, cuatro repeticiones válidas del mismo hablante y frase produjeron scores `0.574`, `0.582`, `0.626` y `0.606` (media técnica `0.597`, rango `0.052`).
- Validación específica B140: 20 passed.
- Suite completa backend: 407 passed.
- `git diff --check`: correcto.
- Commit técnico: `77ce27e`.

Límites:
Estas mediciones solo evidencian reproducibilidad técnica bajo un corpus inicial muy limitado. No representan porcentajes de pronunciación correcta, no permiten fijar umbrales pedagógicos y no sustituyen una calibración posterior con voces humanas representativas, etiquetado independiente y criterios pedagógicos.

Estado:
B140 técnicamente cerrado y validado. Publicación Git/GitHub pendiente.
