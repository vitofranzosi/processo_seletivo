"""Leva ao banco a imutabilidade da Avaliação concluída, salvo a reabertura (012, FR-036, FR-094).

Como a role de produção, `UPDATE avaliacoes_avaliacao SET pontuacao = pontuacao + 10 WHERE estado =
'CONCLUIDA'` passava (A-03, auditoria de prontidão de 31/10/2026). A `ConclusaoAvaliacao` guardava
a cópia, mas o Resultado lê a Avaliação, e a nota corrente podia divergir da preservada sem que nada
recusasse.

**Uma transição sai legitimamente de `CONCLUIDA`: a reabertura da presidência**
(`avaliacao.reabrir`). Ela tem forma exata, e o gatilho exige essa forma campo a campo: estado volta
a `RASCUNHO`; `concluida_em`, `concluida_por` e `versao` são zerados; a revisão avança **uma**
unidade, como `compare_and_swap` faz; **todo o resto fica igual**. Admitir "qualquer `UPDATE` que
leve a `RASCUNHO`" deixaria passar `SET estado = 'RASCUNHO', pontuacao = 99` como se fosse
reabertura. Nota, sentido e parecer ficam,
porque são o ponto de partida do rascunho reaberto; o que governou a conclusão anterior está na
`ConclusaoAvaliacao`, que é append-only nas duas camadas.

**O limite, dito para que ninguém o leia como mais do que é.** O gatilho garante a *forma* da
transição, e não *quem* a pratica: um `UPDATE` cru com privilégio de escrita que reproduza
exatamente a reabertura passa. A autorização da presidência, o motivo, o `AtoAdministrativo` e a
trilha continuam sendo da aplicação, e não há segundo mecanismo de autorização no banco. O que o
banco passa a garantir é que nenhuma escrita reescreve o conteúdo de uma conclusão.

Fora daqui, deliberadamente: conferir que existe `ConclusaoAvaliacao` para a conclusão reaberta, e
que nenhum Resultado vigente se funda nela (`_recusar_se_fundamenta_resultado`). Seriam garantias
novas, além do que A-03 pede (`doc/parecer-a03-imutabilidade-2026-11-01.md`).

A tabela fica fora de `TABELAS_APPEND_ONLY`: o rascunho muda, e privilégio não lê `estado`.
"""

from django.db import migrations

# Copiados de `Avaliacao.Estado`, e **não** importados (ver `requerimentos/0002`).
CONCLUIDA = "CONCLUIDA"
RASCUNHO = "RASCUNHO"

PROTEGER = f"""
CREATE FUNCTION reject_concluded_evaluation_mutation() RETURNS trigger AS $$
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
       AND NEW.parecer = OLD.parecer
    THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'concluded evaluations are immutable except by reopening';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER avaliacao_concluida_imutavel
BEFORE UPDATE OR DELETE ON avaliacoes_avaliacao
FOR EACH ROW WHEN (OLD.estado = '{CONCLUIDA}')
EXECUTE FUNCTION reject_concluded_evaluation_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS avaliacao_concluida_imutavel ON avaliacoes_avaliacao;
DROP FUNCTION IF EXISTS reject_concluded_evaluation_mutation();
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
    dependencies = [("avaliacoes", "0003_sentido_restrito_aos_dois_valores")]

    operations = [migrations.RunPython(proteger, desproteger)]
