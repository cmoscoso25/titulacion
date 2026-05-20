
---

# 5. docs/arquitectura.md

```markdown id="lbsh0q"
# Arquitectura General - Titulación INACAP

## Backend

Django + SQLite.

Responsable de:
- ceremonias,
- estudiantes,
- QR,
- permisos,
- dashboards.

---

# Frontend

HTML + CSS + JS institucional.

---

# Flujo principal

1. Administrador gestiona ceremonia.
2. Estudiante queda asociado.
3. Sistema genera invitación.
4. QR permite control acceso.
5. Dashboard muestra métricas.