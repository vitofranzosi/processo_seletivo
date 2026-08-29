"""Leva a imutabilidade do histórico normativo para o banco (FR-023 da 003).

`VersaoConsolidada`, `Publicacao`, `DocumentoPublicado` e a auditoria já eram protegidas por
trigger. `Retificacao`, `AlteracaoNormativa`, `AtoAdministrativo` e `RevisaoEdital` dependiam de
disciplina da aplicação: um `QuerySet.update()` distraído, um script de manutenção ou acesso
administrativo direto reescreveriam ato normativo já publicado sem que nada recusasse.

A proteção não pode ser uniforme, porque as tabelas não são iguais:

- `AtoAdministrativo` e `RevisaoEdital` **nascem imutáveis** — a aplicação só as cria, nunca as
  altera. Trigger absoluta.
- `Retificacao` e `AlteracaoNormativa` **mudam legitimamente enquanto o ato está em curso**: a
  Retificação transita de estado, é devolvida, é editada; as alterações são substituídas a cada
  edição de rascunho. Congelá-las por completo quebraria o fluxo. O que precisa ser imutável é o
  que já produziu efeito, então a trigger é condicional ao estado final.

A condição olha `OLD.status`: a transição que *torna* a Retificação final parte de um estado não
final e é admitida; qualquer alteração posterior encontra `PUBLICADA` ou `CANCELADA` e é recusada.
"""

from django.db import migrations

FINAIS = "('PUBLICADA', 'CANCELADA')"

PROTEGER = f"""
CREATE FUNCTION reject_final_retification_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'retifications in a final state are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER retificacao_final_imutavel
BEFORE UPDATE OR DELETE ON publicacoes_retificacao
FOR EACH ROW WHEN (OLD.status IN {FINAIS})
EXECUTE FUNCTION reject_final_retification_mutation();

CREATE FUNCTION reject_final_change_mutation() RETURNS trigger AS $$
DECLARE
    parent_status text;
BEGIN
    SELECT status INTO parent_status
    FROM publicacoes_retificacao WHERE id = OLD.retificacao_id;
    IF parent_status IN {FINAIS} THEN
        RAISE EXCEPTION 'normative changes of a final retification are immutable';
    END IF;
    -- Numa trigger BEFORE, o valor devolvido é a linha que segue adiante: devolver OLD num
    -- UPDATE descartaria a alteração em silêncio, que é pior do que não ter trigger nenhuma.
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER alteracao_normativa_final_imutavel
BEFORE UPDATE OR DELETE ON publicacoes_alteracaonormativa
FOR EACH ROW EXECUTE FUNCTION reject_final_change_mutation();

CREATE FUNCTION reject_administrative_act_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'administrative acts are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ato_administrativo_append_only
BEFORE UPDATE OR DELETE ON processos_atoadministrativo
FOR EACH ROW EXECUTE FUNCTION reject_administrative_act_mutation();

CREATE FUNCTION reject_edital_revision_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'edital revisions are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER revisao_edital_append_only
BEFORE UPDATE OR DELETE ON publicacoes_revisaoedital
FOR EACH ROW EXECUTE FUNCTION reject_edital_revision_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS retificacao_final_imutavel ON publicacoes_retificacao;
DROP FUNCTION IF EXISTS reject_final_retification_mutation();
DROP TRIGGER IF EXISTS alteracao_normativa_final_imutavel ON publicacoes_alteracaonormativa;
DROP FUNCTION IF EXISTS reject_final_change_mutation();
DROP TRIGGER IF EXISTS ato_administrativo_append_only ON processos_atoadministrativo;
DROP FUNCTION IF EXISTS reject_administrative_act_mutation();
DROP TRIGGER IF EXISTS revisao_edital_append_only ON publicacoes_revisaoedital;
DROP FUNCTION IF EXISTS reject_edital_revision_mutation();
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [
        ("publicacoes", "0006_backfill_precondicoes"),
        ("processos", "0001_initial"),
    ]

    operations = [migrations.RunPython(proteger, desproteger)]
