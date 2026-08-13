# Bitácora del proyecto app-ingles-backend

## Estado actual

- Backend: FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy
- Driver: psycopg
- Última suite backend completa confirmada: 1277 passed durante la primera slice estructural del contrato curricular v1
- Suite frontend completa actual confirmada para el checkpoint B181: 44 passed
- Último bloque cerrado integralmente: B180
- Bloque activo: primera slice estructural del contrato curricular v1, pendiente de cierre documental y publicación; B181 continúa pausado en puerta pedagógica

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

## B141 — Protocolo técnico para corpus fonético humano representativo

Fecha: 2026-07-29

Objetivo:
Preparar contratos, trazabilidad y medición objetiva de cobertura para construir posteriormente un corpus fonético humano representativo sin convertir scores técnicos en conclusiones pedagógicas.

Resultado:
- Se añadió `RepresentativePhoneticCalibrationSample` con `speaker_id` y `session_id` pseudónimos.
- Se añadió `RepresentativePhoneticCalibrationObservation` para conservar muestra e identidad junto con su medición acústica.
- Se añadió un loader específico de manifiestos representativos sin modificar el contrato B140.
- El flujo representativo reutiliza la verificación SHA-256, confinamiento de rutas y scorer productivo de B140/B139.
- `RepresentativePhoneticCalibrationCoverage` registra únicamente número de muestras, hablantes y sesiones observadas.
- Las sesiones se contabilizan por `(speaker_id, session_id)` para evitar colisiones entre hablantes.
- Se añadió `manifest.representative.example.json` y un protocolo versionable en `calibration/phonetic/README.md`.
- Validación específica B141: 32 passed.
- Suite completa backend: 421 passed.
- `git diff --check`: correcto.
- Commit técnico: `4c00418`.

Límites:
B141 define cómo construir y medir un corpus humano representativo, pero no demuestra todavía representatividad real. No establece mínimos de hablantes, umbrales fonéticos, porcentajes de pronunciación correcta, feedback pedagógico, mastery ni retention.

Estado:
B141 cerrado, publicado y sincronizado con GitHub.

## B142 — Etiquetado fonético humano independiente y trazable

Fecha: 2026-07-29

Objetivo:
Separar explícitamente los juicios humanos de las mediciones acústicas para permitir una futura calibración pedagógica sin convertir scores técnicos en conclusiones humanas.

Resultado:
- Se añadió `PhoneticCalibrationHumanLabel` con `sample_id`, `labeler_id` pseudónimo, `rubric_version` y clasificación cualitativa.
- Las etiquetas permitidas son `acceptable`, `variant` y `known_error`.
- Se añadió un loader independiente para manifiestos de etiquetas humanas.
- Se añadió validación de integridad entre etiquetas y corpus: toda etiqueta debe apuntar a una muestra existente.
- Se rechazan duplicados de `(sample_id, labeler_id, rubric_version)`.
- Se versionó `human-labels.example.json`, permitiendo conservar desacuerdos entre evaluadores.
- Se versionó `human-labeling-rubric-1.0.md`, independiente del scorer acústico.
- Validación específica B142: 32 passed.
- Suite completa backend: 431 passed.
- `git diff --check`: correcto.
- Commit técnico: `8eee6c8`.

Límites:
B142 preserva juicios humanos independientes y trazables, pero no calcula consenso, no decide qué evaluador tiene razón, no compara aún etiquetas humanas con scores del modelo y no define umbrales pedagógicos, mastery ni retention.

Estado:
B142 cerrado, publicado y sincronizado con GitHub.

## B143 — Acuerdo humano descriptivo y trazable

Fecha: 2026-07-29

Objetivo:
Describir el grado de coincidencia observado entre evaluadores humanos sin convertir mayoría, unanimidad o desacuerdo en verdad pedagógica.

Resultado:
- Se añadió `PhoneticCalibrationHumanAgreement`.
- El resumen mantiene `sample_id` y `rubric_version` para impedir mezclar criterios de rúbricas distintas.
- Se conserva la distribución completa de `acceptable`, `variant` y `known_error`.
- Se registran número de etiquetas y número de evaluadores distintos.
- Se indica únicamente si la observación es unánime.
- El servicio agrupa por muestra y versión de rúbrica.
- El ejemplo versionado de B142 conserva correctamente su desacuerdo humano.
- Validación específica B143: 7 passed.
- Regresión de calibración B140-B143: 39 passed.
- Suite completa backend: 438 passed.
- `git diff --check`: correcto.
- Commit técnico: `a9ad708`.

Límites:
B143 no elige una etiqueta correcta, no calcula una mayoría como verdad, no compara todavía juicios humanos con scores acústicos y no establece umbrales pedagógicos, mastery ni retention.

Estado:
B143 cerrado, publicado y sincronizado con GitHub.

## B144 — Relación descriptiva entre evidencia técnica y humana

Fecha: 2026-07-29

Objetivo:
Relacionar de forma descriptiva y trazable la medición acústica técnica con las etiquetas humanas independientes y el acuerdo humano disponible, sin convertir ninguna señal en verdad o decisión pedagógica.

Resultado:
- Se añadió `PhoneticCalibrationHumanRelationship`.
- La relación conserva la `PhoneticCalibrationMeasurement`, las `PhoneticCalibrationHumanLabel` independientes y el `PhoneticCalibrationHumanAgreement`.
- Se exige coherencia de `sample_id` entre medición y acuerdo.
- Las etiquetas humanas deben compartir `sample_id` y `rubric_version` con el acuerdo asociado.
- El servicio preserva múltiples mediciones técnicas de una misma muestra sin sobrescribir evidencia.
- Las distintas versiones de rúbrica permanecen separadas.
- Los acuerdos sin medición correspondiente no generan relaciones artificiales.
- Validación específica B144: 9 passed.
- Regresión B142-B144: 19 passed.
- Suite completa backend: 447 passed.
- `git diff --check`: correcto.
- Commit técnico: `9eae15a`.

Límites:
B144 describe relaciones entre evidencia técnica y humana, pero no deriva una etiqueta verdadera, no interpreta el score como corrección fonética, no calcula umbrales pedagógicos, no genera feedback, mastery ni retention, y no convierte mayoría o unanimidad en decisión automática.

Estado:
B144 cerrado, publicado y sincronizado con GitHub.

## B145 — Resumen descriptivo modelo-humano

Fecha: 2026-07-29

Objetivo:
Describir de forma agregada la relación observada entre scores acústicos técnicos y evaluación humana, preservando el contexto versionado y sin convertir la relación en una decisión pedagógica.

Resultado:
- Se añadió `PhoneticCalibrationModelHumanObservation`.
- Cada observación conserva `sample_id`, identidad y versión del analizador, versión de rúbrica, score técnico y acuerdo humano descriptivo.
- Se añadió `PhoneticCalibrationModelHumanSummary`.
- Los resúmenes se agrupan por `analyzer_id`, `analyzer_version` y `rubric_version`.
- Se conservan `observation_count`, `sample_count`, `score_min`, `score_max` y `score_mean`.
- Se acumula la distribución completa de `acceptable`, `variant` y `known_error`.
- Se conserva el número de observaciones unánimes sin interpretar unanimidad como verdad.
- Versiones distintas de analizador o rúbrica permanecen separadas.
- Validación específica B145: 13 passed.
- Regresión B142-B145: 32 passed.
- Suite completa backend: 460 passed.
- `git diff --check`: correcto.
- Commit técnico: `125ff37`.

Límites:
B145 produce únicamente evidencia descriptiva agregada. No calcula correlación causal o pedagógica, no define umbrales de pronunciación, no clasifica automáticamente muestras, no genera feedback pedagógico, mastery ni retention, y no interpreta mayoría o unanimidad como verdad.

Estado:
B145 cerrado, publicado y sincronizado con GitHub.

## B146 — Distribución descriptiva de scores por etiqueta humana

Fecha: 2026-07-29

Objetivo:
Describir cómo se distribuyen los scores acústicos técnicos dentro de cada etiqueta humana observada, conservando desacuerdo y contexto versionado sin convertir ninguna etiqueta en verdad.

Resultado:
- Se añadió `PhoneticCalibrationHumanLabelScoreSummary`.
- Los resúmenes se agrupan por `analyzer_id`, `analyzer_version`, `rubric_version` y etiqueta humana.
- Se conservan `observation_count`, `sample_count`, `score_min`, `score_max` y `score_mean`.
- Una misma muestra puede contribuir a distintas etiquetas cuando los evaluadores discrepan.
- El desacuerdo humano se conserva sin seleccionar una etiqueta correcta.
- Versiones distintas de analizador o rúbrica permanecen separadas.
- Validación específica B146: 10 passed.
- Regresión B142-B146: 42 passed.
- Suite completa backend: 470 passed.
- `git diff --check`: correcto.
- Commit técnico: `7f2e3b0`.

Límites:
B146 describe distribuciones de scores por juicio humano observado. No define umbrales, no clasifica automáticamente pronunciaciones, no interpreta una etiqueta como verdad, no genera feedback pedagógico, mastery ni retention.

Estado:
B146 cerrado, publicado y sincronizado con GitHub.

## B147 — Distribución robusta de scores por etiqueta humana

Fecha: 2026-07-29

Objetivo:
Describir de forma robusta la distribución de scores acústicos dentro de cada etiqueta humana mediante Q25, mediana y Q75, preservando contexto versionado y sin convertir percentiles en umbrales pedagógicos.

Resultado:
- Se añadió `PhoneticCalibrationHumanLabelScoreDistribution`.
- Se añadió un cálculo determinista de Q25, mediana y Q75 mediante interpolación lineal.
- Las distribuciones se separan por `analyzer_id`, `analyzer_version`, `rubric_version` y etiqueta humana.
- Se conservan `observation_count` y `sample_count`.
- Una única observación produce Q25, mediana y Q75 iguales a su score.
- El desacuerdo humano permanece representado por etiquetas independientes.
- Validación específica B147: 10 passed.
- Regresión B142-B147: 52 passed.
- Suite completa backend: 480 passed.
- `git diff --check`: correcto.
- Commit técnico: `1bcdce1`.

Límites:
B147 describe dispersión y posición de scores observados. Q25, mediana y Q75 no son umbrales de pronunciación, no clasifican automáticamente, no establecen verdad pedagógica y no generan feedback, mastery ni retention.

Estado:
B147 técnicamente cerrado y validado. Publicación Git/GitHub pendiente.

## B148 — Solapamiento descriptivo entre distribuciones humanas

Se añadió la descripción del solapamiento entre rangos intercuartílicos Q25–Q75 de pares de etiquetas humanas dentro del mismo contexto `analyzer_id + analyzer_version + rubric_version`.

El contrato distingue explícitamente casos con y sin solapamiento y el servicio no compara distribuciones de contextos versionados incompatibles.

Límites: el solapamiento sigue siendo evidencia descriptiva. No define verdad, separabilidad, umbral fonético, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B148 específico: 11 passed.
- Regresión B142–B148: 63 passed.
- Suite backend completa: 491 passed.
- `git diff --check`: limpio.
- Commit técnico: `4d7821e`.

## B149 — Informe descriptivo consolidado de calibración modelo-humano

Se añadió `PhoneticCalibrationDescriptiveReport` para consolidar, por `analyzer_id + analyzer_version + rubric_version`, el resumen modelo-humano, las distribuciones robustas por etiqueta y los solapamientos IQR ya calculados en bloques anteriores.

