from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .generador_qr import generar_qr_estudiante, generar_qr_invitacion
from .models import (
    AreaAcademica,
    BloqueCeremonia,
    CambioCeremonia,
    Ceremonia,
    EstudianteTitulado,
    Invitacion,
    PlanEstudio,
    RegistroIngreso,
    generar_codigo_qr_estudiante,
    generar_codigo_qr_invitacion,
)
from .procesador_excel import procesar_excel_titulados


DIRECCION_CEREMONIA = "Avenida Chile 1108"


DIAS_SEMANA = {
    0: "LUNES",
    1: "MARTES",
    2: "MIÉRCOLES",
    3: "JUEVES",
    4: "VIERNES",
    5: "SÁBADO",
    6: "DOMINGO",
}


MESES = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}


def formatear_hora(hora):
    if not hora:
        return ""

    return hora.strftime("%H:%M")


def datos_fecha_bloque(bloque):
    if not bloque or not bloque.fecha:
        return {
            "fecha_es": "",
            "hora_es": "",
            "dia_semana": "",
            "numero_dia": "",
            "mes_es": "",
        }

    fecha = bloque.fecha

    return {
        "fecha_es": f"{fecha.day:02d} de {MESES[fecha.month].lower()} de {fecha.year}",
        "hora_es": formatear_hora(bloque.hora_inicio),
        "dia_semana": DIAS_SEMANA[fecha.weekday()],
        "numero_dia": f"{fecha.day:02d}",
        "mes_es": MESES[fecha.month],
    }


def obtener_area_estudiante(estudiante):
    if estudiante and estudiante.plan_estudio and estudiante.plan_estudio.area:
        return estudiante.plan_estudio.area.nombre

    return ""


def obtener_plan_estudiante(estudiante):
    if estudiante and estudiante.plan_estudio:
        return estudiante.plan_estudio.nombre

    return ""


def obtener_bloque_estudiante(estudiante):
    if estudiante and estudiante.bloque_ceremonia:
        return estudiante.bloque_ceremonia.nombre

    return ""


def obtener_ceremonia_activa():
    return BloqueCeremonia.objects.filter(
        estado_registro="ABIERTA"
    ).select_related(
        "ceremonia"
    ).first()


def bloque_esta_cerrado(bloque):
    if not bloque:
        return False

    return bloque.estado_registro == "CERRADA"


def asegurar_qr_estudiante(estudiante):
    if not estudiante.codigo_qr_estudiante or not estudiante.imagen_qr_estudiante:
        generar_qr_estudiante(estudiante)

    for invitacion in estudiante.invitaciones.all():
        if not invitacion.codigo_qr or not invitacion.imagen_qr:
            generar_qr_invitacion(invitacion)


def regenerar_qr_estudiante_e_invitaciones(estudiante):
    if estudiante.imagen_qr_estudiante:
        estudiante.imagen_qr_estudiante.delete(save=False)

    estudiante.codigo_qr_estudiante = generar_codigo_qr_estudiante()
    estudiante.imagen_qr_estudiante = None
    estudiante.save()

    generar_qr_estudiante(estudiante)

    for invitacion in estudiante.invitaciones.all():
        if invitacion.imagen_qr:
            invitacion.imagen_qr.delete(save=False)

        invitacion.codigo_qr = generar_codigo_qr_invitacion()
        invitacion.imagen_qr = None
        invitacion.usada = False
        invitacion.fecha_uso = None
        invitacion.save()

        generar_qr_invitacion(invitacion)


def aplicar_filtros_estudiantes(queryset, request):
    busqueda = request.GET.get("q", "").strip()
    bloque_id = request.GET.get("bloque", "").strip()
    ceremonia_id = request.GET.get("ceremonia", "").strip()
    area = request.GET.get("area", "").strip()
    plan = request.GET.get("plan", "").strip()
    estado = request.GET.get("estado", "").strip()

    if busqueda:
        queryset = queryset.filter(
            Q(rut__icontains=busqueda) |
            Q(nombre_completo__icontains=busqueda) |
            Q(plan_estudio__nombre__icontains=busqueda) |
            Q(plan_estudio__area__nombre__icontains=busqueda) |
            Q(bloque_ceremonia__nombre__icontains=busqueda)
        )

    if bloque_id:
        queryset = queryset.filter(bloque_ceremonia_id=bloque_id)

    if ceremonia_id:
        queryset = queryset.filter(bloque_ceremonia__ceremonia_id=ceremonia_id)

    if area:
        queryset = queryset.filter(plan_estudio__area__nombre=area)

    if plan:
        queryset = queryset.filter(plan_estudio__nombre=plan)

    if estado == "presentes":
        queryset = queryset.filter(ingreso_confirmado=True)

    if estado == "pendientes":
        queryset = queryset.filter(ingreso_confirmado=False)

    if estado == "atrasados":
        queryset = queryset.filter(
            registros__resultado="ATRASADO"
        ).distinct()

    return queryset


