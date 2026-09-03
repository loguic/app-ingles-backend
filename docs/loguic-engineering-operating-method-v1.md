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

### ChatGPT — orquestador

- actúa como arquitecto y orquestador;
- determina el siguiente slice o bloque desde la evidencia vigente;
- decide qué herramienta corresponde y cuándo aplican preflight, contrato, postflight y Bash;
- evita enviar a Codex tareas deterministas que Bash puede resolver directamente;
- reutiliza resultados vigentes y no repite validaciones sin cambio material;
- aplica el routing LOGUIC y redacta instrucciones ejecutables para Codex;
- revisa resultados y mantiene separadas las garantías contractuales;
- no obliga al usuario a administrar detalles técnicos ya sistematizados.

### Codex CLI — Codex-first

- se usa principalmente para inspección semántica directa del repositorio e implementación;
- modifica de forma controlada código, tests o documentación autorizados;
- ejecuta tests específicos o regresiones acotadas cuando forman parte natural del trabajo del agente;
- realiza revisión técnica o contractual que requiere razonamiento;
- reutiliza helpers y allowlists existentes;
- no obliga a copiar o pegar código al chat cuando puede inspeccionarlo directamente.

### Bash — Bash-first

- es la vía directa para tareas deterministas donde la IA no aporta valor, especialmente `python3 scripts/engineering/operational_state.py validate`, `python3 scripts/engineering/conversation_checkpoint.py prepare`, `python3 scripts/engineering/conversation_checkpoint.py resume`, `git diff --check` y la suite backend completa mediante `.venv/bin/python -m pytest`;
- ejecuta directamente los helpers deterministas de cierre o validación cuando corresponda, incluidos `block_close.py` y `git_close.py`;
- si una regresión o suite ejecutada desde Codex queda `INDETERMINADA`, se ejecuta una sola vez directamente en Bash;
- el resultado Bash pasa a ser la evidencia canónica para ese intento, sin repetir después la misma validación salvo causa nueva;
- `prepare` y `resume` son Bash-first: ChatGPT indica su ejecución directa en Bash cuando corresponde y no las envía a Codex sin una razón técnica concreta;
- `git_close.py` sigue siendo la vía segura de cierre y no se reconstruyen manualmente `add`/`commit`/`push`; Codex puede invocarlo dentro de una tarea agentic autorizada, pero Bash es válido y preferible cuando solo queda ejecutar determinísticamente el cierre ya decidido;
- auto-review evita aprobaciones rutinarias, pero no cambia esta separación de responsabilidades.

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
→ suite completa cuando corresponda
→ postflight independiente
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
3. no repetir una validación `PASS` vigente solo para confirmar: ejecutarla de nuevo únicamente si cambia materialmente algún archivo o input cubierto, o si el método de cierre exige evidencia nueva tras un cambio;
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

## 8. Continuidad y guard anti-degradación

Estas reglas son obligatorias tras cambio de conversación, agotamiento de contexto/tokens, interrupción de cuota o cualquier recuperación:

