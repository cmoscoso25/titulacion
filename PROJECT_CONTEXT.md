# Contexto Proyecto — Titulación INACAP 2026

Sistema Django: gestión de Ceremonias de Titulación, Sede Arica.
Funciones: ceremonias, invitaciones QR, acceso físico, dashboard, administración.

## Módulos y estado

| Módulo | URL | Layout/Prefijo CSS | Estado |
|---|---|---|---|
| Inicio | `/inicio/` | ops-layout | ✓ ESTABLE |
| Panel de Control | `/panel-control/` | ops-layout + `pc-*` | ✓ ESTABLE |
| Registro de Ingreso | `/registro/` | ops-layout + `reg-*` | ✓ ESTABLE |
| Entrega Invitaciones | `/entrega-invitaciones/` | ops-layout | ✓ ESTABLE |
| Reportes | `/reportes/` | ops-layout + `rep-*` | ✓ ESTABLE |
| Agregar Estudiante | `/agregar-estudiante/` | ops-layout + `ag-*` workspace | ✓ ESTABLE |
| Carga Masiva Excel | `/cargar-excel/` | ops-layout + `ce-*` | ✓ ESTABLE |
| Cambio de Ceremonia | `/cambio-ceremonia/` | ops-layout + `cc-*` workspace | ✓ ESTABLE |
| Tarjetas QR | `/tarjetas/` | `.marco` (legacy, sin sidebar) | — |
| Login | `/login/` | fullscreen | — |

## Estándar visual ops-layout (todos los módulos excepto tarjetas)
- Estructura: `ops-sidebar` + `ops-main` (`ops-topbar` + `ops-overlay` + `ops-mensajes` + `ops-scroll`)
- Workspace pattern: `[xx-view] → xx-cmd-bar (52px) + xx-workspace (grid 1fr [lateral])`
- Cards: fondo blanco, `border: 1px solid #dbe3ea`, `radius: 10px`, `box-shadow: 0 1px 3px`
- Card titles: `0.62rem / #9ca3af / uppercase / border-bottom:#f3f4f6`
- Inputs: `34px`. Botón acción: navy pill `#06152f`. Cancelar: gray outline.
- Ver `FRONTEND_MAP.md` para breakpoints, IDs JS y clases específicas.

## Decisiones técnicas clave
- **Panel Control:** inicia vacío; carga solo cuando `filtroBloque !== ""`. Auto-refresh 15s.
  ORM: ~12 queries fijas (era ~900 con N+1). JS: AbortController + caché 8s por filtro.
- **Context processor:** `titulacion/context_processors.py` inyecta `perm_*` — registrado en `settings.py TEMPLATES`.
- **Cambio de Ceremonia:** `form.cc-cambio-form` (flex-column gap-10px) envuelve 2 cards separadas.
  `cc-card-form` tiene `border-top: 3px solid #06152f`. Trazabilidad y QR intactos.
- **Carga Excel:** objeto `resumen` del procesador: claves `estudiantes_creados`, `estudiantes_actualizados`, `invitaciones_creadas`, `filas_omitidas`.
- **Agregar Estudiante:** JS `actualizarPlanes()` + `actualizarInstitucion()` filtran planes por área dinámicamente.
- **Reportes:** `rep-view` zeroes padding. KPI grids: `auto-fit minmax` — nunca `repeat(N, 1fr)`.
  **Auditoría 2026-06-11:** KPIs institucionales filtran `tipo="ESTUDIANTE"` en RegistroIngreso.
  Tiempos de 30 min: `TruncMinute` + bucket Python. PDF: `reporte_pdf.html` / `/reportes/pdf/`.
  **Reporte Vicerrectoría (2026-06-11):** `reporte_vicerrectoria_pdf.html` / `/reportes/vicerrectoria-pdf/`.
  Incluye análisis cuantitativo por ceremonia, análisis cualitativo rule-based (`_generar_analisis_ia`),
  recomendaciones automáticas, gestión DACOM y motivos de no asistencia.
- **Entrega Invitaciones — Resultado Gestión (2026-06-11):** `marcar_entrega_invitaciones` acepta POST
  con `resultado_gestion`, `motivo_no_asistencia` (obligatorio si NO_ASISTIRA), `detalle_motivo` (obligatorio si OTRO).
  Nuevos campos en `EstudianteTitulado` (migración 0005). JS condicional en entrega_invitaciones.html.
  Breakpoints `1025-1366px` + `max-height:800px` aplican simultáneamente en notebook — HDMI gana (viene último).
- **Comando reset_registro_ingreso (2026-06-09):** `python manage.py reset_registro_ingreso`
  Elimina `RegistroIngreso`, resetea `ingreso_confirmado`/`fecha_hora_ingreso` en estudiantes y
  `usada`/`fecha_uso` en invitaciones. Requiere escribir "CONFIRMAR" (o flag `--confirmar`).
  No borra QRs, invitaciones, ceremonias ni datos de estudiantes.
- **Registro de Ingreso — mensajes QR (2026-06-09):** `validar_codigo_ingreso` retorna campo `tipo_entrada`
  ("Estudiante" / "Invitado 1" / "Invitado 2") y `ceremonia` (nombre del bloque) en todos los JsonResponse
  de `registrar_ingreso_estudiante` y `registrar_ingreso_invitado`. El template usa `tipo_entrada` en el
  campo "Tipo" del grid de resultado y muestra "Ceremonia" como nuevo campo wide. `datos.tipo` sigue siendo
  el código de estado (PERMITIDO/DUPLICADO/OTRA_CEREMONIA/…) para la lógica JS — no alterado.

## Sistema de permisos
Grupos Django: `ADMIN_TITULACION` / `ADMISION` / `CURRICULAR` / `ENTREGA_INVITACIONES` / `INGRESO` / `DACOM`.
Ver `titulacion/permisos.py`. Funciones: `es_admin_titulacion()`, `es_admision()`, `es_curricular()`, `es_entrega()`, `es_ingreso()`.
QR: `titulacion/generador_qr.py` → `generar_qr_estudiante()`, `generar_qr_invitacion()`, `crear_imagen_qr()`.
Lector QR: USB HID teclado, endpoint `POST /validar-codigo/` → JSON.

## Despliegue en PythonAnywhere
- **Cuenta:** titulacion2026.pythonanywhere.com · **Ruta:** `~/titulacion` · **Rama:** `main`
- **Flujo:** `git pull origin main` → `python manage.py collectstatic --noinput` → Reload (tab Web)
- Estáticos: servidos desde `~/titulacion/staticfiles/` (NO desde `titulacion/static/`).
- Siempre ejecutar `collectstatic` + Reload al cambiar CSS/static.

## Colores institucionales (base.css)
`--rojo:#e30613` · `--rojo-oscuro:#b10510` · `--azul:#06152f` (navy) · `--negro:#161616`
`--oro:#c9a227` · `--crema:#faf5ea` · `--crema-borde:#dfc98a`
Módulos nuevos usan `#06152f` como primario — NO `var(--rojo)`.
