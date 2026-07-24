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
