"""A origem `AGENDA` no aviso: o aviso de agenda da Etapa (167, FR-7230, D-010).

**Três constraints e uma coluna que passa a aceitar nulo; nenhuma tabela.** A origem nova entra na
lista conhecida; o ato que ela cita é a agenda publicada, pela frase da referência, como a chamada;
e o `marco_id` passa a aceitar nulo **só** nela, porque a agenda é da Etapa e não de um marco.
Nenhuma linha existente muda — as três origens anteriores continuam aceitas pelas mesmas condições,
e todas têm marco —, e as tabelas continuam append-only, com os mesmos gatilhos e privilégios.

**A `168`** (orientação da verificação) traz a origem `PASSO`, que também não tem marco. Quem
entrar depois refaz estes `CHECK` com as cinco origens, e `marco_id` nulo continua permitido só às
que não têm marco (plan da `167`, *Coordenação com a 168*).
"""

from django.db import migrations, models

ORIGENS = ("RESULTADO", "CHAMADA", "PENDENCIA", "AGENDA")


class Migration(migrations.Migration):
    dependencies = [
        ("avisos", "0002_origem_pendencia"),
    ]

    operations = [
        migrations.RemoveConstraint(model_name="aviso", name="ck_aviso_origem_conhecida"),
        migrations.RemoveConstraint(model_name="aviso", name="ck_aviso_ato_da_origem"),
        migrations.AlterField(
            model_name="aviso",
            name="origem",
            field=models.CharField(choices=[(o, o) for o in ORIGENS], max_length=16),
        ),
        migrations.AlterField(
            model_name="aviso",
            name="marco_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="aviso",
            constraint=models.CheckConstraint(
                condition=models.Q(("origem__in", ORIGENS)),
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
                    models.Q(
                        ("natureza", ""),
                        ("origem", "AGENDA"),
                        models.Q(("referencia_da_publicacao", ""), _negated=True),
                    ),
                    _connector="OR",
                ),
                name="ck_aviso_ato_da_origem",
            ),
        ),
        migrations.AddConstraint(
            model_name="aviso",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("marco_id__isnull", False), ("origem", "AGENDA"), _connector="OR"
                ),
                name="ck_aviso_marco_da_origem",
            ),
        ),
    ]
