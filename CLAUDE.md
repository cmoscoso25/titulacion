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
- templates principales
- CSS institucional

---

# Mapeo CSS ↔ Template ↔ Vista

Cada página tiene su propio CSS. El CSS y el HTML DEBEN usar exactamente las mismas clases. Si se modifica uno, revisar el otro.

| URL | Vista (views.py) | Template | CSS |
|-----|-----------------|----------|-----|
| `/` | `inicio` | `inicio.html` | `base.css` |
| `/tarjetas/` | `tarjetas_invitacion` | `tarjetas.html` | `tarjetas.css` |
| `/entrega-invitaciones/` | `entrega_invitaciones` | `entrega_invitaciones.html` | `entrega.css` |
| `/registro-ingreso/` | `registro_ingreso` | `registro_ingreso.html` | `registro.css` |

**REGLA CRÍTICA**: Antes de modificar cualquier CSS, leer el HTML correspondiente para verificar las clases reales. Antes de modificar cualquier HTML, leer el CSS correspondiente. Una discrepancia de nombres de clase rompe el diseño silenciosamente.

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

### registro_ingreso.html → registro.css
Lector QR USB HID (modo teclado HID, no cámara):
- `.lector-usb` — contenedor del lector
- `.indicador-lector` — indicador visual de estado
- `.input-qr-usb` — campo con `autofocus`, captura código por Enter
- `.pulso-qr` — animación de pulso verde

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