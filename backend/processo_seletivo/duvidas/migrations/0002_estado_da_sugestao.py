"""O estado da pergunta sugerida, respondida pela `070` sem o modelo (protótipo da Fase C).

Só a lista do `CHECK` muda: a troca da sugestão é gravada como as outras, porque é da tabela, e não
do navegador, que o histórico da conversa sai (`FR-1494`).
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("duvidas", "0001_initial"),
        ("processos", "0004_metodo_de_sorteio_comum"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="trocadopiloto",
            name="ck_troca_estado",
        ),
        migrations.AddConstraint(
            model_name="trocadopiloto",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    (
                        "estado__in",
                        (
                            "RESPONDIDA_E_CONFERIDA",
                            "NAO_PASSOU_NA_CONFERENCIA",
                            "INCOMPLETA",
                            "POSSIVEL_CORTE",
                            "MODELO_DIFERENTE",
                            "RESPOSTA_MALFORMADA",
                            "INDISPONIVEL",
                            "TEMPO_ESGOTADO",
                            "LIMITE_DO_SERVICO",
                            "ORCAMENTO_ESGOTADO",
                            "LIMITE_DE_USO",
                            "EXCEDE_O_CONTEXTO",
                            "PERGUNTA_RECUSADA",
                            "SEM_TOKENIZER",
                            "RESPOSTA_DA_SUGESTAO",
                        ),
                    )
                ),
                name="ck_troca_estado",
            ),
        ),
    ]
