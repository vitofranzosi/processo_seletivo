"""O registro de geração do arquivo de importação, e a trava que o mantém append-only (031).

**Duas camadas, e elas são independentes** — a forma que a `019` e a `014` já usam. O privilégio
ausente vem de `seguranca/papeis.py::TABELAS_APPEND_ONLY`, que passa a contar **32** tabelas com
esta; o gatilho abaixo recusa a mutação mesmo de quem tenha privilégio. Nenhuma das duas depende de
a aplicação se comportar, e é por isso que as duas existem.

**Fora do PostgreSQL o gatilho é no-op, e é honesto que seja**: o SQLite não tem esta forma de
gatilho, e fingir que tem faria a suíte em modo padrão afirmar uma garantia que não existe ali. É
por isso que o roteiro desta feature roda `make test-pg`, e não `make test`.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE FUNCTION reject_enrollment_export_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'enrollment file generations are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER geracao_de_arquivo_append_only
BEFORE UPDATE OR DELETE ON matriculas_geracaodearquivo
FOR EACH ROW EXECUTE FUNCTION reject_enrollment_export_mutation();
"""

# **A reversão existe porque sem ela não há rollback de deploy**, e
# `test_every_migration_declares_a_reverse_path` recusa operação irreversível. A ordem importa: o
# gatilho sai antes da função de que ele depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS geracao_de_arquivo_append_only ON matriculas_geracaodearquivo;
DROP FUNCTION IF EXISTS reject_enrollment_export_mutation();
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
    initial = True

    dependencies = [
        ("processos", "0004_metodo_de_sorteio_comum"),
    ]

    operations = [
        migrations.CreateModel(
            name="GeracaoDeArquivo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "populacao_especie",
                    models.CharField(
                        choices=[("CONVOCACAO", "CONVOCACAO"), ("RESULTADO", "RESULTADO")],
                        max_length=20,
                    ),
                ),
                ("populacao_referencia", models.UUIDField()),
                ("populacao_rotulo", models.CharField(max_length=255)),
                ("quantidade_de_linhas", models.PositiveIntegerField()),
                ("versao_do_resultado", models.CharField(max_length=64)),
                ("versao_dos_mapeamentos", models.PositiveIntegerField()),
                ("requerimentos", models.JSONField(default=list)),
                ("gerado_por", models.CharField(max_length=255)),
                ("gerado_em", models.DateTimeField()),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="geracoes_de_matricula",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "verbose_name": "geração de arquivo de matrícula",
                "verbose_name_plural": "gerações de arquivo de matrícula",
                "indexes": [
                    models.Index(
                        fields=["edital", "-gerado_em"], name="matriculas__edital__594c7f_idx"
                    )
                ],
            },
        ),
        migrations.RunPython(proteger, desproteger),
    ]
