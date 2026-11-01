"""Leva ao banco a imutabilidade da Inscrição enviada e dos documentos dela (009, FR-054 e FR-064).

A `Inscricao.save` e a `DocumentoSubmetido.save/delete` recusam desde a `009`, e a primeira diz na
própria docstring que "não é garantia de banco". A auditoria de prontidão de 31/10/2026 (A-03)
mostrou o que isso significava: como a role de produção, `UPDATE inscricoes_inscricao SET nome = …,
cpf = … WHERE status = 'SUBMETIDA'` passava, e devolver a enviada a `RASCUNHO` também. Nome e CPF
relacionais alimentam o resultado, a relação do sorteio, o arquivo de matrícula e o comprovante.

**Condicional ao estado, e por isso gatilho e não privilégio** — a razão de
`requerimentos/0002`, cujo molde este arquivo segue: o rascunho muda o tempo todo, e privilégio não
lê `status`. As duas tabelas ficam **fora** de `TABELAS_APPEND_ONLY`, e o total do provisionamento
não muda (`doc/parecer-a03-imutabilidade-2026-11-01.md`).

A condição olha `OLD.status`: o envio parte de `RASCUNHO` e passa; tudo o que vier depois encontra
`SUBMETIDA` e é recusado. Nenhum caminho de produção altera inscrição enviada — o parecer conferiu.

**O documento olha a Inscrição-mãe, e com `FOR SHARE`.** Ele não tem estado próprio. A leitura trava
a linha da Inscrição em modo compartilhado, que conflita com o `FOR NO KEY UPDATE` do `UPDATE` do
envio: uma escrita de documento que chegue durante o envio espera o envio terminar, relê
`SUBMETIDA` e é recusada. A trava da chave estrangeira não bastaria — `FOR KEY SHARE` não conflita
com o `UPDATE` do envio, que não muda a chave. Nos fluxos da aplicação a linha já está travada pela
própria transação (`_rascunho_travado`), e o `FOR SHARE` não espera nada. `FOR SHARE` exige `UPDATE`
na tabela travada, e a runtime o tem: `inscricoes_inscricao` não é append-only, e por isso a lição
de A-01 não se aplica aqui. Cobre também o `INSERT`: acrescentar documento a inscrição enviada muda
o que a comissão abre tanto quanto substituí-lo.

**Nada aqui importa `processo_seletivo`**: `'SUBMETIDA'` vai copiado (ver `requerimentos/0002`).
"""

from django.db import migrations

# Copiado de `Inscricao.Status.SUBMETIDA`, e **não** importado.
SUBMETIDA = "SUBMETIDA"

PROTEGER = f"""
CREATE FUNCTION reject_submitted_enrollment_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'submitted enrollments are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER inscricao_enviada_imutavel
BEFORE UPDATE OR DELETE ON inscricoes_inscricao
FOR EACH ROW WHEN (OLD.status = '{SUBMETIDA}')
EXECUTE FUNCTION reject_submitted_enrollment_mutation();

CREATE FUNCTION reject_submitted_document_mutation() RETURNS trigger AS $$
DECLARE
    parent_status text;
BEGIN
    -- `OLD` e `NEW` separados: mover um documento de uma inscrição para outra toca as duas.
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        SELECT status INTO parent_status
        FROM inscricoes_inscricao WHERE id = OLD.inscricao_id FOR SHARE;
        IF parent_status = '{SUBMETIDA}' THEN
            RAISE EXCEPTION 'documents of a submitted enrollment are immutable';
        END IF;
    END IF;
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        SELECT status INTO parent_status
        FROM inscricoes_inscricao WHERE id = NEW.inscricao_id FOR SHARE;
        IF parent_status = '{SUBMETIDA}' THEN
            RAISE EXCEPTION 'documents of a submitted enrollment are immutable';
        END IF;
    END IF;
    -- Numa trigger BEFORE, devolver OLD num UPDATE descartaria a alteração em silêncio.
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documento_da_enviada_imutavel
BEFORE INSERT OR UPDATE OR DELETE ON inscricoes_documentosubmetido
FOR EACH ROW EXECUTE FUNCTION reject_submitted_document_mutation();
"""

# A ordem importa: cada gatilho sai antes da função de que ele depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS documento_da_enviada_imutavel ON inscricoes_documentosubmetido;
DROP FUNCTION IF EXISTS reject_submitted_document_mutation();
DROP TRIGGER IF EXISTS inscricao_enviada_imutavel ON inscricoes_inscricao;
DROP FUNCTION IF EXISTS reject_submitted_enrollment_mutation();
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
    dependencies = [("inscricoes", "0006_valor_de_fato_append_only")]

    operations = [migrations.RunPython(proteger, desproteger)]
