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
        ("avaliacoes", "0002_conclusao_por_forma"),
        ("publicacoes", "0008_remover_ancoras"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="avaliacao",
            name="ck_avaliacao_concluida_completa",
        ),
        migrations.RemoveConstraint(
            model_name="conclusaoavaliacao",
            name="ck_conclusao_completa_por_forma",
        ),
        migrations.AddConstraint(
            model_name="avaliacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("estado", "RASCUNHO"),
                    models.Q(
                        ("concluida_em__isnull", False),
                        ("estado", "CONCLUIDA"),
                        ("versao__isnull", False),
                        models.Q(("concluida_por", ""), _negated=True),
                        models.Q(
                            models.Q(
                                ("forma", "PONTUADA"), ("pontuacao__isnull", False), ("sentido", "")
                            ),
                            models.Q(
                                ("forma", "DECISORIA"),
                                ("pontuacao__isnull", True),
                                ("sentido__in", ["FAVORAVEL", "DESFAVORAVEL"]),
                            ),
                            _connector="OR",
                        ),
                    ),
                    _connector="OR",
                ),
                name="ck_avaliacao_concluida_completa",
            ),
        ),
        migrations.AddConstraint(
            model_name="conclusaoavaliacao",
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
                name="ck_conclusao_completa_por_forma",
            ),
        ),
    ]
