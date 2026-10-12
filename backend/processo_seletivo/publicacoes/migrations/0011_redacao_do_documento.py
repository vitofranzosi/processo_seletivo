"""A redação com que o documento foi composto, registrada na Publicação (069, FR-1397, R-015).

Uma coluna com padrão constante, pela mesma razão da `0009` e da `0010`: `ADD COLUMN` com padrão
constante é só metadado no PostgreSQL, nenhuma linha é reescrita, e o gatilho append-only de
`publicacoes_publicacao`, que recusa `UPDATE`, não dispara. As Publicações que já existem ficam com
1 — a redação de antes da `069`, que é a que elas publicaram.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0010_unidade_do_ato")]

    operations = [
        migrations.AddField(
            model_name="publicacao",
            name="redacao_do_documento",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
