"""As quatro tabelas da entrega documental à formalização, e os gatilhos append-only (117).

**Duas camadas, independentes**: os gatilhos abaixo recusam a mutação mesmo de quem tem
privilégio, e o papel de runtime não recebe `UPDATE` nem `DELETE` — o segundo vem de
`TABELAS_APPEND_ONLY`, que passa a contar **53** tabelas com estas, e é por isso que o
provisionamento roda de novo depois.

**O gatilho de coerência confere o que `CHECK` não alcança**: o registro da exportação cita a
designação e a definição **do mesmo Edital**. Uma exportação gravada com a designação de outro
Edital diria que alguém foi autorizado a um pacote que nenhuma designação cobriu.

**Nenhuma definição nasce aqui** (FR-3660): os Editais existentes começam com a lista vazia.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_formalization_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'formalization records are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER definicao_formalizacao_append_only
BEFORE UPDATE OR DELETE ON formalizacao_definicaodosdocumentosdaformalizacao
FOR EACH ROW EXECUTE FUNCTION reject_formalization_mutation();
CREATE TRIGGER designacao_formalizacao_append_only
BEFORE UPDATE OR DELETE ON formalizacao_designacaoparaformalizacao
FOR EACH ROW EXECUTE FUNCTION reject_formalization_mutation();
CREATE TRIGGER revogacao_formalizacao_append_only
BEFORE UPDATE OR DELETE ON formalizacao_revogacaodadesignacao
FOR EACH ROW EXECUTE FUNCTION reject_formalization_mutation();
CREATE TRIGGER exportacao_formalizacao_append_only
BEFORE UPDATE OR DELETE ON formalizacao_exportacaodeformalizacao
FOR EACH ROW EXECUTE FUNCTION reject_formalization_mutation();

CREATE OR REPLACE FUNCTION check_formalization_export_coherence() RETURNS trigger AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM formalizacao_designacaoparaformalizacao
        WHERE id = NEW.designacao_id AND edital_id = NEW.edital_id
    ) THEN
        RAISE EXCEPTION 'formalization export cites a designation of another call';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM formalizacao_definicaodosdocumentosdaformalizacao
        WHERE id = NEW.definicao_id AND edital_id = NEW.edital_id
    ) THEN
        RAISE EXCEPTION 'formalization export cites a definition of another call';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER exportacao_formalizacao_coerente
BEFORE INSERT ON formalizacao_exportacaodeformalizacao
FOR EACH ROW EXECUTE FUNCTION check_formalization_export_coherence();
"""

