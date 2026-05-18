import uuid

from django.db import models
from django.utils import timezone


def generar_codigo_qr_estudiante():
    return f"EST-{uuid.uuid4().hex.upper()}"


def generar_codigo_qr_invitacion():
    return f"INV-{uuid.uuid4().hex.upper()}"


class Ceremonia(models.Model):
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField(default=2026)
    lugar = models.CharField(max_length=255, default="Avenida Chile 1108")
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ceremonia"
        verbose_name_plural = "Ceremonias"
        ordering = ["-anio", "nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.anio}"


class BloqueCeremonia(models.Model):
    ESTADOS = [
        ("PROGRAMADA", "Programada"),
        ("ABIERTA", "Abierta"),
        ("CERRADA", "Cerrada"),
    ]

    ceremonia = models.ForeignKey(
        Ceremonia,
        on_delete=models.CASCADE,
        related_name="bloques"
    )

    nombre = models.CharField(max_length=255)
    fecha = models.DateField()
    hora_inicio = models.TimeField()

    estado_registro = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="PROGRAMADA"
    )

    fecha_apertura_registro = models.DateTimeField(blank=True, null=True)
    fecha_cierre_registro = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Bloque de ceremonia"
        verbose_name_plural = "Bloques de ceremonia"
        ordering = ["fecha", "hora_inicio", "nombre"]
        unique_together = ("ceremonia", "nombre")

    def __str__(self):
        return f"{self.nombre} - {self.fecha} {self.hora_inicio}"

    def esta_programada(self):
        return self.estado_registro == "PROGRAMADA"

    def esta_abierta(self):
        return self.estado_registro == "ABIERTA"

    def esta_cerrada(self):
        return self.estado_registro == "CERRADA"

    def abrir(self):
        BloqueCeremonia.objects.filter(
            estado_registro="ABIERTA"
        ).exclude(
            id=self.id
        ).update(
            estado_registro="PROGRAMADA",
            fecha_apertura_registro=None,
            fecha_cierre_registro=None,
        )

        self.estado_registro = "ABIERTA"
        self.fecha_apertura_registro = timezone.now()
        self.fecha_cierre_registro = None
        self.save()

    def cerrar(self):
        self.estado_registro = "CERRADA"
        self.fecha_cierre_registro = timezone.now()
        self.save()

    def reprogramar(self):
        self.estado_registro = "PROGRAMADA"
        self.fecha_apertura_registro = None
        self.fecha_cierre_registro = None
        self.save()


class AreaAcademica(models.Model):
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Área académica"
        verbose_name_plural = "Áreas académicas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class PlanEstudio(models.Model):
    area = models.ForeignKey(
        AreaAcademica,
        on_delete=models.CASCADE,
        related_name="planes"
    )

    nombre = models.CharField(max_length=255)

    institucion = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Plan de estudio"
        verbose_name_plural = "Planes de estudio"
        ordering = ["area__nombre", "nombre"]
        unique_together = ("area", "nombre", "institucion")

    def __str__(self):
        return self.nombre


class EstudianteTitulado(models.Model):
    rut = models.CharField(max_length=20)
    nombre_completo = models.CharField(max_length=255)

    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    jornada = models.CharField(max_length=100, blank=True, null=True)

    bloque_ceremonia = models.ForeignKey(
        BloqueCeremonia,
        on_delete=models.CASCADE,
        related_name="estudiantes"
    )

    plan_estudio = models.ForeignKey(
        PlanEstudio,
        on_delete=models.CASCADE,
        related_name="estudiantes"
    )

    codigo_qr_estudiante = models.CharField(
        max_length=255,
        unique=True,
        default=generar_codigo_qr_estudiante,
        editable=False
    )

    imagen_qr_estudiante = models.ImageField(
        upload_to="qr_estudiantes/",
        blank=True,
        null=True
    )

    ingreso_confirmado = models.BooleanField(default=False)
    fecha_hora_ingreso = models.DateTimeField(blank=True, null=True)

    invitaciones_entregadas = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estudiante titulado"
        verbose_name_plural = "Estudiantes titulados"
        ordering = ["nombre_completo"]
        unique_together = ("rut", "bloque_ceremonia", "plan_estudio")

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


class Invitacion(models.Model):
    estudiante = models.ForeignKey(
        EstudianteTitulado,
        on_delete=models.CASCADE,
        related_name="invitaciones"
    )

    numero_invitacion = models.IntegerField()

    codigo_qr = models.CharField(
        max_length=255,
        unique=True,
        default=generar_codigo_qr_invitacion,
        editable=False
    )

    imagen_qr = models.ImageField(
        upload_to="qr_invitaciones/",
        blank=True,
        null=True
    )

    usada = models.BooleanField(default=False)
    fecha_uso = models.DateTimeField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invitación"
        verbose_name_plural = "Invitaciones"
        ordering = ["estudiante__nombre_completo", "numero_invitacion"]
        unique_together = ("estudiante", "numero_invitacion")

    def __str__(self):
        return f"{self.estudiante.nombre_completo} - Invitación {self.numero_invitacion}"


class RegistroIngreso(models.Model):
    TIPOS = [
        ("ESTUDIANTE", "Estudiante"),
        ("INVITADO", "Invitado"),
    ]

    RESULTADOS = [
        ("PERMITIDO", "Permitido"),
        ("DENEGADO", "Denegado"),
        ("DUPLICADO", "Duplicado"),
        ("ATRASADO", "Atrasado"),
        ("OTRA_CEREMONIA", "Otra ceremonia"),
    ]

    estudiante = models.ForeignKey(
        EstudianteTitulado,
        on_delete=models.CASCADE,
        related_name="registros",
        blank=True,
        null=True
    )

    invitacion = models.ForeignKey(
        Invitacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros"
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)
    resultado = models.CharField(max_length=30, choices=RESULTADOS)

    fecha_hora = models.DateTimeField(default=timezone.now)

    observacion = models.TextField(blank=True, null=True)

    usuario_registro = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Registro de ingreso"
        verbose_name_plural = "Registros de ingreso"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"{self.tipo} - {self.resultado}"


class CambioCeremonia(models.Model):
    estudiante = models.ForeignKey(
        EstudianteTitulado,
        on_delete=models.CASCADE,
        related_name="cambios_ceremonia"
    )

    bloque_origen = models.ForeignKey(
        BloqueCeremonia,
        on_delete=models.PROTECT,
        related_name="cambios_origen"
    )

    bloque_destino = models.ForeignKey(
        BloqueCeremonia,
        on_delete=models.PROTECT,
        related_name="cambios_destino"
    )

    motivo = models.TextField()

    usuario_responsable = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    fecha_cambio = models.DateTimeField(default=timezone.now)

    observacion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Cambio de ceremonia"
        verbose_name_plural = "Cambios de ceremonia"
        ordering = ["-fecha_cambio"]

    def __str__(self):
        return (
            f"{self.estudiante.nombre_completo} | "
            f"{self.bloque_origen.nombre} → {self.bloque_destino.nombre}"
        )