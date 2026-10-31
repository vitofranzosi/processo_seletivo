"""O escopo de Processo Seletivo e de Edital não muda depois de criado (110, FR-3333, `D-013`).

O escopo é a unidade a que o objeto pertence, e cada leitura da gestão filtra por ele. Nenhum
caminho da aplicação o muda — a varredura de 31/10 não achou `update` nem atribuição fora da
criação —, mas um `QuerySet.update()` distraído, ou SQL direto, moveria um Edital para outra
unidade sem que nada recusasse: os atos, os vínculos e a trilha continuariam na de origem.

**Dois gatilhos, e nenhum privilégio a menos.** As duas tabelas mudam legitimamente em outras
colunas, e por isso ficam fora de `TABELAS_APPEND_ONLY`; o `M` do provisionamento não muda. É o
molde de `unidade_codigo_imutavel` (`unidades/0002`): `IS DISTINCT FROM` deixa passar o `save()`
completo que regrava o mesmo valor, e recusa só a mudança, venha de onde vier.

**Por que não uma chave estrangeira para `Unidade.codigo`**: ela conferiria a existência da unidade
na inserção, que não é o risco com causa plausível, e não impediria mover o objeto para outra
unidade existente, que é. E custaria registrar a unidade alheia em todo teste de isolamento
(decisão dois da `060`).
"""

from django.db import migrations

PROTEGER = """
CREATE FUNCTION reject_processo_scope_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'the institution scope of a processo is immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER processo_escopo_imutavel
BEFORE UPDATE ON processos_processoseletivo
FOR EACH ROW WHEN (OLD.institution_scope IS DISTINCT FROM NEW.institution_scope)
EXECUTE FUNCTION reject_processo_scope_change();

CREATE FUNCTION reject_edital_scope_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'the institution scope of an edital is immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER edital_escopo_imutavel
BEFORE UPDATE ON processos_edital
FOR EACH ROW WHEN (OLD.institution_scope IS DISTINCT FROM NEW.institution_scope)
EXECUTE FUNCTION reject_edital_scope_change();
"""

# A ordem importa: cada gatilho sai antes da função de que ele depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS edital_escopo_imutavel ON processos_edital;
DROP FUNCTION IF EXISTS reject_edital_scope_change();
DROP TRIGGER IF EXISTS processo_escopo_imutavel ON processos_processoseletivo;
DROP FUNCTION IF EXISTS reject_processo_scope_change();
"""


def proteger(apps, schema_editor):
    # Fora do PostgreSQL é no-op, como na `unidades/0002`: fingir o gatilho no SQLite faria a suíte
    # em modo padrão afirmar uma garantia que não existe ali.
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [("processos", "0004_metodo_de_sorteio_comum")]

    operations = [migrations.RunPython(proteger, desproteger)]
