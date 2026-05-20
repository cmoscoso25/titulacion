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