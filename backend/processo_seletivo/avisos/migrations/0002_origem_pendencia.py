"""A origem `PENDENCIA` no aviso: o aviso de pendência documental (134, FR-4618, SC-1448).

**Só duas constraints, e nenhuma tabela ou coluna.** A origem nova entra na lista conhecida, e o
ato que ela cita não é publicação nem referência: é a convocação do destinatário. Nenhuma linha
existente muda — as duas origens da `066` continuam aceitas pelas mesmas condições —, e as tabelas
continuam append-only, com os mesmos gatilhos e privilégios.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("avisos", "0001_initial"),
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="aviso",
            name="ck_aviso_origem_conhecida",
        ),
        migrations.RemoveConstraint(
            model_name="aviso",
            name="ck_aviso_ato_da_origem",
        ),
        migrations.AlterField(
            model_name="aviso",
            name="origem",
            field=models.CharField(
                choices=[
                    ("RESULTADO", "RESULTADO"),
                    ("CHAMADA", "CHAMADA"),
                    ("PENDENCIA", "PENDENCIA"),
                ],
                max_length=16,
            ),
        ),
        migrations.AddConstraint(
            model_name="aviso",
            constraint=models.CheckConstraint(
                condition=models.Q(("origem__in", ("RESULTADO", "CHAMADA", "PENDENCIA"))),
                name="ck_aviso_origem_conhecida",
            ),
        ),
        migrations.AddConstraint(
            model_name="aviso",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("natureza__in", ("PRELIMINAR", "DEFINITIVA")),
                        ("origem", "RESULTADO"),
                        ("referencia_da_publicacao", ""),
                    ),
                    models.Q(
                        ("natureza", ""),
                        ("origem", "CHAMADA"),
                        models.Q(("referencia_da_publicacao", ""), _negated=True),
                    ),
                    models.Q(
                        ("natureza", ""), ("origem", "PENDENCIA"), ("referencia_da_publicacao", "")
                    ),
                    _connector="OR",
                ),
                name="ck_aviso_ato_da_origem",
            ),
        ),
    ]