El contrato valida que todas las piezas pertenezcan exactamente al mismo contexto versionado y el servicio solo reúne evidencia compatible, sin añadir nueva interpretación.

Límites: el informe sigue siendo exclusivamente descriptivo. No define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B149 específico: 7 passed.
- Regresión B142–B149: 70 passed.
- Suite backend completa: 498 passed.
- `git diff --check`: limpio.
- Commit técnico: `e91a011`.

## B150 — Identidad reproducible del informe descriptivo de calibración

Se añadió `PhoneticCalibrationDescriptiveReportArtifact` para identificar reproduciblemente cada informe descriptivo mediante `report_version` y un SHA-256 calculado sobre una serialización canónica del informe completo y su versión.

El servicio conserva el informe original y garantiza que el mismo contenido y versión produzcan la misma huella, mientras que cambios en el contenido o en `report_version` generan una identidad diferente.

Límites: B150 aporta trazabilidad e identidad reproducible del artefacto. No define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B150 específico: 11 passed.
- Regresión B142–B150: 81 passed.
- Suite backend completa: 509 passed.
- `git diff --check`: limpio.
- Commit técnico: `1c07f43`.

## B151 — Verificación de integridad del artefacto descriptivo de calibración

Se añadió `PhoneticCalibrationDescriptiveReportArtifactVerification` y un servicio que recalcula mediante el mecanismo canónico de B150 la huella SHA-256 del informe y la compara con la identidad almacenada en el artefacto.

La verificación conserva `report_version`, el hash esperado, el hash recalculado y el resultado `matches_content`, permitiendo detectar alteraciones sin duplicar la lógica de generación de identidad.

Límites: B151 verifica integridad técnica del artefacto. No define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B151 específico: 15 passed.
- Regresión B142–B151: 96 passed.
- Suite backend completa: 524 passed.
- `git diff --check`: limpio.
- Commit técnico: `6954a58`.

## B152 — Comparación descriptiva reproducible entre artefactos de calibración

Se añadió `PhoneticCalibrationDescriptiveReportArtifactComparison` y un servicio que compara dos artefactos descriptivos después de verificar independientemente su integridad mediante B151.

La comparación conserva identidad, SHA-256 y versión del analizador de ambos lados y exige una misma `rubric_version`, evitando mezclar evidencia humana definida por rúbricas incompatibles.

Límites: B152 describe una comparación reproducible entre artefactos. No determina qué analizador es mejor, ni define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B152 específico: 22 passed.
- Regresión B142–B152: 118 passed.
- Suite backend completa: 546 passed.
- `git diff --check`: limpio.
- Commit técnico: `858d36b`.

## B153 — Identidad reproducible de evidencia humana para comparación

Se añadió `PhoneticCalibrationHumanEvidenceIdentity` y un servicio que construye una identidad reproducible de la evidencia humana mediante `rubric_version`, número de muestras distintas y SHA-256 de una representación canónica de los acuerdos humanos compatibles.

La identidad es independiente del orden de entrada, cambia cuando cambia la evidencia humana y mantiene separadas las rúbricas, permitiendo comprobar posteriormente si dos calibraciones se apoyan sobre la misma base humana.

Límites: B153 aporta trazabilidad de la evidencia humana. No compara todavía diferencias de score entre analizadores ni define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B153 específico: 13 passed.
- Regresión B142–B153: 131 passed.
- Suite backend completa: 559 passed.
- `git diff --check`: limpio.
- Commit técnico: `75dae4c`.

## B154 — Compatibilidad reproducible de evidencia humana entre calibraciones

Se añadió `PhoneticCalibrationHumanEvidenceCompatibility` y un servicio que compara dos identidades B153 para determinar si representan exactamente la misma evidencia humana.

`same_evidence` solo es verdadero cuando coinciden `rubric_version`, `sample_count` y `evidence_sha256`, sin inferir equivalencias parciales ni conclusiones sobre el rendimiento de los analizadores.

Límites: B154 comprueba comparabilidad de la base humana. No determina qué analizador es mejor ni define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B154 específico: 6 passed.
- Regresión B142–B154: 137 passed.
- Suite backend completa: 565 passed.
- `git diff --check`: limpio.
- Commit técnico: `66b8b39`.

## B155 — Contexto reproducible de calibración comparable

Se añadió `PhoneticCalibrationComparableArtifactContext` y un servicio que combina la comparación reproducible de artefactos B152 con la compatibilidad de evidencia humana B154.

El contexto solo puede construirse cuando ambos artefactos son comparables, comparten la misma `rubric_version` y las identidades humanas representan exactamente la misma evidencia. Esto prepara una base controlada para análisis técnicos posteriores sin calcular todavía diferencias de score ni rendimiento.

Límites: B155 establece condiciones de comparabilidad técnica. No determina qué analizador es mejor ni define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B155 específico: 6 passed.
- Regresión B142–B155: 143 passed.
- Suite backend completa: 571 passed.
- `git diff --check`: limpio.
- Commit técnico: `3927ebb`.

## B156 — Identidad reproducible de cobertura técnica de calibración

Se añadió `PhoneticCalibrationTechnicalCoverageIdentity` y un servicio que identifica reproduciblemente la cobertura técnica mediante `analyzer_id`, `analyzer_version`, `rubric_version`, número de muestras distintas y SHA-256 del conjunto canónico de `sample_id`.

La identidad es independiente del orden de entrada y de observaciones duplicadas sobre una misma muestra, pero cambia cuando cambia el conjunto efectivo de muestras técnicamente observadas.

Límites: B156 aporta trazabilidad de cobertura técnica para comparaciones posteriores. No calcula diferencias de score, no determina qué analizador es mejor y no define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B156 específico: 16 passed.
- Regresión B142–B156: 159 passed.
- Suite backend completa: 587 passed.
- `git diff --check`: limpio.
- Commit técnico: `45189b8`.

## B157 — Compatibilidad reproducible de cobertura técnica entre calibraciones

Se añadió `PhoneticCalibrationTechnicalCoverageCompatibility` y un servicio que compara dos identidades B156 para determinar si representan exactamente la misma cobertura técnica.

`same_coverage` solo es verdadero cuando coinciden `rubric_version`, `sample_count` y `sample_ids_sha256`. `analyzer_id` y `analyzer_version` pueden diferir, permitiendo comparar analizadores distintos siempre que hayan evaluado exactamente el mismo conjunto efectivo de muestras.

Límites: B157 comprueba comparabilidad de cobertura técnica. No calcula diferencias de score, no determina qué analizador es mejor y no define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B157 específico: 6 passed.
- Regresión B142–B157: 165 passed.
- Suite backend completa: 593 passed.
- `git diff --check`: limpio.
- Commit técnico: `437723a`.

## B158 — Contexto reproducible de comparación técnica completa

Se añadió `PhoneticCalibrationTechnicalComparisonContext` y un servicio que combina el contexto comparable B155 con la compatibilidad de cobertura técnica B157.

El contexto solo puede construirse cuando los artefactos son íntegros y comparables, comparten exactamente la misma evidencia humana reproducible y corresponden a exactamente la misma cobertura técnica de muestras. Además, cada identidad de cobertura debe corresponder al analizador, versión y rúbrica de su lado de la comparación.

Límites: B158 establece las condiciones completas de comparabilidad técnica. No calcula diferencias de score, mejoras o degradaciones, no determina qué analizador es mejor y no define verdad, separabilidad, umbrales fonéticos, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B158 específico: 7 passed.
- Regresión B142–B158: 172 passed.
- Suite backend completa: 600 passed.
- `git diff --check`: limpio.
- Commit técnico: `6fc5e7a`.

## B159 — Comparación descriptiva de scores por etiqueta humana

Se añadió `PhoneticCalibrationHumanLabelScoreComparison` y el servicio `compare_phonetic_calibration_human_label_scores`.

La comparación se realiza únicamente dentro de un `PhoneticCalibrationTechnicalComparisonContext` B158 ya validado. Cada distribución debe corresponder exactamente al analizador, versión y rúbrica de su lado, y ambas deben representar la misma etiqueta humana.

El resultado conserva las medianas izquierda y derecha, los conteos de observaciones y calcula de forma reproducible `median_difference = right_median - left_median`.

Durante la validación se corrigió la integración con el contrato B147 real, usando `sample_count`, `score_q25`, `score_median` y `score_q75`.

Límites: B159 describe diferencias técnicas de mediana. No interpreta el signo o magnitud como mejora, degradación o superioridad del analizador, y no define separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B159 específico: 7 passed.
- Regresión B142–B159: 179 passed.
- Suite backend completa: 607 passed.
- `git diff --check`: limpio.
- Commit técnico: `cb70582`.

## B160 — Comparación robusta de distribuciones por etiqueta humana

Se añadió `PhoneticCalibrationHumanLabelScoreDistributionComparison` y el servicio `compare_phonetic_calibration_human_label_score_distributions`.

La comparación se realiza únicamente dentro de un `PhoneticCalibrationTechnicalComparisonContext` B158 válido. Cada distribución debe corresponder exactamente al analizador, versión y rúbrica de su lado y ambas deben representar la misma etiqueta humana.

El resultado conserva los conteos de muestras y los valores robustos Q25, mediana y Q75 de ambos lados, calculando reproduciblemente:

- `score_q25_difference = right_score_q25 - left_score_q25`
- `score_median_difference = right_score_median - left_score_median`
- `score_q75_difference = right_score_q75 - left_score_q75`

Límites: B160 describe diferencias técnicas robustas de distribución. No interpreta signo, magnitud ni forma de estas diferencias como mejora, degradación, superioridad del analizador, separabilidad, umbral pedagógico, clasificación automática, feedback, mastery ni retention.

Validación:
- B160 específico: 8 passed.
- Regresión B142–B160: 187 passed.
- Suite backend completa: 615 passed.
- `git diff --check`: limpio.
- Commit técnico: `a64bec7`.

## B161 — Informe consolidado de comparación técnica por etiquetas

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonReport` y el servicio `build_phonetic_calibration_technical_distribution_comparison_report`.

El informe agrupa comparaciones robustas B160 por etiqueta humana dentro de un único `PhoneticCalibrationTechnicalComparisonContext` B158 válido.

Cada comparación debe corresponder exactamente a los analizadores, versiones y rúbrica del contexto. El informe exige etiquetas humanas únicas y el servicio exige que ambos lados utilicen exactamente el mismo conjunto de etiquetas, generando el resultado en orden determinista.

Límites: B161 consolida evidencia técnica descriptiva. No interpreta diferencias de Q25, mediana o Q75 como mejora, degradación o superioridad del analizador y no introduce separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B161 específico: 7 passed.
- Regresión B142–B161: 194 passed.
- Suite backend completa: 622 passed.
- `git diff --check`: limpio.
- Commit técnico: `58b95d2`.

## B162 — Artefacto reproducible del informe de comparación técnica

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonReportArtifact` y el servicio `build_phonetic_calibration_technical_distribution_comparison_report_artifact`.

El artefacto versiona un informe B161 completo mediante `artifact_version` y una identidad `content_sha256` calculada sobre una representación JSON canónica que incluye la versión y todo el contenido del informe.

La identidad es reproducible para contenido idéntico y cambia cuando cambia la versión del artefacto o cualquier contenido del informe.

