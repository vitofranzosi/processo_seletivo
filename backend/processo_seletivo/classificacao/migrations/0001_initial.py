"""O ato de ordenação, suas posições e as duas garantias que precisam viver no banco.

`ato_de_ordenacao_append_only` impede qualquer mutação do cabeçalho já emitido. `posicao_coerente`
impede que uma posição nasça vinculando ao ato uma Inscrição de outro Edital ou Perfil; congelar
uma posição incoerente seria pior do que deixá-la mutável. As duas tabelas também recebem a recusa
do modelo e a restrição de privilégios do papel de runtime.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


def proteger_ato_e_posicoes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION reject_ordering_act_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'ordering acts are append-only';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER ato_de_ordenacao_append_only
        BEFORE UPDATE OR DELETE ON classificacao_atodeordenacao
        FOR EACH ROW EXECUTE FUNCTION reject_ordering_act_mutation();

        CREATE OR REPLACE FUNCTION check_order_position_scope() RETURNS trigger AS $$
        DECLARE
            escopo RECORD;
        BEGIN
            SELECT a.edital_id AS ato_edital_id,
                   a.perfil_id AS ato_perfil_id,
                   i.edital_id AS inscricao_edital_id,
                   i.profile_id AS inscricao_perfil_id
              INTO escopo
              FROM classificacao_atodeordenacao a
              JOIN inscricoes_inscricao i ON i.id = NEW.inscricao_id
             WHERE a.id = NEW.ato_id;

            IF NOT FOUND
               OR escopo.ato_edital_id IS DISTINCT FROM escopo.inscricao_edital_id
               OR escopo.ato_perfil_id IS DISTINCT FROM escopo.inscricao_perfil_id THEN
                RAISE EXCEPTION 'ordering position does not match its act scope';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER posicao_coerente
        BEFORE INSERT ON classificacao_posicaonaordem
        FOR EACH ROW EXECUTE FUNCTION check_order_position_scope();
        """
    )


def desproteger_ato_e_posicoes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        DROP TRIGGER IF EXISTS posicao_coerente ON classificacao_posicaonaordem;
        DROP FUNCTION IF EXISTS check_order_position_scope();
        DROP TRIGGER IF EXISTS ato_de_ordenacao_append_only ON classificacao_atodeordenacao;
        DROP FUNCTION IF EXISTS reject_ordering_act_mutation();
        """
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("inscricoes", "0004_valor_de_fato"),
        ("processos", "0002_teto_de_inscricoes"),
        ("publicacoes", "0008_remover_ancoras"),
    ]

    operations = [
        migrations.CreateModel(
            name="AtoDeOrdenacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("perfil_id", models.UUIDField()),
                ("marco_id", models.UUIDField()),
                ("motivo_da_sucessao", models.TextField(blank=True, default="")),
                ("universo", models.JSONField(default=dict)),
                ("emitido_por", models.CharField(max_length=255)),
                ("emitido_em", models.DateTimeField()),
                (
                    "ato_anterior",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sucessores",
                        to="classificacao.atodeordenacao",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="atos_de_ordenacao",
                        to="processos.edital",
                    ),
                ),
                (
                    "versao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="atos_de_ordenacao",
                        to="publicacoes.versaoconsolidada",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PosicaoNaOrdem",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("posicao", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "pontuacao_combinada",
                    models.DecimalField(blank=True, decimal_places=4, max_digits=19, null=True),
                ),
                ("modalidade_id", models.UUIDField(blank=True, null=True)),
                ("consequencia", models.CharField(max_length=20)),
                ("motivo", models.TextField(blank=True, default="")),
                ("empate_residual", models.BooleanField(default=False)),
                ("desempate", models.JSONField(default=list)),
                (
                    "ato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posicoes",
                        to="classificacao.atodeordenacao",
                    ),
                ),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="posicoes_na_ordem",
                        to="inscricoes.inscricao",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="atodeordenacao",
            index=models.Index(
                fields=["edital", "perfil_id", "marco_id"], name="classificac_edital__fa7b6b_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="atodeordenacao",
            constraint=models.UniqueConstraint(
                condition=models.Q(("ato_anterior__isnull", True)),
                fields=("edital", "perfil_id", "marco_id"),
                name="uq_ato_raiz_por_marco",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodeordenacao",
            constraint=models.UniqueConstraint(
                condition=models.Q(("ato_anterior__isnull", False)),
                fields=("ato_anterior",),
                name="uq_ato_sucessor_unico",
            ),
        ),
        migrations.AddConstraint(
            model_name="atodeordenacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("ato_anterior__isnull", True),
                    models.Q(("motivo_da_sucessao", ""), _negated=True),
                    _connector="OR",
                ),
                name="ck_sucessao_com_motivo",
            ),
        ),
        migrations.AddIndex(
            model_name="posicaonaordem",
            index=models.Index(fields=["ato", "posicao"], name="classificac_ato_id_f469db_idx"),
        ),
        migrations.AddConstraint(
            model_name="posicaonaordem",
            constraint=models.UniqueConstraint(
                fields=("ato", "inscricao"), name="uq_posicao_por_ato_inscricao"
            ),
        ),
        migrations.AddConstraint(
            model_name="posicaonaordem",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("motivo", ""), ("posicao__gte", 1), ("posicao__isnull", False)),
                    models.Q(("posicao__isnull", True), models.Q(("motivo", ""), _negated=True)),
                    _connector="OR",
                ),
                name="ck_posicao_ou_motivo",
            ),
        ),
        migrations.RunPython(proteger_ato_e_posicoes, desproteger_ato_e_posicoes),
    ]
