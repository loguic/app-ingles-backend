# LOGUIC English — Método operativo de ingeniería v1

## 1. Propósito y autoridades

Este documento es el método operativo canónico para continuar LOGUIC English de forma profesional entre conversaciones. Define roles, routing, flujo de slices, validación, permisos, cambio de conversación y reanudación. No sustituye contratos pedagógicos o técnicos ni conserva el estado mutable del proyecto.

Las autoridades se separan así:

- `docs/estado-operativo.md` es la fuente canónica del checkpoint operativo vigente;
- `docs/loguic-ai-model-routing-policy-v1.md` es la política detallada de routing de modelos;
- este documento es la autoridad del método de trabajo;
- la bitácora conserva historia, pero no sustituye el checkpoint actual;
- `conversation_checkpoint.py prepare|resume` genera vistas efímeras validadas y no crea otra fuente de verdad.

## 2. Roles

### ChatGPT

- actúa como arquitecto y orquestador;
- determina el siguiente slice o bloque desde la evidencia vigente;
- decide cuándo corresponden preflight, contrato, postflight y Bash;
- aplica el routing LOGUIC y redacta instrucciones ejecutables para Codex;
- revisa resultados y mantiene separadas las garantías contractuales;
- no obliga al usuario a administrar detalles técnicos ya sistematizados.

### Codex CLI

- inspecciona directamente el repositorio dentro del alcance autorizado;
- implementa cambios, tests y documentación autorizados;
- ejecuta validaciones acotadas y reporta evidencia material;
- reutiliza helpers y allowlists existentes;
- no obliga a copiar o pegar código al chat cuando puede inspeccionarlo directamente.

### Bash

- es la autoridad determinista para suites completas, helpers y validaciones donde la IA no aporta valor;
- si una regresión o suite ejecutada desde Codex queda `INDETERMINADA`, se ejecuta una sola vez directamente en Bash;
- un resultado Bash confirmado reemplaza la indeterminación operativa, sin reejecutar después la misma validación salvo causa nueva.

### Usuario

- dirige prioridades y producto;
- aprueba decisiones reales y cambios de alcance;
- no debe escoger repetidamente modelo, reasoning, comandos Git, inspecciones o permisos que el método ya resuelve.

## 3. Routing LOGUIC

Se usan primero herramientas deterministas cuando bastan. Si la tarea requiere modelo, se selecciona el mínimo fiable; modelo y reasoning son dimensiones separadas.

- default operativo: `Terra / medium`;
- Luna: tareas mecánicas, acotadas y verificables;
- Terra: implementación y revisión moderadas con arquitectura cerrada;
- Sol: arquitectura, contradicciones, decisiones fundacionales, seguridad o debugging complejo;
- cuando la incertidumbre se cierra, degradar `Sol → Terra → Luna`;
- no pedir al usuario cambiar manualmente modelo o reasoning salvo indisponibilidad real, contradicción o decisión nueva que impida continuar.

La política detallada y vigente permanece en `docs/loguic-ai-model-routing-policy-v1.md`.

## 4. Flujo de un slice

El flujo normal es:

```text
definición / preflight
→ contrato
→ publicación del contrato cuando corresponda
→ implementación
→ tests específicos
→ regresión seleccionada
→ postflight independiente
→ suite completa cuando corresponda
→ documentación
→ cierre Git seguro
→ checkpoint estable
```

No todas las tareas necesitan cada etapa, pero ninguna se omite cuando su garantía sea necesaria para el cierre. Reutilizar antes de reconstruir operaciones manuales:

- `scripts/engineering/operational_state.py`;
- `scripts/engineering/conversation_checkpoint.py`;
- `scripts/engineering/block_close.py`;
- `scripts/engineering/git_close.py`;
- cualquier helper adicional marcado como vigente en `docs/estado-operativo.md`.

## 5. No repetición

Antes de inspeccionar, ejecutar o validar:

1. comprobar si el checkpoint ya contiene evidencia vigente suficiente;
2. reutilizar resultados confirmados mientras no cambien los archivos cubiertos;
3. no repetir tests históricos sin causa material nueva;
4. no reinspeccionar archivos sin cambio material;
5. evitar `cat`/`sed` más copiar y pegar código al chat cuando Codex puede trabajar directamente sobre el repositorio.

Evidencia documentada significa evidencia reutilizable, no autorización para atribuir garantías más amplias.

## 6. Cambio de conversación

La frase humana **“Cambiar conversación”** significa:

1. cerrar o registrar con precisión el estado actual;
2. actualizar `docs/estado-operativo.md` con timestamp local timezone-aware;
3. registrar último bloque estable, bloque activo o local, validaciones, fronteras, siguiente objetivo y archivos clave;
4. validar mediante `python3 scripts/engineering/operational_state.py validate` con el path correspondiente cuando sea necesario;
5. ejecutar `python3 scripts/engineering/conversation_checkpoint.py prepare`;
6. cambiar de conversación solo con checkpoint válido.

`prepare` no crea una segunda fuente de verdad. Produce una vista efímera validada; `docs/estado-operativo.md` continúa siendo la fuente operativa canónica.

## 7. Reanudación

Las frases humanas **“Reanudar App Inglés”** y **“Recuperar el método consolidado”** activan el mismo protocolo:

1. ejecutar primero `python3 scripts/engineering/conversation_checkpoint.py resume`;
2. usar su salida y `docs/estado-operativo.md` como autoridad del estado vigente;
3. recuperar este método operativo canónico;
4. continuar directamente desde el último bloque o frontera confirmados.

No volver a pedir `pwd`, `git status`, copia del estado, inspecciones, selección de modelo/reasoning o decisiones ya resueltas salvo contradicción real. `resume` reconstruye Git y el checkpoint operativo como vista efímera read-only. La evidencia histórica documentada no implica reejecutar tests.

## 8. Permisos Codex

- usar el permiso mínimo necesario;
- reutilizar helpers y allowlists seguros;
- si el sandbox exige una aprobación inevitable, solicitar únicamente esa aprobación mínima;
- no convertir permisos en una secuencia manual de decisiones;
- no recomendar autorizaciones persistentes amplias por comodidad;
- si una publicación autorizada falla y el contrato prohíbe retry o fallback, detenerse y reportar el estado exacto.

## 9. Interacción paso a paso

- trabajar con una sola acción o comando por paso;
- explicar de forma breve el objetivo y el resultado esperado;
- ofrecer opciones numeradas únicamente cuando exista una decisión real;
- si solo existe un siguiente paso correcto, ejecutarlo o proponerlo sin opciones artificiales;
- no trasladar al usuario decisiones internas ya cubiertas por contrato, routing o helpers.

## 10. Autocorrección del método

Si el flujo se degrada:

1. reconocer la desviación;
2. volver al último estado estable documentado;
3. identificar la regla vulnerada;
4. aplicar la corrección mínima;
5. retomar con un solo paso.

La autocorrección del método no modifica garantías técnicas ni pedagógicas y no permite cerrar un bloque sin evidencia.

## 11. Cierre

Un bloque no está cerrado hasta disponer, cuando aplique, de:

- cambio técnico;
- tests específicos y regresiones pertinentes;
- revisión independiente;
- documentación;
- validación final;
- Git limpio y sincronizado.

Un contrato publicado no equivale a implementación publicada. Tests positivos no equivalen por sí solos a cierre documental o Git. Active source integrity no equivale a loader readiness. El checkpoint debe reflejar siempre el estado real, incluidos cambios locales aún no publicados.
