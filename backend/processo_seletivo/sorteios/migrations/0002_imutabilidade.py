"""As quatro triggers de imutabilidade do sorteio.

**A segunda camada, e ela não depende da aplicação se comportar.** `save`/`delete` recusam no
modelo; a role de runtime não recebe `UPDATE` nem `DELETE` (`seguranca/papeis.py`); e estas
triggers recusam mesmo quem tenha privilégio. As três são independentes, e é essa independência
que faz a garantia valer para quem chegue por fora — psql, script de manutenção, ORM de terceiro.

Nesta feature a imutabilidade não é higiene: a relação publicada **é** o compromisso do universo
anterior à semente. Uma linha que se pudesse reescrever depois de conhecida a ocorrência devolveria
ao certame exatamente a escolha que a `021` existe para eliminar (FR-007).
"""

from django.db import migrations

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_eligible_relation_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'eligible relations are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER relacao_de_habilitados_append_only
BEFORE UPDATE OR DELETE ON sorteios_relacaodehabilitados
FOR EACH ROW EXECUTE FUNCTION reject_eligible_relation_mutation();

CREATE OR REPLACE FUNCTION reject_eligible_participant_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'eligible participants are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER participante_habilitado_append_only
BEFORE UPDATE OR DELETE ON sorteios_participantehabilitado
FOR EACH ROW EXECUTE FUNCTION reject_eligible_participant_mutation();

CREATE OR REPLACE FUNCTION reject_source_occurrence_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'source occurrences are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER ocorrencia_da_fonte_append_only
BEFORE UPDATE OR DELETE ON sorteios_ocorrenciadafonte
FOR EACH ROW EXECUTE FUNCTION reject_source_occurrence_mutation();

CREATE OR REPLACE FUNCTION reject_draw_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'draws are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER sorteio_append_only
BEFORE UPDATE OR DELETE ON sorteios_sorteio
FOR EACH ROW EXECUTE FUNCTION reject_draw_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS sorteio_append_only ON sorteios_sorteio;
DROP FUNCTION IF EXISTS reject_draw_mutation();
DROP TRIGGER IF EXISTS ocorrencia_da_fonte_append_only ON sorteios_ocorrenciadafonte;
DROP FUNCTION IF EXISTS reject_source_occurrence_mutation();
DROP TRIGGER IF EXISTS participante_habilitado_append_only ON sorteios_participantehabilitado;
DROP FUNCTION IF EXISTS reject_eligible_participant_mutation();
DROP TRIGGER IF EXISTS relacao_de_habilitados_append_only ON sorteios_relacaodehabilitados;
DROP FUNCTION IF EXISTS reject_eligible_relation_mutation();
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
    dependencies = [("sorteios", "0001_initial")]

    operations = [migrations.RunPython(proteger, desproteger)]
