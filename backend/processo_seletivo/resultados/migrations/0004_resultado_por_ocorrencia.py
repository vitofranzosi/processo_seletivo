"""O Resultado passa a existir sem Avaliação, e a versão normativa passa a ser dele (D-1).

Três mudanças que são uma só. `origem` diz de onde veio a evidência; `avaliacao` fica anulável
porque o desfecho de quem não foi avaliado não tem fonte a citar; e `versao` deixa de ser alcançada
por `avaliacao__versao` e vira campo do Resultado, porque no ramo sem Avaliação aquele caminho não
existe — e um Resultado sem a norma que o fundamentou contradiz I-2 do briefing da 013.

**Por que a versão não fica só no ramo sem Avaliação.** Seria mais barato e criaria duas formas de
responder à mesma pergunta: uma leitura por junção num ramo e por coluna no outro, divergindo no
dia em que alguém esquecer de tratar os dois. Ela é exigida sempre, e a trigger confere que
coincide com a da Avaliação quando há Avaliação — que é como as outras quatro contradições
possíveis já são impedidas.

**Por que o backfill desliga a trigger append-only.** `versao` não tem valor constante para nascer
com `DEFAULT`: cada Resultado herda a versão da sua Avaliação, e isso é um `UPDATE` linha a linha —
que é exatamente o que `resultado_etapa_append_only` existe para recusar. Desligá-la pelo tempo do
preenchimento é o que a migração pode fazer e o runtime não: o papel de migração é o dono da
tabela, e o de runtime nem `UPDATE` tem. Ela volta antes do fim da mesma transação.

**Por que a trigger é recriada por inteiro**, e não emendada: é o molde da migration da forma, e a
única maneira de `CREATE OR REPLACE` funcionar nos dois sentidos. A função nova ganha um ramo
para a Ocorrência — que confere o que ela **não** pode ter, e que a versão citada é do próprio
Edital — e acrescenta `versao_id` à conferência do ramo com Avaliação.
"""

import django.db.models.deletion
from django.db import migrations, models

CONFERIR = """
CREATE OR REPLACE FUNCTION check_stage_result_source() RETURNS trigger AS $$
DECLARE
    fonte RECORD;
    edital_da_versao UUID;
BEGIN
    IF NEW.origem = 'OCORRENCIA' THEN
        -- A Ocorrência não tem fonte a conferir, e por isso o que se confere é a ausência dela:
        -- uma linha que se diz constatação e cita Avaliação afirma as duas coisas ao mesmo tempo.
        IF NEW.avaliacao_id IS NOT NULL THEN
            RAISE EXCEPTION 'stage result by occurrence must not cite a source evaluation';
        END IF;
        -- E a norma citada precisa ser deste Edital. Sem Avaliação não há de onde a versão vir
        -- copiada, então esta é a única conferência que sobra — e sem ela a proveniência do ramo
        -- por Ocorrência seria promessa de código, que é o que estas triggers existem para negar.
        SELECT v.edital_id INTO edital_da_versao
          FROM publicacoes_versaoconsolidada v
         WHERE v.id = NEW.versao_id;
        IF NOT FOUND OR edital_da_versao IS DISTINCT FROM NEW.edital_id THEN
            RAISE EXCEPTION 'stage result cites a consolidated version of another edital';
        END IF;
        RETURN NEW;
    END IF;

    IF NEW.origem <> 'AVALIACAO' OR NEW.avaliacao_id IS NULL THEN
        RAISE EXCEPTION 'stage result does not match its source evaluation';
    END IF;

    SELECT a.estado, a.forma, a.pontuacao, a.sentido, a.versao_id,
           t.inscricao_id, t.etapa_id, t.edital_id, t.ativo
      INTO fonte
      FROM avaliacoes_avaliacao a
      JOIN avaliacoes_atribuicao t ON t.id = a.atribuicao_id
     WHERE a.id = NEW.avaliacao_id;

    IF NOT FOUND
       OR fonte.inscricao_id IS DISTINCT FROM NEW.inscricao_id
       OR fonte.etapa_id IS DISTINCT FROM NEW.etapa_id
       OR fonte.edital_id IS DISTINCT FROM NEW.edital_id
       OR fonte.forma IS DISTINCT FROM NEW.forma
       OR fonte.pontuacao IS DISTINCT FROM NEW.pontuacao
       OR fonte.sentido IS DISTINCT FROM NEW.sentido
       OR fonte.versao_id IS DISTINCT FROM NEW.versao_id
       OR fonte.estado <> 'CONCLUIDA'
       OR NOT fonte.ativo THEN
        RAISE EXCEPTION 'stage result does not match its source evaluation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

CONFERIR_ANTERIOR = """
CREATE OR REPLACE FUNCTION check_stage_result_source() RETURNS trigger AS $$
DECLARE
    fonte RECORD;
BEGIN
    SELECT a.estado, a.forma, a.pontuacao, a.sentido,
           t.inscricao_id, t.etapa_id, t.edital_id, t.ativo
      INTO fonte
      FROM avaliacoes_avaliacao a
      JOIN avaliacoes_atribuicao t ON t.id = a.atribuicao_id
     WHERE a.id = NEW.avaliacao_id;

    IF NOT FOUND
       OR fonte.inscricao_id IS DISTINCT FROM NEW.inscricao_id
       OR fonte.etapa_id IS DISTINCT FROM NEW.etapa_id
       OR fonte.edital_id IS DISTINCT FROM NEW.edital_id
       OR fonte.forma IS DISTINCT FROM NEW.forma
       OR fonte.pontuacao IS DISTINCT FROM NEW.pontuacao
       OR fonte.sentido IS DISTINCT FROM NEW.sentido
       OR fonte.estado <> 'CONCLUIDA'
       OR NOT fonte.ativo THEN
        RAISE EXCEPTION 'stage result does not match its source evaluation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def conferir_a_origem(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR)


