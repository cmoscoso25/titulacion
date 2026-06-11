from .permisos import es_admin_titulacion, es_admision, es_curricular, es_entrega, es_ingreso, es_reportes


def permisos_titulacion(request):
    u = request.user
    return {
        "perm_admin":      es_admin_titulacion(u),
        "perm_admision":   es_admision(u),
        "perm_curricular": es_curricular(u),
        "perm_entrega":    es_entrega(u),
        "perm_ingreso":    es_ingreso(u),
        "perm_reportes":   es_reportes(u),
    }