def aplicar_filtros_registros(queryset, request):
    busqueda = request.GET.get("q", "").strip()
    bloque_id = request.GET.get("bloque", "").strip()
    ceremonia_id = request.GET.get("ceremonia", "").strip()
    area = request.GET.get("area", "").strip()
    plan = request.GET.get("plan", "").strip()
    tipo_acceso = request.GET.get("tipo_acceso", "").strip()
    resultado = request.GET.get("resultado", "").strip()

    if busqueda:
        queryset = queryset.filter(
            Q(estudiante__rut__icontains=busqueda) |
            Q(estudiante__nombre_completo__icontains=busqueda) |
            Q(estudiante__plan_estudio__nombre__icontains=busqueda) |
            Q(estudiante__plan_estudio__area__nombre__icontains=busqueda) |
            Q(estudiante__bloque_ceremonia__nombre__icontains=busqueda) |
            Q(observacion__icontains=busqueda)
        )

    if bloque_id:
        queryset = queryset.filter(estudiante__bloque_ceremonia_id=bloque_id)

    if ceremonia_id:
        queryset = queryset.filter(estudiante__bloque_ceremonia__ceremonia_id=ceremonia_id)

    if area:
        queryset = queryset.filter(estudiante__plan_estudio__area__nombre=area)

    if plan:
        queryset = queryset.filter(estudiante__plan_estudio__nombre=plan)

    if tipo_acceso:
        queryset = queryset.filter(tipo=tipo_acceso)

    if resultado:
        queryset = queryset.filter(resultado=resultado)

    return queryset


def inicio(request):
    total_estudiantes = EstudianteTitulado.objects.count()

    estudiantes_presentes = EstudianteTitulado.objects.filter(
        ingreso_confirmado=True
    ).count()

    invitados_presentes = Invitacion.objects.filter(
        usada=True
    ).count()

    total_atrasados = RegistroIngreso.objects.filter(
        resultado="ATRASADO"
    ).count()

    bloques = BloqueCeremonia.objects.select_related(
        "ceremonia"
    ).order_by(
        "fecha",
        "hora_inicio",
        "nombre"
    )

    return render(
        request,
        "titulacion/inicio.html",
        {
            "total_estudiantes": total_estudiantes,
            "estudiantes_presentes": estudiantes_presentes,
            "invitados_presentes": invitados_presentes,
            "total_asistentes": estudiantes_presentes + invitados_presentes,
            "total_atrasados": total_atrasados,
            "bloques": bloques,
        }
    )


def cargar_excel(request):
    resumen = None

    if request.method == "POST":
        archivo_excel = request.FILES.get("archivo_excel")

        if not archivo_excel:
            messages.error(request, "Debes seleccionar un archivo Excel.")
            return redirect("titulacion:cargar_excel")

        try:
            resumen = procesar_excel_titulados(archivo_excel)

            messages.success(
                request,
                "Archivo Excel procesado correctamente."
            )

        except Exception as error:
            messages.error(
                request,
                f"Ocurrió un error al procesar el archivo: {str(error)}"
            )

    estudiantes_preview = EstudianteTitulado.objects.select_related(
        "bloque_ceremonia",
        "bloque_ceremonia__ceremonia",
        "plan_estudio",
        "plan_estudio__area",
    ).order_by(
        "-id"
    )[:30]

    return render(
        request,
        "titulacion/cargar_excel.html",
        {
            "resumen": resumen,
            "estudiantes_preview": estudiantes_preview,
            "estudiantes": estudiantes_preview,
            "total_estudiantes": EstudianteTitulado.objects.count(),
            "total_ceremonias": Ceremonia.objects.count(),
            "total_bloques": BloqueCeremonia.objects.count(),
            "total_areas": AreaAcademica.objects.count(),
            "total_planes": PlanEstudio.objects.count(),
            "total_invitaciones": Invitacion.objects.count(),
            "total_alertas": RegistroIngreso.objects.filter(
                resultado__in=["DENEGADO", "DUPLICADO", "OTRA_CEREMONIA"]
            ).count(),
        }
    )


def registro_ingreso(request):
    bloques = BloqueCeremonia.objects.select_related(
        "ceremonia"
    ).order_by(
        "fecha",
        "hora_inicio",
        "nombre"
    )

    ultimos_registros = RegistroIngreso.objects.select_related(
        "estudiante",
        "invitacion",
        "estudiante__bloque_ceremonia",
        "estudiante__plan_estudio",
        "estudiante__plan_estudio__area",
    ).order_by(
        "-fecha_hora"
    )[:20]

    return render(
        request,
        "titulacion/registro_ingreso.html",
        {
            "bloques": bloques,
            "ultimos_registros": ultimos_registros,
            "bloque_activo": obtener_ceremonia_activa(),
        }
    )


@csrf_exempt
@require_POST
def validar_codigo_ingreso(request):
    codigo = request.POST.get("codigo", "").strip().upper()

    if not codigo:
        return JsonResponse({
            "estado": "error",
            "ok": False,
            "titulo": "Código vacío",
            "mensaje": "No se recibió un código válido.",
        })

    bloque_activo = obtener_ceremonia_activa()

    if not bloque_activo:
        return JsonResponse({
            "estado": "rechazado",
            "ok": False,
            "tipo": "SIN_CEREMONIA_ACTIVA",
            "titulo": "Sin ceremonia activa",
            "mensaje": "Debe abrir una ceremonia antes de registrar ingresos.",
        })

    estudiante = EstudianteTitulado.objects.select_related(
        "bloque_ceremonia",
        "bloque_ceremonia__ceremonia",
        "plan_estudio",
        "plan_estudio__area",
    ).filter(
        codigo_qr_estudiante=codigo
    ).first()

    if estudiante:
        return registrar_ingreso_estudiante(
            estudiante=estudiante,
            bloque_activo=bloque_activo
        )

    invitacion = Invitacion.objects.select_related(
        "estudiante",
        "estudiante__bloque_ceremonia",
        "estudiante__bloque_ceremonia__ceremonia",
        "estudiante__plan_estudio",
        "estudiante__plan_estudio__area",
    ).filter(
        codigo_qr=codigo
    ).first()

    if invitacion:
        return registrar_ingreso_invitado(
            invitacion=invitacion,
            bloque_activo=bloque_activo
        )

    RegistroIngreso.objects.create(
        estudiante=None,
        invitacion=None,
        tipo="INVITADO",
        resultado="DENEGADO",
        observacion=f"Código inválido: {codigo}",
    )

    return JsonResponse({
        "estado": "error",
        "ok": False,
        "tipo": "INVALIDO",
        "titulo": "QR no encontrado",
        "mensaje": "El código escaneado no pertenece a esta ceremonia.",
    })