# A ordem importa: cada gatilho sai antes da função de que depende.
DESPROTEGER = """
DROP TRIGGER IF EXISTS exportacao_formalizacao_coerente ON formalizacao_exportacaodeformalizacao;
DROP FUNCTION IF EXISTS check_formalization_export_coherence();
DROP TRIGGER IF EXISTS exportacao_formalizacao_append_only ON formalizacao_exportacaodeformalizacao;
DROP TRIGGER IF EXISTS revogacao_formalizacao_append_only ON formalizacao_revogacaodadesignacao;
DROP TRIGGER IF EXISTS designacao_formalizacao_append_only
    ON formalizacao_designacaoparaformalizacao;
DROP TRIGGER IF EXISTS definicao_formalizacao_append_only
    ON formalizacao_definicaodosdocumentosdaformalizacao;
DROP FUNCTION IF EXISTS reject_formalization_mutation();
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
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.CreateModel(
            name="DefinicaoDosDocumentosDaFormalizacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("requisitos", models.JSONField(blank=True, default=list)),
                ("motivo", models.TextField()),
                ("definido_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("definido_em", models.DateTimeField()),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="definicoes_da_formalizacao",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "ordering": ["definido_em", "id"],
            },
        ),
        migrations.CreateModel(
            name="DesignacaoParaFormalizacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("pessoa", models.CharField(max_length=255)),
                ("perfis", models.JSONField(blank=True, default=list)),
                ("motivo", models.TextField()),
                ("designado_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("designado_em", models.DateTimeField()),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="designacoes_da_formalizacao",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "ordering": ["designado_em", "id"],
            },
        ),
        migrations.CreateModel(
            name="ExportacaoDeFormalizacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("alcance", models.CharField(max_length=16)),
                ("perfil_id", models.UUIDField(blank=True, null=True)),
                ("resultado", models.CharField(max_length=16)),
                ("pessoas", models.JSONField(default=list)),
                ("documentos", models.JSONField(default=list)),
                ("quantidade_de_arquivos", models.PositiveIntegerField()),
                ("tamanho", models.PositiveBigIntegerField()),
                ("hash_do_pacote", models.CharField(max_length=64)),
                ("exportado_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("exportado_em", models.DateTimeField()),
                (
                    "definicao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="exportacoes",
                        to="formalizacao.definicaodosdocumentosdaformalizacao",
                    ),
                ),
                (
                    "designacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="exportacoes",
                        to="formalizacao.designacaoparaformalizacao",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="exportacoes_da_formalizacao",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "ordering": ["-exportado_em", "-id"],
            },
        ),
        migrations.CreateModel(
            name="RevogacaoDaDesignacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("motivo", models.TextField()),
                ("revogado_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("revogado_em", models.DateTimeField()),
                (
                    "designacao",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="revogacao",
                        to="formalizacao.designacaoparaformalizacao",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="definicaodosdocumentosdaformalizacao",
            index=models.Index(fields=["edital", "definido_em"], name="ix_definicao_formalizacao"),
        ),
        migrations.AddConstraint(
            model_name="definicaodosdocumentosdaformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("motivo", ""), _negated=True),
                name="ck_definicao_formalizacao_com_motivo",
            ),
        ),
        migrations.AddIndex(
            model_name="designacaoparaformalizacao",
            index=models.Index(fields=["edital", "pessoa"], name="ix_designacao_formalizacao"),
        ),
        migrations.AddIndex(
            model_name="designacaoparaformalizacao",
            index=models.Index(fields=["pessoa"], name="ix_designacao_formalizacao_pes"),
        ),
        migrations.AddConstraint(
            model_name="designacaoparaformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("motivo", ""), _negated=True),
                name="ck_designacao_formalizacao_com_motivo",
            ),
        ),
        migrations.AddConstraint(
            model_name="designacaoparaformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("designado_por", models.F("pessoa")), _negated=True),
                name="ck_designacao_formalizacao_sem_autodesignacao",
            ),
        ),
        migrations.AddIndex(
            model_name="exportacaodeformalizacao",
            index=models.Index(
                fields=["edital", "exportado_em"], name="ix_exportacao_formalizacao"
            ),
        ),
        migrations.AddConstraint(
            model_name="exportacaodeformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("alcance__in", ["PESSOA", "SELECAO", "RECORTE"])),
                name="ck_exportacao_formalizacao_alcance",
            ),
        ),
        migrations.AddConstraint(
            model_name="exportacaodeformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("resultado__in", ["COMPLETO", "PARCIAL"])),
                name="ck_exportacao_formalizacao_resultado",
            ),
        ),
        migrations.AddConstraint(
            model_name="exportacaodeformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("hash_do_pacote", ""), _negated=True),
                name="ck_exportacao_formalizacao_hash",
            ),
        ),
        migrations.AddConstraint(
            model_name="exportacaodeformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("quantidade_de_arquivos__gt", 0)),
                name="ck_exportacao_formalizacao_com_arquivo",
            ),
        ),
        migrations.AddConstraint(
            model_name="exportacaodeformalizacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("alcance", "PESSOA"), _negated=True),
                    models.Q(("perfil_id__isnull", True), ("resultado", "COMPLETO")),
                    _connector="OR",
                ),
                name="ck_exportacao_formalizacao_pessoa",
            ),
        ),
        migrations.AddConstraint(
            model_name="revogacaodadesignacao",
            constraint=models.CheckConstraint(
                condition=models.Q(("motivo", ""), _negated=True),
                name="ck_revogacao_formalizacao_com_motivo",
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
