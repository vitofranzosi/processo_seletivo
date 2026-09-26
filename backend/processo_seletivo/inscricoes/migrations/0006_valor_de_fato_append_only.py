"""O gatilho que faltava ao `ValorDeFato` (015, D-2; `doc/achado-valor-de-fato-sem-gatilho.md`).

A tabela nasceu na `0004` como `CreateModel` puro e entrou em `TABELAS_APPEND_ONLY`: o runtime não
tem `UPDATE` nem `DELETE`, e essa era a única camada. Quem conecta com privilégio — a role de
migração, o superusuário da suíte, uma correção pelo `psql` — reescrevia o valor congelado em
silêncio, e o `AtoDeOrdenacao` que o leu passaria a citar uma entrada que já não é a dele.

**Não percorre linha nenhuma.** Nada atualiza nem apaga a tabela fora deste gatilho — a única
escrita é o `bulk_create` do envio —, e por isso ele não tem o que quebrar no que já existe.

**Esperou a `0005`.** A correção foi decidida em 25/09 para depois da `044`, porque uma `0005`
escrita da `main` de então abriria duas folhas no grafo de `inscricoes`.
"""

from django.db import migrations

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_frozen_fact_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'frozen fact values are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER valor_de_fato_append_only
BEFORE UPDATE OR DELETE ON inscricoes_valordefato
FOR EACH ROW EXECUTE FUNCTION reject_frozen_fact_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS valor_de_fato_append_only ON inscricoes_valordefato;
DROP FUNCTION IF EXISTS reject_frozen_fact_mutation();
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
        ("inscricoes", "0005_item_da_lista_exigida"),
    ]

    operations = [
        migrations.RunPython(proteger, desproteger),
    ]
