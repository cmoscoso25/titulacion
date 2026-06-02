# Instrucciones para Claude - Proyecto Titulación INACAP

Este proyecto corresponde al sistema institucional de Ceremonia de Titulación INACAP Sede Arica 2026.

## Regla principal

Antes de modificar cualquier archivo:

1. Usar CodeGraph para explorar el proyecto.
2. No leer archivos completos innecesariamente.
3. Identificar primero archivos relacionados.
4. Explicar qué archivos se modificarán antes de editar.
5. No romper funcionalidades existentes.
6. Mantener diseño institucional.
7. Entregar siempre archivos completos.
8. Mantener compatibilidad responsive.

---

# Preferencias del desarrollador

- Responder en español.
- Código claro y entendible.
- Mantener naming consistente.
- No simplificar eliminando lógica existente.
- No romper endpoints.
- No eliminar responsive existente.
- No alterar estructura sin explicar impacto.

---

# Stack

- Django
- Python
- SQLite
- HTML
- CSS
- JavaScript

---

# Objetivo del sistema

El sistema permite:

- gestión de ceremonias,
- entrega de invitaciones,
- control acceso mediante QR,
- dashboard institucional,
- validación asistentes,
- administración de estudiantes,
- gestión de permisos,
- cambio de ceremonia,
- control de estados.

---

# Archivos críticos

Antes de modificar revisar:

- manage.py
- configuracion/settings.py
- titulacion/views.py
- titulacion/urls.py
- titulacion/models.py
- titulacion/permisos.py  ← sistema de grupos/roles
- templates principales
- CSS institucional

---

# Sistema de permisos (permisos.py)

**IMPORTANTE**: El sistema valida por **nombre de grupo Django**, NO por permisos de modelo Django. Los permisos asignados en Django Admin a un grupo no tienen efecto; lo que importa es el nombre del grupo.

## Grupos definidos en `permisos.py`

| Constante | Nombre grupo Django | Acceso |
|-----------|--------------------|----|
| `GRUPO_ADMIN` | `ADMIN_TITULACION` | Todo el sistema |
| `GRUPO_ADMISION` | `ADMISION` | Registro de ingreso + Entrega |
| `GRUPO_CURRICULAR` | `CURRICULAR` | Panel control, reportes, cambio ceremonia |
| `GRUPO_ENTREGA` | `ENTREGA_INVITACIONES` | Solo entrega de invitaciones |
| `GRUPO_INGRESO` | `INGRESO` | Solo registro de ingreso QR (DAE) |
| `GRUPO_DACOM` | `DACOM` | Solo entrega de invitaciones (DACOM) |

## Funciones de chequeo

- `es_admin_titulacion(u)` → is_superuser o ADMIN_TITULACION
- `es_admision(u)` → ADMIN o ADMISION
- `es_curricular(u)` → ADMIN o CURRICULAR
- `es_entrega(u)` → ADMIN, ADMISION, ENTREGA_INVITACIONES o DACOM
- `es_ingreso(u)` → ADMIN, ADMISION o INGRESO

## Decorators y rutas protegidas

- `acceso_admin` → cargar-excel, agregar-estudiante, tarjetas, reprogramar bloque
- `acceso_curricular` → panel-control, cambio-ceremonia, reportes
- `acceso_entrega` → entrega-invitaciones
- `acceso_ingreso` → registro/, validar-codigo/, registro-ultimos/, bloques abrir/cerrar
- `acceso_general` → inicio/ (solo requiere login)

## Regla al crear nuevo usuario

Al crear un usuario en Django Admin, asignarle el grupo correcto según su rol. **No asignar permisos individuales de modelo** — solo el grupo.

---

# Mapeo CSS ↔ Template ↔ Vista

Cada página tiene su propio CSS. El CSS y el HTML DEBEN usar exactamente las mismas clases. Si se modifica uno, revisar el otro.

| URL | Vista (views.py) | Template | CSS |
|-----|-----------------|----------|-----|
| `/login/` | auth Django | `login.html` | `login.css` (usa vars de base.css) |
| `/inicio/` | `inicio` | `inicio.html` | `inicio.css` |
| `/cargar-excel/` | `cargar_excel` | `cargar_excel.html` | `carga_excel.css` |
| `/agregar-estudiante/` | `agregar_estudiante` | `agregar_estudiante.html` | `agregar_estudiante.css` |
| `/panel-control/` | `panel_control` | `panel_control.html` | `dashboard.css` |
| `/cambio-ceremonia/` | `cambio_ceremonia` | `cambio_ceremonia.html` | `cambio_ceremonia.css` |
| `/tarjetas/` | `tarjetas_invitacion` | `tarjetas.html` | `tarjetas.css` |
| `/entrega-invitaciones/` | `entrega_invitaciones` | `entrega_invitaciones.html` | `entrega.css` |
| `/registro/` | `registro_ingreso` | `registro_ingreso.html` | `registro.css` |
| `/reportes/` | `reportes` | `reportes.html` | `reportes.css` |
| `/reportes/datos/` | `datos_reportes` | — JSON | — |
| `/reportes/exportar/excel/` | `exportar_reportes_excel` | — Excel | — |
| `/registro-ultimos/` | `ultimos_registros_ajax` | — JSON | — |
| `/validar-codigo/` | `validar_codigo_ingreso` | — JSON | — |

