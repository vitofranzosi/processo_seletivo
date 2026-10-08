"""A unidade que praticou o ato e o ato de nomeação de quem respondeu por ele (060, FR-1128).

Seis colunas com padrão constante, pela razão da `publicacoes/0009`: `ADD COLUMN` com padrão
constante é só metadado no PostgreSQL, e o gatilho append-only de `divulgacao_publicacaoresultado`,
que recusa `UPDATE`, não dispara. Não há Publicação de Resultado em produção.
"""

from django.db import migrations, models


def _texto(tamanho):
    return models.CharField(blank=True, default="", max_length=tamanho)


class Migration(migrations.Migration):
    dependencies = [("divulgacao", "0003_lista_de_concorrencia")]

    operations = [
        migrations.AddField(
            model_name="publicacaoresultado",
            name="signatario_ato_de_nomeacao",
            field=_texto(255),
        ),
        migrations.AddField(
            model_name="publicacaoresultado", name="unidade_codigo", field=_texto(100)
        ),
        migrations.AddField(
            model_name="publicacaoresultado", name="unidade_sigla", field=_texto(30)
        ),
        migrations.AddField(
            model_name="publicacaoresultado", name="unidade_nome", field=_texto(255)
        ),
        migrations.AddField(
            model_name="publicacaoresultado",
            name="unidade_cabecalho",
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name="publicacaoresultado", name="unidade_local", field=_texto(120)
        ),
    ]
