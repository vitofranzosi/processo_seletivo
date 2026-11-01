"""Leva ao banco a imutabilidade da Homologação — salvo a revogação, uma vez.

Como a role de produção, `UPDATE publicacoes_homologacao SET homologated_by = 'alguem'` passava
(A-03, auditoria de prontidão de 31/10/2026): a autoria de um ato que liberou o Edital para
publicação podia ser reescrita sem que nada recusasse.

**Não é append-only**, e por isso fica fora de `TABELAS_APPEND_ONLY`: a revogação
(`publish_edital.revoke_homologation`) grava `revoked_at`, `revoked_by` e `revocation_reason` na
própria linha. É a única escrita depois do `INSERT`, e o gatilho admite só ela — com a homologação
ainda vigente, preenchendo instante, autor e motivo, e sem tocar o que foi homologado, por quem,
quando e por quê. O motivo é obrigatório no contrato (`MotivoRequest`, `minLength: 1`), na tela
(`exige_motivo`) e no comando; o gatilho diz o mesmo a quem não passa por nenhum deles. Revogar de
novo, reescrever a revogação ou apagar a linha são recusados.

O modelo **não** ganha `save`/`delete` que recusem: o guardião de
`test_imutabilidade_do_historico` exige que todo modelo que se declara append-only esteja em
`TABELAS_APPEND_ONLY`, e este não é.
"""

from django.db import migrations

PROTEGER = """
CREATE FUNCTION reject_homologation_mutation() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'UPDATE'
       AND OLD.revoked_at IS NULL
       AND NEW.revoked_at IS NOT NULL
       AND NEW.revoked_by <> ''
       AND btrim(NEW.revocation_reason) <> ''
       AND NEW.id = OLD.id
       AND NEW.revisao_id = OLD.revisao_id
       AND NEW.homologated_by = OLD.homologated_by
       AND NEW.reason = OLD.reason
       AND NEW.homologated_at = OLD.homologated_at
    THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'homologations are immutable except by a single revocation';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER homologacao_imutavel
BEFORE UPDATE OR DELETE ON publicacoes_homologacao
FOR EACH ROW EXECUTE FUNCTION reject_homologation_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS homologacao_imutavel ON publicacoes_homologacao;
DROP FUNCTION IF EXISTS reject_homologation_mutation();
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
    dependencies = [("publicacoes", "0011_redacao_do_documento")]

    operations = [migrations.RunPython(proteger, desproteger)]