def registrar_ingreso_estudiante(estudiante, bloque_activo):
    bloque_estudiante = estudiante.bloque_ceremonia

    if bloque_estudiante.id != bloque_activo.id:
        RegistroIngreso.objects.create(
            estudiante=estudiante,
            invitacion=None,
            tipo="ESTUDIANTE",
            resultado="OTRA_CEREMONIA",
            observacion=(
                f"Intento de ingreso en {bloque_activo.nombre}. "
                f"El QR pertenece a {bloque_estudiante.nombre}."
            ),
        )

        return JsonResponse({
            "estado": "rechazado",
            "ok": False,
            "tipo": "OTRA_CEREMONIA",
            "titulo": "QR de otra ceremonia",
            "mensaje": f"Este QR pertenece a {bloque_estudiante.nombre}, no a {bloque_activo.nombre}.",
            "nombre": estudiante.nombre_completo,
            "rut": estudiante.rut,
            "area": obtener_area_estudiante(estudiante),
            "plan": obtener_plan_estudiante(estudiante),
            "bloque": obtener_bloque_estudiante(estudiante),
            "atrasado": False,
        })

    es_atrasado = bloque_esta_cerrado(bloque_estudiante)

    if estudiante.ingreso_confirmado:
        RegistroIngreso.objects.create(
            estudiante=estudiante,
            invitacion=None,
            tipo="ESTUDIANTE",
            resultado="DUPLICADO",
            observacion="Se intentó registrar nuevamente la tarjeta del estudiante.",
        )

        return JsonResponse({
            "estado": "rechazado",
            "ok": False,
            "tipo": "DUPLICADO",
            "titulo": "QR ya utilizado",
            "mensaje": "Este estudiante ya fue registrado anteriormente.",
            "nombre": estudiante.nombre_completo,
            "rut": estudiante.rut,
            "area": obtener_area_estudiante(estudiante),
            "plan": obtener_plan_estudiante(estudiante),
            "bloque": obtener_bloque_estudiante(estudiante),
            "atrasado": False,
        })

    estudiante.ingreso_confirmado = True
    estudiante.fecha_hora_ingreso = timezone.now()
    estudiante.save()

    resultado = "ATRASADO" if es_atrasado else "PERMITIDO"

    RegistroIngreso.objects.create(
        estudiante=estudiante,
        invitacion=None,
        tipo="ESTUDIANTE",
        resultado=resultado,
        observacion=(
            "Ingreso del estudiante registrado como atrasado."
            if es_atrasado
            else "Ingreso del estudiante registrado correctamente."
        ),
    )

    return JsonResponse({
        "estado": "permitido",
        "ok": True,
        "tipo": resultado,
        "titulo": "Ingreso atrasado registrado" if es_atrasado else "Ingreso autorizado",
        "mensaje": (
            "Estudiante registrado después del cierre de ingreso."
            if es_atrasado
            else "Estudiante registrado correctamente."
        ),
        "nombre": estudiante.nombre_completo,
        "rut": estudiante.rut,
        "area": obtener_area_estudiante(estudiante),
        "plan": obtener_plan_estudiante(estudiante),
        "bloque": obtener_bloque_estudiante(estudiante),
        "atrasado": es_atrasado,
    })


