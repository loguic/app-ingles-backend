# Estado operativo — LOGUIC English

Actualizado: 2026-10-12T05:20:11+02:00
Baseline Git previa a este checkpoint: 3089b08682fcb6872280d87eb92975ee0fa181ee
Formato: checkpoint operativo compacto

## Dirección vigente

- Producto: entrenador de fluidez conversacional funcional.
- Autoridad semántica durable: este documento; Git vivo se obtiene únicamente mediante inspección read-only de `conversation_checkpoint.py`.
- Método vigente: `docs/loguic-engineering-operating-method-v1.md`; routing default `Terra / medium`.
- El historial de cierres y decisiones permanece en `docs/bitacora.md`, `docs/roadmap.md` y Git publicado.

## Último bloque cerrado

`A1-V4-REAL-VERTICAL-SLICE`: **CLOSED / PUBLISHED / SYNCED** por este Closure Gate. El milestone de tres turnos —producción propia de agua → agua con menor apoyo → transferencia cercana a comida— queda satisfecho y publicado en backend y frontend; el frontend se publicó en `36f12735006db893a701a10825edc8281dc617fa`.

El postflight final acreditó **19 PASS / 5 skipped**, `git diff --check` PASS, estado operativo PASS, checkpoint PASS y `UNEXPECTED_FILES = NONE`. Qwen runtime/provenance `qwen3:8b` permanece evidencia PASS existente, sin repetición. Loader/runtime pointer/B181/mastery/progreso/completion y cambios a `content/content_tree.json` siguen no autorizados.

`Development Supervisor v1` queda **CLOSED / PUBLISHED / SYNCED** en `0349fa8d3928c98a83de0449b49d4dc5a8146c64` (`fix close development supervisor v1 routing and continuity`). El Closure Gate acreditó 14 tests PASS, block-close PASS, git-close PASS y checkpoint-prepare PASS, con árbol limpio y sincronizado.

La consolidación documental de decisiones iniciales del MVP Pre-A1 + A1 quedó
publicada y sincronizada en `d10a99a9f17ffc29fe34308b0398975096b04a88`.

La publicación de BASELINE V0 quedó recuperada y sincronizada en
`90bf9e780124b2dc1ffc43c4526e83aedf215af4`. La ejecución original del Closure
Gate falló durante `git_close` al hacer push por error DNS de resolución de
`github.com`, después de crear el commit local. Posteriormente se publicó el
commit existente con `git push origin master` y
`conversation_checkpoint.py prepare` terminó PASS, CLEAN y SYNCED. Esto no
reclasifica retrospectivamente la ejecución original como Closure Gate PASS.

## Bloque activo

BASELINE V0 del MVP: **PUBLISHED / SYNCED** tras recuperación de publicación.
Measurement V1 está documentada y sus cinco decisiones metodológicas fueron
aprobadas humanamente. La aplicación verificable queda pendiente de criterios
definitivos, pesos internos, reglas operativas, responsables y entradas
económicas; ningún incremento técnico está autorizado.

Dirty documentación reconocida: `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`.
Dirty backend reconocido: `docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`.


No activar ni publicar A1: loader/runtime pointer permanecen no autorizados; no modificar `content/content_tree.json`; no iniciar B181, human review, adjudicación, winner, mastery, progreso ni completion.

## Automatización disponible

- `scripts/engineering/validation_recipe.py approved-v1` ejecuta, en orden y fail-closed, pytest con rutas explícitas, `git diff --check`, `operational_state.py validate` y `conversation_checkpoint.py prepare --format compact`; no cierra Git.

## Método operativo vigente

Git real es autoridad exclusiva para hechos vivos; este documento conserva continuidad semántica y baseline previa validable. Las operaciones deterministas usan la receta approved-v1.

## Fronteras obligatorias

- La baseline previa no es HEAD actual; evidencia no equivale a progreso, mastery ni finalización curricular.
- No iniciar human review, adjudicación, B52, loader, runtime o B181 sin autorización y evidencia específicas.

## Próximo objetivo

NEXT = preparar la aplicación verificable de Measurement V1 a los 24
entregables desde BASELINE V0, una vez definidos los criterios individuales,
pesos internos, responsables, evidencia, estados parciales y entradas
económicas pendientes. Ningún incremento técnico está autorizado.

## Decisiones pedagógicas y comerciales consolidadas

El primer MVP se encuadra provisionalmente en Pre-A1 + A1 inicial, dentro de
la visión Pre-A1 hasta C2; Pre-A1 no es todavía un nivel curricular
independiente aprobado definitivamente. La matriz provisional es: 15 %
Pre-A1/diagnóstico, 20 % experiencias A1, 15 % escucha-habla-pronunciación,
15 % tutor adaptativo, 10 % feedback, 10 % transferencia-retención, 10 %
experiencia-accesibilidad y 5 % preparación para lanzamiento.

El seguimiento distingue avance acreditado del producto, avance técnico
aprovechable, coste y esfuerzo económico, y confianza de las estimaciones.
Siguen pendientes de validación el desglose provisional de 24 entregables,
criterios de aceptación, horas/costes, escenarios/precios, auditoría de
reutilización técnica y recomendaciones condicionadas sobre repositorios.

Los hallazgos A1 V4 incluyen dificultad con instrucciones iniciales, confusión
entre grabación, reconocimiento y feedback, “Great job!” sin comprobación
necesaria del resultado evaluado y necesidad de revisión para principiantes.
La publicación técnica del vertical slice no acredita por sí sola aprendizaje
humano.

## Archivos clave

`docs/estado-operativo.md`, `docs/bitacora.md`, `docs/roadmap.md`, `scripts/engineering/operational_state.py`, `scripts/engineering/validation_recipe.py` y `scripts/engineering/conversation_checkpoint.py`.
