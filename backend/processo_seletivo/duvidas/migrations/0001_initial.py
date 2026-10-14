"""A tabela do piloto do assistente do Edital (071, data-model §3, §6).

**A primeira migration do pacote, e sem gatilho.** `TrocaDoPiloto` não é append-only nem dado
normativo: é o histórico das conversas e o registro da avaliação, excluído por comando 90 dias
depois do relatório final. Por isso não entra em `TABELAS_APPEND_ONLY`, e o papel de execução recebe
`DELETE` pelos privilégios padrão. Numa base já provisionada, rodar o provisionamento de novo
depois desta migration, como depois de qualquer tabela nova.

O caminho de volta apaga a tabela: só serve numa máquina sem registros a preservar.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("processos", "0004_metodo_de_sorteio_comum"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrocaDoPiloto",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("conversa", models.UUIDField(db_index=True)),
                ("ordem", models.PositiveIntegerField()),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("instante", models.DateTimeField()),
                ("origem", models.CharField(max_length=16)),
                ("versao", models.UUIDField(blank=True, null=True)),
                ("versao_curta", models.CharField(blank=True, max_length=32)),
                ("pergunta", models.TextField()),
                ("estado", models.CharField(max_length=40)),
                ("tipo", models.CharField(blank=True, max_length=40)),
                ("trechos", models.JSONField(blank=True, null=True)),
                ("fontes_citadas", models.JSONField(blank=True, null=True)),
                ("conferencia", models.JSONField(blank=True, null=True)),
                ("historico_desde", models.PositiveIntegerField(blank=True, null=True)),
                ("chamou_o_servico", models.BooleanField(default=False)),
                ("servico", models.CharField(max_length=16)),
                ("modelo_configurado", models.CharField(max_length=200)),
                ("modelo_que_respondeu", models.CharField(blank=True, max_length=200)),
                ("parametros", models.JSONField(default=dict)),
                ("impressao_das_fontes", models.CharField(blank=True, max_length=64)),
                ("versao_das_instrucoes", models.CharField(max_length=16)),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="trocas_do_piloto",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "ordering": ("conversa", "ordem"),
                "constraints": [
                    models.UniqueConstraint(
                        fields=("conversa", "ordem"), name="uq_troca_conversa_ordem"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("ordem__gte", 1)), name="ck_troca_ordem_positiva"
                    ),
                    models.CheckConstraint(
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
                                ),
                            )
                        ),
                        name="ck_troca_estado",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("tipo", ""),
                            (
                                "tipo__in",
                                (
                                    "RESPONDIDA",
                                    "NAO_INFORMA",
                                    "DEPENDE_DA_LEITURA",
                                    "FONTES_DIVERGENTES",
                                    "DETALHE_EM_ANEXO",
                                    "DECISAO_NAO_TOMADA",
                                    "OUTRA_SELECAO",
                                    "FORA_DO_ESCOPO",
                                ),
                            ),
                            _connector="OR",
                        ),
                        name="ck_troca_tipo",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("origem__in", ("TELA", "AVALIACAO"))),
                        name="ck_troca_origem",
                    ),
                ],
            },
        ),
    ]
