from django.apps import AppConfig


class TitulacionConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'

    name = 'titulacion'

    verbose_name = "Control de Titulación"

    def ready(self):

        import titulacion.eventos