1. ChatGPT actúa como arquitecto, orquestador y reviewer. El usuario no reconstruye el estado del proyecto, analiza logs largos, compara archivos ni recuerda decisiones técnicas previas.
2. Codex es el agente de implementación y revisión. Bash y los scripts canónicos son la autoridad determinista para tests, validación, Git y cierres seguros.
3. En cada conversación nueva o recuperación se ejecuta primero `conversation_checkpoint.py resume`; ChatGPT interpreta el checkpoint, continúa desde la última frontera canónica exacta y no pide al usuario interpretarlo ni repite evidencia válida sin causa concreta.
4. Toda tarea Codex declara explícitamente el modelo elegido, el esfuerzo de reasoning y por qué ese routing es apropiado.
5. El routing usa primero herramientas deterministas/Bash; Luna para trabajo claro, mecánico y verificable; Terra para implementación o revisión acotada; Sol para arquitectura, pedagogía o gobernanza fundacional, seguridad y trabajo irreversible, de alto impacto o muy acoplado. Modelo y reasoning se deciden por separado.
6. La interacción con el usuario avanza un comando o acción por paso, indicando objetivo, acción exacta y resultado esperado; las decisiones reales se presentan numeradas. El usuario ejecuta y ChatGPT analiza.
7. Nunca se exige al usuario analizar manualmente output largo: ChatGPT/Codex lo resume o produce un informe/archivo cuando corresponda, y el usuario aporta solo el resultado necesario para orquestar.
8. Ante interrupción, tokens o cuota, no se continúa mediante parches improvisados: se congela la última frontera estable, se recupera el checkpoint, se reconcilia documentación stale y se reanuda el bloque exacto inacabado.
9. Antes de tocar código por un fallo nuevo, se clasifica como regresión del slice actual, deuda preexistente, problema de entorno/harness o fallo no relacionado. Una causa ajena no se corrige modificando la feature vigente.
10. Preflight, tests focalizados, regresión, postflight y suite completa ya válidos siguen siendo autoridad mientras no cambie el código cubierto ni aparezca una contradicción concreta.
11. La disciplina de cierre es: cambio técnico → validación focalizada → regresión/suite cuando aplique → postflight independiente → documentación → cierre Git seguro → checkpoint canónico. Sin documentación y Git limpio/sincronizado no hay bloque cerrado.
12. Si ChatGPT detecta degradación del método, detiene de inmediato el avance técnico, identifica la desviación, vuelve al último estado estable, restaura este flujo y reanuda con un paso pequeño.
13. No se añaden abstracciones, herramientas, migraciones, capas, inspecciones ni validaciones repetidas salvo que resuelvan un problema confirmado.
14. `docs/estado-operativo.md` es la fuente compacta de continuidad; `docs/bitacora.md` aporta trazabilidad histórica; este documento define cómo se trabaja. Sus funciones no se confunden.
15. Tras recuperar contexto, ChatGPT explicita bloque actual, último commit cerrado, trabajo pendiente, contratos/fronteras relevantes, routing de modelo y siguiente acción exacta; el usuario no debe volver a explicarlos.

## 9. Permisos Codex

- Codex CLI opera normalmente con sandbox `Workspace` y el proyecto mantiene `trust_level = "trusted"`;
- las aprobaciones rutinarias se gestionan mediante `approvals_reviewer = "auto_review"` en `~/.codex/config.toml`; el estado esperado en `/status` es `Permissions: Workspace (Approve for me)`;
- `Approve for me` no elimina el sandbox ni otorga acceso irrestricto: las operaciones realmente sensibles pueden seguir bloqueadas o requerir intervención;
- no usar `--yolo`, `dangerously-bypass-approvals-and-sandbox` ni equivalentes como configuración normal;
- los prompts siguen delimitando la tarea autorizada; auto-review evita convertir las aprobaciones rutinarias en trabajo manual del usuario, sin ampliar ese alcance;
- si una nueva conversación muestra `Workspace (Ask for approval)`, comprobar primero la configuración persistente y que Codex se haya reiniciado antes de cambiar el flujo técnico;
- no pedir al usuario administrar permisos repetitivamente mientras esta configuración siga vigente;
- esta corrección de permisos no cambia el modelo ni el reasoning;
- reutilizar helpers y allowlists seguros y, si el sandbox exige una aprobación inevitable, solicitar únicamente la aprobación mínima;
- si una publicación autorizada falla y el contrato prohíbe retry o fallback, detenerse y reportar el estado exacto.

## 10. Interacción paso a paso

- trabajar con una sola acción o comando por paso;
- explicar de forma breve el objetivo y el resultado esperado;
- ofrecer opciones numeradas únicamente cuando exista una decisión real;
- si solo existe un siguiente paso correcto, ejecutarlo o proponerlo sin opciones artificiales;
- no trasladar al usuario decisiones internas ya cubiertas por contrato, routing o helpers.

## 11. Autocorrección del método

Si el flujo se degrada:

1. reconocer la desviación;
2. volver al último estado estable documentado;
3. identificar la regla vulnerada;
4. aplicar la corrección mínima;
5. retomar con un solo paso.

La autocorrección del método no modifica garantías técnicas ni pedagógicas y no permite cerrar un bloque sin evidencia.

## 12. Cierre

Un bloque no está cerrado hasta disponer, cuando aplique, de:

- cambio técnico;
- tests específicos y regresiones pertinentes;
- revisión independiente;
- documentación;
- validación final;
- Git limpio y sincronizado.

Un contrato publicado no equivale a implementación publicada. Tests positivos no equivalen por sí solos a cierre documental o Git. Active source integrity no equivale a loader readiness. El checkpoint debe reflejar siempre el estado real, incluidos cambios locales aún no publicados.
