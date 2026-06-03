# Frontend Map — Titulación INACAP

> Leer SOLO para tareas de frontend / CSS / JavaScript.

## URL → Template → CSS → Vista

| URL | Template | CSS | Vista (views.py) |
|---|---|---|---|
| `/login/` | `login.html` | `login.css` | auth Django |
| `/inicio/` | `inicio.html` | `inicio.css` | `inicio` |
| `/cargar-excel/` | `cargar_excel.html` | `carga_excel.css` | `cargar_excel` |
| `/agregar-estudiante/` | `agregar_estudiante.html` | `agregar_estudiante.css` | `agregar_estudiante` |
| `/panel-control/` | `panel_control.html` | `inicio.css` + `dashboard.css` | `panel_control` |
| `/cambio-ceremonia/` | `cambio_ceremonia.html` | `cambio_ceremonia.css` | `cambio_ceremonia` |
| `/tarjetas/` | `tarjetas.html` | `tarjetas.css` | `tarjetas_invitacion` |
| `/entrega-invitaciones/` | `entrega_invitaciones.html` | `entrega.css` | `entrega_invitaciones` |
| `/registro/` | `registro_ingreso.html` | `registro.css` | `registro_ingreso` |
| `/reportes/` | `reportes.html` | `reportes.css` | `reportes` |
| `/reportes/datos/` | — JSON | — | `datos_reportes` |
| `/validar-codigo/` | — JSON | — | `validar_codigo_ingreso` |

## Prefijos CSS por módulo

| Prefijo | Módulo | Patrón |
|---|---|---|
| `ops-*` | Layout global (`inicio.css`) | sidebar, topbar, nav, scroll, overlay |
| `ag-*` | Agregar Estudiante | workspace 2 cols: `ag-workspace` / `ag-card` / `ag-field` |
| `cc-*` | Cambio de Ceremonia | workspace 2 cols: `cc-workspace` / `cc-card` / `cc-field` |
| `ce-*` | Carga Masiva Excel | `ce-cmd-bar` + `ce-kpi-strip` + cards |
| `pc-*` | Panel de Control | `pc-cmd-bar` + `pc-kpi-strip` + `pc-filter-bar` |
| `reg-*` | Registro de Ingreso | `reg-cmd-bar` + `reg-kpi-strip` + `reg-body` 2 cols |
| `rep-*` | Reportes | `rep-header` + `rep-strip` + `rep-main` + `rep-tabs-seg` |
| `tf-*` | Tarjetas Físicas | grid 3 cols horizontal |

## IDs y clases JS-referenced (NO renombrar)

### Panel de Control (`dashboard.css` + `panel_control.html`)
**Filtros:** `#filtroCeremonia`, `#filtroBloque`, `#filtroBusqueda`, `#filtroArea`, `#filtroPlan`, `#filtroEstado`, `#filtroTipoAcceso`, `#filtroResultado`
**KPIs:** `#kpiEstudiantesPresentes`, `#kpiEstudiantesPendientes`, `#kpiInvitadosPresentes`, `#kpiTotalAsistentes`, `#kpiTotalAtrasados`, `#kpiAlertasQr`, `#kpiPctEstudiantes`, `#kpiPctInvitados`
**Tablas:** `#tablaAvancePlanes`, `#tablaUltimosMovimientos`, `#tablaAtrasados`, `#tablaSeguimiento`
**UI:** `#pc-empty-state`, `#pc-tabs-content`, `#pcAutoupdate`, `#planCount`, `#resultadoBusqueda`, `#ultimaActualizacion`
**Clases JS:** `.tab-dashboard`, `.panel-tab`, `.activo`, `.resultado-busqueda`, `.rb-*`, `.badge-si/no/atrasado`, `.fila-estado-*`, `.barra-progreso`
**Funciones:** `cargarDashboard()` (setInterval 15s), `cambiarTab()`, `limpiarFiltros()`, `cargarPlanesPorArea()`, `_mostrarEstadoInicial()`, `_mostrarDatos()`
**⚠️ Flujo:** Panel inicia vacío; datos solo cuando `filtroBloque.value !== ""`.

### Agregar Estudiante (`agregar_estudiante.html`)
**IDs:** `#bloque_id`, `#rut`, `#nombre_completo`, `#jornada`, `#correo`, `#telefono`, `#area_sel`, `#plan_id`, `#institucion_display`
**Funciones:** `actualizarPlanes()`, `actualizarInstitucion()` — filtrado dinámico de planes por área.

### Cambio de Ceremonia (`cambio_ceremonia.html`)
**names/IDs form:** `name="bloque_destino"`, `id="bloque_destino"`, `name="motivo"`, `id="motivo"`, `name="estudiante_id"`, `name="q"`
**form wrapper:** `class="cc-cambio-form"` (flex-column gap-10px — permite gap entre 2 cards dentro del form)

### Carga Masiva Excel (`cargar_excel.html`)
**IDs:** `#archivo_excel`, `#nombreArchivo`

