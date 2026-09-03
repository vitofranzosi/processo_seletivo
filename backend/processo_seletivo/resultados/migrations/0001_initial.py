"""O Resultado da Etapa, e as duas triggers que o guardam.

Elas são o mesmo raciocínio em tempos diferentes: `resultado_etapa_coerente` impede que a linha
**nasça errada**, `resultado_etapa_append_only` impede que ela **mude depois**. Sem a primeira, a
segunda apenas congelaria o erro — e num registro append-only, congelar o erro é pior do que
deixá-lo mudar (013, T-011).

A verificação de coerência custa uma junção que já era obrigatória: `Avaliacao.atribuicao` é
`OneToOne`, e é a **Atribuição** que carrega `inscricao_id`, `etapa_id`, `edital_id` e `ativo`. A
mesma leitura confere os quatro campos redundantes, o estado da conclusão e a elegibilidade.

`ativo` é conferido **no `INSERT`**, e é exatamente isso que a invariante afirma: a fonte *era*
elegível quando consolidada. Impedimento posterior inativa a Atribuição e contesta o Resultado sem
invalidá-lo — anular é ato explícito, e não efeito colateral.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


def proteger_resultado(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        CREATE OR REPLACE FUNCTION reject_stage_result_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'stage results are append-only';
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER resultado_etapa_append_only
        BEFORE UPDATE OR DELETE ON resultados_resultadoetapa
        FOR EACH ROW EXECUTE FUNCTION reject_stage_result_mutation();

        CREATE OR REPLACE FUNCTION check_stage_result_source() RETURNS trigger AS $$
        DECLARE
            fonte RECORD;
        BEGIN
            SELECT a.estado, a.pontuacao, t.inscricao_id, t.etapa_id, t.edital_id, t.ativo
              INTO fonte
              FROM avaliacoes_avaliacao a
              JOIN avaliacoes_atribuicao t ON t.id = a.atribuicao_id
             WHERE a.id = NEW.avaliacao_id;

            IF NOT FOUND
               OR fonte.inscricao_id IS DISTINCT FROM NEW.inscricao_id
               OR fonte.etapa_id IS DISTINCT FROM NEW.etapa_id
               OR fonte.edital_id IS DISTINCT FROM NEW.edital_id
               OR fonte.pontuacao IS DISTINCT FROM NEW.pontuacao
               OR fonte.estado <> 'CONCLUIDA'
               OR NOT fonte.ativo THEN
                RAISE EXCEPTION 'stage result does not match its source evaluation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        CREATE TRIGGER resultado_etapa_coerente
        BEFORE INSERT ON resultados_resultadoetapa
        FOR EACH ROW EXECUTE FUNCTION check_stage_result_source();
        """
    )


def desproteger_resultado(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        """
        DROP TRIGGER IF EXISTS resultado_etapa_coerente ON resultados_resultadoetapa;
        DROP FUNCTION IF EXISTS check_stage_result_source();
        DROP TRIGGER IF EXISTS resultado_etapa_append_only ON resultados_resultadoetapa;
        DROP FUNCTION IF EXISTS reject_stage_result_mutation();
        """
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("avaliacoes", "0001_initial"),
        ("inscricoes", "0003_cpf_na_submetida"),
        ("processos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResultadoEtapa",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("etapa_id", models.UUIDField()),
                ("pontuacao", models.DecimalField(decimal_places=4, max_digits=7)),
                (
                    "consequencia",
                    models.CharField(
                        choices=[("HABILITADA", "Habilitada"), ("ELIMINADA", "Eliminada")],
                        max_length=20,
                    ),
                ),
                ("motivo", models.TextField()),
                ("consolidado_em", models.DateTimeField()),
                ("consolidado_por", models.CharField(max_length=255)),
                (
                    "avaliacao",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resultado_da_etapa",
                        to="avaliacoes.avaliacao",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resultados",
                        to="processos.edital",
                    ),
                ),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resultados",
                        to="inscricoes.inscricao",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.UniqueConstraint(
                fields=("inscricao", "etapa_id"), name="uq_resultado_inscricao_etapa"
            ),
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(("consequencia__in", ("HABILITADA", "ELIMINADA"))),
                name="ck_resultado_consequencia",
            ),
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(("motivo", ""), _negated=True),
                name="ck_resultado_motivo_presente",
            ),
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(("consolidado_por", ""), _negated=True),
                name="ck_resultado_autor_presente",
            ),
        ),
        migrations.AddIndex(
            model_name="resultadoetapa",
            index=models.Index(
                fields=["edital", "etapa_id"], name="resultados__edital__0ff1a3_idx"
            ),
        ),
        migrations.RunPython(proteger_resultado, desproteger_resultado),
    ]
