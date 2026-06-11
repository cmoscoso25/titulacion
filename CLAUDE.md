# Claude — Titulación INACAP 2026

## Al iniciar cada sesión
1. Leer `PROJECT_CONTEXT.md` siempre.
2. Para tareas frontend/CSS/JS: leer también `FRONTEND_MAP.md`.
3. Usar Ruflo `memory_search` para recuperar contexto de sesiones anteriores.
4. Usar CodeGraph ANTES de leer archivos: `codegraph_context` → `codegraph_search` → `codegraph_node`.

## Reglas obligatorias

**Antes de modificar:**
1. Usar CodeGraph para identificar archivos relacionados. No leer archivos completos innecesariamente.
2. Explicar: problema detectado · archivos afectados · solución propuesta · riesgos.
3. No modificar sin haber explicado el impacto.

**Durante:**
4. No romper funcionalidades existentes.
5. No alterar backend, modelos, vistas, permisos ni URLs salvo solicitud explícita.
6. Entregar archivos COMPLETOS cuando se reescriben. No fragmentos parciales.
7. CSS y HTML deben usar exactamente las mismas clases — discrepancia silenciosa.

**Al finalizar:**
8. Actualizar `CLAUDE.md`, `PROJECT_CONTEXT.md` y/o `FRONTEND_MAP.md` según corresponda.
9. Guardar decisiones importantes en Ruflo (`memory_store`, namespace `titulacion_inacap`).
10. Commit + push si fue solicitado.

## Preferencias del desarrollador
- Responder en español · código claro · naming consistente.
- No simplificar eliminando lógica · no romper responsive existente.
- No alterar estructura sin explicar impacto.

## Stack
Django · Python · SQLite · HTML · CSS · JS (vanilla)

## Archivos críticos
- `configuracion/settings.py` — base del sistema
- `titulacion/views.py` — toda la lógica de vistas
- `titulacion/urls.py` — todas las rutas
- `titulacion/models.py` — EstudianteTitulado, Invitacion, BloqueCeremonia, Ceremonia
- `titulacion/permisos.py` — sistema de grupos (validación por nombre, no por permisos de modelo)
- `titulacion/context_processors.py` — inyecta `perm_*` en todos los templates

## Sistema de permisos ⚠️ CRÍTICO
Valida por **nombre de grupo Django**, NO por permisos de modelo.

| Grupo Django | Acceso |
|---|---|
| `ADMIN_TITULACION` | Todo el sistema |
| `ADMISION` | Registro de ingreso + Entrega |
| `CURRICULAR` | Panel control, reportes, cambio ceremonia |
| `ENTREGA_INVITACIONES` | Solo entrega |
| `INGRESO` | Solo registro QR (DAE) |
| `DACOM` | Solo entrega (DACOM) |

Context vars en todos los templates: `perm_admin`, `perm_admision`, `perm_curricular`, `perm_entrega`, `perm_ingreso`.
Decorators de ruta: `acceso_admin` / `acceso_curricular` / `acceso_entrega` / `acceso_ingreso` / `acceso_general`.
Al crear usuarios en Django Admin: asignar solo el grupo — NO permisos individuales de modelo.

## Advertencias técnicas
- `base.css` tiene alta especificidad en `button[type="submit"]` — anular con selector más específico o `!important`.
- Logout: vista custom `logout_view` (acepta GET+POST) — no usar `auth_views.LogoutView`.
- Panel Control ORM: sets `_estudiantes_atrasados_ids`, `_invitaciones_atrasadas_ids`, `_atrasados_por_plan` DEBEN pre-calcularse ANTES de los loops. Nunca reinsertar `.exists()` ni `.count()` dentro de ellos (provoca N+1 ~900 queries).
- Reportes KPI grids: usar `repeat(auto-fit, minmax(...))` — NUNCA `repeat(N, 1fr)` forzado con sidebar activo.
- Comando `reset_registro_ingreso`: en `titulacion/management/commands/`. Resetea SOLO RegistroIngreso +
  campos de presencia (ingreso_confirmado, usada). NO toca QRs, invitaciones ni ceremonias. Requiere "CONFIRMAR" o `--confirmar`.
- Registro de Ingreso QR: el JSON de `validar_codigo_ingreso` tiene campo `tipo_entrada` ("Estudiante" / "Invitado 1" / "Invitado 2") y `ceremonia` (nombre del bloque). El campo `tipo` sigue siendo el código de estado para lógica JS — no cambiar.

## Reportes — separación Indicadores Institucionales vs DACOM ⚠️ CRÍTICO
Auditado 2026-06-11. Regla: **KPIs institucionales solo usan `EstudianteTitulado` + `RegistroIngreso` con `tipo="ESTUDIANTE"`**.

**Indicadores Institucionales** (base = total de estudiantes titulados):
`total_titulados`, `total_ingresados`, `total_ausentes`, `pct_asistencia`, `total_puntuales`, `total_atrasados`, `hora_peak`, puntualidad por bloque, tiempos de ingreso → filtro `tipo="ESTUDIANTE"` aplicado en todos.

**Indicadores Operativos DACOM** (base = invitaciones):
`total_inv_usadas`, `inv_gestionadas_b`, `inv_no_gestionadas_b` → correctamente separados en bloque `invitaciones_resumen`.

**Métrica combinada `total_asistentes`** = `ingresados_b + inv_usadas_b`:
Mostrada como "Total Presentes (Tit.+Inv.)" — etiqueta explícita en todos los templates.
**NUNCA usar como denominador de % institucional.** No afecta % Asistencia ni % Gestión.

**Filtros obligatorios** en `_calcular_reportes` para métricas de tiempo/puntualidad:
```python
tipo="ESTUDIANTE"  # en ingresos_qs, por_minuto_qs, tiempos_global, atrasados_b, tiempos_b, hora_peak_b_row
```

## Reglas frontend (resumen)
- Para cualquier tarea visual: leer `FRONTEND_MAP.md` primero.
- No crear layouts nuevos — reutilizar `ops-layout` (inicio.css).
- No usar hero rojo en módulos nuevos — patrón: cmd-bar + workspace.
- `tarjetas.html` es el único módulo sin ops-layout (usa `.marco`).
- Responsive obligatorio. No generar scroll horizontal.
- CSS load order siempre: `base.css` → `inicio.css` → `[módulo].css`.