**REGLA CRÍTICA**: Antes de modificar cualquier CSS, leer el HTML correspondiente para verificar las clases reales. Antes de modificar cualquier HTML, leer el CSS correspondiente. Una discrepancia de nombres de clase rompe el diseño silenciosamente.

## Regla crítica: base.css define los heroes y paneles

**IMPORTANTE**: Cuando se agrega un nuevo módulo, sus clases `.hero-X`, `.hero-X-contenido` y `.hero-X h1/p` deben agregarse a las listas de selectores en `base.css`. Si no están en esas listas, el banner rojo y los estilos de tipografía del hero NO se aplicarán.

Lo mismo aplica para paneles: las clases `.panel-X` deben agregarse a la lista de paneles en `base.css` para recibir `background`, `border-radius`, `box-shadow` y `border`.

**Listas a actualizar en `base.css` al crear nuevo módulo:**
1. Selector principal del hero (línea ~278) — fondo rojo gradiente
2. Selector `::after` del hero (línea ~291) — círculo decorativo
3. Selector de contenido del hero (línea ~309) — ancho y padding
4. Selector `h1` del hero (línea ~323)
5. Selector `p` del hero (línea ~335)
6. Lista de paneles (línea ~387) — sombra, borde, fondo blanco
7. Responsive 320-480px: contenedor hero (línea ~622)
8. Responsive 481-767px: contenedor hero (línea ~645)
9. Responsive max-height 800px: contenedor y h1 (línea ~683)

## Arquitectura visual del módulo Reportes (premium)

`reportes.html` NO usa `hero-reportes`. Tiene layout propio:
- `.rep-header` — command bar gris claro (fondo `#f8fafc`), no rojo
- `.rep-strip` — franja blanca con 4 KPIs rápidos (IDs: `stripTit`, `stripIng`, `stripPct`, `stripPeak`)
- `.rep-main` — fondo página `#f4f6f9`
- `.rep-tabs-seg` — segment control tabs (pill style, no underline)
- `.kpi-rep` — cards con `border-top` semántico + gradiente sutil de fondo
- `.panel-rep` — paneles blancos con sombra enterprise

Reglas de color para reportes:
- NO usar `var(--rojo)` como color primario (solo en badges de denegado/error)
- Primario: `--c-navy:#06152f` (azul marino)
- Éxito/presencia: `--c-ok:#16a34a`
- Alerta: `--c-warn:#d97706`
- Error: `--c-err:#dc2626`

Sistema de variables en reportes.css:
`--c-ok`, `--c-err`, `--c-warn`, `--c-info`, `--c-navy`, `--c-teal` + sus variantes `-bg` y `-border`

**REGLA**: Si se crea otro módulo de análisis/dashboard, seguir el patrón `.rep-header` + `.rep-strip` + `.rep-main` en lugar del hero rojo estándar.

## Clases principales por página

### tarjetas.html → tarjetas.css
Diseño horizontal 3 columnas (ticket institucional):
- `.tarjeta-fisica` — contenedor principal, `grid-template-columns: 230px 1fr 210px`
- `.tf-izq` — columna izquierda, fondo crema `#faf5ea`
- `.tf-centro` — columna central, blanca
- `.tf-der` — columna derecha oscura
- `.tf-der-azul` — fondo azul marino (titulado)
- `.tf-der-rojo` — fondo rojo oscuro (invitado)
- `.tf-titulo-inv` — "INVITACIÓN" en Georgia itálica dorada
- `.tf-msg-logro` — "tu logro" en Georgia itálica dorada
- `.tf-cod-val` — código en Courier New blanco

### entrega_invitaciones.html → entrega.css
Diseño horizontal 3 columnas (descargable como PNG via html2canvas):
- `.tarjeta` — contenedor principal, `grid-template-columns: 210px 1fr 190px`
- `.tarjeta-left` — columna izquierda, fondo crema
- `.tarjeta-center` — columna central, blanca
- `.tarjeta-right` — columna derecha oscura
- `.tarjeta-right-titulado` — fondo `var(--azul)`
- `.tarjeta-right-invitado` — fondo `var(--rojo-oscuro)`
- `.tipo-invitacion` — "INVITACIÓN" en Georgia itálica dorada
- `.texto-logro h3` — "tu logro" en Georgia itálica dorada
- `.codigo-acceso` — código en Courier New blanco

### inicio.html → inicio.css (layout global ops-layout, responsive mobile-first)
Sistema de tarjetas: toda la tarjeta es `<a class="modulo">` (link completo, sin botón separado).
Iconografía: SVG inline Lucide (15px en contenedor 30px). NO usar siglas de texto como iconos.
Color accent: `style="--mc:#HEX"` en cada `.modulo` → `::before` usa `var(--mc)` para la línea deslizante en hover.
Variables globales: `--sb-w` (ancho sidebar), `--topbar-h` (altura topbar), `--rojo-ops`, `--negro-ops`.

