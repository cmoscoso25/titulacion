from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


GRUPO_ADMIN = "ADMIN_TITULACION"
GRUPO_ADMISION = "ADMISION"
GRUPO_CURRICULAR = "CURRICULAR"
GRUPO_ENTREGA = "ENTREGA_INVITACIONES"
GRUPO_INGRESO = "INGRESO"         # Control de acceso QR (DAE)
GRUPO_DACOM = "DACOM"             # Entrega de invitaciones (DACOM)
GRUPO_REPORTES = "SOLO_REPORTES"  # Solo acceso a reportes (ej. Vicerrectoría)


def usuario_en_grupo(usuario, nombre_grupo):
    if not usuario.is_authenticated:
        return False

    return usuario.groups.filter(name=nombre_grupo).exists()


def es_admin_titulacion(usuario):
    return usuario.is_authenticated and (
        usuario.is_superuser or usuario_en_grupo(usuario, GRUPO_ADMIN)
    )


def es_admision(usuario):
    return usuario.is_authenticated and (
        es_admin_titulacion(usuario)
        or usuario_en_grupo(usuario, GRUPO_ADMISION)
    )


def es_curricular(usuario):
    return usuario.is_authenticated and (
        es_admin_titulacion(usuario)
        or usuario_en_grupo(usuario, GRUPO_CURRICULAR)
    )


def redireccion_sin_permiso(request):
    messages.error(
        request,
        "No tienes los privilegios para acceder a este módulo."
    )

    return redirect("titulacion:inicio")


def acceso_admin(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_admin_titulacion(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def acceso_admision(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_admision(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def acceso_curricular(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_curricular(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def es_reportes(usuario):
    return usuario.is_authenticated and (
        es_admin_titulacion(usuario)
        or usuario_en_grupo(usuario, GRUPO_CURRICULAR)
        or usuario_en_grupo(usuario, GRUPO_REPORTES)
    )


def acceso_reportes(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_reportes(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def es_entrega(usuario):
    return usuario.is_authenticated and (
        es_admin_titulacion(usuario)
        or usuario_en_grupo(usuario, GRUPO_ADMISION)
        or usuario_en_grupo(usuario, GRUPO_ENTREGA)
        or usuario_en_grupo(usuario, GRUPO_DACOM)
    )


def acceso_entrega(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_entrega(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def es_ingreso(usuario):
    """Acceso a Registro de Ingreso: ADMIN, ADMISION e INGRESO (DAE)."""
    return usuario.is_authenticated and (
        es_admin_titulacion(usuario)
        or usuario_en_grupo(usuario, GRUPO_ADMISION)
        or usuario_en_grupo(usuario, GRUPO_INGRESO)
    )


def acceso_ingreso(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        if es_ingreso(request.user):
            return view_func(request, *args, **kwargs)

        return redireccion_sin_permiso(request)

    return wrapper


def acceso_general(view_func):

    @wraps(view_func)
    @login_required(login_url="titulacion:login")
    def wrapper(request, *args, **kwargs):

        return view_func(request, *args, **kwargs)

    return wrapper