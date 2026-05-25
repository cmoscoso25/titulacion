import uuid
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile


def generar_codigo_unico_estudiante(estudiante):
    from .models import EstudianteTitulado

    if estudiante.codigo_qr_estudiante:
        return estudiante.codigo_qr_estudiante

    for _ in range(30):
        codigo = f"EST-{estudiante.rut}-{uuid.uuid4().hex[:10].upper()}"

        existe = EstudianteTitulado.objects.filter(
            codigo_qr_estudiante=codigo
        ).exclude(
            id=estudiante.id
        ).exists()

        if not existe:
            return codigo

    return f"EST-{estudiante.rut}-{uuid.uuid4().hex.upper()}"


def generar_codigo_unico_invitacion(invitacion):
    from .models import Invitacion

    if invitacion.codigo_qr:
        return invitacion.codigo_qr

    rut = invitacion.estudiante.rut
    numero = invitacion.numero_invitacion

    for _ in range(30):
        codigo = f"INV{numero}-{rut}-{uuid.uuid4().hex[:10].upper()}"

        existe = Invitacion.objects.filter(
            codigo_qr=codigo
        ).exclude(
            id=invitacion.id
        ).exists()

        if not existe:
            return codigo

    return f"INV{numero}-{rut}-{uuid.uuid4().hex.upper()}"


def crear_imagen_qr(codigo):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )

    qr.add_data(codigo)
    qr.make(fit=True)

    imagen = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("RGB")

    buffer = BytesIO()
    imagen.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)

    return buffer


def generar_qr_estudiante(estudiante):
    codigo = generar_codigo_unico_estudiante(estudiante)

    estudiante.codigo_qr_estudiante = codigo

    buffer = crear_imagen_qr(codigo)

    nombre_archivo = f"qr_estudiante_{estudiante.rut}_{uuid.uuid4().hex[:8]}.png"

    estudiante.imagen_qr_estudiante.save(
        nombre_archivo,
        ContentFile(buffer.getvalue()),
        save=False
    )

    estudiante.save()

    return estudiante


def generar_qr_invitacion(invitacion):
    codigo = generar_codigo_unico_invitacion(invitacion)

    invitacion.codigo_qr = codigo

    buffer = crear_imagen_qr(codigo)

    nombre_archivo = (
        f"qr_invitacion_{invitacion.numero_invitacion}_"
        f"{invitacion.estudiante.rut}_{uuid.uuid4().hex[:8]}.png"
    )

    invitacion.imagen_qr.save(
        nombre_archivo,
        ContentFile(buffer.getvalue()),
        save=False
    )

    invitacion.save()

    return invitacion