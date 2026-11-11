"""O detalhamento por critério na Avaliação e na Conclusão preservada (146, D-004, FR-5219).

Duas colunas JSON com default `[]`, e nenhuma tabela nova: o detalhamento é sempre lido e escrito
junto com a conclusão, e a tabela das conclusões já é append-only nas duas camadas. Acrescentar a
coluna com default não reescreve linha nem dispara gatilho — o PostgreSQL grava o default no
catálogo —, e por isso a `ConclusaoAvaliacao` recebe a coluna sem que a proteção dela seja tocada.

**O cuidado é o gatilho da concluída** (`avaliacoes/0004`). A função enumera, coluna a coluna, o
que a reabertura não muda; uma coluna nova fora da lista ficaria mutável justamente no ato que
reabre, e `SET estado = 'RASCUNHO', criterios = '[…]'` passaria como reabertura. A função é
recriada aqui com `criterios` na lista, e a desfeita devolve a anterior.
"""

from django.db import migrations, models

# Copiados de `Avaliacao.Estado`, e **não** importados (ver `requerimentos/0002`).
RASCUNHO = "RASCUNHO"


def _funcao(com_criterios):
    criterios = (
        "\n       AND NEW.criterios IS NOT DISTINCT FROM OLD.criterios" if com_criterios else ""
    )
    return f"""
CREATE OR REPLACE FUNCTION reject_concluded_evaluation_mutation() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND NEW.estado = '{RASCUNHO}'
       AND NEW.concluida_em IS NULL
       AND NEW.concluida_por = ''
       AND NEW.versao_id IS NULL
       AND NEW.revision = OLD.revision + 1
       AND NEW.id = OLD.id
       AND NEW.atribuicao_id = OLD.atribuicao_id
       AND NEW.identity_subject = OLD.identity_subject
       AND NEW.etapa_id = OLD.etapa_id
       AND NEW.inscricao_id = OLD.inscricao_id
       AND NEW.forma = OLD.forma
       AND NEW.pontuacao IS NOT DISTINCT FROM OLD.pontuacao
       AND NEW.sentido = OLD.sentido
       AND NEW.parecer = OLD.parecer{criterios}
    THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'concluded evaluations are immutable except by reopening';
END;
$$ LANGUAGE plpgsql;
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(_funcao(com_criterios=True))


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(_funcao(com_criterios=False))


class Migration(migrations.Migration):
    dependencies = [("avaliacoes", "0004_imutabilidade_da_concluida")]

    operations = [
        migrations.AddField(
            model_name="avaliacao",
            name="criterios",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="conclusaoavaliacao",
            name="criterios",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