Límites: B162 añade versionado e identidad reproducible al informe técnico consolidado. No verifica todavía integridad posterior del artefacto y no interpreta las diferencias técnicas como mejora, degradación, superioridad del analizador ni decisión pedagógica.

Validación:
- B162 específico: 6 passed.
- Regresión B142–B162: 200 passed.
- Suite backend completa: 628 passed.
- `git diff --check`: limpio.
- Commit técnico: `51e85f0`.

## B163 — Verificación de integridad del artefacto de comparación técnica

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonReportArtifactVerification` y el servicio `verify_phonetic_calibration_technical_distribution_comparison_report_artifact`.

La verificación reconstruye el artefacto mediante el constructor canónico B162 usando el mismo `artifact_version` y el contenido actual del informe. El resultado conserva el SHA-256 almacenado, el SHA-256 recomputado y `matches_content`, permitiendo detectar si el contenido actual ya no corresponde a la identidad registrada.

Límites: B163 verifica integridad reproducible del artefacto técnico. No interpreta las diferencias de Q25, mediana o Q75 como mejora, degradación o superioridad del analizador y no introduce separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B163 específico: 5 passed.
- Regresión B142–B163: 205 passed.
- Suite backend completa: 633 passed.
- `git diff --check`: limpio.
- Commit técnico: `953ba52`.

## B164 — Comparación reproducible entre artefactos técnicos verificados

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison` y el servicio `compare_phonetic_calibration_technical_distribution_comparison_report_artifacts`.

La comparación solo acepta artefactos B162 cuya integridad B163 sea válida. Conserva las versiones y SHA-256 de ambos artefactos, así como las identidades de los analizadores y versiones que cada informe compara.

El servicio rechaza artefactos con integridad inválida y exige que ambos utilicen la misma `rubric_version`.

Límites: B164 establece identidad y trazabilidad reproducible entre artefactos técnicos verificados. No compara todavía las diferencias internas entre informes, no determina mejora, degradación o superioridad de analizadores y no introduce separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B164 específico: 7 passed.
- Regresión B142–B164: 212 passed.
- Suite backend completa: 640 passed.
- `git diff --check`: limpio.
- Commit técnico: `5a18bcd`.

## B165 — Deltas descriptivos entre comparaciones técnicas

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDelta` y el servicio `compare_phonetic_calibration_technical_distribution_comparison_deltas`.

B165 compara dos comparaciones robustas B160 dentro de un contexto B164 ya validado. Cada lado debe corresponder exactamente a los analizadores, versiones y rúbrica de su artefacto técnico, y ambas comparaciones deben representar la misma etiqueta humana.

El resultado conserva las diferencias de Q25, mediana y Q75 de ambos informes y calcula reproduciblemente:

- `score_q25_difference_delta = right_score_q25_difference - left_score_q25_difference`
- `score_median_difference_delta = right_score_median_difference - left_score_median_difference`
- `score_q75_difference_delta = right_score_q75_difference - left_score_q75_difference`

Límites: B165 describe cambios entre diferencias técnicas. No interpreta signo ni magnitud como mejora, degradación o superioridad del analizador y no introduce separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B165 específico: 8 passed.
- Regresión B142–B165: 220 passed.
- Suite backend completa: 648 passed.
- `git diff --check`: limpio.
- Commit técnico: `9964241`.

## B166 — Informe consolidado de deltas técnicos por etiqueta

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReport` y el servicio `build_phonetic_calibration_technical_distribution_comparison_delta_report`.

B166 consolida los deltas descriptivos B165 por etiqueta humana dentro de una comparación reproducible B164 válida. El contrato exige que todos los deltas compartan la misma `rubric_version` del contexto y que cada etiqueta humana aparezca una sola vez.

El servicio exige etiquetas únicas en ambos lados, exactamente el mismo conjunto de etiquetas y genera los deltas en orden determinista reutilizando B165.

Límites: B166 consolida cambios técnicos descriptivos. No interpreta signo ni magnitud de los deltas como mejora, degradación o superioridad del analizador y no introduce separabilidad, umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B166 específico: 7 passed.
- Regresión B142–B166: 227 passed.
- Suite backend completa: 655 passed.
- `git diff --check`: limpio.
- Commit técnico: `403306f`.

## B167 — Sistematización del cierre de bloques

Se añadió `scripts/engineering/block_close.py` como herramienta determinista para reducir operaciones repetitivas del cierre técnico sin automatizar las decisiones de diseño.

B167 incorpora validación de raíz del repositorio, `git diff --check`, ejecución de pruebas específicas, descubrimiento y ejecución determinista de la regresión `test_phonetic_calibration_*.py`, suite backend completa, modo `--technical-preflight`, barrera que impide mezclar documentación en el cierre técnico y staging limitado exclusivamente a las rutas previamente validadas mediante `--stage-technical`.

La automatización conserva puntos de control humanos: no crea commits, no modifica documentación y no publica a GitHub. Su objetivo es sistematizar tareas repetitivas sin ocultar decisiones arquitectónicas ni reducir la trazabilidad.

Validación:
- Pruebas propias B167: 19 passed.
- Regresión fonética automática: 246 passed en 53 archivos.
- Suite backend completa: 674 passed.
- `git diff --check`: limpio.
- Commit técnico: `5f249d4`.

## B168 — Artefacto reproducible del informe de deltas técnicos

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifact` y `build_phonetic_calibration_technical_distribution_comparison_delta_report_artifact`.

B168 versiona el informe consolidado B166 con `artifact_version`, conserva el informe completo y calcula una identidad `content_sha256` reproducible sobre JSON canónico con claves ordenadas.

La identidad incorpora tanto la versión del artefacto como el contenido del informe: el mismo contenido y versión producen el mismo SHA-256, mientras que cambiar la versión o el contenido produce una identidad diferente.

Límites: B168 aporta versionado e identidad reproducible al informe de deltas técnicos. No interpreta signo ni magnitud como mejora, degradación o superioridad, ni introduce umbrales, clasificación automática, feedback pedagógico, mastery o retention.

Validación:
- B168 específico: 6 passed.
- Regresión fonética automática: 252 passed en 55 archivos.
- Suite backend completa: 680 passed.
- `git diff --check`: limpio.
- Commit técnico: `89d1fec`.

## B169 — Verificación de integridad del artefacto de deltas técnicos

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactVerification` y `verify_phonetic_calibration_technical_distribution_comparison_delta_report_artifact`.

B169 verifica la integridad del artefacto reproducible B168 reconstruyéndolo a partir de su `report` y `artifact_version` mediante el mismo builder canónico. El resultado conserva el SHA-256 almacenado como `expected_sha256`, el SHA-256 recomputado como `computed_sha256` y declara explícitamente `matches_content`.

La verificación permite distinguir un artefacto íntegro de uno cuyo hash almacenado ya no corresponde con su contenido actual.

Límites: B169 verifica únicamente integridad reproducible. No interpreta signo ni magnitud de los deltas como mejora, degradación o superioridad y no introduce umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B169 específico: 5 passed.
- Regresión fonética automática: 257 passed en 57 archivos.
- Suite backend completa: 685 passed.
- `git diff --check`: limpio.
- Commit técnico: `140ea14`.

## B170 — Comparación reproducible entre artefactos de deltas técnicos

Se añadió `PhoneticCalibrationTechnicalDistributionComparisonDeltaReportArtifactComparison` y `compare_phonetic_calibration_technical_distribution_comparison_delta_report_artifacts`.

B170 compara reproduciblemente dos artefactos B168 después de verificar la integridad de ambos mediante B169. El resultado conserva la versión y el SHA-256 de cada artefacto, junto con su contexto completo `PhoneticCalibrationTechnicalDistributionComparisonArtifactComparison`.

La comparación exige que ambos informes utilicen la misma `rubric_version`. Un artefacto cuya integridad no coincida con su contenido es rechazado antes de construir la comparación.

Límites: B170 establece identidad y contexto reproducible entre artefactos de deltas. No interpreta los deltas como mejora, degradación o superioridad y no introduce umbrales, clasificación automática, feedback pedagógico, mastery ni retention.

Validación:
- B170 específico: 7 passed.
- Regresión fonética automática: 264 passed en 59 archivos.
- Suite backend completa: 692 passed.
- `git diff --check`: limpio.
- Commit técnico: `e34d18d`.

## B171 — Distancia descriptiva entre IQR por etiqueta humana

Se añadió `PhoneticCalibrationHumanLabelScoreIqrGap` y `describe_phonetic_calibration_human_label_score_iqr_gaps`.

B171 complementa el solapamiento IQR descriptivo B148 conservando la distancia entre dos IQR cuando no se solapan. Para distribuciones versionadas compatibles, `gap_width` representa la distancia normalizada entre los extremos más próximos de ambos IQR y `separated` indica únicamente si existe una separación geométrica positiva.

Cuando los IQR se solapan o se tocan, `gap_width` es `0.0` y `separated=False`. Los contextos con distinto analizador, versión o rúbrica permanecen separados y no se comparan.

Límites: B171 describe distancia geométrica observada entre IQR. No convierte `gap_width` en separabilidad pedagógica, no define umbrales, no clasifica pronunciaciones, no determina superioridad del analizador y no genera feedback, mastery ni retention.

Validación:
- B171 específico: 7 passed.
- Regresión fonética automática: 271 passed en 61 archivos.
- Suite backend completa: 699 passed.
- `git diff --check`: limpio.
- Commit técnico: `094571a`.

## B172 — Relación descriptiva unificada de evidencia IQR

Se añadió `PhoneticCalibrationHumanLabelScoreIqrRelationship` y `relate_phonetic_calibration_human_label_score_iqr_evidence`.

B172 vincula la evidencia descriptiva de B148 (`overlap`) y B171 (`gap`) cuando ambas describen exactamente el mismo contexto versionado y par de etiquetas humanas. El servicio conserva las evidencias originales, exige correspondencia uno a uno, rechaza claves duplicadas y devuelve relaciones en orden determinista.

Los IQR que se tocan permanecen coherentes: `overlaps=True` con `overlap_width=0.0` y `separated=False` con `gap_width=0.0`.

B172 no modifica `PhoneticCalibrationDescriptiveReport` ni los artefactos reproducibles B150–B151, preservando sus contratos históricos.

Límite: esta relación describe geometría observada entre distribuciones. No establece separabilidad pedagógica, umbrales, clasificación automática, feedback, mastery ni retention.

Validación:
- B172 específico: 10 passed.
- Regresión fonética: 281 passed en 63 archivos.
- Suite backend completa: 716 passed.
- Commit técnico: `bb0dcdd`.

## B173 — Cobertura regional de referencia del corpus fonético humano

Se añadió `RegionalRepresentativePhoneticCalibrationSample`, extendiendo el contrato representativo B141 sin modificarlo, con `reference_locale` limitado a `en-US` y `en-GB`.

`reference_locale` identifica la variante de pronunciación utilizada como referencia para la muestra. No representa nacionalidad, procedencia ni acento personal del hablante.

Se añadió `load_regional_representative_phonetic_calibration_manifest` como loader independiente, preservando compatibilidad con los manifiestos B141 existentes.

También se añadió `RegionalRepresentativePhoneticCalibrationCoverage` y `summarize_regional_representative_phonetic_calibration_coverage`, que describen por variante de referencia el número observado de muestras, hablantes pseudónimos y sesiones únicas `(speaker_id, session_id)`.

Los cuatro WAV históricos de B140 permanecen sin `reference_locale`, porque no existe evidencia trazable que permita asignarles retrospectivamente `en-US` o `en-GB`.

