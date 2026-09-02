"""A retomada da reconciliação ganha finalidade própria.

Reformatada à mão para caber no limite do projeto, como as anteriores.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("identidade", "0002_reconciliacao"),
    ]

    operations = [
        migrations.AlterField(
            model_name="desafiodeacesso",
            name="finalidade",
            field=models.CharField(
                choices=[
                    ("ENTRAR", "Entrar"),
                    ("ADICIONAR_CREDENCIAL", "Adicionar Credencial"),
                    ("RETOMAR", "Retomar"),
                ],
                max_length=30,
            ),
        ),
    ]
