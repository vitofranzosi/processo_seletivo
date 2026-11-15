"""A habilitação do assistente (170): a tabela dos atos e o gatilho append-only.

As duas travas de sempre: o gatilho que recusa `UPDATE` e `DELETE`, e o privilégio ausente, pela
entrada em `seguranca/papeis.py::TABELAS_APPEND_ONLY`. Numa base já provisionada é preciso **rodar o
comando de novo** depois desta migration — é a segunda passada do preparo.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

TABELA = "duvidas_habilitacao_do_assistente"
GATILHO = "habilitacao_do_assistente_append_only"

FUNCAO = """
CREATE OR REPLACE FUNCTION reject_assistant_enablement_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'assistant enablement records are append-only';
END;
$$ LANGUAGE plpgsql;
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(FUNCAO)
    schema_editor.execute(
        f"CREATE TRIGGER {GATILHO} BEFORE UPDATE OR DELETE ON {TABELA} "
        "FOR EACH ROW EXECUTE FUNCTION reject_assistant_enablement_mutation();"
    )


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(f"DROP TRIGGER IF EXISTS {GATILHO} ON {TABELA};")
    schema_editor.execute("DROP FUNCTION IF EXISTS reject_assistant_enablement_mutation();")


class Migration(migrations.Migration):
    dependencies = [
        ("duvidas", "0002_estado_da_sugestao"),
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.CreateModel(
            name="HabilitacaoDoAssistente",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("frente", models.CharField(max_length=16)),
                ("ordem", models.PositiveIntegerField()),
                ("habilitada", models.BooleanField()),
                ("motivo", models.TextField()),
                ("autor", models.CharField(max_length=255)),
                ("criado_em", models.DateTimeField()),
                (
                    "edital",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="habilitacoes_do_assistente",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "db_table": "duvidas_habilitacao_do_assistente",
                "ordering": ("frente", "edital", "ordem"),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("frente", "PILOTO"), ("edital__isnull", True)),
                            models.Q(("frente", "PAGINA_PUBLICA"), ("edital__isnull", False)),
                            _connector="OR",
                        ),
                        name="ck_habilitacao_frente_e_edital",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("ordem__gte", 1)), name="ck_habilitacao_ordem_positiva"
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("motivo__regex", "^\\s*$"), _negated=True),
                        name="ck_habilitacao_motivo_preenchido",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("frente", "PILOTO")),
                        fields=("ordem",),
                        name="uq_habilitacao_ordem_do_piloto",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("frente", "PAGINA_PUBLICA")),
                        fields=("edital", "ordem"),
                        name="uq_habilitacao_ordem_do_edital",
                    ),
                ],
            },
        ),
        migrations.RunPython(proteger, desproteger),
    ]