Límites: B173 amplía la trazabilidad y cobertura observable del futuro corpus humano. No demuestra representatividad real, no define mínimos de suficiencia, no clasifica el acento del hablante y no establece umbrales, feedback pedagógico, mastery ni retention.

Validación:
- B173 específico: 16 passed.
- Regresión fonética automática: 297 passed en 67 archivos.
- Suite backend completa: 725 passed.
- `git diff --check`: limpio.
- Commit técnico: `dbefa49`.

## B174 — Cobertura regional de evidencia humana del corpus fonético

Se añadió `RegionalPhoneticCalibrationHumanEvidenceCoverage` junto con `summarize_regional_phonetic_calibration_human_evidence_coverage`.

B174 relaciona las muestras regionales B173 con los acuerdos humanos B143 y las etiquetas independientes B142 para describir evidencia revisada por `reference_locale + rubric_version`.

La cobertura conserva muestras, hablantes pseudónimos, sesiones, etiquetas, evaluadores pseudónimos distintos, distribución completa de `acceptable` / `variant` / `known_error` y número de muestras con acuerdo unánime.

`labeler_count` se calcula desde los `labeler_id` distintos de B142 dentro de cada contexto, evitando sumar repetidamente evaluadores que hayan revisado varias muestras.

Las muestras sin acuerdo humano no se contabilizan como evidencia humana revisada. Las distintas versiones de rúbrica permanecen separadas.

`reference_locale` continúa identificando la variante de pronunciación utilizada como referencia; no representa nacionalidad, procedencia ni acento personal del hablante.

B174 sigue siendo estrictamente descriptivo: no demuestra representatividad o suficiencia del corpus, no deriva etiqueta mayoritaria ni verdad, y no introduce separabilidad, umbrales, clasificación automática, feedback, mastery o retention.

Validación:
- B174 específico: 14 passed.
- Regresión fonética: 311 pruebas en 69 archivos.
- Suite backend completa: 746 pruebas.
- Commit técnico: `a7cdac4`.

## B175 — Auditoría de reutilización tecnológica y extensibilidad multilingüe

Se auditó la arquitectura actual para evitar reconstruir capacidades tecnológicas ya disponibles y preparar LOGUIC para incorporar otros idiomas sin convertir el núcleo en una implementación específica de inglés.

Decisión principal:
`open-source/local first`.

Durante la construcción se priorizarán herramientas, modelos y runtimes abiertos ejecutables localmente. Las APIs de pago permanecerán únicamente como posibles adaptadores futuros. Una capacidad solo se desarrollará desde cero cuando una limitación demostrada de las soluciones existentes afecte al diferencial pedagógico de LOGUIC.

Clasificación consolidada:
- LOGUIC Core: usuarios, progreso, Skills, intentos, evidencias, evaluación, feedback y futuras decisiones pedagógicas.
- Capacidades compartidas: audio, STT, pronunciación, conversación y generación mediante contratos independientes del proveedor.
- Módulos de idioma: progresión, contenido, representaciones lingüísticas, locales, fonética y políticas específicas.
- Adaptadores: Sherpa-ONNX, WavLM, runtimes locales y posibles proveedores futuros.

Hallazgos principales:
- El proveedor fonético local reutiliza WavLM-Large, un modelo CTC, G2P, Torch y Transformers. El runner y los contratos LOGUIC se conservan como integración intercambiable.
- El checkpoint fonético conserva métricas técnicas, pero no documenta de forma suficiente la procedencia y licencia de su corpus de entrenamiento. Su aprobación productiva queda pendiente.
- El pipeline produce información por palabra y fonema que actualmente se reduce a un score global en el contrato backend.
- El STT reutiliza Sherpa-ONNX y Moonshine detrás de `SpeechRecognitionController`. El contrato ya transporta `languageCode` y `locale`.
- La fábrica STT actual selecciona un único directorio de modelo y la tokenización de palabras está limitada al alfabeto latino inglés.
- La reproducción y grabación reutilizan `audioplayers` y `record`; la capa de audio es independiente del idioma y no ejecuta TTS durante el uso normal.
- La evaluación semántica actual es local, determinista y basada en reglas explícitas.
- `openai` está instalado como dependencia, pero no existe una integración del SDK dentro de `app`.
- Los modos guiado y ramificado están implementados. El modo libre está declarado en contenido, pero no dispone todavía de sesiones, mensajes dinámicos ni generador.
- Qwen3.5-4B quedó registrado únicamente como candidato local y gratuito para un benchmark futuro; no se instaló ni integró ningún modelo.
- El contenido sigue acoplado a inglés y español mediante campos `en` y `es`, niveles CEFR globales, un único árbol de contenido y catálogos visuales `en-US` / `en-GB`.

Deuda técnica confirmada:
`ProductionEvaluationCriterion` referencia una `EvidenceDefinition`, pero el validador no exige actualmente que ambos contratos compartan el mismo `measurement_mode` ni el mismo `success_threshold` cuando corresponda.

B175 fue una auditoría arquitectónica. No modificó código, contratos, base de datos, dependencias ni modelos locales, y no requirió ejecutar la suite de pruebas.

## B176 — Reorientación estratégica y pedagógica

B176 detuvo y canceló su alcance técnico original después de comprobar que la diferencia entre `EvidenceDefinition.measurement_mode` y `ProductionEvaluationCriterion.measurement_mode` no constituye por sí sola una incoherencia.

Una evidencia pedagógica `contextual_response` puede registrar la finalización de una actividad mediante `completion`, mientras las producciones concretas asociadas son evaluadas mediante criterios semánticos `binary` o fonéticos `score`. Ambos contratos representan responsabilidades diferentes.

El bloque detectó que el proyecto había acumulado capacidades técnicas sin disponer de un puerto de llegada pedagógico suficientemente explícito. Como corrección de rumbo, se definió y aprobó el Modelo Pedagógico Maestro de LOGUIC English.

Decisiones principales:

- fluidez conversacional funcional como puerto de llegada;
- horizonte intensivo orientativo de tres a seis meses;
- conversación espontánea, inteligible y transferible como demostración final;
- cuatro fases pedagógicas: desbloqueo mental, automatización, continuidad conversacional y transferencia;
- diagnóstico conversacional basado en desempeño;
- Plan Conversacional Inicial personalizado;
- sesiones centradas en tiempo real escuchando y hablando;
- Método 1: Construcción directa en inglés;
- pronunciación funcional transversal;
- primera ancla sonora `/iː/–/ɪ/–/e/`;
- inteligibilidad prioritaria frente a imitación obligatoria de un acento nativo;
- desarrollo mediante macrobloques pedagógicos completos;
- tres puertas humanas: definición, plan de implementación y cierre;
- futura incorporación controlada de Codex para ejecución técnica;
- tecnología subordinada a aprendizaje observable y transferencia.

Se creó `docs/modelo-pedagogico-maestro.md` como fuente canónica del puerto de llegada, el recorrido pedagógico y el nuevo sistema operativo de desarrollo.

Se actualizó `docs/roadmap.md` para:

- declarar el Modelo Pedagógico Maestro como dirección vigente;
- conservar el historial técnico B1–B175;
- corregir el hallazgo contractual erróneo registrado en B175;
- retirar la antigua secuencia automática de bloques B176–B178;
- exigir que el próximo macrobloque supere primero la Puerta 1.

B176 no modificó código, contratos, base de datos, dependencias ni comportamiento runtime. Por tratarse de un bloque exclusivamente estratégico y documental, no requirió ejecutar la suite backend.

Validación documental:

- estructura del Modelo Pedagógico Maestro revisada;
- roadmap alineado con el puerto de llegada;
- historial técnico conservado;
- `git diff --check`: limpio.

Commit documental principal: `f8ae50e`.

Estado: documentación completada y commit principal creado; pendiente publicación y verificación final de Git.
## B177 — Etapa A: contratos puros del diagnóstico conversacional

Estado: implementación técnica completada y validada.

Se añadieron contratos puros para:

- sesión diagnóstica;
- contexto autorizado;
- actividad diagnóstica;
- apoyo utilizado;
- observación diagnóstica;
- Perfil Conversacional Inicial;
- trazabilidad entre perfil y observaciones.

Separaciones preservadas:

- producción distinta de observación diagnóstica;
- evaluación técnica distinta de decisión pedagógica;
- perfil inicial distinto de progreso y mastery.

La etapa no incluye todavía validaciones cruzadas, persistencia, migraciones, API, contenido piloto ni integración Flutter.

Validación confirmada:

- 67 pruebas específicas superadas;
- 806 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `6d4a52b`.

Contrato canónico: `docs/conversational-diagnostic-contract.md`.


## B177 — Etapa B: validaciones cruzadas del diagnóstico conversacional

Estado: implementación técnica completada y validada.

Se añadieron validaciones cruzadas para:

- pertenencia entre sesión, contexto y actividad;
- autorización de audio para actividades de voz;
- secuencia de actividades y apoyos;
- apoyos disponibles, utilizados y retirados;
- coherencia entre observación y nivel real de apoyo;
- trazabilidad entre actividad y producción mediante `prompt_id`;
- coincidencia de modalidad entre actividad y producción;
- trazabilidad entre observación, producción y evaluaciones técnicas;
- propiedad exclusiva de cada producción respecto de una actividad;
- relación entre perfil inicial, sesión y evidencias diagnósticas.

Separaciones preservadas:

- producción distinta de observación diagnóstica;
- evaluación técnica distinta de interpretación pedagógica;
- Perfil Conversacional Inicial distinto de progreso y mastery;
- apoyo utilizado distinto de nivel lingüístico;
- evidencia descriptiva distinta de decisión automática.

Límites vigentes:

- sin generación automática del perfil;
- sin persistencia ni migraciones;
- sin API;
- sin contenido piloto;
- sin integración Flutter.

Validación confirmada:

- 71 pruebas específicas superadas;
- 879 pruebas del backend superadas;
- `git diff --check` limpio;
- commit técnico `e4e287c`.

Contrato canónico actualizado: `docs/conversational-diagnostic-contract.md`.

## B177 — Etapa C: generación del Perfil Conversacional Inicial

Estado: implementación técnica completada y validada.

Se añadió una generación determinista, trazable y revisable del Perfil Conversacional Inicial.

La Etapa C incorpora:

- roles explícitos de evidencia diagnóstica;
- referencias autorizadas a contextos motivadores;
- un plan pedagógico separado de las observaciones;
- selección validada de la primera lección mediante `Lesson.id`;
- exigencia de `LessonExperience` en la lección recomendada;
- generación de perfiles `provisional` y `confirmed`;
- trazabilidad completa mediante `InitialConversationalProfileEvidence`;
- rechazo de evidencia incompleta para perfiles confirmados;
- validación de pertenencia entre sesión y contexto.

Separaciones preservadas:

- observación diagnóstica ≠ decisión pedagógica;
- score técnico ≠ juicio diagnóstico;
- perfil inicial ≠ progreso;
- perfil inicial ≠ mastery;
- perfil inicial ≠ certificación MCER.

Validación final:

- pruebas específicas del diagnóstico superadas;
- 915 pruebas del backend superadas;
- `git diff --check` limpio.

Commit técnico: `d0004fd`.

## B178 — Sistematización profesional del método de trabajo

Estado: implementación técnica y documentación completadas.

Problema corregido:

