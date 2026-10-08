"""Leva ao banco o que o registro de unidades e autoridades não pode perder (060, R-006).

**Cinco gatilhos, e nenhum privilégio a menos.** As duas tabelas mudam legitimamente: desativar a
Unidade, encerrar a autoridade e gravar o primeiro uso são `UPDATE`. E `TABELAS_APPEND_ONLY` revoga
`UPDATE` e `DELETE` juntos. Uma segunda lista, só sem `DELETE`, daria a segunda camada ao custo de
mudar o provisionamento e o `N de M` que o CLAUDE.md ensina a ler. Fica registrada como alternativa;
o gatilho é proporcional a duas tabelas de cadastro.

- **Nada se exclui** (FR-1109, FR-1120): a Publicação congela o identificador da autoridade e a
  trilha aponta para as duas pelo `id`.
- **O código da Unidade não muda** (FR-1108): é o valor do escopo institucional, e mudá-lo a
  desligaria de tudo o que o escopo já marcou.
- **A unidade da autoridade não muda**, nem antes do uso (FR-1121): a tela não expõe o campo, mas o
  que só a tela protege um `QuerySet.update()` distraído desfaz.
- **A autoridade usada não se reescreve** (FR-1121, `D-004`): nome, cargo, ato de nomeação, início e
  o próprio instante do primeiro uso. E o fim não pode cair antes do dia do primeiro ato, ou o
  registro passaria a dizer que ela não estava vigente quando assinou (FR-1120).

**O que o banco não cobre do encerramento retroativo.** A regra inteira, fim no dia do encerramento
ou depois, é do domínio. O banco cobre o caso grave, o fim antes do primeiro ato; entre o primeiro e
o último, só o comando protege, porque cobrir o intervalo pediria gravar o último uso a cada ato.

**Nada aqui importa `processo_seletivo`**: o fuso vai escrito por extenso, copiado de
`shared/tempo.ZONA`, pela razão de `requerimentos/0002` — migration que importa domínio muda
retroativamente o efeito de uma migration já executada.
"""

from django.db import migrations

# Copiado de `shared.tempo.ZONA`, e **não** importado — ver a docstring.
ZONA = "America/Sao_Paulo"

PROTEGER = f"""
CREATE FUNCTION reject_unit_deletion() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'unidades are never deleted; deactivate instead';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER unidade_nao_se_exclui
BEFORE DELETE ON unidades_unidade
FOR EACH ROW EXECUTE FUNCTION reject_unit_deletion();

CREATE FUNCTION reject_unit_code_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'the code of an unidade is immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER unidade_codigo_imutavel
BEFORE UPDATE ON unidades_unidade
FOR EACH ROW WHEN (OLD.codigo IS DISTINCT FROM NEW.codigo)
EXECUTE FUNCTION reject_unit_code_change();

CREATE FUNCTION reject_authority_deletion() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'authorities are never deleted; end their term instead';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER autoridade_nao_se_exclui
BEFORE DELETE ON unidades_autoridadehabilitada
FOR EACH ROW EXECUTE FUNCTION reject_authority_deletion();

CREATE FUNCTION reject_authority_unit_change() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'the unidade of an authority is immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER autoridade_unidade_imutavel
BEFORE UPDATE ON unidades_autoridadehabilitada
FOR EACH ROW WHEN (OLD.unidade_id IS DISTINCT FROM NEW.unidade_id)
EXECUTE FUNCTION reject_authority_unit_change();

CREATE FUNCTION reject_used_authority_rewrite() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'an authority already used in an act cannot be rewritten';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER autoridade_usada_imutavel
BEFORE UPDATE ON unidades_autoridadehabilitada
FOR EACH ROW WHEN (
    OLD.usada_em IS NOT NULL AND (
        (OLD.nome, OLD.cargo, OLD.ato_de_nomeacao, OLD.inicio_vigencia, OLD.usada_em)
            IS DISTINCT FROM
        (NEW.nome, NEW.cargo, NEW.ato_de_nomeacao, NEW.inicio_vigencia, NEW.usada_em)
        OR NEW.fim_vigencia < (OLD.usada_em AT TIME ZONE '{ZONA}')::date
    )
)
EXECUTE FUNCTION reject_used_authority_rewrite();
"""

# A ordem importa: cada gatilho sai antes da função de que ele depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS autoridade_usada_imutavel ON unidades_autoridadehabilitada;
DROP FUNCTION IF EXISTS reject_used_authority_rewrite();
DROP TRIGGER IF EXISTS autoridade_unidade_imutavel ON unidades_autoridadehabilitada;
DROP FUNCTION IF EXISTS reject_authority_unit_change();
DROP TRIGGER IF EXISTS autoridade_nao_se_exclui ON unidades_autoridadehabilitada;
DROP FUNCTION IF EXISTS reject_authority_deletion();
DROP TRIGGER IF EXISTS unidade_codigo_imutavel ON unidades_unidade;
DROP FUNCTION IF EXISTS reject_unit_code_change();
DROP TRIGGER IF EXISTS unidade_nao_se_exclui ON unidades_unidade;
DROP FUNCTION IF EXISTS reject_unit_deletion();
"""


def proteger(apps, schema_editor):
    # Fora do PostgreSQL é no-op, e é honesto que seja: fingir o gatilho no SQLite faria a suíte em
    # modo padrão afirmar uma garantia que não existe ali.
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(PROTEGER)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESPROTEGER)


class Migration(migrations.Migration):
    dependencies = [("unidades", "0001_initial")]

    operations = [migrations.RunPython(proteger, desproteger)]
