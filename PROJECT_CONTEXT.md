# Contexto Proyecto Titulación INACAP

## Descripción general

Sistema institucional de Titulación INACAP Sede Arica 2026.

Permite administrar ceremonias de titulación, invitados, accesos QR y control de asistentes.

## Agregar Estudiante migrado a ops-layout (2026-06-02)

`agregar_estudiante.html` + `agregar_estudiante.css` migrados al estándar global:
- Reemplaza `.marco` + `<header class="barra">` por `ops-layout` con sidebar + `ops-topbar`
- Agrega `inicio.css` al head (load order: base → inicio → agregar_estudiante)
- `ops-scroll ag-view` — `.ag-view` en CSS zeroes padding del scroll
- Sidebar con permisos idéntico al resto, "Agregar Estudiante" activo (bajo perm_admin)
- Mensajes migrados a `ops-mensajes` antes del `ops-scroll`
- JS `actualizarPlanes()` / `actualizarInstitucion()` sin modificaciones
- Negative margins (-30px) del hero preservados — paneles siguen superponiéndose al hero rojo
- Notebook 1025-1366px: inputs 36px, botones 38px, secciones 16px, padding panel reducido
- HDMI max-height:800px: compactación adicional de todos los elementos verticales

## Reportes compactación notebook (2026-06-02)

Segunda ronda de ajuste fino para 1366×768: breakpoints `1025-1366px` y `max-height:800px` reemplazados con valores más agresivos. Cambios clave: `rep-header` 44→42px, `rep-strip-item` padding 8→7px, `kpi-rep` padding 9→8px, `kpi-rep-top margin-bottom` 5→4px, `panel-rep` padding 10→9px, `rep-tabs-wrapper margin-bottom` ahora explícito en ambos breakpoints (7px/5px), `rep-actualizacion margin` reducido. Para 1366×768, ambos breakpoints son activos simultáneamente (width + height) y el HDMI gana por orden CSS.

## Reportes CSS responsive corregido (2026-06-02)

`reportes.css` — grids KPI y gráfico ajustados para ops-layout (viewport - sidebar):
- `.kpis-reportes` y `.kpis-op`: de `repeat(N, 1fr)` forzado a `repeat(auto-fit, minmax(..., 1fr))` en todos los breakpoints — cards siempre ≥175px/150px, sin textos cortados
- `.rep-kpis-2col` (tab Tiempos): eliminado `max-width:560px`, ahora ocupa 100% del contenedor
- `kpi-rep-valor`: `clamp(1.3rem, 1.5vw, 1.75rem)` — evita overflow en cards pequeñas
- `kpi-rep-texto`: añadido `word-break:break-word` — nombres de ceremonia ya no se cortan
- `chart-container`: `clamp(200px, 28vh, 300px)` — gráfico respeta alto disponible por resolución
- Breakpoint notebook 1025-1366px: padding compacto `11px 13px` + font reducido
- Breakpoint HDMI (max-height:800px): todos los elementos compactados ~15%

## Reportes integrado a ops-layout (2026-06-02)

`reportes.html` migrado de layout propio (`.marco` + `<header class="barra">`) a `ops-layout` global:
- Sidebar con permisos (igual que los demás módulos), "Reportes" como item activo
- `ops-topbar` global (elimina header duplicado)
- `ops-scroll rep-view` — `.rep-view` en `reportes.css` zeroes padding del scroll
- El `.rep-header` (command bar con filtros, Excel, Imprimir), `.rep-strip` y los 5 tabs no se tocaron
- `@media print` actualizado: referencia `ops-layout` en vez de `.marco`/`.barra`
- Ahora responsive por herencia de `inicio.css` + breakpoints propios de `reportes.css`

## Menú y Inicio por permisos (2026-06-02)

Nuevo `titulacion/context_processors.py` agrega `perm_admin`, `perm_admision`, `perm_curricular`, `perm_entrega`, `perm_ingreso` a todos los templates automáticamente (registrado en `settings.py`).

Sidebars actualizados (nuevas secciones por permisos):
- PRINCIPAL (todos), GESTIÓN DE ESTUDIANTES (perm_admin), OPERACIÓN DE CEREMONIA (perm_entrega/perm_ingreso), GESTIÓN Y CONTROL (perm_curricular), ANÁLISIS (perm_curricular/perm_admin), SISTEMA (perm_admin)
- Templates actualizados: `inicio.html`, `panel_control.html`, `registro_ingreso.html`, `entrega_invitaciones.html`
- Sin sidebar: `cambio_ceremonia`, `reportes`, `cargar_excel`, `agregar_estudiante`, `tarjetas` (usan layout propio `.marco`)