def registrar_ingreso_invitado(invitacion, bloque_activo):
    estudiante = invitacion.estudiante
    bloque_estudiante = estudiante.bloque_ceremonia

    if bloque_estudiante.id != bloque_activo.id:
        RegistroIngreso.objects.create(
            estudiante=estudiante,
            invitacion=invitacion,
            tipo="INVITADO",
            resultado="OTRA_CEREMONIA",
            observacion=(
                f"Intento de ingreso en {bloque_activo.nombre}. "
                f"La invitación pertenece a {bloque_estudiante.nombre}."
            ),
        )

        return JsonResponse({
            "estado": "rechazado",
            "ok": False,
            "tipo": "OTRA_CEREMONIA",
            "titulo": "Invitación de otra ceremonia",
            "mensaje": f"Esta invitación pertenece a {bloque_estudiante.nombre}, no a {bloque_activo.nombre}.",
            "nombre": estudiante.nombre_completo,
            "rut": estudiante.rut,
            "area": obtener_area_estudiante(estudiante),
            "plan": obtener_plan_estudiante(estudiante),
            "bloque": obtener_bloque_estudiante(estudiante),
            "invitacion": invitacion.numero_invitacion,
            "atrasado": False,
        })

    es_atrasado = bloque_esta_cerrado(bloque_estudiante)

    if invitacion.usada:
        RegistroIngreso.objects.create(
            estudiante=estudiante,
            invitacion=invitacion,
            tipo="INVITADO",
            resultado="DUPLICADO",
            observacion="Se intentó reutilizar una invitación.",
        )

        return JsonResponse({
            "estado": "rechazado",
            "ok": False,
            "tipo": "DUPLICADO",
            "titulo": "Invitación ya utilizada",
            "mensaje": "Esta invitación ya fue registrada anteriormente.",
            "nombre": estudiante.nombre_completo,
            "rut": estudiante.rut,
            "area": obtener_area_estudiante(estudiante),
            "plan": obtener_plan_estudiante(estudiante),
            "bloque": obtener_bloque_estudiante(estudiante),
            "invitacion": invitacion.numero_invitacion,
            "atrasado": False,
        })

    invitacion.usada = True
    invitacion.fecha_uso = timezone.now()
    invitacion.save()

    resultado = "ATRASADO" if es_atrasado else "PERMITIDO"

    RegistroIngreso.objects.create(
        estudiante=estudiante,
        invitacion=invitacion,
        tipo="INVITADO",
        resultado=resultado,
        observacion=(
            f"Ingreso atrasado registrado para invitación {invitacion.numero_invitacion}."
            if es_atrasado
            else f"Ingreso registrado para invitación {invitacion.numero_invitacion}."
        ),
    )

    return JsonResponse({
        "estado": "permitido",
        "ok": True,
        "tipo": resultado,
        "titulo": "Ingreso atrasado registrado" if es_atrasado else "Ingreso autorizado",
        "mensaje": (
            f"Invitación {invitacion.numero_invitacion} registrada después del cierre de ingreso."
            if es_atrasado
            else f"Invitación {invitacion.numero_invitacion} registrada correctamente."
        ),
        "nombre": estudiante.nombre_completo,
        "rut": estudiante.rut,
        "area": obtener_area_estudiante(estudiante),
        "plan": obtener_plan_estudiante(estudiante),
        "bloque": obtener_bloque_estudiante(estudiante),
        "invitacion": invitacion.numero_invitacion,
        "invitados_presentes": estudiante.invitaciones.filter(usada=True).count(),
        "atrasado": es_atrasado,
    })


def panel_control(request):
    bloques = BloqueCeremonia.objects.select_related(
        "ceremonia"
    ).order_by(
        "fecha",
        "hora_inicio",
        "nombre"
    )

    ceremonias = Ceremonia.objects.all().order_by(
        "-anio",
        "nombre"
    )

    ceremonia_principal = ceremonias.first()

    areas = AreaAcademica.objects.all().order_by(
        "nombre"
    )

    planes = PlanEstudio.objects.select_related(
        "area"
    ).all().order_by(
        "nombre"
    )

    return render(
        request,
        "titulacion/panel_control.html",
        {
            "bloques": bloques,
            "ceremonias": ceremonias,
            "ceremonia_principal": ceremonia_principal,
            "areas": areas,
            "planes": planes,
        }
    )


