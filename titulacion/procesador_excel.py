import re
from datetime import date, time

import pandas as pd
from django.db import transaction

from .generador_qr import generar_qr_estudiante, generar_qr_invitacion
from .models import (
    AreaAcademica,
    BloqueCeremonia,
    Ceremonia,
    EstudianteTitulado,
    Invitacion,
    PlanEstudio,
)


CEREMONIA_PRINCIPAL = "Ceremonia de Titulación 2026"
ANIO_CEREMONIA = 2026
LUGAR_CEREMONIA = "Avenida Chile 1108"


CONFIGURACION_BLOQUES = {
    "Ceremonia IP - UTC": {
        "nombre": "IP / UTC",
        "fecha": date(2026, 6, 11),
        "hora_inicio": time(10, 0),
    },
    "CFT Ceremonia 1": {
        "nombre": "CFT Ceremonia 1",
        "fecha": date(2026, 6, 10),
        "hora_inicio": time(10, 0),
    },
    "CFT Ceremonia 2": {
        "nombre": "CFT Ceremonia 2",
        "fecha": date(2026, 6, 10),
        "hora_inicio": time(16, 0),
    },
}


COLUMNAS_POSIBLES = {
    "rut": ["rut alumno", "rut", "run", "run alumno", "rut estudiante"],
    "nombre": ["nombre alumno", "alumno", "nombre estudiante", "nombre completo", "nombre"],
    "programa": ["programa estudio", "programa", "plan estudio", "plan de estudio", "carrera"],
    "area": ["área académica", "area academica", "área", "area"],
    "jornada": ["jornada"],
    "institucion": ["institución", "institucion", "tipo institución", "tipo institucion"],
    "correo": ["email alumno", "e-mail alumno", "correo alumno", "correo", "email", "mail"],
    "telefono": ["celular alumno", "telefono alumno", "teléfono alumno", "celular", "telefono", "teléfono"],
}


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = re.sub(r"\s+", " ", texto)
    return texto


def normalizar_columna(nombre):
    nombre = str(nombre).strip().lower()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }

    for origen, destino in reemplazos.items():
        nombre = nombre.replace(origen, destino)

    nombre = re.sub(r"\s+", " ", nombre)
    return nombre


def limpiar_rut(valor):
    if pd.isna(valor):
        return ""

    rut = str(valor).strip().upper()
    rut = rut.replace(".", "")
    rut = rut.replace(" ", "")

    if rut.endswith(".0"):
        rut = rut[:-2]

    return rut


def rut_valido(rut):
    if not rut:
        return False

    rut_limpio = rut.upper().replace(".", "").replace(" ", "")
    rut_sin_guion = rut_limpio.replace("-", "")

    invalidos = [
        "RUT",
        "RUTALUMNO",
        "RUN",
        "RUNALUMNO",
        "RUTESTUDIANTE",
        "NAN",
        "NONE",
    ]

    if rut_sin_guion in invalidos:
        return False

    patron = r"^[0-9]{7,8}-?[0-9K]$"
    return bool(re.match(patron, rut_limpio))


def limpiar_correo(valor):
    if pd.isna(valor):
        return ""

    correo = str(valor).strip().lower()

    if correo in ["nan", "none", "-", "sin correo", "no registra", "no informado"]:
        return ""

    return correo


def limpiar_telefono(valor):
    if pd.isna(valor):
        return ""

    telefono = str(valor).strip()

    if telefono.endswith(".0"):
        telefono = telefono[:-2]

    telefono = telefono.replace(" ", "")

    if telefono.lower() in ["nan", "none", "-", "sin telefono", "sin teléfono", "no registra", "no informado"]:
        return ""

    return telefono


def obtener_columna(df, tipo):
    columnas_normalizadas = {
        normalizar_columna(columna): columna
        for columna in df.columns
    }

    for nombre_posible in COLUMNAS_POSIBLES[tipo]:
        nombre_normalizado = normalizar_columna(nombre_posible)

        if nombre_normalizado in columnas_normalizadas:
            return columnas_normalizadas[nombre_normalizado]

    for columna_normalizada, columna_original in columnas_normalizadas.items():
        for nombre_posible in COLUMNAS_POSIBLES[tipo]:
            nombre_normalizado = normalizar_columna(nombre_posible)

            if nombre_normalizado in columna_normalizada:
                return columna_original

    return None


