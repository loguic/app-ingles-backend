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

## Fase 5 — Frontend

Estado: siguiente fase.

Objetivo: conectar el backend con una aplicación visual.

Decisión técnica inicial:

- El backend FastAPI se mantendrá en WSL2.
- El frontend Flutter se trabajará en Ubuntu VMware.
- La comunicación entre frontend y backend será mediante API HTTP.

## Fase 6 — IA controlada

Objetivo: usar IA para feedback, generación de ejercicios y personalización.
