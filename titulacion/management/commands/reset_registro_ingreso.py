"""
Comando de administración: reinicia el registro de ingresos a cero.

Afecta ÚNICAMENTE:
  - RegistroIngreso         → elimina todos los registros de log
  - EstudianteTitulado      → resetea ingreso_confirmado y fecha_hora_ingreso
  - Invitacion              → resetea usada y fecha_uso

NO toca:
  - EstudianteTitulado (el registro en sí, nombre, RUT, QR, etc.)
  - Invitacion (el registro, codigo_qr, invitaciones_entregadas)
  - BloqueCeremonia / Ceremonia / PlanEstudio / AreaAcademica

Uso:
  python manage.py reset_registro_ingreso
  python manage.py reset_registro_ingreso --confirmar   # sin prompt interactivo
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from titulacion.models import EstudianteTitulado, Invitacion, RegistroIngreso


class Command(BaseCommand):
    help = (
        "Reinicia el registro de ingresos a cero antes de la ceremonia. "
        "Mantiene intactos estudiantes, invitaciones y códigos QR."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Ejecutar sin solicitar confirmación interactiva (útil en scripts).",
        )

    def handle(self, *args, **options):
        n_registros   = RegistroIngreso.objects.count()
        n_estudiantes = EstudianteTitulado.objects.filter(ingreso_confirmado=True).count()
        n_invitados   = Invitacion.objects.filter(usada=True).count()

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("=" * 62))
        self.stdout.write(self.style.WARNING("  REINICIO DE REGISTRO DE INGRESOS — Titulación INACAP 2026"))
        self.stdout.write(self.style.WARNING("=" * 62))
        self.stdout.write("")
        self.stdout.write("  Se realizarán las siguientes operaciones:")
        self.stdout.write(
            f"    • Eliminar  {n_registros:>5}  registros de ingreso (RegistroIngreso)"
        )
        self.stdout.write(
            f"    • Resetear  {n_estudiantes:>5}  estudiantes marcados como ingresados"
        )
        self.stdout.write(
            f"    • Resetear  {n_invitados:>5}  invitaciones marcadas como usadas"
        )
        self.stdout.write("")
        self.stdout.write(
            "  NO se eliminarán: datos de estudiantes, invitaciones, QRs ni ceremonias."
        )
        self.stdout.write("")

        if not options["confirmar"]:
            self.stdout.write(
                self.style.ERROR(
                    "  ADVERTENCIA: Esta operación no puede deshacerse."
                )
            )
            self.stdout.write("")
            self.stdout.write(
                '  Escribe CONFIRMAR (en mayúsculas) y presiona Enter para continuar,'
            )
            self.stdout.write("  o presiona Enter sin escribir nada para cancelar.")
            self.stdout.write("")
            self.stdout.write("  > ")
            self.stdout.flush()

            try:
                respuesta = input().strip()
            except (EOFError, KeyboardInterrupt):
                self.stdout.write("")
                self.stdout.write(self.style.WARNING("Operación cancelada."))
                return

            if respuesta != "CONFIRMAR":
                self.stdout.write(self.style.WARNING("Operación cancelada. No se modificó ningún dato."))
                return

        self.stdout.write("")
        self.stdout.write("  Ejecutando dentro de una transacción atómica...")

        with transaction.atomic():
            eliminados, _ = RegistroIngreso.objects.all().delete()

            estudiantes_reset = EstudianteTitulado.objects.all().update(
                ingreso_confirmado=False,
                fecha_hora_ingreso=None,
            )

            invitaciones_reset = Invitacion.objects.all().update(
                usada=False,
                fecha_uso=None,
            )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 62))
        self.stdout.write(self.style.SUCCESS("  Reinicio completado exitosamente."))
        self.stdout.write(self.style.SUCCESS("=" * 62))
        self.stdout.write(
            f"    ✓ Registros de ingreso eliminados  : {eliminados}"
        )
        self.stdout.write(
            f"    ✓ Estudiantes reseteados           : {estudiantes_reset}"
        )
        self.stdout.write(
            f"    ✓ Invitaciones reseteadas          : {invitaciones_reset}"
        )
        self.stdout.write("")
        self.stdout.write(
            "  El sistema está listo para la ceremonia."
        )
        self.stdout.write("")