Cards de Inicio también filtradas por permisos (secciones vacías no se renderizan).

## UX Panel de Control — bloque requerido (2026-06-02)

Nuevo flujo:
- Al abrir `/panel-control/`, selector `#filtroBloque` inicia vacío y aparece estado vacío "Seleccione un bloque" (no carga datos automáticamente).
- Al seleccionar un bloque, se dispara `cargarDashboard()` automáticamente (sin botón Aplicar).
- Auto-refresh de 15s solo se ejecuta cuando hay un bloque seleccionado.
- Limpiar vuelve al estado inicial (vacío).
- Bloque ABIERTA se marca con "▶ ... (Abierta)" en el selector.
- Contador de planes visible como badge en el tab "Avance por plan".
- Botón "Aplicar" eliminado. Solo queda "Buscar" y "Limpiar".
- Nuevos estilos en `dashboard.css`: `.pc-empty-state`, `.pc-tab-count`.

## Optimización Panel de Control (2026-06-02)

`datos_panel_control` fue optimizado para eliminar N+1 queries:
- `_estudiantes_atrasados_ids` (set) → ya existía para KPIs; ahora también se usa en el loop de seguimiento (elimina 1 query por estudiante)
- `_invitaciones_atrasadas_ids` (set) → nueva query única antes del loop (elimina hasta 2 queries por estudiante)
- `_atrasados_por_plan` (dict) → nueva query `annotate` antes del loop de planes (elimina 1 query por plan)
- Resultado: de ~900 queries por llamada a ~12 queries fijas, independiente del volumen

Frontend `panel_control.html` JS:
- `AbortController` — cancela petición anterior si el usuario cambia filtros rápido
- Caché 8s por clave de filtros — respuesta instantánea al volver a un filtro reciente
- Indicador "actualizando..." solo si la respuesta tarda >300ms
- `setInterval` pasa `esAutoRefresh=true` — no interrumpe fetch manual activo
- `limpiarFiltros` y cambio de bloque invalidan caché

---

## Estado del responsive (2026-06-02)

El layout global (`inicio.css`) está **optimizado y estable** para:
- Notebook 15" a 1366×768 — sin scroll, todo visible, sidebar compacto 172px
- Monitor 22" a 1920×1080 — diseño estándar, sidebar 220px
- TV/HDMI — sidebar 240px, tipografía y padding grandes (1921px+)
- Tablet/móvil — sidebar en drawer con hamburger (≤768px)

No modificar `inicio.css` sin probar en ambas resoluciones (1366×768 y 1920×1080).

---

# Objetivos principales

- modernizar proceso de titulación,
- digitalizar invitaciones,
- controlar acceso,
- gestionar ceremonias,
- facilitar administración institucional.

---

# Funcionalidades principales

## Gestión ceremonias

- creación ceremonias,
- asignación estudiantes,
- cambio ceremonia,
- estados.

---

## Invitaciones

- generación invitaciones,
- entrega invitaciones,
- control estados.

---

## QR

- generación QR,
- validación QR,
- control ingreso.

---

## Dashboard

- KPIs,
- estadísticas,
- asistentes,
- estados.

---

# Estructura principal

