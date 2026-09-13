"""A porta por onde a `019` mexe na contagem, com as **duas** travas de sempre (019, `R-003`).

Gatilho **e** privilégio ausente. A função `reject_occupancy_mutation()` já existe desde a
`0001_initial`, e é reusada: uma segunda função com outro nome diria que esta tabela é imutável por
outra razão, quando é pela mesma.

A tabela entra em `seguranca/papeis.py::TABELAS_APPEND_ONLY` na mesma leva — levando o total de 26
para 27. Numa base já provisionada é preciso **rodar o comando de novo** depois desta migration:
privilégio não se concede a tabela que ainda não existia.

**A FK aponta para `processos.Edital` e para mais nada.** `inscricao_id` e `ato_de_origem_id` são
UUID opaco de propósito: uma FK de `ocupacao` para `inscricoes` ou para `convocacao` inverteria
aqui, no grafo de migrations, a dependência que a feature inteira existe para manter num sentido só.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE TRIGGER efeito_de_ocupacao_imutavel
BEFORE UPDATE OR DELETE ON ocupacao_efeitodeocupacao
FOR EACH ROW EXECUTE FUNCTION reject_occupancy_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS efeito_de_ocupacao_imutavel ON ocupacao_efeitodeocupacao;
"""


def proteger(apps, schema_editor):
    # O gatilho é PostgreSQL puro. Fora dele a migration passa sem instalar nada, e os testes que
    # dependem da garantia são pulados — é a mesma guarda que a `0001_initial` usa.
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [
        ("ocupacao", "0002_liberacao_nao_e_movimento"),
        ("processos", "0002_teto_de_inscricoes"),
    ]

    operations = [
        migrations.CreateModel(
            name="EfeitoDeOcupacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("perfil_id", models.UUIDField()),
                ("marco_id", models.UUIDField()),
                ("lista_id", models.UUIDField(blank=True, null=True)),
                ("inscricao_id", models.UUIDField()),
                (
                    "especie",
                    models.CharField(
                        choices=[
                            ("EXCLUSAO", "Exclusão do conjunto de ocupantes"),
                            ("INCLUSAO", "Inclusão no conjunto de ocupantes"),
                        ],
                        max_length=16,
                    ),
                ),
                ("fundamento", models.TextField()),
                ("ato_de_origem_id", models.UUIDField()),
                ("rotulo_da_origem", models.CharField(max_length=120)),
                ("registrado_por", models.CharField(max_length=255)),
                ("registrado_em", models.DateTimeField()),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="efeitos_de_ocupacao",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["edital", "perfil_id", "marco_id", "lista_id"],
                        name="ix_efeito_recorte",
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("especie__in", ["EXCLUSAO", "INCLUSAO"])),
                        name="ck_efeito_especie",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("fundamento", ""), _negated=True),
                        name="ck_efeito_com_fundamento",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("rotulo_da_origem", ""), _negated=True),
                        name="ck_efeito_com_rotulo_da_origem",
                    ),
                ],
            },
        ),
        migrations.RunPython(proteger, desproteger),
    ]
