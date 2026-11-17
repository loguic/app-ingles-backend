# LOGUIC English — UI/UX Design Review v1

- **Fecha:** 2026-11-16
- **Decisión:** APPROVED / HUMAN
- **Ámbito:** LOGUIC English, primer piloto.
- **Tipo:** skill de instrucciones **repo-local**, no servicio, agente permanente ni sistema paralelo.
- **Estado de distribución:** preparado para instalación local controlada; la instalación en Ubuntu y el registro en autoridades canónicas requieren verificación de ejecución. No se declara publicado ni cerrado en Git.
- **Trazabilidad:** propuesta aprobada por el usuario en conversación Desarrollo de App Inglés; vinculada a Weekly Goals v1 y a la revisión visual V1.

## Necesidad

Las capturas Flutter revisadas el 2026-11-16 mostraron defectos visibles pese a que pruebas unitarias y análisis estático pasaban: contraste muy bajo en Niveles, imagen desproporcionada y controles desplazados en Estación de tren, distribución pobre en Perfil, vista provisional de Repaso, y error de carga de unidades en Aprender (causa no verificada). La skill agrega una revisión de diseño enfocada, **sin confundir tests PASS con validación visual**.

## Decisión y condiciones

1. Crear una skill Codex local en el frontend bajo `.agents/skills/loguic-uiux-design-review/SKILL.md` con metadatos estándar `name` y `description`.
2. Activarla **solo para revisiones solicitadas o gates visuales**, no en segundo plano. Primera fase = evaluación y reporte; cambios de código necesitan autorización y alcance específico.
3. Mantener el flujo de producto universal: **Requisitos → Flujos de usuario → Maquetas aprobadas → Prototipo navegable → Arquitectura → Implementación incremental → Pruebas integrales → Entrega**, con DevOps y DevSecOps transversales.
4. Revisar fidelidad a referencias, UX pedagógica, responsive, accesibilidad, contraste, semántica, consistencia del tema, y disabled real para funciones `En preparación`.
5. No afirmar métricas ficticias, evaluación pedagógica, progreso o aprobaciones no realizadas.
6. **Aprobación visual final siempre humana**; un resultado de la skill nunca equivale a aceptación.
7. Integrar la revisión en **Weekly Goals v1**, sin abrir un nuevo bloque curricular, nueva shell, ni introducir frameworks o servicios. Escalar a LOGUIC OS solo si se aprueba reutilización o gobernanza compartida.

## Ruteo y coste

Orden: módulos canónicos y pruebas Flutter existentes → inspección de capturas y validación humana → IA local cuando aporte valor → Luna 0–3 → Terra 4–7 → Sol 8–10 → Astra excepcional. No gastar Codex en tareas deterministas, evitar repetir auditorías/audio ya validados, máximo un encargo principal de IA más una corrección justificada por objetivo. Dos intervenciones de IA sin avance funcional: STOP.

## Piloto 1 — Estación de tren

**Entrada:** dos capturas humanas del 2026-11-16 (imagen enorme y controles de escucha/grabación desplazados en vertical).

**Esperado de la revisión:** hallazgos por severidad con evidencia y corrección mínima; comprobar relación imagen/actividad, distribución en escritorio/ventana estrecha, legibilidad, controles accesibles; sin tocar Kokoro, backend ni MB1.

**Aceptación:** (a) pantalla visible y controles de aprendizaje accesibles sin que la imagen domine; (b) comprobación visual en al menos dos anchos relevantes; (c) pruebas focalizadas y ausencia de overflow; (d) Human Review Gate explícito. No aprobar automáticamente.

## Salida y trazabilidad

Registro compacto por pantalla: `PANTALLA / REFERENCIA`, `HALLAZGOS`, `VERIFICADO / PENDIENTE`, `ESTADO`, `NEXT`. No generar informes largos por defecto. Registrar la decisión en bitácora/roadmap según normas canónicas después de verificar instalación; el límite de 140 líneas de `docs/estado-operativo.md` permanece obligatorio.

## Prohibiciones

- No sustituir maquetas históricas ni inventar aprobación; las dos imágenes de dashboard/lección recientes son referencias similares, no prueba de que se recuperaron los archivos originales.
- No crear nuevos agentes, pipelines, herramientas paralelas ni dependencias externas para esta primera skill.
- No modificar cambios locales ajenos, progreso real, audio, contratos curriculares ni datos personales.
- No ejecutar commit/push/reset/clean automáticamente.

## Revisión inicial

Decisión humana: **APPROVED**. Instalación local, evidencia de detección por Codex y reconciliación con autoridades maestras: **PENDIENTES DE CONFIRMACIÓN** hasta salida local verificable. Publicación Git: **NO REALIZADA**.