### Registro de Ingreso (`registro_ingreso.html`)
**Lector:** `.lector-usb`, `.indicador-lector`, `.input-qr-usb`, `.pulso-qr`
**Estados:** `.lector-activo`, `.lector-procesando`, `.lector-capturando`, `.lector-sin-foco`, `.lector-enfocado`
**Resultado:** `.resultado-validacion.visible`, `.permitido`, `.rechazado`, `.atrasado`, `.error`
**Estado grande:** `.estado-grande`, `.estado-ok`, `.estado-no`, `.estado-alerta`, `.estado-tarde`, `.estado-duplicado`
**Detalle:** `.resultado-detalle-grid`, `.rd-item`, `.rd-item--wide`
**Timeline:** `.reg-evento--{permitido|duplicado|atrasado|rechazado}`, `.reg-evento-dot/body/nombre/tipo/meta/badge/hora`, `.reg-tl-empty`
**⚠️ REGLA:** NO usar `ops-kpis` ni `kpi-card` — usar clases `reg-*` propias.

## Breakpoints globales (inicio.css — ESTABLE)

| Rango | `--sb-w` | `--topbar-h` | Nota |
|---|---|---|---|
| ≤480px | oculto | 48px | KPIs 2 cols, módulos 1 col |
| 481–767px | oculto | 48px | KPIs 2 cols, módulos 2 cols |
| ≤768px | drawer | 48px | hamburger overlay |
| 768–1024px | 192px | 48px | grupos 1 col |
| **1025–1366px** | **172px** | **44px** | notebook: todo compacto |
| 1367–1920px | 220px | 48px | desktop estándar |
| 1921px+ | 240px | 54px | TV/HDMI grande |
| `max-height:800px` + wide | — | — | HDMI compacto |

**Regla notebook 1366×768:** breakpoints `1025-1366px` y `max-height:800px` aplican simultáneamente.
El breakpoint HDMI (`max-height:800px`) SIEMPRE va último en el CSS y gana sobre el de ancho.
Olvidar esto es la causa más frecuente de overflow vertical en notebook.

## Patrón workspace estándar (ag-* / cc-*)

```
ops-scroll.xx-view             padding:0 !important; flex-column; bg:#f4f6f9
  .xx-cmd-bar                  h:52px (46px notebook); bg:#fff; border-bottom:#dbe3ea
    .xx-cmd-icon               30px; bg:#06152f; radius:6px
    .xx-cmd-title              0.92rem; fw:700; color:#06152f
    .xx-cmd-sub                0.68rem; color:#6b7280
  .xx-workspace                grid:[1fr lateral]; gap:12px; padding:12px 16px
    .xx-col-main               flex-column; gap:10px
      .xx-card                 bg:#fff; border:#dbe3ea; radius:10px; shadow:0 1px 3px; p:14px 16px
        .xx-card-title         0.62rem; #9ca3af; uppercase; border-bottom:#f3f4f6
    .xx-col-side (290-360px)   flex-column; gap:10px
      .xx-card                 historial / últimos registros
  .ops-page-footer             0.7rem; #9ca3af; text-center; border-top:#f3f4f6
```

**Inputs/controles:** height `34px` (32px notebook). Labels: `0.62rem / #6b7280 / uppercase`.
**Botón acción:** navy `#06152f` pill `border-radius:999px`. Cancelar: gray outline.
**Notebook overrides (1025-1366px):** cmd-bar `46px`, cards padding `12px 14px`, inputs `32px`, btn `33px`.
**HDMI overrides (max-height:800px):** cmd-bar `44px`, cards padding `10px 14px`, inputs `31px`.

## Patrones especiales

### Reportes (rep-*)
Tiene layout propio dentro de ops-layout — NO sigue el patrón ag/cc:
- `rep-header` (command bar + filtros) → `rep-strip` (KPI franja) → `rep-main` → `rep-tabs-seg`
- KPI grids: `repeat(auto-fit, minmax(175px/150px, 1fr))` — NUNCA `repeat(N, 1fr)` con sidebar
- Variables: `--c-navy:#06152f`, `--c-ok:#16a34a`, `--c-warn:#d97706`, `--c-err:#dc2626`
- `rep-tabs-wrapper margin-bottom` + `rep-actualizacion margin` DEBEN estar en AMBOS breakpoints

### Tarjetas (tf-*)
- Layout `.marco` (sin ops-layout). Grid horizontal 3 cols: `230px 1fr 210px`
- `.tf-der-azul` (titulado) / `.tf-der-rojo` (invitado). Tipografía Georgia itálica dorada.
- Entrega invitaciones: misma estructura sin prefijo `tf-`, descargable via html2canvas.

### base.css → módulos nuevos
- NO agregar `.hero-X` a base.css — los módulos nuevos usan cmd-bar, no hero rojo.
- `button[type="submit"]` tiene alta especificidad — anular con selector más específico o `!important`.
- Panels (`.panel-X`) heredan sombra/borde de base.css si se registran en sus listas de selectores.
  Los módulos nuevos (`ag-card`, `cc-card`, etc.) definen su propio `box-shadow` directamente.
