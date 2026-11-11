"""A publicação de convocados no GPS: o ato, o vínculo de cada convocação e o documento (148).

**Nascem append-only, nas três camadas**: `save`/`delete` recusam na aplicação, as triggers abaixo
recusam a mutação mesmo de quem tem privilégio, e o papel de runtime não recebe `UPDATE` nem
`DELETE` — o terceiro vem de `TABELAS_APPEND_ONLY`, e é por isso que o provisionamento precisa rodar
de novo depois desta migration (o `M` passa de 53 a 56).

**A trigger de coerência confere o que `CHECK` não alcança**, porque atravessa tabelas: a
convocação, a comunicação e o ato são do mesmo Edital; a comunicação é da convocação; e, no efeito
*convoca*, a comunicação é a publicação registrada pelo próprio ato, no instante dele (D-003). Sem
ela, um caminho que não passasse pela aplicação poderia ligar ao ato uma comunicação de outra
pessoa — e a página do candidato apontaria para a publicação errada.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_published_call_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'published calls are append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER publicacao_de_convocados_append_only
BEFORE UPDATE OR DELETE ON convocacao_publicacaodeconvocados
FOR EACH ROW EXECUTE FUNCTION reject_published_call_mutation();

CREATE TRIGGER convocacao_publicada_append_only
BEFORE UPDATE OR DELETE ON convocacao_convocacaopublicada
FOR EACH ROW EXECUTE FUNCTION reject_published_call_mutation();

CREATE TRIGGER documento_da_publicacao_de_convocados_append_only
BEFORE UPDATE OR DELETE ON convocacao_documentodapublicacaodeconvocados
FOR EACH ROW EXECUTE FUNCTION reject_published_call_mutation();

CREATE OR REPLACE FUNCTION check_published_call_coherence() RETURNS trigger AS $$
DECLARE
    ato RECORD;
    chamada RECORD;
    emitida RECORD;
BEGIN
    SELECT p.edital_id, p.publicado_em INTO ato
      FROM convocacao_publicacaodeconvocados p WHERE p.id = NEW.publicacao_id;
    SELECT c.edital_id INTO chamada
      FROM convocacao_convocacao c WHERE c.id = NEW.convocacao_id;
    SELECT e.convocacao_id, e.forma, e.resultado, e.enviado_em INTO emitida
      FROM convocacao_comunicacaoemitida e WHERE e.id = NEW.comunicacao_id;
    IF chamada.edital_id IS DISTINCT FROM ato.edital_id THEN
        RAISE EXCEPTION 'published call from another notice';
    END IF;
    IF emitida.convocacao_id IS DISTINCT FROM NEW.convocacao_id THEN
        RAISE EXCEPTION 'published call cites a communication of another call';
    END IF;
    IF emitida.resultado IS DISTINCT FROM 'ENVIADA' THEN
        RAISE EXCEPTION 'published call cites a communication that did not succeed';
    END IF;
    IF NEW.efeito = 'CONVOCA' AND (
        emitida.forma IS DISTINCT FROM 'PUBLICATION'
        OR emitida.enviado_em IS DISTINCT FROM ato.publicado_em
    ) THEN
        RAISE EXCEPTION 'a call published by the act is the publication recorded at its instant';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER convocacao_publicada_coerente
BEFORE INSERT ON convocacao_convocacaopublicada
FOR EACH ROW EXECUTE FUNCTION check_published_call_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS convocacao_publicada_coerente ON convocacao_convocacaopublicada;
DROP FUNCTION IF EXISTS check_published_call_coherence();
DROP TRIGGER IF EXISTS documento_da_publicacao_de_convocados_append_only
    ON convocacao_documentodapublicacaodeconvocados;
DROP TRIGGER IF EXISTS convocacao_publicada_append_only ON convocacao_convocacaopublicada;
DROP TRIGGER IF EXISTS publicacao_de_convocados_append_only ON convocacao_publicacaodeconvocados;
DROP FUNCTION IF EXISTS reject_published_call_mutation();
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
        ("convocacao", "0006_modelo_da_mensagem"),
        ("processos", "0005_escopo_imutavel"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicacaoDeConvocados",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("numero", models.PositiveIntegerField()),
                ("conteudo_publico", models.BinaryField()),
                ("conteudo_publico_hash", models.CharField(max_length=64)),
                ("publicado_por", models.CharField(max_length=255)),
                ("publicado_em", models.DateTimeField()),
                ("declaracao_do_veiculo", models.TextField(blank=True, default="")),
                ("signatario_id", models.UUIDField()),
                ("signatario_nome", models.CharField(max_length=255)),
                ("signatario_cargo", models.CharField(max_length=255)),
                (
                    "signatario_ato_de_nomeacao",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("unidade_codigo", models.CharField(blank=True, default="", max_length=100)),
                ("unidade_sigla", models.CharField(blank=True, default="", max_length=30)),
                ("unidade_nome", models.CharField(blank=True, default="", max_length=255)),
                ("unidade_cabecalho", models.JSONField(default=list)),
                ("unidade_local", models.CharField(blank=True, default="", max_length=120)),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_de_convocados",
                        to="processos.edital",
                    ),
                ),
            ],
            options={
                "ordering": ["edital", "numero"],
            },
        ),
        migrations.CreateModel(
            name="DocumentoDaPublicacaoDeConvocados",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("bytes", models.BinaryField()),
                ("content_type", models.CharField(default="application/pdf", max_length=100)),
                ("documento_hash", models.CharField(max_length=64)),
                (
                    "publicacao",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documento",
                        to="convocacao.publicacaodeconvocados",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ConvocacaoPublicada",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "efeito",
                    models.CharField(
                        choices=[("CONVOCA", "Convoca"), ("DIVULGA", "Divulga")], max_length=8
                    ),
                ),
                (
                    "comunicacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_de_convocados",
                        to="convocacao.comunicacaoemitida",
                    ),
                ),
                (
                    "convocacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_de_convocados",
                        to="convocacao.convocacao",
                    ),
                ),
                (
                    "publicacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="convocacoes_publicadas",
                        to="convocacao.publicacaodeconvocados",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="publicacaodeconvocados",
            constraint=models.UniqueConstraint(
                fields=("edital", "numero"), name="uq_publicacao_de_convocados_numero"
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodeconvocados",
            constraint=models.CheckConstraint(
                condition=models.Q(("numero__gte", 1)),
                name="ck_publicacao_de_convocados_numero_positivo",
            ),
        ),
        migrations.AddIndex(
            model_name="convocacaopublicada",
            index=models.Index(fields=["publicacao"], name="ix_convocacao_publicada_ato"),
        ),
        migrations.AddConstraint(
            model_name="convocacaopublicada",
            constraint=models.UniqueConstraint(
                fields=("convocacao",), name="uq_convocacao_publicada_uma_vez"
            ),
        ),
        migrations.AddConstraint(
            model_name="convocacaopublicada",
            constraint=models.UniqueConstraint(
                fields=("comunicacao",), name="uq_convocacao_publicada_por_comunicacao"
            ),
        ),
        migrations.AddConstraint(
            model_name="convocacaopublicada",
            constraint=models.CheckConstraint(
                condition=models.Q(("efeito__in", ["CONVOCA", "DIVULGA"])),
                name="ck_convocacao_publicada_efeito",
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