- exceso de microinspecciones;
- confirmaciones demasiado frecuentes;
- recuperación de contexto dependiente de la conversación;
- uso de la IA como generador manual de comandos;
- duplicación potencial de automatizaciones existentes.

Se convirtió `docs/estado-operativo.md` en un checkpoint compacto y se añadieron:

- `scripts/engineering/operational_state.py`;
- `scripts/engineering/block_workflow.py`;
- `tests/test_operational_state.py`;
- `tests/test_block_workflow.py`.

El nuevo flujo valida el contexto operativo antes de delegar en `scripts/engineering/block_close.py`.

Validación final:

- 8 pruebas específicas;
- 923 pruebas backend;
- `git diff --check` limpio.

Commit técnico: `c08196d`.

## B179 — Hito A: modelos persistentes y migración Alembic

Estado: cerrado técnicamente mediante validación directa de respaldo.

Se persistieron las siete entidades principales del diagnóstico conversacional y se normalizaron dos relaciones críticas:

- `conversational_diagnostic_activity_productions`, con propiedad exclusiva y coincidencia obligatoria de sesión, actividad, `prompt_id` y producción;
- `conversational_diagnostic_observation_evaluations`, con integridad relacional entre observación, evaluación técnica y producción.

Los perfiles iniciales conservan un historial acumulativo, sin sobrescritura destructiva. `ck_diagnostic_observation_required_production` exige producción para las ocho dimensiones que dependen de ella. La revisión Alembic `3c4f1a2b7d90` incluye `upgrade` y `downgrade` validados de forma aislada.

Validación final:

- 14 pruebas específicas en 1.13 s;
- 7 pruebas de regresión relacionada en 0.31 s;
- 937 pruebas backend en 2.91 s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión final de Codex: sin defectos accionables;
- commit técnico: `40a30b3`.

El intento de cierre con `block_workflow.py` no finalizó correctamente. Codex quedó esperando una terminal secundaria sin recuperar el resultado; al interrumpirlo permaneció un proceso hijo activo que tuvo que detenerse manualmente. La evidencia final se obtuvo ejecutando la validación directamente en Kitty.

Se registra como deuda operativa separada que la interrupción de `block_workflow.py` puede dejar procesos hijos activos o perder la salida final. No se corrige dentro de B179 Hito A.

Límites conservados: sin servicio transaccional, API, Flutter, progreso ni mastery. La conversión entre contratos Pydantic y tablas normalizadas corresponde al Hito B.

## B179 — Puerta DevSecOps, Hito S1

Estado: contrato ejecutable de seguridad cerrado técnicamente.

Se añadió una puerta pura y reutilizable para impedir que una operación potencialmente destructiva avance sin evidencia verificable de recuperación. El plan JSON exige entorno explícito, identidad no secreta, backup existente y verificable por SHA-256, restauración satisfactoria del backup exacto y dentro de la antigüedad permitida, ensayo aislado con upgrade y downgrade, revisiones compatibles y rollback explícito.

El comportamiento es fail-closed y producción se rechaza siempre en S1. El núcleo no conecta a bases, ejecuta Alembic, crea o restaura backups, inicia procesos externos ni accede a red. Tampoco sustituye una prueba real de restauración.

Validación final:

- 17 pruebas específicas;
- 27 pruebas de regresión de ingeniería;
- suite backend: 954 passed in 2.89s;
- revisión de Codex: sin defectos accionables;
- `operational_state.py validate`: válido;
- `git diff --check`: limpio;
- commit técnico: `0472093`.

LOGUIC English será el piloto. El núcleo común se extraerá posteriormente a un repositorio independiente versionado; CNAPP-Lite, AutoRadar ES, AgencyForge y otros usarán adaptadores propios para base, backups, migraciones, pruebas y entornos. No se copiarán scripts manualmente ni se propagará el sistema antes de validar backup y restauración reales en un entorno aislado.

La deuda por procesos hijos y pérdida de salida al interrumpir `block_workflow.py` permanece separada y no se corrige en S1.

## B179 — Puerta DevSecOps, Hito S2

Estado: adaptador PostgreSQL cerrado técnicamente mediante integración real aislada.

Se añadió `scripts/engineering/postgresql_devsecops_adapter.py` y su prueba específica. El adaptador administra un clúster temporal marcado bajo `/tmp`, con socket Unix, puerto dinámico distinto de `5432`, sin servicio PostgreSQL del sistema y sin reutilizar la `DATABASE_URL` real. SQLAlchemy y Alembic usan explícitamente Psycopg 3 mediante `postgresql+psycopg://`.

El ensayo creó una base fuente aislada, generó un backup custom, verificó SHA-256, restauró en una base distinta, comprobó esquema y datos deterministas, ejecutó upgrade Alembic hasta `3c4f1a2b7d90`, volvió por downgrade a la revisión inicial y eliminó el workspace únicamente después de detener PostgreSQL.

Codex preparó y revisó el código y las pruebas. La integración real se ejecutó directamente en Kitty para conservar la salida y la comprobación externa de recursos.

Validación final:

- integración aislada: 1 passed in 2.47s;
- `INTEGRATION_EXIT_CODE=0`;
- suite backend: 967 passed in 5.56s;
- ningún proceso PostgreSQL residual;
- ningún socket o clúster temporal residual;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- commit técnico: `d0efe1e`.

S2 no autoriza migraciones sobre desarrollo, staging o producción reales. Persisten riesgos no ensayados de volumen, permisos, configuración y datos reales, que requieren controles y autorización adicionales.

## B179 — Hito B, primer incremento transaccional

Estado: incremento cerrado técnicamente; Hito B permanece activo.

Se creó `ConversationalDiagnosticSessionSetup` para agrupar sesión, contexto y actividades sin redefinir sus contratos. La operación de guardado valida todo antes del primer `add`, rechaza identificadores existentes sin sobrescribir ni aceptar reintentos idempotentes, realiza tres `flush`, exactamente un `commit` y rollback ante errores esperados e inesperados.

La consulta reconstruye el agregado Pydantic desde los modelos SQLAlchemy, ordena actividades por `sequence_order` y `activity_id`, no ejecuta commit y no depende de lazy loading. Se incorporaron errores públicos para sesión existente, referencia ausente, invariantes y fallos generales de persistencia.

Validación final:

- 16 pruebas específicas;
- 190 pruebas de regresión diagnóstica;
- suite backend: 983 passed in 5.55s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `56a3d42`.

No se modificaron modelos ni migraciones. Permanecen pendientes propiedad actividad–producción, apoyos, observaciones, enlaces observación–evaluación, perfiles, evidencias e historial completo. El siguiente incremento recomendado resolverá producciones preexistentes y persistirá atómicamente propiedad y usos de apoyo.

Límites: sin API, Flutter, progreso ni mastery; S2 no autoriza operaciones sobre bases reales.

## B179 — Hito B, segundo incremento transaccional

Estado: incremento cerrado técnicamente; Hito B permanece activo.

Se añadieron `ConversationalDiagnosticActivityProductionSetup` y `ConversationalDiagnosticProductionSupportsBatch`. `ConversationalDiagnosticSessionSetup` incorpora `production_supports=[]` sin romper los agregados válidos del primer incremento.

La creación inicial puede persistir sesión, contexto, actividades, propiedad actividad–producción y apoyos en una sola transacción: conserva tres `flush` de configuración y añade dos para asociaciones y apoyos. `save_conversational_diagnostic_production_supports(batch, db)` usa estos dos últimos para enriquecer una sesión existente. Ambas rutas realizan exactamente un commit y rollback integral, sin sobrescritura ni idempotencia implícita.

Cada `LearnerProduction` debe existir previamente y solo se consulta. El servicio valida sesión, actividad, `prompt_id`, modalidad, propiedad exclusiva, asociaciones existentes, apoyos disponibles y secuencias de utilización y retirada, considerando también el historial previo. La recuperación es explícita, ordenada, sin lazy loading y sin commit.

Validación final:

- 41 pruebas específicas en 0.72 s;
- 190 pruebas de regresión diagnóstica en 1.29 s;
- suite backend: 1008 passed in 5.60s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `719aa74`.

No se modificaron modelos ni migraciones. Permanecen pendientes observaciones, enlaces observación–evaluación, perfiles, evidencias e historial completo consultable. El siguiente incremento recomendado persistirá observaciones y resolverá evaluaciones técnicas preexistentes.

Límites: sin API, Flutter, progreso ni mastery; S2 no autoriza operaciones sobre bases reales.

## B179 — Hito B, tercer incremento transaccional

Estado: incremento cerrado técnicamente; Hito B permanece activo.

Se añadió `ConversationalDiagnosticObservationsBatch` y `ConversationalDiagnosticSessionSetup` incorporó `observations=[]` sin romper los dos incrementos anteriores. La creación inicial acepta observaciones y `save_conversational_diagnostic_observations(batch, db)` enriquece sesiones existentes.

La escritura valida antes del primer `add` sesión, actividad, propiedad actividad–producción, dimensiones dependientes, `prompt_id`, modalidad, apoyos realmente utilizados, evaluaciones de la producción observada, contexto motivador e identificadores únicos. Observaciones y enlaces usan dos `flush`, exactamente un commit y rollback integral.

`evaluation_result_ids` permanece como lista Pydantic, se persiste mediante enlaces normalizados y se recupera en orden ascendente estable. `ProductionEvaluationResult` debe existir previamente y nunca se crea, modifica o elimina; puede respaldar varias observaciones compatibles. La recuperación es explícita, ordenada, sin lazy loading ni commit.

Se preserva producción ≠ evaluación técnica ≠ observación diagnóstica ≠ decisión pedagógica. El servicio no deriva progreso, mastery, consenso ni decisión pedagógica.

Validación final:

- 69 pruebas específicas en 1.28 s;
- 190 pruebas de regresión diagnóstica en 1.35 s;
- suite backend: 1036 passed in 6.10s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `f30887f`.

No se modificaron modelos ni migraciones. Permanecen pendientes perfiles iniciales, evidencias perfil–observación e historial completo orientado a consulta. El siguiente incremento recomendado persistirá perfiles y evidencias sobre observaciones preexistentes.

Límites: sin API, Flutter, progreso ni mastery; S2 no autoriza operaciones sobre bases reales.

## B179 — Hito B, Incremento 4A: transición de sesión

Estado: incremento cerrado técnicamente; Hito B permanece activo.

Se añadió `ConversationalDiagnosticSessionTransition` y la operación `transition_conversational_diagnostic_session(command, db)`. Las sesiones nuevas solo se crean `in_progress` con `completed_at=None`. Se permiten `in_progress → provisional|completed|cancelled` y `provisional → completed|cancelled`; completed y cancelled son terminales.

El comando exige `expected_current_status` y `transitioned_at`. La actualización se condiciona por `diagnostic_session_id` y estado esperado y exige exactamente una fila afectada. No admite reapertura, repetición ni idempotencia implícita. `completed_at` representa el cierre del estado vigente, pero no se conserva un historial de transiciones.

Completed requiere cobertura diagnóstica completa. Esta regla quedó consolidada en un único validador canónico reutilizado por perfiles confirmados; provisional y cancelled no requieren cobertura completa. La operación realiza exactamente un commit y rollback integral sin generar perfiles ni modificar actividades, producciones, apoyos, observaciones o evaluaciones.

Validación final:

- validación diagnóstica: 88 passed;
- persistencia transaccional: 85 passed;
- perfiles: 20 passed;
- esquemas diagnósticos: 82 passed;
- persistencia relacional: 14 passed;
- suite backend: 1066 passed in 6.66s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `94a620e`.

No se modificaron modelos ni migraciones. El siguiente incremento recomendado persistirá perfiles iniciales append-only y evidencias perfil–observación sobre observaciones preexistentes. Permanecen fuera el historial de transiciones, API, Flutter, progreso, mastery, retención y adaptación; S2 no autoriza operaciones sobre bases reales.

## B179 — Hito B, Incremento 4B: perfiles iniciales append-only

Estado: incremento y Hito B cerrados técnicamente; B179 permanece activo hasta su cierre integral.

Se añadieron `InitialConversationalProfileSetup`, `ConversationalDiagnosticProfilesBatch` y `save_conversational_diagnostic_profiles(batch, db)`; el agregado incorpora `profiles=[]` con compatibilidad hacia los incrementos anteriores. Los perfiles llegan ya generados y se guardan solo mediante enriquecimiento: sesión provisional con perfil provisional y completed con confirmed; in_progress y cancelled no admiten perfiles.

La política es exclusivamente append-only. Admite múltiples perfiles históricos con `profile_id` distintos y rechaza duplicados persistidos o dentro del lote, sobrescritura e idempotencia implícita. Las evidencias son obligatorias, únicas y enlazan observaciones preexistentes de la misma sesión. Una observación puede respaldar perfiles históricos distintos sin crearse, modificarse ni eliminarse. Los perfiles confirmed reutilizan la cobertura diagnóstica completa canónica.

`first_lesson_id` se conserva exactamente sin consultas al catálogo desde persistencia. La escritura valida antes del primer `add`, ejecuta dos `flush`, exactamente un commit y rollback integral. La recuperación ordena perfiles por `generated_at` y `profile_id`, y evidencias por secuencia de actividad, `activity_id`, `observed_at` y `observation_id`; no usa lazy loading, no hace commit y no reinterpreta perfiles históricos contra el estado actual.

Validación final:

- persistencia transaccional: 105 passed;
- perfiles: 20 passed;
- validación diagnóstica: 88 passed;
- esquemas diagnósticos: 82 passed;
- persistencia relacional: 14 passed;
- total relacionado: 309 passed in 3.17s;
- marcador: `B179_HITO_B_INCREMENTO_4B_VALIDATED`;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `c9e3bab`.

El agregado recuperado ya constituye el historial consultable interno comprometido: reúne configuración, producciones y apoyos, observaciones y evaluaciones técnicas, y perfiles con evidencias, todo estructurado y ordenado. No queda otro incremento técnico interno para Hito B. Permanecen fuera historial de transiciones, API, Flutter, progreso, mastery, retención y adaptación; S2 no autoriza operaciones sobre bases reales.

## B179 — cierre integral definitivo

Estado: cerrado técnica e integralmente. Quedan cerrados Hito A, Puerta DevSecOps S1 y S2, y Hito B con sus incrementos 1–3, 4A y 4B.

La trazabilidad técnica final comprende: modelo relacional y migración `3c4f1a2b7d90` (`40a30b3`); puerta preventiva fail-closed (`0472093`); PostgreSQL temporal con backup, SHA-256, restauración y Alembic reversible (`d0efe1e`); configuración transaccional (`56a3d42`); producciones y apoyos (`719aa74`); observaciones y evaluaciones normalizadas (`f30887f`); máquina de estados con actualización condicional (`94a620e`); perfiles históricos append-only y evidencias (`c9e3bab`).

El resultado conserva validación previa, un commit por operación pública, rollback integral, rechazo de duplicados y sobrescrituras, referencias técnicas preexistentes e inmutables y recuperación explícita, estructurada y ordenada sin lazy loading. Se mantienen producción ≠ evaluación técnica, evaluación técnica ≠ observación diagnóstica, observación diagnóstica ≠ perfil inicial, perfil inicial ≠ progreso y progreso ≠ mastery.

Validación final directa en Kitty:

- suite backend: 1086 passed in 6.93s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- Git: `## master...origin/master`;
- marcador: `B179_INTEGRAL_VALIDATED`.

Permanecen fuera API y endpoints, Flutter, progreso, mastery, retención, adaptación automática, historial persistente de transiciones y migraciones sobre bases reales. S2 no autoriza desarrollo, staging o producción reales. La deuda de interrupción de `block_workflow.py` continúa separada.

El siguiente bloque deberá diseñarse desde una capacidad observable del estudiante y el modelo pedagógico maestro. El historial técnico no determina automáticamente cuál será.

## B180 — Incremento 1: construcción directa en la primera lección

Estado: incremento cerrado técnicamente; B180 quedó cerrado integralmente tras completar sus cuatro incrementos.

Se rediseñó `a1-u1-l1`, sin cambiar su identificador, como `Introduce yourself directly`. La capacidad observable es construir oralmente una respuesta directamente en inglés desde una intención, ampliarla con información pertinente y transferir el patrón ante una variación inesperada con ayuda mínima y sin copiar una frase completa.

La lección reutiliza `a1_introduce_yourself` y Persona + Verbo. Sus cinco etapas son modelo consciente con refuerzo fonético, construcción guiada, ampliación, transferencia y cierre. Las evidencias independientes `guided`, `expanded` y `transfer` reducen el apoyo de anclas a palabra inicial y ninguno. Voz queda declarada como modalidad principal y texto como respaldo; ampliación y transferencia prohíben el modelo completo.

Se incorporó un banco de cuatro variantes de transferencia y una política de máximo una orientación por producción, con prioridad de pertinencia, construcción directa, inteligibilidad y precisión secundaria. El validador determinista comprueba estos contratos sin decidir la corrección ni evaluar semántica libre, progreso o mastery.

El refuerzo previo reutiliza audio e IPA en-US/en-GB para escucha, ritmo, shadowing y `/iː/` natural. No es evidencia de transferencia y no introduce infraestructura fonética nueva. El Karaoke Fonético queda pospuesto, no descartado, para una capacidad aislada posterior con audio sincronizado, texto, fonemas, colores, shadowing, dictado y grabación; no se implementaron timestamps, sincronización ni UI.

Validación final:

- suite backend: 1104 passed in 9.20s;
- `operational_state.py validate`: correcto;
- `git diff --check`: limpio;
- revisión sin defectos accionables;
- commit técnico: `ccafaaa`.

Quedan fuera selección runtime de variantes, comprobación semántica, captura efectiva de modalidad y apoyo, elección real de corrección, persistencia adicional no demostrada, API, Flutter, progreso, mastery y adaptación automática.

El siguiente incremento recomendado implementará primero el comportamiento pedagógico interno mínimo para seleccionar una variante y registrar modalidad y apoyo realmente utilizados, sin saltar todavía a API o Flutter.

## B180 — Incremento 2: ejecución interna de construcción directa

Estado: incremento cerrado técnicamente; B180 quedó cerrado integralmente tras completar sus cuatro incrementos.

Se añadieron intentos completos persistentes y sus enlaces con `LearnerProduction`, sin duplicar la producción real. Las operaciones internas inician, finalizan y recuperan el intento en una sola transacción. La persistencia conversacional existente aporta un helper sin commit; su operación pública conserva el comportamiento previo.

La variante de transferencia se selecciona mediante SHA-256 determinista (`sha256-v1`) sobre la identidad canónica del intento y se conserva como snapshot histórico. La modalidad efectiva procede de `LearnerProduction`; apoyo configurado y usado se registran por separado. Texto o apoyo adicional permanecen como evidencia de lo ocurrido.

`completion_requirements_met` se calcula estructuralmente al leer: exige guided, expanded y transfer, voz en las tres, retirada prevista y transfer sin apoyo. No se persiste como verdad pedagógica y `false` no equivale a fracaso, progreso o mastery.

La migración `7d8e9f0a1b2c` fue validada en PostgreSQL mediante `3c4f1a2b7d90 → 7d8e9f0a1b2c → 3c4f1a2b7d90` (1 passed in 2.30s). El ensayo S2 completo validó `f81a78f8c1c4 → 7d8e9f0a1b2c → f81a78f8c1c4`. El defecto observado fue solo la concatenación ambigua de `pg_constraint.contype`; la prueba usa `contype::text` y conserva diagnósticos sanitizados. La migración no requirió cambios.

Validación final: 34 específicas; 148 relacionadas y 1 omitida; S2 unitario 22 y 1 omitida; regresión segura S1/S2/B180 119 y 1 omitida; suite backend 1149 passed in 9.59s; `operational_state.py validate` correcto; `git diff --check` limpio; revisión sin defectos; commit `f77f560`.

El Preflight de Impacto identificó el target fijo obsoleto de S2. El adaptador conserva `f81a78f8c1c4` como frontera histórica, descubre un único head con las APIs de Alembic, valida ascendencia y congela hashes concretos antes de crear recursos. En adelante, todo cambio estructural aplicará Preflight de Impacto y demostrará en Postflight que sus dependencias no quedaron desactualizadas, limitado al radio real del cambio.

Al cierre del Incremento 2 se recomendó registrar una única orientación pedagógica prioritaria por producción, sin selección automática, semántica libre, API, Flutter, progreso o mastery. El Karaoke Fonético continuó pospuesto, no descartado.

## B180 — Incremento 3: orientación prioritaria por producción

Estado: incremento cerrado técnicamente; B180 quedó cerrado integralmente tras completar sus cuatro incrementos.

Se añadió `DirectEnglishConstructionProductionOrientation`, asociada mediante una única FK a `DirectEnglishConstructionAttemptProduction`, y la migración `a4c8e2f6b901`. Cada enlace admite cero o una orientación: la primera escritura se conserva y toda segunda escritura, update, delete, overwrite o idempotencia implícita queda fuera.

La orientación guarda prioridad, `guidance_text` exacta de hasta 2000 caracteres, fuente y fecha. Las fuentes `human` admiten versión opcional; `external` exige una versión no blanca y ambas requieren `source_id` no secreto. `get_direct_english_construction_attempt` recupera orientación opcional para guided, expanded y transfer sin lazy loading, commit, inferencia o recálculo.

La prioridad se valida contra `CorrectionGuidancePolicy`, pero llega ya seleccionada: el backend no determina su corrección. `ProductionFeedback` no se reutilizó porque depende de evaluación técnica y tiene otra semántica. La orientación no modifica `LearnerProduction`, el enlace ni el intento y permanece separada de evaluación, verdad pedagógica, progreso, mastery y selección automática.

Postflight: nuevo head `a4c8e2f6b901`; S2 lo descubrió sin cambiar su adaptador ni fijar target. PostgreSQL focal: 1 passed in 2.48s; S2 completo: 1 passed in 2.38s; suite backend 1171 passed in 10.30s; `operational_state.py validate` correcto; `git diff --check` limpio; revisión sin defectos; commit `2f396d3`.

La infraestructura interna ya cubre las responsabilidades necesarias. El siguiente incremento debe demostrar comportamiento pedagógico: presentar una única orientación ya registrada antes de un nuevo intento y retirar de nuevo el apoyo, sin sumar persistencia salvo necesidad probada. Karaoke Fonético sigue pospuesto, no descartado.

## B180 — Incremento 4: preparación de reintento guiado

Estado: incremento cerrado técnicamente; B180 queda cerrado integralmente en el cierre posterior.