def datos_panel_control(request):
    estudiantes_base = EstudianteTitulado.objects.select_related(
        "bloque_ceremonia",
        "bloque_ceremonia__ceremonia",
        "plan_estudio",
        "plan_estudio__area",
    ).prefetch_related(
        "invitaciones"
    ).all()

    estudiantes_filtrados = aplicar_filtros_estudiantes(
        estudiantes_base,
        request
    )

    registros_base = RegistroIngreso.objects.select_related(
        "estudiante",
        "invitacion",
        "estudiante__bloque_ceremonia",
        "estudiante__bloque_ceremonia__ceremonia",
        "estudiante__plan_estudio",
        "estudiante__plan_estudio__area",
    ).all()

    registros_filtrados = aplicar_filtros_registros(
        registros_base,
        request
    )

    estudiantes_totales = estudiantes_filtrados.count()

    estudiantes_presentes = estudiantes_filtrados.filter(
        ingreso_confirmado=True
    ).count()

    estudiantes_pendientes = estudiantes_filtrados.filter(
        ingreso_confirmado=False
    ).count()

    estudiantes_atrasados = RegistroIngreso.objects.filter(
        estudiante__in=estudiantes_filtrados,
        tipo="ESTUDIANTE",
        resultado="ATRASADO",
    ).values(
        "estudiante_id"
    ).distinct().count()

    invitaciones_filtradas = Invitacion.objects.select_related(
        "estudiante",
        "estudiante__bloque_ceremonia",
        "estudiante__plan_estudio",
        "estudiante__plan_estudio__area",
    ).filter(
        estudiante__in=estudiantes_filtrados
    )

    invitados_presentes = invitaciones_filtradas.filter(
        usada=True
    ).count()

    invitados_atrasados = RegistroIngreso.objects.filter(
        estudiante__in=estudiantes_filtrados,
        tipo="INVITADO",
        resultado="ATRASADO",
    ).count()

    invitaciones_totales = invitaciones_filtradas.count()
    invitaciones_pendientes = invitaciones_totales - invitados_presentes

    total_asistentes = estudiantes_presentes + invitados_presentes
    total_atrasados = estudiantes_atrasados + invitados_atrasados

    alertas_qr = registros_filtrados.filter(
        resultado__in=["DENEGADO", "DUPLICADO", "OTRA_CEREMONIA"]
    ).count()

    porcentaje_estudiantes = 0

    if estudiantes_totales > 0:
        porcentaje_estudiantes = round(
            (estudiantes_presentes / estudiantes_totales) * 100,
            1
        )

    porcentaje_invitaciones = 0

    if invitaciones_totales > 0:
        porcentaje_invitaciones = round(
            (invitados_presentes / invitaciones_totales) * 100,
            1
        )

    avance_por_plan = []

    planes = estudiantes_filtrados.values(
        "plan_estudio__nombre"
    ).annotate(
        total=Count("id"),
        presentes=Count("id", filter=Q(ingreso_confirmado=True)),
    ).order_by(
        "plan_estudio__nombre"
    )

    for item in planes:
        total = item["total"]
        presentes = item["presentes"]

        porcentaje = 0

        if total > 0:
            porcentaje = round((presentes / total) * 100, 1)

        atrasados_plan = RegistroIngreso.objects.filter(
            estudiante__in=estudiantes_filtrados.filter(
                plan_estudio__nombre=item["plan_estudio__nombre"]
            ),
            resultado="ATRASADO",
        ).count()

        avance_por_plan.append({
            "plan": item["plan_estudio__nombre"] or "Sin plan informado",
            "total": total,
            "presentes": presentes,
            "pendientes": total - presentes,
            "atrasados": atrasados_plan,
            "porcentaje": porcentaje,
        })

    seguimiento_estudiantes = []

    for estudiante in estudiantes_filtrados.order_by(
        "bloque_ceremonia__fecha",
        "bloque_ceremonia__hora_inicio",
        "nombre_completo"
    )[:300]:
        invitaciones = list(
            estudiante.invitaciones.all().order_by("numero_invitacion")
        )

        invitacion_1 = invitaciones[0] if len(invitaciones) >= 1 else None
        invitacion_2 = invitaciones[1] if len(invitaciones) >= 2 else None

        estudiante_atrasado = RegistroIngreso.objects.filter(
            estudiante=estudiante,
            tipo="ESTUDIANTE",
            resultado="ATRASADO",
        ).exists()

        invitacion_1_atrasada = False
        invitacion_2_atrasada = False

        if invitacion_1:
            invitacion_1_atrasada = RegistroIngreso.objects.filter(
                invitacion=invitacion_1,
                resultado="ATRASADO",
            ).exists()

        if invitacion_2:
            invitacion_2_atrasada = RegistroIngreso.objects.filter(
                invitacion=invitacion_2,
                resultado="ATRASADO",
            ).exists()

        if estudiante.ingreso_confirmado:
            estado_texto = "Presente"
            estado_clase = "presente"
        elif estudiante_atrasado:
            estado_texto = "Atrasado"
            estado_clase = "atrasado"
        else:
            estado_texto = "Pendiente"
            estado_clase = "pendiente"

        seguimiento_estudiantes.append({
            "nombre": estudiante.nombre_completo,
            "rut": estudiante.rut,
            "area": obtener_area_estudiante(estudiante),
            "plan": obtener_plan_estudiante(estudiante),
            "bloque": obtener_bloque_estudiante(estudiante),
            "estudiante_presente": estudiante.ingreso_confirmado,
            "estudiante_atrasado": estudiante_atrasado,
            "estado_texto": estado_texto,
            "estado_clase": estado_clase,
            "invitacion_1": invitacion_1.usada if invitacion_1 else False,
            "invitacion_1_atrasada": invitacion_1_atrasada,
            "invitacion_2": invitacion_2.usada if invitacion_2 else False,
            "invitacion_2_atrasada": invitacion_2_atrasada,
            "invitaciones_gestionadas": estudiante.invitaciones_entregadas,
        })

    ultimos_registros = registros_filtrados.order_by("-fecha_hora")[:30]

    registros = []

    for registro in ultimos_registros:
        estudiante = registro.estudiante

        registros.append({
            "nombre": estudiante.nombre_completo if estudiante else "Sin estudiante",
            "rut": estudiante.rut if estudiante else "-",
            "tipo_acceso": registro.tipo,
            "resultado": registro.get_resultado_display(),
            "codigo_resultado": registro.resultado,
            "ingreso_atrasado": registro.resultado == "ATRASADO",
            "hora": registro.fecha_hora.strftime("%H:%M:%S"),
            "area": obtener_area_estudiante(estudiante) if estudiante else "-",
            "plan": obtener_plan_estudiante(estudiante) if estudiante else "-",
            "bloque": obtener_bloque_estudiante(estudiante) if estudiante else "-",
        })

    registros_atrasados = registros_filtrados.filter(
        resultado="ATRASADO"
    ).order_by(
        "-fecha_hora"
    )[:80]

    atrasados = []

    for registro in registros_atrasados:
        estudiante = registro.estudiante

        atrasados.append({
            "nombre": estudiante.nombre_completo if estudiante else "Sin estudiante",
            "rut": estudiante.rut if estudiante else "-",
            "tipo_acceso": registro.tipo,
            "resultado": registro.get_resultado_display(),
            "hora": registro.fecha_hora.strftime("%H:%M:%S"),
            "area": obtener_area_estudiante(estudiante) if estudiante else "-",
            "plan": obtener_plan_estudiante(estudiante) if estudiante else "-",
            "bloque": obtener_bloque_estudiante(estudiante) if estudiante else "-",
            "ceremonia": (
                estudiante.bloque_ceremonia.ceremonia.nombre
                if estudiante
                and estudiante.bloque_ceremonia
                and estudiante.bloque_ceremonia.ceremonia
                else "-"
            ),
        })

    return JsonResponse({
        "kpis": {
            "estudiantes_totales": estudiantes_totales,
            "estudiantes_presentes": estudiantes_presentes,
            "estudiantes_pendientes": estudiantes_pendientes,
            "estudiantes_atrasados": estudiantes_atrasados,
            "invitados_presentes": invitados_presentes,
            "invitados_atrasados": invitados_atrasados,
            "invitaciones_totales": invitaciones_totales,
            "invitaciones_pendientes": invitaciones_pendientes,
            "total_asistentes": total_asistentes,
            "total_atrasados": total_atrasados,
            "alertas_qr": alertas_qr,
            "porcentaje_estudiantes": porcentaje_estudiantes,
            "porcentaje_invitaciones": porcentaje_invitaciones,
        },
        "avance_por_plan": avance_por_plan,
        "seguimiento_estudiantes": seguimiento_estudiantes,
        "ultimos_registros": registros,
        "ingresos_atrasados": atrasados,
        "busqueda": request.GET.get("q", "").strip(),
    })


