"""O detalhamento da correção fixada numa Etapa com barema (146, D-004, FR-5227).

Uma coluna JSON com default `[]` na `DecisaoRecurso`, que é append-only nas duas camadas:
acrescentar coluna com default não reescreve linha nem dispara o gatilho, e as decisões que já
existem leem a lista vazia — que é verdade: nenhuma delas fixou critério. A coerência da decisão
(`decisao_recurso_coerente`) não lê a coluna, e o total continua em `pontuacao`.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("recursos", "0002_ato_de_instrucao")]

    operations = [
        migrations.AddField(
            model_name="decisaorecurso",
            name="criterios",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
