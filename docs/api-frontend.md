# Contrato API inicial para frontend

Este documento define los endpoints iniciales que podrá consumir una aplicación visual.

## Base URL

/api/v1

## Progreso del usuario

### POST /progress
Uso: registrar un intento de ejercicio realizado por el estudiante.
Campos: user_id, level_id, unit_id, lesson_id, exercise_id, selected_index, correct.

### GET /progress/{user_id}
Uso: obtener todos los intentos registrados de un estudiante.

### GET /progress/{user_id}/stats
Uso: obtener total de intentos, aciertos y precision general.
Respuesta: user_id, total_attempts, correct_attempts, accuracy.

### GET /progress/{user_id}/recommendation
Uso: obtener una recomendacion general basada en el progreso.
Respuesta: user_id, accuracy, message.

## Habilidades

### GET /progress/{user_id}/skills/{skill_id}/mastery
Uso: obtener el dominio del estudiante sobre una habilidad concreta.
Respuesta: user_id, skill_id, total_attempts, correct_attempts, mastery_score.

### GET /progress/{user_id}/skills/{skill_id}/review
Uso: saber si una habilidad debe repasarse.
Respuesta: user_id, skill_id, mastery_score, should_review, message.

## Pantallas para frontend

### GET /progress/{user_id}/dashboard
Uso: mostrar un resumen inicial del estudiante en una sola pantalla.
Respuesta: user_id, total_attempts, correct_attempts, accuracy, recommendation.

### GET /progress/{user_id}/next-action
Uso: indicar que debe hacer el estudiante despues.
Respuesta: user_id, action_type, target_id, message.

Valores iniciales de action_type:
- start_first_lesson
- review_skill
- continue_lesson

## Ejemplos de respuesta JSON

### GET /progress/{user_id}/stats

```json
{
  "user_id": "test-user",
  "total_attempts": 3,
  "correct_attempts": 2,
  "accuracy": 0.67
}
```

### GET /progress/{user_id}/recommendation

```json
{
  "user_id": "test-user",
  "accuracy": 0.67,
  "message": "Review weak skills before moving forward."
}
```

### GET /progress/{user_id}/skills/{skill_id}/mastery

```json
{
  "user_id": "test-user",
  "skill_id": "a1_greetings_basic",
  "total_attempts": 3,
  "correct_attempts": 2,
  "mastery_score": 0.67
}
```

### GET /progress/{user_id}/skills/{skill_id}/review

```json
{
  "user_id": "test-user",
  "skill_id": "a1_greetings_basic",
  "mastery_score": 0.67,
  "should_review": true,
  "message": "Review this skill before moving forward."
}
```

### GET /progress/{user_id}/dashboard

```json
{
  "user_id": "test-user",
  "total_attempts": 3,
  "correct_attempts": 2,
  "accuracy": 0.67,
  "recommendation": "Review weak skills before moving forward."
}
```

### GET /progress/{user_id}/next-action

```json
{
  "user_id": "test-user",
  "action_type": "review_skill",
  "target_id": "a1_greetings_basic",
  "message": "Review weak skills before moving forward."
}
```