def conferir_como_antes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR_ANTERIOR)


def herdar_a_versao_da_avaliacao(apps, schema_editor):
    """Cada Resultado recebe a versão da sua Avaliação — que é a que ele já reproduzia por junção.

    Uma consulta, e não um laço: `Subquery` correlacionada resolve tudo num `UPDATE` só. Nada de
    novo é afirmado — o Resultado passa a guardar a norma que a leitura por `avaliacao__versao`
    devolvia.

    Se sobrasse alguma linha sem versão, o `SET NOT NULL` seguinte falharia aqui e agora, e é o
    lugar certo de falhar: uma Avaliação concluída sem versão já é recusada por
    `ck_avaliacao_concluida_completa`, e o Resultado só nasce sobre conclusão.
    """
    from django.db.models import OuterRef, Subquery

    Avaliacao = apps.get_model("avaliacoes", "Avaliacao")
    Resultado = apps.get_model("resultados", "ResultadoEtapa")

    pendentes = Resultado.objects.filter(versao__isnull=True)
    if schema_editor.connection.vendor != "postgresql":
        pendentes.update(
            versao_id=Subquery(
                Avaliacao.objects.filter(pk=OuterRef("avaliacao_id")).values("versao_id")[:1]
            )
        )
        return
    schema_editor.execute(
        "ALTER TABLE resultados_resultadoetapa DISABLE TRIGGER resultado_etapa_append_only"
    )
    try:
        pendentes.update(
            versao_id=Subquery(
                Avaliacao.objects.filter(pk=OuterRef("avaliacao_id")).values("versao_id")[:1]
            )
        )
    finally:
        schema_editor.execute(
            "ALTER TABLE resultados_resultadoetapa ENABLE TRIGGER resultado_etapa_append_only"
        )


# A mesma guarda de `0002_resultado_por_forma`, e pelo mesmo motivo: reverter devolve `avaliacao` a
# obrigatória, e um Resultado por Ocorrência não tem Avaliação para oferecer. A recusa nomeia o ato
# que precisa vir antes, em vez de deixar o `migrate` falhar com um erro de coluna nula que não
# explica nada.
RECUSAR = (
    "Existem {quantas} Resultados de Etapa registrados por Ocorrência. Reverter esta migration "
    "devolveria a Avaliação a obrigatória, e esses Resultados não têm Avaliação. Desfazê-los é "
    "ato administrativo, e precisa acontecer antes."
)


def _recusar_se_houver_ocorrencia(apps, schema_editor):
    from django.db.migrations.exceptions import IrreversibleError

    quantas = (
        apps.get_model("resultados", "ResultadoEtapa").objects.filter(origem="OCORRENCIA").count()
    )
    if quantas:
        raise IrreversibleError(RECUSAR.format(quantas=quantas))


class Migration(migrations.Migration):
    # `publicacoes` entra por `versao`, e `avaliacoes` porque o SQL da função lê `versao_id` da
    # Avaliação: o grafo do Django não infere dependência de uma string de SQL.
    dependencies = [
        ("avaliacoes", "0003_sentido_restrito_aos_dois_valores"),
        ("inscricoes", "0003_cpf_na_submetida"),
        ("processos", "0001_initial"),
        ("publicacoes", "0008_remover_ancoras"),
        ("resultados", "0003_sentido_restrito_aos_dois_valores"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultadoetapa",
            name="origem",
            field=models.CharField(
                choices=[("AVALIACAO", "Avaliacao"), ("OCORRENCIA", "Ocorrencia")],
                default="AVALIACAO",
                max_length=20,
            ),
            # Todo Resultado que existe hoje nasceu de Avaliação — a coluna não podia ser nula —,
            # e o `DEFAULT` sai do esquema em seguida, para não afirmar para sempre que Resultado
            # sem origem declarada veio de Avaliação.
            preserve_default=False,
        ),
        # Anulável primeiro, preenchida depois, obrigatória por último: é a única ordem possível
        # numa tabela que já tem linhas e nenhum valor constante a oferecer.
        migrations.AddField(
            model_name="resultadoetapa",
            name="versao",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="resultados",
                to="publicacoes.versaoconsolidada",
            ),
        ),
        migrations.RunPython(herdar_a_versao_da_avaliacao, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="resultadoetapa",
            name="versao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="resultados",
                to="publicacoes.versaoconsolidada",
            ),
        ),
        migrations.AlterField(
            model_name="resultadoetapa",
            name="avaliacao",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="resultado_da_etapa",
                to="avaliacoes.avaliacao",
            ),
        ),
        migrations.AlterField(
            model_name="resultadoetapa",
            name="forma",
            field=models.CharField(
                blank=True,
                choices=[("PONTUADA", "Pontuada"), ("DECISORIA", "Decisoria")],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ("avaliacao__isnull", False),
                        ("origem", "AVALIACAO"),
                        models.Q(("forma", ""), _negated=True),
                    ),
                    models.Q(("avaliacao__isnull", True), ("forma", ""), ("origem", "OCORRENCIA")),
                    _connector="OR",
                ),
                name="ck_resultado_origem",
            ),
        ),
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
                    models.Q(("forma", ""), ("pontuacao__isnull", True), ("sentido", "")),
                    _connector="OR",
                ),
                name="ck_resultado_completo_por_forma",
            ),
        ),
        migrations.RunPython(conferir_a_origem, conferir_como_antes),
        # Última na lista, e por isso **primeira** na reversão.
        migrations.RunPython(migrations.RunPython.noop, _recusar_se_houver_ocorrencia),
    ]