def obtener_planes_por_area(request):
    area = request.GET.get("area", "").strip()

    planes = PlanEstudio.objects.select_related(
        "area"
    ).all()

    if area:
        planes = planes.filter(area__nombre=area)

    planes = planes.values_list(
        "nombre",
        flat=True
    ).distinct().order_by("nombre")

    return JsonResponse({
        "planes": list(planes)
    })


def tarjetas_invitacion(request):
    busqueda = request.GET.get("q", "").strip()
    bloque_id = request.GET.get("bloque", "").strip()
    ceremonia_id = request.GET.get("ceremonia", "").strip()
    area = request.GET.get("area", "").strip()
    tipo = request.GET.get("tipo", "").strip()

    estudiantes = EstudianteTitulado.objects.select_related(
        "bloque_ceremonia",
        "bloque_ceremonia__ceremonia",
        "plan_estudio",
        "plan_estudio__area",
    ).prefetch_related(
        "invitaciones"
    ).all().order_by(
        "nombre_completo",
        "bloque_ceremonia__fecha",
        "bloque_ceremonia__hora_inicio",
    )

    if busqueda:
        estudiantes = estudiantes.filter(
            Q(rut__icontains=busqueda) |
            Q(nombre_completo__icontains=busqueda)
        )

    if bloque_id:
        estudiantes = estudiantes.filter(bloque_ceremonia_id=bloque_id)

    if ceremonia_id:
        estudiantes = estudiantes.filter(bloque_ceremonia__ceremonia_id=ceremonia_id)

    if area:
        estudiantes = estudiantes.filter(plan_estudio__area__nombre=area)

    tarjetas = []

    for estudiante in estudiantes:
        asegurar_qr_estudiante(estudiante)

        datos_fecha = datos_fecha_bloque(estudiante.bloque_ceremonia)

        if tipo in ["", "ESTUDIANTE"]:
            tarjetas.append({
                "tipo": "ESTUDIANTE",
                "numero_invitacion": "",
                "nombre": estudiante.nombre_completo,
                "rut": estudiante.rut,
                "area": obtener_area_estudiante(estudiante),
                "plan": obtener_plan_estudiante(estudiante),
                "bloque": obtener_bloque_estudiante(estudiante),
                "dia_semana": datos_fecha["dia_semana"],
                "numero_dia": datos_fecha["numero_dia"],
                "mes": datos_fecha["mes_es"],
                "hora": datos_fecha["hora_es"],
                "lugar": DIRECCION_CEREMONIA,
                "qr": estudiante.imagen_qr_estudiante.url if estudiante.imagen_qr_estudiante else "",
                "codigo": estudiante.codigo_qr_estudiante,
                "utilizado": estudiante.ingreso_confirmado,
            })

        if tipo in ["", "INVITACION"]:
            for invitacion in estudiante.invitaciones.all().order_by("numero_invitacion"):
                tarjetas.append({
                    "tipo": "INVITACION",
                    "numero_invitacion": invitacion.numero_invitacion,
                    "nombre": estudiante.nombre_completo,
                    "rut": estudiante.rut,
                    "area": obtener_area_estudiante(estudiante),
                    "plan": obtener_plan_estudiante(estudiante),
                    "bloque": obtener_bloque_estudiante(estudiante),
                    "dia_semana": datos_fecha["dia_semana"],
                    "numero_dia": datos_fecha["numero_dia"],
                    "mes": datos_fecha["mes_es"],
                    "hora": datos_fecha["hora_es"],
                    "lugar": DIRECCION_CEREMONIA,
                    "qr": invitacion.imagen_qr.url if invitacion.imagen_qr else "",
                    "codigo": invitacion.codigo_qr,
                    "utilizado": invitacion.usada,
                })

    return render(
        request,
        "titulacion/tarjetas.html",
        {
            "tarjetas": tarjetas,
            "total_tarjetas": len(tarjetas),
            "bloques": BloqueCeremonia.objects.all().order_by("fecha", "hora_inicio"),
            "ceremonias": Ceremonia.objects.all().order_by("-anio", "nombre"),
            "areas": AreaAcademica.objects.all().order_by("nombre"),
            "busqueda": busqueda,
            "bloque_seleccionado": bloque_id,
            "ceremonia_seleccionada": ceremonia_id,
            "area_seleccionada": area,
            "tipo_seleccionado": tipo,
        }
    )


