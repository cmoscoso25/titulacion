# Contexto Proyecto Titulación INACAP

## Descripción general

Sistema institucional de Titulación INACAP Sede Arica 2026.

Permite administrar ceremonias de titulación, invitados, accesos QR y control de asistentes.

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
│       ├── dashboard.css         ← KPIs coloreados, filtros, tabs, barra-progreso
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