**Grids con auto-fit** (se adaptan solos sin breakpoints explícitos):
- `ops-kpis`: `repeat(auto-fit, minmax(130px, 1fr))` — 5 cols en wide, menos en estrecho
- `ops-grupos`: `repeat(auto-fit, minmax(280px, 1fr))` — 2 cols en wide, 1 en estrecho
- `ops-mods`: `repeat(auto-fit, minmax(160px, 1fr))` — 2 cols normalmente
- `ops-footer-row`: `1fr clamp(200px, 22vw, 280px)` — columna derecha flexible

**Breakpoints responsivos explícitos en inicio.css:**
| Rango | `--sb-w` | Comportamiento |
|---|---|---|
| ≤480px | sidebar oculto | KPIs 2 cols, módulos 1 col |
| 481–767px | sidebar oculto | KPIs 2 cols, módulos 2 cols |
| ≤768px | oculto (hamburger) | sidebar en drawer overlay |
| 768–1024px | 196px | KPIs auto-fit, grupos 1 col |
| 1025–1366px | 200px | KPIs auto-fit, padding reducido |
| 1367–1920px | 220px (default) | sin overrides |
| 1921px+ | 240px | tipografías y padding más grandes |
| height≤700 + wide | sin cambio | spacing ultra-compacto (HDMI) |

### agregar_estudiante.html → agregar_estudiante.css
Formulario manual con selección de ceremonia/bloque y filtrado dinámico de planes:
- `.hero-agregar` / `.hero-agregar-contenido` — registrados en `base.css`
- `.panel-formulario` / `.panel-recientes` — registrados en `base.css`
- `.seccion-form` — sección con separador horizontal dentro del formulario
- `.grid-campos` — grid responsivo de campos (1→2→3 columnas)
- `.campo-ancho` — campo que ocupa 2 columnas en layouts anchos
- `.campo-readonly` — display de institución (no editable)
- `.btn-guardar` / `.btn-cancelar` — acciones del formulario
- `.tabla-recientes` — tabla con últimos 10 estudiantes agregados

### registro_ingreso.html → registro.css
Centro de control operativo. Lector QR USB HID (modo teclado HID, no cámara).
Sin scroll vertical en uso normal. Optimizado 1366×768 y 1920×1080.

**Estructura visual (patrón similar a reportes.html):**
- `.reg-view` — clase adicional sobre `ops-scroll`; zeroes padding, activa flex-column. Define variables `--ok`, `--wrn`, `--err`, `--nvy`, `--bd`, `--bg`
- `.reg-cmd-bar` — command bar 52px: título + ícono navy + info ceremonia activa + badge ABIERTA/CERRADA
- `.reg-kpi-strip` — franja 5 KPIs compactos (colores semánticos via `::after` top-border)
- `.reg-body` — grid 2×1fr, `flex:1`, `overflow:hidden`
- `.reg-col-scanner` — panel izquierdo: lector QR + resultado escaneo + ingreso manual
- `.reg-col-monitor` — panel derecho: timeline tiempo real (scroll interno en `.reg-timeline`)
- `.reg-cer-strip` — barra inferior 52px: chips ceremonia con botones Abrir/Cerrar/Reprogramar

**Clases JS-referenced (NO renombrar):**
- `.lector-usb`, `.indicador-lector`, `.input-qr-usb`, `.pulso-qr`
- `.lector-activo`, `.lector-procesando`, `.lector-capturando`, `.lector-sin-foco`, `.lector-enfocado`
- `.resultado-validacion` + `.visible`, `.permitido`, `.rechazado`, `.atrasado`, `.error`
- `.estado-grande` + `.estado-ok`, `.estado-no`, `.estado-alerta`, `.estado-tarde`, `.estado-duplicado`
- `.resultado-detalle-grid`, `.rd-item`, `.rd-item--wide`
- `.reg-evento--{permitido|duplicado|atrasado|rechazado}`, `.reg-evento-dot`, `.reg-evento-body`, `.reg-evento-nombre`, `.reg-evento-tipo`, `.reg-evento-meta`, `.reg-evento-badge`, `.reg-evento-hora`, `.reg-tl-empty`

**REGLA**: NO usar `ops-kpis` ni `kpi-card` en este módulo. Usar clases `reg-*` propias.

---

# Forma de trabajo

Antes de editar:

1. Explicar problema detectado.
2. Explicar archivos relacionados.
3. Explicar solución propuesta.
4. Explicar riesgos posibles.
5. Esperar aprobación antes de modificar.

---

# Reglas frontend

- Mantener identidad institucional INACAP.
- Mantener diseño premium.
- Responsive obligatorio.
- No generar scroll innecesario.
- Mantener experiencia fluida en móviles y TV.

---

# Regla importante

Siempre entregar archivos completos.

Usar:

"Reemplaza TODO el archivo por este código"

No entregar fragmentos parciales salvo que se solicite explícitamente.