def entrega_invitaciones(request):
    busqueda = request.GET.get("q", "").strip()

    estudiantes = EstudianteTitulado.objects.none()
    resultados = []

    if busqueda:
        estudiantes = EstudianteTitulado.objects.select_related(
            "bloque_ceremonia",
            "bloque_ceremonia__ceremonia",
            "plan_estudio",
            "plan_estudio__area",
        ).prefetch_related(
            "invitaciones"
        ).filter(
            Q(rut__icontains=busqueda) |
            Q(nombre_completo__icontains=busqueda) |
            Q(plan_estudio__nombre__icontains=busqueda)
        ).order_by(
            "nombre_completo",
            "bloque_ceremonia__fecha",
            "bloque_ceremonia__hora_inicio",
            "plan_estudio__nombre",
        )

        for estudiante in estudiantes:
            asegurar_qr_estudiante(estudiante)

            datos_fecha = datos_fecha_bloque(estudiante.bloque_ceremonia)

            resultados.append({
                "estudiante": estudiante,
                "invitaciones": estudiante.invitaciones.all().order_by("numero_invitacion"),
                "fecha_es": datos_fecha["fecha_es"],
                "hora_es": datos_fecha["hora_es"],
                "dia_semana": datos_fecha["dia_semana"],
                "numero_dia": datos_fecha["numero_dia"],
                "mes_es": datos_fecha["mes_es"],
                "direccion_ceremonia": DIRECCION_CEREMONIA,
            })

    return render(
        request,
        "titulacion/entrega_invitaciones.html",
        {
            "busqueda": busqueda,
            "resultados": resultados,
            "total_resultados": len(resultados),
            "direccion_ceremonia": DIRECCION_CEREMONIA,
        }
    )


@require_POST
def marcar_entrega_invitaciones(request, estudiante_id):
    estudiante = get_object_or_404(
        EstudianteTitulado,
        id=estudiante_id
    )

    estudiante.invitaciones_entregadas = True
    estudiante.save()

    messages.success(
        request,
        f"Invitaciones de {estudiante.nombre_completo} para {estudiante.bloque_ceremonia.nombre} marcadas como gestionadas."
    )

    return redirect(
        f"/entrega-invitaciones/?q={estudiante.rut}"
    )


def cambio_ceremonia(request):
    busqueda = request.GET.get("q", "").strip()
    estudiante_id = request.GET.get("estudiante", "").strip()

    estudiantes = EstudianteTitulado.objects.none()
    estudiante_seleccionado = None

    bloques_destino = BloqueCeremonia.objects.select_related(
        "ceremonia"
    ).order_by(
        "fecha",
        "hora_inicio",
        "nombre"
    )

    historial = CambioCeremonia.objects.select_related(
        "estudiante",
        "bloque_origen",
        "bloque_destino",
    ).order_by(
        "-fecha_cambio"
    )[:25]

    if busqueda:
        estudiantes = EstudianteTitulado.objects.select_related(
            "bloque_ceremonia",
            "bloque_ceremonia__ceremonia",
            "plan_estudio",
            "plan_estudio__area",
        ).prefetch_related(
            "invitaciones"
        ).filter(
            Q(rut__icontains=busqueda) |
            Q(nombre_completo__icontains=busqueda) |
            Q(plan_estudio__nombre__icontains=busqueda)
        ).order_by(
            "nombre_completo",
            "bloque_ceremonia__fecha",
            "bloque_ceremonia__hora_inicio",
        )

    if estudiante_id:
        estudiante_seleccionado = get_object_or_404(
            EstudianteTitulado.objects.select_related(
                "bloque_ceremonia",
                "bloque_ceremonia__ceremonia",
                "plan_estudio",
                "plan_estudio__area",
            ).prefetch_related(
                "invitaciones"
            ),
            id=estudiante_id
        )

    if request.method == "POST":
        estudiante_id_post = request.POST.get("estudiante_id", "").strip()
        bloque_destino_id = request.POST.get("bloque_destino", "").strip()
        motivo = request.POST.get("motivo", "").strip()

        estudiante = get_object_or_404(
            EstudianteTitulado.objects.select_related(
                "bloque_ceremonia",
                "plan_estudio",
            ).prefetch_related(
                "invitaciones"
            ),
            id=estudiante_id_post
        )

        bloque_destino = get_object_or_404(
            BloqueCeremonia,
            id=bloque_destino_id
        )

        bloque_origen = estudiante.bloque_ceremonia

        if not motivo:
            messages.error(
                request,
                "Debes ingresar el motivo institucional del cambio."
            )
            return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

        if bloque_destino.id == bloque_origen.id:
            messages.error(
                request,
                "El estudiante ya pertenece a la ceremonia seleccionada."
            )
            return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

        if estudiante.ingreso_confirmado:
            messages.error(
                request,
                "No se puede cambiar de ceremonia porque el estudiante ya registra ingreso."
            )
            return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

        if estudiante.invitaciones.filter(usada=True).exists():
            messages.error(
                request,
                "No se puede cambiar de ceremonia porque una o más invitaciones ya fueron utilizadas."
            )
            return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

        duplicado = EstudianteTitulado.objects.filter(
            rut=estudiante.rut,
            bloque_ceremonia=bloque_destino,
            plan_estudio=estudiante.plan_estudio,
        ).exclude(
            id=estudiante.id
        ).exists()

        if duplicado:
            messages.error(
                request,
                "No se puede realizar el cambio porque ya existe este RUT en el bloque destino con el mismo plan de estudio."
            )
            return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

        usuario_responsable = None

        if request.user.is_authenticated:
            usuario_responsable = request.user.get_username()

        with transaction.atomic():
            CambioCeremonia.objects.create(
                estudiante=estudiante,
                bloque_origen=bloque_origen,
                bloque_destino=bloque_destino,
                motivo=motivo,
                usuario_responsable=usuario_responsable,
                observacion=(
                    "Cambio de ceremonia realizado desde módulo institucional. "
                    "Se regeneraron QR de estudiante e invitaciones."
                ),
            )

            RegistroIngreso.objects.create(
                estudiante=estudiante,
                invitacion=None,
                tipo="ESTUDIANTE",
                resultado="OTRA_CEREMONIA",
                observacion=(
                    f"CAMBIO ADMINISTRATIVO DE CEREMONIA: "
                    f"{bloque_origen.nombre} → {bloque_destino.nombre}. "
                    f"Motivo: {motivo}"
                ),
                usuario_registro=usuario_responsable,
            )

            estudiante.bloque_ceremonia = bloque_destino
            estudiante.invitaciones_entregadas = False
            estudiante.save()

            regenerar_qr_estudiante_e_invitaciones(estudiante)

        messages.success(
            request,
            f"El estudiante {estudiante.nombre_completo} fue cambiado correctamente a {bloque_destino.nombre}. Se regeneraron sus QR."
        )

        return redirect(f"{request.path}?q={estudiante.rut}&estudiante={estudiante.id}")

    return render(
        request,
        "titulacion/cambio_ceremonia.html",
        {
            "busqueda": busqueda,
            "estudiantes": estudiantes,
            "estudiante_seleccionado": estudiante_seleccionado,
            "bloques_destino": bloques_destino,
            "historial": historial,
        }
    )


