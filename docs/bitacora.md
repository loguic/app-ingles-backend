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
