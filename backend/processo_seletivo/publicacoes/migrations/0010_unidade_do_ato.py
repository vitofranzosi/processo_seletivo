"""A unidade que praticou o ato, registrada na Publicação (060, FR-1128).

Cinco colunas com padrão constante, pela mesma razão da `0009`: `ADD COLUMN` com padrão constante é
só metadado no PostgreSQL, nenhuma linha é reescrita, e o gatilho append-only de
`publicacoes_publicacao`, que recusa `UPDATE`, não dispara. Não há Publicação em produção; no banco
de demonstração as anteriores ficam vazias, e se re-semeia.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0009_ato_de_nomeacao_do_signatario")]

    operations = [
        migrations.AddField(
            model_name="publicacao",
            name="unidade_codigo",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="publicacao",
            name="unidade_sigla",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="publicacao",
            name="unidade_nome",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="publicacao",
            name="unidade_cabecalho",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="publicacao",
            name="unidade_local",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
    ]
