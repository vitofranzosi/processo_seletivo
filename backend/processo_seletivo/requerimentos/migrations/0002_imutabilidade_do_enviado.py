"""Leva ao banco a imutabilidade do requerimento enviado (029, `FR-396`).

**Condicional ao estado, e é por isso que é gatilho e não privilégio.** O requerimento muda
legitimamente enquanto é rascunho — a pessoa preenche em várias sessões, e `revision` avança a cada
gravação. Depois do envio, nada: ele virou peça de ato administrativo, a análise documental o lê, e
o indeferimento se funda nele. Alterá-lo reescreveria o que fundamentou uma decisão já tomada.

Imutabilidade condicional **não cabe em privilégio de tabela**: a role de runtime precisa de
`UPDATE` para o rascunho existir, e privilégio não sabe ler `status`. É a mesma razão pela qual
`Inscricao` e `Retificacao` ficam de fora de `TABELAS_APPEND_ONLY` — e por isso o total do
provisionamento continua **31**, e não 32.

A forma é a de `publicacoes/migrations/0007_imutabilidade_do_historico.py`, que congela a
Retificação em estado final com a razão escrita: *"o que precisa ser imutável é o que já produziu
efeito, então a trigger é condicional ao estado final"*.

**A guarda de aplicação continua existindo, e não é redundância.** Ela recusa cedo, com mensagem
legível para quem está no fluxo; este gatilho recusa **mesmo quem não passa por ela** — um
`QuerySet.update()` distraído, um comando de manutenção, um `psql` aberto. A `Inscricao` declara no
próprio comentário que a guarda dela *"não é garantia de banco"*, e foi esse achado que trouxe este
arquivo.

**Nada aqui importa `processo_seletivo`**: `'ENVIADO'` vai copiado. Migration que importa
domínio faz uma alteração futura mudar retroativamente o efeito de uma migration já executada, e
`test_migrations_do_not_import_domain_or_application_code` recusa.
"""

from django.db import migrations

# Copiado de `requerimentos.domain.nomes.ENVIADO`, e **não** importado — ver a docstring.
ENVIADO = "ENVIADO"

PROTEGER = f"""
CREATE FUNCTION reject_sent_enrollment_request_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'sent enrollment requests are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER requerimento_enviado_imutavel
BEFORE UPDATE OR DELETE ON requerimentos_requerimentodematricula
FOR EACH ROW WHEN (OLD.status = '{ENVIADO}')
EXECUTE FUNCTION reject_sent_enrollment_request_mutation();
"""

# **A reversão existe porque sem ela não há rollback de deploy**, e
# `test_every_migration_declares_a_reverse_path` recusa operação irreversível. A ordem importa: o
# gatilho sai antes da função de que ele depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS requerimento_enviado_imutavel ON requerimentos_requerimentodematricula;
DROP FUNCTION IF EXISTS reject_sent_enrollment_request_mutation();
"""


def proteger(apps, schema_editor):
    # Fora do PostgreSQL é no-op, e é honesto que seja: o SQLite não tem esta forma de gatilho, e
    # fingir que tem faria a suíte em modo padrão afirmar uma garantia que não existe ali.
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [("requerimentos", "0001_inicial")]

    operations = [migrations.RunPython(proteger, desproteger)]
