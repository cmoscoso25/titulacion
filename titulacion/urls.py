from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .permisos import (
    acceso_admin,
    acceso_admision,
    acceso_curricular,
    acceso_general,
)

app_name = "titulacion"


urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="titulacion/login.html",
            redirect_authenticated_user=False,
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="titulacion:login",
        ),
        name="logout",
    ),

    path(
        "inicio/",
        acceso_general(views.inicio),
        name="inicio",
    ),

    path(
        "cargar-excel/",
        acceso_admin(views.cargar_excel),
        name="cargar_excel",
    ),

    path(
        "agregar-estudiante/",
        acceso_admin(views.agregar_estudiante),
        name="agregar_estudiante",
    ),

    path(
        "tarjetas/",
        acceso_admin(views.tarjetas_invitacion),
        name="tarjetas",
    ),

    path(
        "entrega-invitaciones/",
        acceso_admision(views.entrega_invitaciones),
        name="entrega_invitaciones",
    ),

    path(
        "entrega-invitaciones/<int:estudiante_id>/marcar/",
        acceso_admision(views.marcar_entrega_invitaciones),
        name="marcar_entrega_invitaciones",
    ),

    path(
        "registro/",
        acceso_admision(views.registro_ingreso),
        name="registro_ingreso",
    ),

    path(
        "validar-codigo/",
        acceso_admision(views.validar_codigo_ingreso),
        name="validar_codigo_ingreso",
    ),

    path(
        "bloques/<int:bloque_id>/abrir/",
        acceso_admision(views.abrir_bloque_ceremonia),
        name="abrir_bloque_ceremonia",
    ),

    path(
        "bloques/<int:bloque_id>/cerrar/",
        acceso_admision(views.cerrar_bloque_ceremonia),
        name="cerrar_bloque_ceremonia",
    ),

    path(
        "bloques/<int:bloque_id>/reprogramar/",
        acceso_admin(views.reprogramar_bloque_ceremonia),
        name="reprogramar_bloque_ceremonia",
    ),

    path(
        "panel-control/",
        acceso_curricular(views.panel_control),
        name="panel_control",
    ),

    path(
        "datos-panel-control/",
        acceso_curricular(views.datos_panel_control),
        name="datos_panel_control",
    ),

    path(
        "planes-por-area/",
        acceso_curricular(views.obtener_planes_por_area),
        name="obtener_planes_por_area",
    ),

    path(
        "planes-por-area-alias/",
        acceso_curricular(views.obtener_planes_por_area),
        name="planes_por_area",
    ),

    path(
        "cambio-ceremonia/",
        acceso_curricular(views.cambio_ceremonia),
        name="cambio_ceremonia",
    ),

    path(
        "api/dashboard/",
        acceso_curricular(views.api_dashboard),
        name="api_dashboard",
    ),

    path(
        "healthcheck/",
        views.healthcheck,
        name="healthcheck",
    ),
]