def detectar_bloque_por_hoja(nombre_hoja):
    nombre_limpio = normalizar_texto(nombre_hoja).lower()

    if "ip" in nombre_limpio or "utc" in nombre_limpio:
        return CONFIGURACION_BLOQUES["Ceremonia IP - UTC"]

    if "cft" in nombre_limpio and "1" in nombre_limpio:
        return CONFIGURACION_BLOQUES["CFT Ceremonia 1"]

    if "cft" in nombre_limpio and "2" in nombre_limpio:
        return CONFIGURACION_BLOQUES["CFT Ceremonia 2"]

    return None


def crear_ceremonia_principal():
    ceremonia, _ = Ceremonia.objects.get_or_create(
        nombre=CEREMONIA_PRINCIPAL,
        anio=ANIO_CEREMONIA,
        defaults={
            "lugar": LUGAR_CEREMONIA,
            "activa": True,
        }
    )

    ceremonia.lugar = LUGAR_CEREMONIA
    ceremonia.activa = True
    ceremonia.save()

    return ceremonia


def crear_bloque(ceremonia, config_bloque):
    bloque, creado = BloqueCeremonia.objects.get_or_create(
        ceremonia=ceremonia,
        nombre=config_bloque["nombre"],
        defaults={
            "fecha": config_bloque["fecha"],
            "hora_inicio": config_bloque["hora_inicio"],
            "estado_registro": "PROGRAMADA",
        }
    )

    bloque.fecha = config_bloque["fecha"]
    bloque.hora_inicio = config_bloque["hora_inicio"]

    if creado:
        bloque.estado_registro = "PROGRAMADA"

    bloque.save()
    return bloque


def asegurar_qr_estudiante_importacion(estudiante):
    if not estudiante.imagen_qr_estudiante:
        generar_qr_estudiante(estudiante)


def crear_invitaciones_para_estudiante(estudiante):
    invitaciones_creadas = 0

    for numero in [1, 2]:
        invitacion, creada = Invitacion.objects.get_or_create(
            estudiante=estudiante,
            numero_invitacion=numero
        )

        if creada:
            invitaciones_creadas += 1

        if not invitacion.imagen_qr:
            generar_qr_invitacion(invitacion)

    return invitaciones_creadas


