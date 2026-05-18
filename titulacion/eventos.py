from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EstudianteTitulado, Invitacion
from .generador_qr import generar_qr_estudiante, generar_qr_invitacion


@receiver(post_save, sender=EstudianteTitulado)
def preparar_tarjetas_del_estudiante(sender, instance, created, **kwargs):
    """
    Al crear un estudiante titulado, se prepara su tarjeta
    y sus dos invitaciones oficiales.
    """

    if not created:
        return

    generar_qr_estudiante(instance)

    ya_tiene_invitaciones = Invitacion.objects.filter(
        estudiante=instance
    ).exists()

    if ya_tiene_invitaciones:
        return

    invitacion_1 = Invitacion.objects.create(
        estudiante=instance,
        numero_invitacion=1
    )

    invitacion_2 = Invitacion.objects.create(
        estudiante=instance,
        numero_invitacion=2
    )

    generar_qr_invitacion(invitacion_1)
    generar_qr_invitacion(invitacion_2)