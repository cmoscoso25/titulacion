from django.contrib import admin

from .models import (
    AreaAcademica,
    BloqueCeremonia,
    CambioCeremonia,
    Ceremonia,
    EstudianteTitulado,
    Invitacion,
    PlanEstudio,
    RegistroIngreso,
)


class BloqueCeremoniaInline(admin.TabularInline):
    model = BloqueCeremonia
    extra = 0


class PlanEstudioInline(admin.TabularInline):
    model = PlanEstudio
    extra = 0


class InvitacionInline(admin.TabularInline):
    model = Invitacion
    extra = 0
    readonly_fields = (
        "codigo_qr",
        "imagen_qr",
        "fecha_uso",
    )


@admin.register(Ceremonia)
class CeremoniaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "anio",
        "lugar",
        "activa",
    )

    list_filter = (
        "anio",
        "activa",
    )

    search_fields = (
        "nombre",
        "lugar",
    )

    inlines = [
        BloqueCeremoniaInline,
    ]


@admin.register(BloqueCeremonia)
class BloqueCeremoniaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "ceremonia",
        "fecha",
        "hora_inicio",
        "estado_registro",
    )

    list_filter = (
        "ceremonia",
        "estado_registro",
        "fecha",
    )

    search_fields = (
        "nombre",
        "ceremonia__nombre",
    )


@admin.register(AreaAcademica)
class AreaAcademicaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
    )

    search_fields = (
        "nombre",
    )

    inlines = [
        PlanEstudioInline,
    ]


@admin.register(PlanEstudio)
class PlanEstudioAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "area",
        "institucion",
    )

    list_filter = (
        "area",
        "institucion",
    )

    search_fields = (
        "nombre",
        "area__nombre",
        "institucion",
    )


@admin.register(EstudianteTitulado)
class EstudianteTituladoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "rut",
        "correo",
        "telefono",
        "bloque_ceremonia",
        "plan_estudio",
        "ingreso_confirmado",
        "invitaciones_entregadas",
    )

    list_filter = (
        "bloque_ceremonia",
        "plan_estudio__area",
        "plan_estudio__institucion",
        "ingreso_confirmado",
        "invitaciones_entregadas",
    )

    search_fields = (
        "nombre_completo",
        "rut",
        "correo",
        "telefono",
        "plan_estudio__nombre",
        "plan_estudio__area__nombre",
        "bloque_ceremonia__nombre",
    )

    readonly_fields = (
        "codigo_qr_estudiante",
        "imagen_qr_estudiante",
        "fecha_hora_ingreso",
    )

    inlines = [
        InvitacionInline,
    ]


@admin.register(Invitacion)
class InvitacionAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "numero_invitacion",
        "codigo_qr",
        "usada",
        "fecha_uso",
    )

    list_filter = (
        "usada",
        "numero_invitacion",
        "estudiante__bloque_ceremonia",
        "estudiante__plan_estudio__area",
    )

    search_fields = (
        "estudiante__nombre_completo",
        "estudiante__rut",
        "codigo_qr",
    )

    readonly_fields = (
        "codigo_qr",
        "imagen_qr",
        "fecha_uso",
    )


@admin.register(RegistroIngreso)
class RegistroIngresoAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "invitacion",
        "tipo",
        "resultado",
        "fecha_hora",
        "usuario_registro",
    )

    list_filter = (
        "tipo",
        "resultado",
        "fecha_hora",
    )

    search_fields = (
        "estudiante__nombre_completo",
        "estudiante__rut",
        "invitacion__codigo_qr",
        "observacion",
        "usuario_registro",
    )

    readonly_fields = (
        "fecha_hora",
    )


@admin.register(CambioCeremonia)
class CambioCeremoniaAdmin(admin.ModelAdmin):
    list_display = (
        "estudiante",
        "bloque_origen",
        "bloque_destino",
        "usuario_responsable",
        "fecha_cambio",
    )

    list_filter = (
        "bloque_origen",
        "bloque_destino",
        "fecha_cambio",
    )

    search_fields = (
        "estudiante__nombre_completo",
        "estudiante__rut",
        "bloque_origen__nombre",
        "bloque_destino__nombre",
        "motivo",
        "usuario_responsable",
    )

    readonly_fields = (
        "estudiante",
        "bloque_origen",
        "bloque_destino",
        "motivo",
        "usuario_responsable",
        "fecha_cambio",
        "observacion",
    )