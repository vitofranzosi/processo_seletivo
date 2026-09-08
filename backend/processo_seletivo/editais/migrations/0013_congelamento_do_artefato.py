"""O artefato publicado é imutável — no banco, e não por disciplina da aplicação (020, FR-010).

A proteção não pode ser uniforme, e a razão é a mesma que a `0007` das publicações escreveu para a
Retificação: o artefato **muda legitimamente enquanto o ato está em curso** — quem elabora troca o
arquivo errado pelo certo, e quem retifica sobe o formulário novo antes de submeter. Congelá-lo por
completo quebraria o fluxo; deixá-lo livre depois de publicado apagaria conteúdo normativo.

A condição olha `OLD.congelado_em`: a transição que *congela* parte de nulo e é admitida; qualquer
alteração posterior encontra o instante gravado e é recusada. A mesma coluna que fecha a escrita é
a que abre a leitura pública, porque as duas perguntas são a mesma — artefato publicado é norma, e
norma é pública (FR-017).

`ArtefatoAnexo` fica **fora** de `TABELAS_APPEND_ONLY` por isso: retirar `UPDATE` e `DELETE` do
papel de runtime impediria a troca no rascunho. Quem separa os dois estados é a trigger, que o
privilégio não sabe distinguir.
"""

from django.db import migrations

PROTEGER = """
CREATE FUNCTION reject_frozen_artifact_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'published attachment artifacts are immutable';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER artefato_anexo_congelado_imutavel
BEFORE UPDATE OR DELETE ON editais_artefatoanexo
FOR EACH ROW WHEN (OLD.congelado_em IS NOT NULL)
EXECUTE FUNCTION reject_frozen_artifact_mutation();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS artefato_anexo_congelado_imutavel ON editais_artefatoanexo;
DROP FUNCTION IF EXISTS reject_frozen_artifact_mutation();
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
        ("editais", "0012_anexo_do_edital"),
    ]

    operations = [migrations.RunPython(proteger, desproteger)]