Se añadieron `DirectEnglishConstructionRetryPreparationRequest`, `DirectEnglishConstructionRetryPreparation` y la operación read-only `prepare_direct_english_construction_retry`. La lectura exige un intento previo finalizado, localiza la producción guided, expanded o transfer y recupera su orientación exacta, conversación, prompt y apoyos configurado y usado. No crea un intento, genera identificadores, escribe en base de datos ni modifica intento, producción u orientación.

La retirada reduce un peldaño desde el apoyo realmente usado y escoge el nivel con menos ayuda frente al configurado, por lo que nunca excede el andamio permitido. Transfer siempre queda en `none`; banco, variante y prompt previos se devuelven como trazabilidad y `new_attempt_selector` declara que el futuro `attempt_id` utilizará el selector determinista existente, incluso si vuelve a elegir la misma variante.

La orientación señala el foco del reintento completo, pero no demuestra aplicación, mejora, aprendizaje, progreso o mastery. No se incorporaron vínculos entre intentos, persistencia, modelos, Alembic, S2, evaluación semántica, API, Flutter o adaptación.

Validación: 71 pruebas focales en 1.23s; 50 de regresión pura/SQLite en 0.37s; suite backend 1191 passed in 10.33s; `operational_state.py validate` correcto; `git diff --check` limpio; revisión sin defectos accionables; commit `70c3dbf`.

El ciclo interno `contenido → producción → orientación → preparación de reintento con menor apoyo → nuevo intento` ya satisface el objetivo comprometido de B180. No se identifica una brecha observable imprescindible para un Incremento 5. Karaoke Fonético permanece pospuesto, no descartado.

## Cierre integral de B180

Estado: bloque cerrado técnica e integralmente; Incrementos 1–4 documentados y publicados.

La primera lección permite construir desde Persona + Verbo, ampliar y transferir mediante producciones guided, expanded y transfer con voz principal, apoyo decreciente y variantes auditables. Los intentos append-only conservan modalidad y apoyo reales; `completion_requirements_met` solo describe estructura. Una orientación prioritaria append-only puede guiar la preparación read-only de un nuevo intento con menor ayuda sin afirmar aplicación, mejora, aprendizaje, progreso o mastery.

Trazabilidad: Incremento 1 `ccafaaa`; Incremento 2 `f77f560`; Incremento 3 `2f396d3`; Incremento 4 `70c3dbf`. Evidencia final: suite backend 1191 passed in 10.33s; migraciones PostgreSQL focales y S2 completo validados; head Alembic `a4c8e2f6b901`; `operational_state.py validate` correcto; `git diff --check` limpio; Git sincronizado antes del cierre.

La siguiente brecha observable, aún sin número, es comprender la intención principal de una intervención oral nueva, responder de forma contingente y mantener un intercambio breve con ayuda reducida. No incluye más persistencia o infraestructura sin necesidad, API, Flutter, progreso, mastery, adaptación automática ni Karaoke Fonético completo.

## B181 — Incremento 1: comprensión contingente y continuidad conversacional breve

Estado: incremento cerrado técnicamente; B181 no queda cerrado integralmente.

La capacidad observable definida es escuchar tres intervenciones breves relacionadas de una persona recién conocida, identificar suficientemente su intención comunicativa, responder oralmente con palabras propias y mantener tres intercambios conectados hasta una reacción o cierre natural, con apoyo visible decreciente.

Se rediseñó `a1-u1-l2`, ahora titulada `Keep the conversation going`, y se añadió la Skill `a1_maintain_short_connected_exchange`. `a1-u1-l1` no se amplió y permanece sin cambios. La conversación `a1-u1-l2-c1` contiene siete turnos: el interlocutor pregunta `Where are you from?`, continúa con `Oh, nice! What do you like doing in your free time?`, introduce el seguimiento inesperado `Nice. Where do you usually do that?` y termina con `Oh, I see. Thanks for telling me. It was nice talking with you. See you!`. Entre esas cuatro intervenciones se requieren tres producciones propias del estudiante.

La voz es la modalidad principal y el texto queda como respaldo. El apoyo visible disminuye `anchors → initial_word → none`; el tercer prompt usa `unexpected_contingent_response`, el seguimiento queda marcado como `unexpected_follow_up` y el último turno como `reaction_closure`. La presentación es audio-first: el audio precede al transcript, que empieza oculto y solo se ofrece como contingencia o accesibilidad. Usarlo representa comprensión asistida, no comprensión exclusivamente auditiva, y nunca funciona como modelo de respuesta.

Las evidencias `a1-u1-l2-ev-place-response`, `a1-u1-l2-ev-interest-response` y `a1-u1-l2-ev-unexpected-followup-response` se asocian una a una con sus prompts. Cada una prevé revisión humana o externa estática en `intention_understanding` y `contingent_response`, con resultados `positive | negative | pending`; ambas dimensiones requieren `positive` para considerar satisfecha esa revisión. Un resultado `negative` o `pending` la impide, pero no genera progreso ni mastery.

El backend solo valida que la revisión esté prevista y correctamente estructurada. No persiste esos juicios ni infiere comprensión real, pertinencia semántica, contingencia real, no literalidad, progreso, aprendizaje, mastery o fluidez. La finalización estructural no equivale a éxito pedagógico. Tampoco se añadieron persistencia, modelos SQLAlchemy, Alembic, S2, API ni Flutter runtime. Karaoke Fonético continúa pospuesto, no descartado.

Validación técnica: la suite backend completa posterior al cambio terminó correctamente y `git diff --check` pasó; no se conserva un número de pruebas disponible para documentar. Commit backend: `c246876`. En frontend, tras incorporar los audios, `flutter analyze` fue correcto, `flutter test` registró 37 tests passed y `git diff --check` quedó limpio; commit publicado `8235449`.

Los ocho WAV en-US/en-GB de los turnos t1, t3, t5 y t7 fueron escuchados y aprobados humanamente. Los ocho usan PCM s16le, 22050 Hz, mono y 16-bit, y las ocho rutas declaradas por backend coinciden exactamente con los ocho assets físicos del frontend.

## B181 — Incremento 2: ejecución audio-first y persistencia de producciones

Estado: incremento cerrado técnica, documental y operativamente; B181 permanece abierto y no queda cerrado integralmente.

El objetivo fue materializar en Flutter la ejecución completa de `a1-u1-l2-c1`: escuchar primero cada intervención, habilitar el transcript solo después de una escucha como contingencia o accesibilidad, responder tres veces por voz con apoyo visible `anchors → initial_word → none` y conservar las tres producciones reales hasta su envío conjunto.

Flutter conserva las extensiones B181 necesarias y mantiene retrocompatibilidad. Las conversaciones heredadas `guided` y `branching` siguen usando su persistencia previa; B181 en modo `free` no utiliza `conversation-attempts`. El reconocimiento técnico puede continuar durante la práctica, pero permanece separado de comprensión, pertinencia y evaluación pedagógica.

Se reutilizó sin cambios la infraestructura backend existente. Cada WAV se sube mediante `POST /api/v1/conversation-production-audio`, que devuelve una referencia `production-audio://...`; las grabaciones se conservan por `prompt_id` y `turn_id`, y las tres producciones se envían en una única `ConversationProductionSubmission` mediante `POST /api/v1/conversation-productions`. No se creó almacenamiento paralelo ni fue necesario modificar backend.

Validación frontend: 9 pruebas focales finales superadas; `flutter analyze` correcto; regresión relacionada 36 passed; suite completa final 39 passed; `git diff --check` limpio; Postflight de compatibilidad superado. La primera ejecución focal detectó exclusivamente una notificación ausente en el doble de audio de prueba, corregida sin evidencia de defecto en runtime productivo.

Trazabilidad publicada: commit técnico frontend `8baf7a6` (`feat ejecutar conversación audio-first B181`) y commit documental frontend `4fe98ad` (`docs documentar ejecución audio-first B181`). Estado final frontend: `## master...origin/master`.

Persistir tres respuestas no demuestra comprensión, progreso, mastery o fluidez, y recorrer la conversación no equivale a éxito pedagógico. Permanecen fuera el uso persistido del transcript, fallback textual, resultados efectivos de `intention_understanding` y `contingent_response`, rollback remoto de WAV parciales, scoring, semántica automática, progreso, mastery, adaptación y Karaoke Fonético.

## B181 — Incremento 3: revisión efectiva independiente

Estado: incremento cerrado técnicamente mediante commit `21d34e5`; B181 permanece abierto y no queda cerrado integralmente.

Se añadió `ShortConnectedExchangeProductionReview` para registrar de forma append-only y trazable resultados independientes `positive`, `negative` o `pending` en `intention_understanding` y `contingent_response`. Cada revisión conserva `review_id`, `production_id`, dimensión, resultado, `source_type`, `source_id`, `source_version` y `reviewed_at`. La FK directa a `LearnerProduction.id` mantiene la producción real como fuente de verdad y evita duplicar submission, prompt, turno, evidencia, lección o conversación.

Se permiten múltiples revisiones históricas para una misma producción y dimensión. No existen update, overwrite, consenso, mayoría, precedencia ni resultado vigente; `pending` es un resultado normal. Un mismo batch rechaza repetir `production_id + dimension`, pero lotes posteriores pueden añadir nuevas revisiones independientes.

`save_short_connected_exchange_production_reviews` valida antes de escribir las referencias, la única submission B181 con sus tres producciones canónicas y la rúbrica activa derivada desde prompt y evidencia. Puede registrar las seis decisiones —tres producciones por dos dimensiones— con exactamente un commit y rollback integral ante referencia inválida, conflicto de `review_id` o error SQL. `get_short_connected_exchange_reviews_by_submission` recupera las tres producciones y todo el historial ordenado por `reviewed_at` y `review_id`, sin agregar, priorizar o transformar resultados.

La revisión `b181c3e4f5a6`, lineal desde `a4c8e2f6b901`, crea la tabla con PK `review_id`, FK `production_id → learner_productions.id` y `ON DELETE CASCADE`, índice por producción, índice `(production_id, dimension, reviewed_at, review_id)` y checks de dimensión, resultado, fuente, identidad y versión. Deliberadamente no existe unicidad sobre `production_id + dimension`.

Validación: esquema/modelo/servicio focal 22 passed; regresión relacionada inicial 122 passed; Postflight relacionado final 149 passed y 1 deselected; migración PostgreSQL focal reversible 1 passed in 2.31s; S2 unitario 22 passed y 1 deselected; S2 completo reversible 1 passed in 2.33s; suite backend completa final 1230 passed in 13.38s; head Alembic único `b181c3e4f5a6`; `git diff --check` limpio. S2 descubrió el head dinámicamente sin cambiar adaptador ni frontera histórica.

Revisión humana o externa no es evaluación técnica, diagnóstico u orientación B180. `positive` no crea progreso o mastery, `negative` no determina fracaso global y `pending` no es error. No se añadieron consenso, mayoría, scoring, semántica o comprensión automáticas, adaptación, API ni Flutter; B180 y el contenido y la rúbrica B181 permanecen intactos.

Permanecen fuera endpoints/API, superficie Flutter para revisión, persistencia del uso del transcript, fallback textual, rollback remoto de WAV, scoring, semántica automática, consenso, progreso, mastery, aprendizaje, fluidez, adaptación y Karaoke Fonético.

## B181 — Incremento 4: revisión humana local controlada

