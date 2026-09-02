"""A anotação do alvo sobrevive ao descarte da identidade que ela aponta.

Reformatada à mão para caber no limite do projeto, como as anteriores.
"""


import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identidade', '0003_retomar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='desafiodeacesso',
            name='reconciliacao_alvo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="identidade.candidateidentity",
            ),
        ),
    ]
