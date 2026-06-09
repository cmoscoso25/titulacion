from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("titulacion", "0003_cambioceremonia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bloqueceremonia",
            name="estado_registro",
            field=models.CharField(
                choices=[
                    ("PROGRAMADA", "Programada"),
                    ("ABIERTA", "Abierta"),
                    ("CERRADA_INGRESO", "Cerrada (acepta atrasados)"),
                    ("CERRADA", "Cerrada"),
                ],
                default="PROGRAMADA",
                max_length=20,
            ),
        ),
    ]