```text
titulacion_inacap/
├── configuracion/
│   └── settings.py
├── titulacion/
│   ├── views.py              ← lógica principal de todas las vistas
│   ├── urls.py               ← rutas del sistema
│   ├── models.py             ← EstudianteTitulado, Invitacion, Bloque, Ceremonia
│   ├── generador_qr.py       ← generación imágenes QR con qrcode library
│   ├── templates/titulacion/
│   │   ├── login.html
│   │   ├── inicio.html               ← 6 módulos con iconos institucionales (siglas)
│   │   ├── cargar_excel.html
│   │   ├── agregar_estudiante.html
│   │   ├── panel_control.html        ← dashboard KPIs + filtros + 4 tabs
│   │   ├── cambio_ceremonia.html
│   │   ├── tarjetas.html             ← impresión tarjetas institucionales
│   │   ├── entrega_invitaciones.html ← búsqueda y descarga PNG de invitaciones
│   │   ├── registro_ingreso.html     ← control de acceso con lector QR USB HID
│   │   └── reportes.html             ← dashboard premium: command bar + kpi-strip + 5 tabs (segment control) + Chart.js + export Excel
│   └── static/titulacion/css/
│       ├── base.css              ← variables, reset, header, botones, badges globales
│       ├── login.css             ← layout fullscreen login (usa vars de base.css)
│       ├── inicio.css            ← layout ops-layout global; auto-fit grids (KPIs, módulos, grupos); breakpoints 480/768/1024/1366/1921px; --sb-w clamp por breakpoint
│       ├── carga_excel.css
│       ├── agregar_estudiante.css
│       ├── dashboard.css         ← rediseño ejecutivo pc-*: cmd-bar + kpi-strip + filter-bar + pc-content. pc-view zeroes ops-scroll padding. NO tiene hero propio.
│       ├── cambio_ceremonia.css
│       ├── tarjetas.css
│       ├── entrega.css
│       ├── registro.css          ← centro control: reg-cmd-bar + reg-kpi-strip + reg-body(2cols) + reg-cer-strip. Sin scroll normal. Variables --ok/--wrn/--err/--nvy
│       └── reportes.css          ← sistema enterprise premium: command-bar, kpi-strip, segment-tabs, kpi-rep border-top, variables semánticas --c-ok/err/warn/info/navy/teal
├── media/                    ← imágenes QR generadas (no en git)
├── staticfiles/              ← salida de collectstatic (no en git)
├── manage.py
├── db.sqlite3
└── requirements.txt
```

---

# Despliegue en PythonAnywhere

**Cuenta:** titulacion2026.pythonanywhere.com
**Ruta del proyecto:** `~/titulacion` (NO `~/titulacion_inacap`)
**Rama:** `main`

## Comandos de despliegue (consola Bash de PythonAnywhere)

```bash
cd ~/titulacion
git pull origin main
python manage.py collectstatic --noinput
```

Luego presionar **Reload** en el tab **Web** de PythonAnywhere.

## Archivos estáticos

- Los archivos en `titulacion/static/` se deben copiar con `collectstatic` a `staticfiles/`.
- PythonAnywhere sirve estáticos desde `~/titulacion/staticfiles/`, no desde `~/titulacion/titulacion/static/`.
- Si un cambio de CSS no se refleja en producción, siempre ejecutar `collectstatic` + Reload.

---

# Colores institucionales INACAP

Definidos en `base.css` como variables CSS:

```css
--rojo: #e30613;
--rojo-oscuro: #b10510;
--azul: #06152f;        /* azul marino institucional */
--negro: #161616;
--blanco: #ffffff;
--oro: #c9a227;         /* dorado decorativo tarjetas */
--crema: #faf5ea;       /* fondo columna izquierda tarjetas */
--crema-borde: #dfc98a; /* borde columna izquierda */
```

---

# Sistema de permisos

El sistema usa **grupos Django** por nombre, NO permisos de modelo. Ver `titulacion/permisos.py`.

| Grupo Django | Acceso |
|---|---|
| `ADMIN_TITULACION` | Todo el sistema |
| `ADMISION` | Registro de ingreso + Entrega de invitaciones |
| `CURRICULAR` | Panel control, reportes, cambio de ceremonia |
| `ENTREGA_INVITACIONES` | Solo entrega de invitaciones |
| `INGRESO` | Solo registro de ingreso QR (usuario DAE) |
| `DACOM` | Solo entrega de invitaciones (DACOM) |

**IMPORTANTE**: Al crear usuarios en Django Admin, asignar el grupo correspondiente. No asignar permisos individuales de modelo.

---

# Lector QR

- **Tipo:** USB HID en modo teclado (no requiere cámara).
- **Funcionamiento:** el lector envía el código como si fuera texto de teclado más Enter.
- **Campo:** `#inputQR` con `autofocus`, captura en evento `keydown` tecla Enter.
- **Vista:** `registro_ingreso` → valida contra `EstudianteTitulado.codigo_qr_estudiante` e `Invitacion.codigo_qr`.
- **Endpoint de validación:** `POST /validar-codigo/` → devuelve JSON con resultado.

---

# Generación de QR

- **Librería:** `qrcode` (Python).
- **Archivo:** `titulacion/generador_qr.py`.
- **Funciones clave:**
  - `generar_qr_estudiante(estudiante)` — genera y guarda QR del titulado.
  - `generar_qr_invitacion(invitacion)` — genera y guarda QR de invitado.
  - `crear_imagen_qr(codigo)` — crea imagen PNG en memoria.
- **Imágenes:** se guardan en `media/` y se referencian desde el modelo vía `ImageField`.