Estado: incremento cerrado técnicamente mediante commit `6a67763`; B181 permanece abierto y no queda cerrado integralmente. La capacidad permite que un revisor humano local, identificado explícitamente pero no autenticado, seleccione una submission real de `a1-u1-l2-c1`, escuche sus tres producciones WAV, consulte la rúbrica activa, registre atómicamente seis decisiones independientes y recupere el historial append-only completo sin Flutter ni HTTP.

La superficie es `scripts/review/short_connected_exchange_review.py`, apoyada por el servicio read-only `app/services/short_connected_exchange_local_review_service.py`. La CLI recibe `submission_id` y `--source-id`; este último es solo una etiqueta declarada. Usa `source_type="human"`, `source_version=None`, seis `review_id` únicos y timestamps UTC timezone-aware, sin presentar al revisor como identidad autenticada.

La preparación valida una submission B181 real, exige exactamente las tres producciones canónicas de voz y deriva desde contenido activo prompt, turno, intervención del interlocutor, evidencia y requisitos de revisión. Cada WAV se resuelve exclusivamente mediante `resolve_production_audio_path`, preservando el esquema `production-audio://`, UUID válido, `PRODUCTION_AUDIO_DIR`, confinamiento y existencia física. Las rutas absolutas solo aparecen en la consola local y no se persisten; el backend no incorpora un reproductor obligatorio.

La CLI muestra únicamente los datos necesarios y no utiliza `recognized_text`, scoring, evaluación técnica, feedback, diagnóstico, progreso o mastery. Recoge `intention_understanding` y `contingent_response` para cada producción con resultados `positive | negative | pending`, conserva las seis decisiones en memoria, presenta el resumen y exige confirmación final. Solo entonces construye un `ShortConnectedExchangeProductionReviewBatch`, llama una vez a `save_short_connected_exchange_production_reviews` y consulta `get_short_connected_exchange_reviews_by_submission`, sin consenso, mayoría, agregación o resultado vigente.

Cancelar o interrumpir antes de confirmar produce cero escrituras y no invoca persistencia. No existe retry automático ante error; si una interrupción ocurre durante o después de escribir, la herramienta exige consultar el historial antes de reintentar, pues otra ejecución representa nuevas revisiones históricas.

Como corrección transversal DevSecOps, el commit `687e394` añadió `scripts/engineering/isolated_postgresql_pytest.py` para impedir que pytest use `app_ingles_db`. Reutiliza primitivas S2, crea un workspace efímero `loguic-pg-s2-*`, socket Unix confinado, puerto dinámico distinto de 5432 y base `isolated_pytest`, rechaza la base de desarrollo, ejecuta `alembic upgrade head`, inyecta la `DATABASE_URL` temporal antes de la colección y ejecuta pytest en subproceso con `shell=False`. Propaga el exit code y detiene y elimina el entorno en `finally`, incluso ante fallo, excepción o `KeyboardInterrupt`, sin modificar el adaptador ni la frontera histórica S2.

Validación: 50 pruebas focales y dependencias SQLite; 21 de contenido y producciones relacionadas; regresión PostgreSQL aislada 8 passed in 0.32s; wrapper DevSecOps 12 passed in 0.19s; suite backend completa mediante PostgreSQL aislado 1262 passed in 12.38s; `git diff --check` limpio y EOF correcto en los seis archivos nuevos. No se modificaron modelos, migraciones, endpoints/router, contenido B181, B180, persistencia del Incremento 3, Flutter ni adaptador S2.

Revisión no es identidad autenticada, evaluación técnica, reconocimiento, consenso, mayoría o resultado vigente. `positive` no crea progreso o mastery, `negative` no determina fracaso global y `pending` no es error. Permanecen fuera API, HTTP, Flutter, panel administrativo, autenticación, roles o permisos, integración externa, reproductor integrado, `recognized_text`, scoring, semántica o comprensión automáticas, adaptación, fallback textual, persistencia del transcript, rollback remoto de WAV y Karaoke Fonético.

La brecha observable restante es ejecutar y demostrar una revisión humana real mediante la CLI sobre una submission real de producto. La infraestructura permite hacerlo, pero esa evidencia todavía no existe; no se define otro incremento ni una solución posterior.

## B181 — Checkpoint canónico de pausa en puerta pedagógica

Estado: **PAUSADO EN PUERTA PEDAGÓGICA — NO CERRADO INTEGRALMENTE**. Esta entrada actualiza el estado canónico sin reescribir la historia de I1–I4. No existe un fallo técnico pendiente que impida continuar.

Antes del piloto se protegieron conjuntamente la base de datos y los audios mediante un recovery set DB + `production-audio`. El ensayo aislado de restauración y migración terminó correctamente. La migración segura de `app_ingles_db` recorrió `f81a78f8c1c4 → 3c4f1a2b7d90 → 7d8e9f0a1b2c → a4c8e2f6b901 → b181c3e4f5a6`, y el Postflight real confirmó `b181c3e4f5a6` como head.

El piloto humano real produjo la submission `555`, enlazada a `LearnerProduction` `1663`, `1664` y `1665`. `wav_exists` fue `true` para las tres producciones. La revisión humana append-only persistió bajo `human:guiller-local` las seis decisiones siguientes:

- `1663`: `intention_understanding=positive`, `contingent_response=positive`;
- `1664`: `intention_understanding=negative`, `contingent_response=negative`;
- `1665`: `intention_understanding=negative`, `contingent_response=negative`.

La primera validación humana no superó la rúbrica, pero demostró end-to-end la infraestructura técnica de producción, audio y revisión humana persistente. También reveló un defecto UX real: presentar la consigna bajo «Tu respuesta» indujo al estudiante a repetir las instrucciones como si fueran el contenido que debía decir.

La corrección frontend local diferencia consigna, respuesta y apoyo mediante «Responde con tus palabras», «Qué debes hacer» y «Responde con información propia. No repitas la instrucción.», además de tratar de forma diferenciada `anchors`, `initial_word` y `none`. El test focal pasó, `flutter analyze` pasó, `git diff --check` pasó y la suite frontend completa registró 44 passed.

Durante una segunda validación humana la nueva microcopy se entendió correctamente. La validación se pausó deliberadamente antes de completarse al aparecer un problema pedagógico más profundo: el contenido A1 existente no constituye todavía una progresión canónica de prerrequisitos.

La auditoría del recorrido desde la L1 prototipo hasta B181 mostró preparación insuficiente de prerrequisitos como procedencia, intereses, frecuencia, referencia anafórica, comprensión auditiva productiva audio-first y continuidad conversacional. Estos hallazgos no significan que una L1 pedagógica definitiva haya fallado: la `a1-u1-l1` actual fue un prototipo/candidato histórico utilizado para desarrollar y demostrar contratos, contenido estructurado, runtime, producción, evaluación, persistencia e infraestructura pedagógica; no es la futura puerta de entrada A1 canónica.

Decisión: no parchear manualmente L1→L2 para hacer pasar B181. La evidencia deberá alimentar el Constructor Pedagógico, el mapa de prerrequisitos, los validadores y la puerta humana de calidad antes de generar un nuevo candidato pedagógico.

La reanudación de B181 requiere revisar el Constructor Pedagógico existente; determinar cómo generará y validará progresiones y prerrequisitos reales; construir canónicamente la entrada A1; generar y revisar después el candidato necesario para B181; y solo entonces reanudar su validación humana.

Actualización de trazabilidad posterior: el retry de persistencia B181 y la corrección UX consigna ≠ respuesta quedaron versionados y publicados en frontend mediante el commit técnico `aabe4a4`; su documentación frontend quedó publicada mediante `505549f`. Se mantienen como evidencia asociada el test focal PASS, `flutter analyze` PASS, `git diff --check` PASS y la suite frontend completa con 44 passed. Esta actualización no cambia el estado pedagógico ni completa la segunda validación humana.

## Contrato curricular v1 — Slice estructural 1

Estado: cerrada, publicada y sincronizada.

Sobre el contrato curricular v1 publicado en `d6b6e7f`, el commit técnico `56e7394` (`feat add curriculum capability contracts v1`) incorpora en `app/schemas/pedagogical_unit.py` los contratos aislados `CurriculumPreparationState`, `LessonCapabilityClaim`, `SkillPrerequisite` y `LessonCapabilityPlan`, con pruebas específicas en `tests/test_curriculum_capability_schema.py`.

La revisión independiente de Codex concluyó PASS sin hallazgos. Evidencia vigente: 15 pruebas específicas, 74 de regresión seleccionada, suite backend completa 1277 passed y `git diff --check` PASS. Los archivos técnicos están commiteados y no han cambiado desde esas validaciones; no corresponde repetir pytest mientras se mantengan intactos.

Se conservaron las fronteras de la slice: `LessonCapabilityPlan` no está integrado en `PedagogicalUnitCandidate`; `PedagogicalUnitSpecification.prerequisites`, `SkillCoverage` y `required_stages` permanecen intactos; no se implementaron ledger, resolución de `artifact_ids`, orden curricular, precedencia, ciclos ni cambios en runtime, progreso, mastery, fonética, feedback o B181.

El commit documental es `c74e259`. El push quedó confirmado hasta ese commit y Git terminó limpio y sincronizado como `## master...origin/master`.

Siguiente objetivo, todavía no abierto: diseñar e implementar el «Checkpoint de cambio de conversación», una herramienta de ingeniería determinista para automatizar la preparación y recuperación de contexto entre conversaciones. `docs/estado-operativo.md` permanece como fuente canónica; se conserva el protocolo Codex CLI + Bash y la regla de no repetir inspecciones o validaciones vigentes.

## Checkpoint de cambio de conversación — Slice estructural 1

Estado: implementación técnica cerrada mediante `bc288fc` (`feat add conversation checkpoint tool`); cierre documental, publicación y sincronización final pendientes.

Se añadieron `scripts/engineering/conversation_checkpoint.py` y `tests/test_conversation_checkpoint.py`. Los comandos read-only `prepare` y `resume` validan `docs/estado-operativo.md` reutilizando `operational_state.py` y generan una vista Markdown efímera, sin persistencia ni red. La inspección Git local informa HEAD, asunto, branch o detached, upstream, ahead/behind, staged, unstaged, untracked y renames. El estado falla cerrado si el checkpoint canónico es inválido, está demostrablemente desactualizado o no reconoce exactamente las rutas con cambios locales.

El postflight detectó y corrigió dos findings: las rutas Git se serializan como JSON ASCII, determinista y reversible, protegiendo Markdown frente a backticks, saltos y controles; y los cambios locales se contrastan exactamente con rutas citadas en `Bloque activo` o `Archivos clave`, incluidos origen y destino de renames.

Validación: 23 pruebas específicas PASS; regresión directa de `tests/test_operational_state.py` y `tests/test_block_workflow.py`, 8 passed; `git diff --check` PASS; postflight final PASS. Las pruebas funcionales reales demostraron rechazo del estado que omitía cambios locales, generación correcta mediante `prepare` tras actualizarlo y reconstrucción del mismo contexto mediante `resume`.

No se ejecutó la suite backend completa: la herramienta es de ingeniería read-only, no modifica código productivo y las pruebas específicas, la regresión directa y las pruebas funcionales cubren el alcance. Limitación no bloqueante: una ruta con backticks requeriría una futura convención documental distinta para figurar literalmente en las secciones canónicas.

El commit técnico existe pero todavía no está publicado. Faltan el commit documental, el push, la prueba final de `prepare` y `resume` con estado publicado y Git limpio, y la comprobación de sincronización final.
