import uuid

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from titulacion.generador_qr import crear_imagen_qr
from titulacion.models import EstudianteTitulado, Invitacion


class Command(BaseCommand):
    help = "Regenera todas las imágenes QR con la calidad mejorada (ERROR_CORRECT_H, box_size=20)"

    def handle(self, *args, **options):
        self._regenerar_estudiantes()
        self._regenerar_invitaciones()
        self.stdout.write(self.style.SUCCESS("Regeneración completada."))

    def _regenerar_estudiantes(self):
        estudiantes = EstudianteTitulado.objects.all()
        total = estudiantes.count()
        self.stdout.write(f"Regenerando QR de {total} estudiante(s)...")

        for i, est in enumerate(estudiantes, 1):
            if not est.codigo_qr_estudiante:
                self.stdout.write(
                    self.style.WARNING(f"  [{i}/{total}] {est.nombre_completo} — sin código QR, omitido")
                )
                continue

            try:
                buffer = crear_imagen_qr(est.codigo_qr_estudiante)
                nombre = f"qr_estudiante_{est.rut}_{uuid.uuid4().hex[:8]}.png"
                est.imagen_qr_estudiante.save(nombre, ContentFile(buffer.getvalue()), save=False)
                EstudianteTitulado.objects.filter(pk=est.pk).update(
                    imagen_qr_estudiante=est.imagen_qr_estudiante.name
                )
                self.stdout.write(f"  [{i}/{total}] {est.nombre_completo} — OK")
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(f"  [{i}/{total}] {est.nombre_completo} — ERROR: {exc}")
                )

    def _regenerar_invitaciones(self):
        invitaciones = Invitacion.objects.select_related("estudiante").all()
        total = invitaciones.count()
        self.stdout.write(f"Regenerando QR de {total} invitación/es...")

        for i, inv in enumerate(invitaciones, 1):
            if not inv.codigo_qr:
                self.stdout.write(
                    self.style.WARNING(
                        f"  [{i}/{total}] Inv#{inv.numero_invitacion} {inv.estudiante.nombre_completo} — sin código QR, omitida"
                    )
                )
                continue

            try:
                buffer = crear_imagen_qr(inv.codigo_qr)
                nombre = (
                    f"qr_invitacion_{inv.numero_invitacion}_"
                    f"{inv.estudiante.rut}_{uuid.uuid4().hex[:8]}.png"
                )
                inv.imagen_qr.save(nombre, ContentFile(buffer.getvalue()), save=False)
                Invitacion.objects.filter(pk=inv.pk).update(imagen_qr=inv.imagen_qr.name)
                self.stdout.write(
                    f"  [{i}/{total}] Inv#{inv.numero_invitacion} {inv.estudiante.nombre_completo} — OK"
                )
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"  [{i}/{total}] Inv#{inv.numero_invitacion} {inv.estudiante.nombre_completo} — ERROR: {exc}"
                    )
                )
