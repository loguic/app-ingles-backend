# LOGUIC English — Weekly Goals v1

**Identificador:** `LOGUIC-ENGLISH-WEEKLY-GOALS-V1`  
**Fecha de decisión humana:** 2026-11-16 (Europe/Madrid)  
**Decisión:** **APPROVED / HUMAN**  
**Estado de esta copia:** registro Markdown preparado para incorporación al repositorio canónico; **no implica que Git local esté actualizado o que exista cierre publicado**.

## 1. Propósito y autoridad

Adoptar un ritmo de trabajo sostenible y verificable: **un resultado importante de producto por semana**, dividido en objetivos diarios pequeños o tramos de 2–3 días cuando sea apropiado. El éxito se mide por lo que un estudiante puede **ver, utilizar y verificar**, nunca por cantidad de prompts, código, pruebas o microbloques.

Esta decisión **no crea un sistema paralelo**. Se incorpora al roadmap, al estado operativo y a la bitácora mediante el método canónico de LOGUIC English, manteniendo sus autoridades y restricciones. En caso de contradicción, **fail closed** y reconciliación previa.

**Autoridades aplicables:** `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `docs/modelo-pedagogico-maestro.md`, `docs/loguic-engineering-operating-method-v1.md` y scripts canónicos. `docs/estado-operativo.md` mantiene el límite contractual de **140 líneas**.

## 2. Normas operativas obligatorias

1. **Una meta activa** de producto; una sola acción verificable por intervención.
2. Cada meta declara: resultado visible, alcance y exclusiones, evidencia de partida, dependencias, criterio de aceptación, responsable/herramienta y condición de STOP.
3. **Cierre por evidencia:** pruebas técnicas + revisión funcional o visual real cuando corresponda + trazabilidad documental. `PASS` automatizado no acredita aprendizaje pedagógico.
4. Priorizar **reutilización** de módulos, servicios, pantallas, maquetas y controles canónicos. No crear nuevas shells, arquitectura paralela ni contratos innecesarios.
5. Mantener las maquetas históricas como referencia; superficies todavía no implementadas visibles y **deshabilitadas**, sin progreso, evaluaciones ni estados inventados.
6. Flujo universal: **Requisitos → Flujos de usuario → Maquetas aprobadas → Prototipo navegable → Arquitectura → Implementación incremental → Pruebas integrales → Entrega**. DevOps/DevSecOps transversales a todas las fases.
7. Antes de trabajar: `conversation_checkpoint.py resume` y recuperación canónica; si falla, **STOP** hasta reconciliar. Preservar cambios locales preexistentes y autoridad Git real.
8. En el cierre de cada jornada, registrar solo **terminado / pendiente / bloqueo / siguiente acción**; no repetir inventarios o pruebas con evidencia válida.
9. Una meta que no cumple su criterio se declara **PARCIAL o BLOQUEADA**, nunca terminada por optimismo.
10. Respetar la salud, el tiempo y el presupuesto del usuario: no extender tareas indefinidamente ni asumir trabajo nocturno.

## 3. Routing y presupuesto de tokens

**Orden:** herramientas y Bash canónicos → IA local → Luna (0–3) → Terra (4–7) → Sol (8–10) → Astra excepcional.

- Operaciones deterministas (Git, validaciones, hash, inventario): Bash/Python local, **sin Codex**.
- Antes de llamar un agente, especificar **objetivo, modelo, salida esperada y criterio STOP**; usar el menor modelo que permita un resultado fiable.
- Por meta: preferencia de **un encargo principal** de IA y, como máximo, **una corrección justificada** antes de detenerse y analizar la fricción.
- **Dos intervenciones de IA sin avance funcional → STOP.**
- Reutilizar evidencias ya verificadas. En particular, ambos audios Kokoro de la estación fueron escuchados en Flutter por el usuario; no repetir la prueba sin causa específica.
- Prohibidas afirmaciones de finalización por el mero número de tests.

## 4. Primera semana propuesta: 16–22 de noviembre de 2026

**Meta semanal:** consolidar la V1 visual existente de LOGUIC English, con navegación integrada, diseño coherente, funciones no disponibles claramente deshabilitadas y revisión real de accesibilidad. **No prometer evaluación pedagógica integral ni publicar currículo MB1 DRAFT.** Las fechas son objetivos ajustables, no garantías.

| Día | Objetivo acotado | Criterio de salida |
| --- | --- | --- |
| Lun 16 | Reanudar estado canónico y contrastar lo aplicado por Codex con la vista real | Checkpoint PASS; cambios preservados; brechas visuales identificadas |
| Mar 17 | Revisar Inicio, Niveles y Aprender frente a las maquetas | Navegación y contraste aprobados por revisión humana |
| Mié 18 | Revisar Listening, Speaking, Reading, pronunciación, vocabulario, gramática y repaso | Pantallas visibles; estados pendientes honestos y controles deshabilitados |
| Jue 19 | Corregir defectos concretos de UX/accesibilidad, incluidos tamaños de ventana | Correcciones verificadas; sin regresiones visibles |
| Vie 20 | Prueba integral de recorrido V1 existente | Abrir → navegar → practicar actividad disponible → regresar; sin fallos bloqueantes; evidencia técnica y humana |
| Sáb 21 | Reconciliación documental y Closure Gate canónico **solo si corresponde y pasa** | Registros trazables, validaciones y Git controlado según contrato; si no, estado PARCIAL |
| Dom 22 | Descanso o margen de contingencia | No iniciar por defecto un nuevo incremento |

**Fuera de alcance esta semana:** nuevas voces/benchmarks, maquetas no autorizadas, reescritura de arquitectura, activación/publicación del candidato curricular MB1, proclamar dominio o progreso no evaluados.

## 5. Próxima meta después de la V1 visual

Consolidada la interfaz, seleccionar una única lección y **reutilizar las capacidades existentes** para comprobar el recorrido escuchar → comprender → hablar → reconocer → orientar → reintentar → comprobar resultado → guardar evidencia. Deben verificarse sus dependencias antes de fijar plazos. No atribuir evaluación de inteligibilidad real hasta que exista y se haya validado.

## 6. Plantilla mínima de seguimiento (dentro de autoridades existentes)

```text
META_SEMANAL: <resultado observable>
META_ACTUAL: <una sola>
EVIDENCIA_BASE: <referencia verificable>
ACEPTACION: <prueba humana + técnica específica>
STATUS: PLANNED | ACTIVE | PASS | PARTIAL | BLOCKED
TOKENS_IA: <agente/modelo y número de intervenciones>
BLOCKERS: <solo los activos>
NEXT: <una acción verificable>
```

## 7. Adopción y cierre documental

Esta política está **aprobada por el usuario** el 2026-11-16. Para hacerla autoridad operativa en su Ubuntu: incorporar la decisión con las herramientas/procedimientos canónicos en `docs/roadmap.md` y `docs/bitacora.md`; reconciliar `docs/estado-operativo.md` sin exceder las 140 líneas; verificar `conversation_checkpoint.py resume`, `loguic.py resume` y validaciones aplicables. **No registrar commit, publicación, revisión ni sincronización sin evidencia real.**

**Estado de integración en repositorio local al crear esta copia:** **PENDING / NOT VERIFIED**.