@require_POST
def abrir_bloque_ceremonia(request, bloque_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=bloque_id
    )

    bloque.abrir()

    messages.success(
        request,
        f"La ceremonia {bloque.nombre} fue abierta correctamente."
    )

    return redirect("titulacion:registro_ingreso")


@require_POST
def cerrar_bloque_ceremonia(request, bloque_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=bloque_id
    )

    bloque.cerrar()

    messages.success(
        request,
        f"La ceremonia {bloque.nombre} fue cerrada correctamente. Los próximos ingresos quedarán como atrasados."
    )

    return redirect("titulacion:registro_ingreso")


@require_POST
def reprogramar_bloque_ceremonia(request, bloque_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=bloque_id
    )

    bloque.reprogramar()

    messages.success(
        request,
        f"La ceremonia {bloque.nombre} volvió al estado programada."
    )

    return redirect("titulacion:registro_ingreso")


@require_POST
def cerrar_registro_ceremonia(request, ceremonia_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=ceremonia_id
    )

    bloque.cerrar()

    messages.success(
        request,
        f"Registro de ingreso cerrado para {bloque.nombre}."
    )

    return redirect("titulacion:registro_ingreso")


@require_POST
def reabrir_registro_ceremonia(request, ceremonia_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=ceremonia_id
    )

    bloque.abrir()

    messages.success(
        request,
        f"Registro de ingreso reabierto para {bloque.nombre}."
    )

    return redirect("titulacion:registro_ingreso")


@require_POST
def cerrar_registro_bloque(request, bloque_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=bloque_id
    )

    bloque.cerrar()

    messages.success(
        request,
        f"Registro cerrado para {bloque.nombre}."
    )

    return redirect("titulacion:panel_control")


@require_POST
def reabrir_registro_bloque(request, bloque_id):
    bloque = get_object_or_404(
        BloqueCeremonia,
        id=bloque_id
    )

    bloque.abrir()

    messages.success(
        request,
        f"Registro reabierto para {bloque.nombre}."
    )

    return redirect("titulacion:panel_control")


def descargar_invitacion_pdf(request, tipo, estudiante_id):
    return redirect(
        f"/entrega-invitaciones/?q={estudiante_id}"
    )


def api_dashboard(request):
    estudiantes = EstudianteTitulado.objects.all()

    return JsonResponse({
        "total_estudiantes": estudiantes.count(),
        "presentes": estudiantes.filter(ingreso_confirmado=True).count(),
        "pendientes": estudiantes.filter(ingreso_confirmado=False).count(),
        "atrasados": RegistroIngreso.objects.filter(resultado="ATRASADO").count(),
        "invitados_presentes": Invitacion.objects.filter(usada=True).count(),
        "invitados_atrasados": RegistroIngreso.objects.filter(
            tipo="INVITADO",
            resultado="ATRASADO"
        ).count(),
        "timestamp": timezone.now().strftime("%H:%M:%S"),
    })


def healthcheck(request):
    return HttpResponse("OK")