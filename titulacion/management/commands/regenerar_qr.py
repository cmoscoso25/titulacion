from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from titulacion.generador_qr import crear_imagen_qr
from titulacion.models import EstudianteTitulado, Invitacion


class Command(BaseCommand):
    help = "Regenera las imágenes QR de todos los estudiantes e invitaciones conservando los códigos existentes."

    def handle(self, *args, **options):
        self._regenerar_estudiantes()
        self._regenerar_invitaciones()
        self.stdout.write(self.style.SUCCESS("Regeneración completada."))

    def _regenerar_estudiantes(self):
        estudiantes = EstudianteTitulado.objects.exclude(codigo_qr_estudiante="").exclude(codigo_qr_estudiante__isnull=True)
        total = estudiantes.count()
        self.stdout.write(f"Regenerando {total} QR de estudiantes...")

        for i, estudiante in enumerate(estudiantes, 1):
            try:
                if estudiante.imagen_qr_estudiante:
                    estudiante.imagen_qr_estudiante.delete(save=False)

                buffer = crear_imagen_qr(estudiante.codigo_qr_estudiante)
                nombre = f"qr_est_{estudiante.rut}.png"
                estudiante.imagen_qr_estudiante.save(
                    nombre,
                    ContentFile(buffer.getvalue()),
                    save=True,
                )
                self.stdout.write(f"  [{i}/{total}] {estudiante.rut} OK")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [{i}/{total}] {estudiante.rut} ERROR: {e}"))

    def _regenerar_invitaciones(self):
        invitaciones = Invitacion.objects.exclude(codigo_qr="").exclude(codigo_qr__isnull=True).select_related("estudiante")
        total = invitaciones.count()
        self.stdout.write(f"Regenerando {total} QR de invitaciones...")

        for i, inv in enumerate(invitaciones, 1):
            try:
                if inv.imagen_qr:
                    inv.imagen_qr.delete(save=False)

                buffer = crear_imagen_qr(inv.codigo_qr)
                nombre = f"qr_inv_{inv.numero_invitacion}_{inv.estudiante.rut}.png"
                inv.imagen_qr.save(
                    nombre,
                    ContentFile(buffer.getvalue()),
                    save=True,
                )
                self.stdout.write(f"  [{i}/{total}] INV{inv.numero_invitacion} {inv.estudiante.rut} OK")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [{i}/{total}] INV{inv.numero_invitacion} ERROR: {e}"))
