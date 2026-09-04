"""O sentido passa a ser restrito aos dois valores, no banco.

`TextChoices` valida no formulário e no `full_clean`, e **não cria constraint**: `bulk_create`, SQL
direto ou código futuro gravariam qualquer texto. A condição anterior só exigia que o sentido não
fosse vazio, e um `INSERT` cru com valor inventado atravessava — depois, `_consequencia_decisoria`
trata tudo que não é `DESFAVORAVEL` como favorável, de modo que a inscrição sairia
**habilitada** por um valor que ninguém escreveu.

É a mesma razão pela qual `ck_resultado_consequencia` já existia do outro lado, e o defeito era não
tê-la seguido aqui.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("avaliacoes", "0003_sentido_restrito_aos_dois_valores"),
        ("inscricoes", "0003_cpf_na_submetida"),
        ("processos", "0001_initial"),
        ("resultados", "0002_resultado_por_forma"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="resultadoetapa",
            name="ck_resultado_completo_por_forma",
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("forma", "PONTUADA"), ("pontuacao__isnull", False), ("sentido", "")),
                    models.Q(
                        ("forma", "DECISORIA"),
                        ("pontuacao__isnull", True),
                        ("sentido__in", ["FAVORAVEL", "DESFAVORAVEL"]),
                    ),
                    _connector="OR",
                ),
                name="ck_resultado_completo_por_forma",
            ),
        ),
    ]