def procesar_hoja(df, nombre_hoja, ceremonia):
    config_bloque = detectar_bloque_por_hoja(nombre_hoja)

    if not config_bloque:
        return {
            "hoja": nombre_hoja,
            "procesada": False,
            "motivo": "La hoja no corresponde a IP/UTC, CFT Ceremonia 1 o CFT Ceremonia 2.",
            "estudiantes_creados": 0,
            "estudiantes_actualizados": 0,
            "filas_omitidas": 0,
            "invitaciones_creadas": 0,
            "duplicados_misma_ceremonia_plan": 0,
        }

    bloque = crear_bloque(ceremonia, config_bloque)

    columna_rut = obtener_columna(df, "rut")
    columna_nombre = obtener_columna(df, "nombre")
    columna_programa = obtener_columna(df, "programa")
    columna_area = obtener_columna(df, "area")
    columna_jornada = obtener_columna(df, "jornada")
    columna_institucion = obtener_columna(df, "institucion")
    columna_correo = obtener_columna(df, "correo")
    columna_telefono = obtener_columna(df, "telefono")

    if not all([columna_rut, columna_nombre, columna_programa, columna_area]):
        return {
            "hoja": nombre_hoja,
            "procesada": False,
            "motivo": "Faltan columnas obligatorias: RUT, Nombre, Programa o Área.",
            "estudiantes_creados": 0,
            "estudiantes_actualizados": 0,
            "filas_omitidas": len(df),
            "invitaciones_creadas": 0,
            "duplicados_misma_ceremonia_plan": 0,
        }

    estudiantes_creados = 0
    estudiantes_actualizados = 0
    filas_omitidas = 0
    invitaciones_creadas = 0
    duplicados_misma_ceremonia_plan = 0

    combinaciones_procesadas = set()

    for _, fila in df.iterrows():
        rut = limpiar_rut(fila.get(columna_rut))

        if not rut_valido(rut):
            filas_omitidas += 1
            continue

        nombre = normalizar_texto(fila.get(columna_nombre))
        programa = normalizar_texto(fila.get(columna_programa))
        area_nombre = normalizar_texto(fila.get(columna_area))

        if not nombre or not programa or not area_nombre:
            filas_omitidas += 1
            continue

        jornada = normalizar_texto(fila.get(columna_jornada)) if columna_jornada else ""
        institucion = normalizar_texto(fila.get(columna_institucion)) if columna_institucion else ""

        if not institucion:
            institucion = bloque.nombre

        correo = limpiar_correo(fila.get(columna_correo)) if columna_correo else ""
        telefono = limpiar_telefono(fila.get(columna_telefono)) if columna_telefono else ""

        area, _ = AreaAcademica.objects.get_or_create(nombre=area_nombre)

        plan, _ = PlanEstudio.objects.get_or_create(
            area=area,
            nombre=programa,
            institucion=institucion,
        )

        clave_unica_excel = (rut, bloque.id, plan.id)

        if clave_unica_excel in combinaciones_procesadas:
            duplicados_misma_ceremonia_plan += 1
            filas_omitidas += 1
            continue

        combinaciones_procesadas.add(clave_unica_excel)

        estudiante, creado = EstudianteTitulado.objects.get_or_create(
            rut=rut,
            bloque_ceremonia=bloque,
            plan_estudio=plan,
            defaults={
                "nombre_completo": nombre,
                "correo": correo,
                "telefono": telefono,
                "jornada": jornada,
            }
        )

        if creado:
            estudiantes_creados += 1
        else:
            estudiante.nombre_completo = nombre
            estudiante.correo = correo
            estudiante.telefono = telefono
            estudiante.jornada = jornada
            estudiante.save()
            estudiantes_actualizados += 1

        asegurar_qr_estudiante_importacion(estudiante)
        invitaciones_creadas += crear_invitaciones_para_estudiante(estudiante)

    return {
        "hoja": nombre_hoja,
        "procesada": True,
        "bloque": bloque.nombre,
        "fecha": bloque.fecha.strftime("%d-%m-%Y"),
        "hora": bloque.hora_inicio.strftime("%H:%M"),
        "estudiantes_creados": estudiantes_creados,
        "estudiantes_actualizados": estudiantes_actualizados,
        "filas_omitidas": filas_omitidas,
        "invitaciones_creadas": invitaciones_creadas,
        "duplicados_misma_ceremonia_plan": duplicados_misma_ceremonia_plan,
    }


@transaction.atomic
def procesar_excel_titulados(archivo_excel):
    libro = pd.ExcelFile(archivo_excel)
    ceremonia = crear_ceremonia_principal()

    resumen_hojas = []

    total_estudiantes_creados = 0
    total_estudiantes_actualizados = 0
    total_filas_omitidas = 0
    total_invitaciones_creadas = 0
    total_duplicados_misma_ceremonia_plan = 0

    for nombre_hoja in libro.sheet_names:
        df = pd.read_excel(
            libro,
            sheet_name=nombre_hoja,
            dtype=str
        )

        df = df.dropna(how="all")

        resultado = procesar_hoja(
            df=df,
            nombre_hoja=nombre_hoja,
            ceremonia=ceremonia
        )

        resumen_hojas.append(resultado)

        total_estudiantes_creados += resultado.get("estudiantes_creados", 0)
        total_estudiantes_actualizados += resultado.get("estudiantes_actualizados", 0)
        total_filas_omitidas += resultado.get("filas_omitidas", 0)
        total_invitaciones_creadas += resultado.get("invitaciones_creadas", 0)
        total_duplicados_misma_ceremonia_plan += resultado.get("duplicados_misma_ceremonia_plan", 0)

    return {
        "ok": True,
        "ceremonia": ceremonia.nombre,
        "anio": ceremonia.anio,
        "lugar": ceremonia.lugar,
        "total_hojas": len(libro.sheet_names),
        "hojas": resumen_hojas,
        "estudiantes_creados": total_estudiantes_creados,
        "estudiantes_actualizados": total_estudiantes_actualizados,
        "filas_omitidas": total_filas_omitidas,
        "invitaciones_creadas": total_invitaciones_creadas,
        "duplicados_misma_ceremonia_plan": total_duplicados_misma_ceremonia_plan,
        "total_estudiantes_bd": EstudianteTitulado.objects.count(),
        "total_invitaciones_bd": Invitacion.objects.count(),
        "total_bloques_bd": BloqueCeremonia.objects.count(),
        "total_planes_bd": PlanEstudio.objects.count(),
        "total_areas_bd": AreaAcademica.objects.count(),
    }