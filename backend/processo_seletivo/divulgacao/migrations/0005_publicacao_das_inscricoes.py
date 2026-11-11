"""A publicação das inscrições (148): o ato, a projeção individual e as três camadas de proteção.

As duas tabelas nascem vazias, e nenhuma linha existente é percorrida (FR-5437). Os gatilhos são os
da `0001`: append-only nas duas, e a coerência do sucessor — mesma cadeia, mesmo Edital, natureza
que não regride. A regressão também é recusada pela aplicação, com mensagem; aqui ela é a segunda
camada, que vale para quem chegar por fora.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_inscriptions_publication_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'inscriptions publications are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER publicacao_das_inscricoes_append_only
BEFORE UPDATE OR DELETE ON divulgacao_publicacaodasinscricoes
FOR EACH ROW EXECUTE FUNCTION reject_inscriptions_publication_mutation();
CREATE TRIGGER inscricao_na_publicacao_append_only
BEFORE UPDATE OR DELETE ON divulgacao_inscricaonapublicacao
FOR EACH ROW EXECUTE FUNCTION reject_inscriptions_publication_mutation();

CREATE OR REPLACE FUNCTION check_inscriptions_publication_coherence() RETURNS trigger AS $$
DECLARE
    anterior RECORD;
    ordem_nova INTEGER;
    ordem_anterior INTEGER;
BEGIN
    IF NEW.publicacao_anterior_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT p.edital_id, p.natureza INTO anterior
      FROM divulgacao_publicacaodasinscricoes p
     WHERE p.id = NEW.publicacao_anterior_id;
    IF NOT FOUND OR anterior.edital_id IS DISTINCT FROM NEW.edital_id THEN
        RAISE EXCEPTION 'inscriptions publication succeeds a publication of another edital';
    END IF;
    ordem_nova := CASE NEW.natureza
        WHEN 'RECEBIDAS' THEN 0 WHEN 'PRELIMINAR' THEN 1 ELSE 2 END;
    ordem_anterior := CASE anterior.natureza
        WHEN 'RECEBIDAS' THEN 0 WHEN 'PRELIMINAR' THEN 1 ELSE 2 END;
    IF ordem_nova < ordem_anterior THEN
        RAISE EXCEPTION 'inscriptions publication nature regresses';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER publicacao_das_inscricoes_coerente
BEFORE INSERT ON divulgacao_publicacaodasinscricoes
FOR EACH ROW EXECUTE FUNCTION check_inscriptions_publication_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS publicacao_das_inscricoes_coerente ON divulgacao_publicacaodasinscricoes;
DROP FUNCTION IF EXISTS check_inscriptions_publication_coherence();
DROP TRIGGER IF EXISTS inscricao_na_publicacao_append_only ON divulgacao_inscricaonapublicacao;
DROP TRIGGER IF EXISTS publicacao_das_inscricoes_append_only
    ON divulgacao_publicacaodasinscricoes;
DROP FUNCTION IF EXISTS reject_inscriptions_publication_mutation();
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
        ("divulgacao", "0004_unidade_e_ato_de_nomeacao"),
        ("inscricoes", "0007_imutabilidade_da_enviada"),
        ("processos", "0005_escopo_imutavel"),
        ("publicacoes", "0012_imutabilidade_da_homologacao"),
        ("resultados", "0006_regularizacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicacaoDasInscricoes",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "natureza",
                    models.CharField(
                        choices=[
                            ("RECEBIDAS", "Relação de inscrições recebidas"),
                            ("PRELIMINAR", "Resultado preliminar da análise das inscrições"),
                            ("HOMOLOGACAO", "Homologação das inscrições"),
                        ],
                        max_length=20,
                    ),
                ),
                ("etapa_id", models.UUIDField(blank=True, null=True)),
                ("motivo_da_sucessao", models.TextField(blank=True, default="")),
                ("admite_recurso", models.BooleanField(blank=True, null=True)),
                ("recurso_evento_id", models.UUIDField(blank=True, null=True)),
                ("recurso_ate", models.DateTimeField(blank=True, null=True)),
                ("quantidade", models.PositiveIntegerField()),
                ("conteudo_publico", models.BinaryField()),
                ("conteudo_publico_hash", models.CharField(db_index=True, max_length=64)),
                ("documento", models.BinaryField()),
                ("documento_hash", models.CharField(max_length=64)),
                ("publicado_por", models.CharField(max_length=255)),
                ("publicado_em", models.DateTimeField()),
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
                        related_name="publicacoes_das_inscricoes",
                        to="processos.edital",
                    ),
                ),
                (
                    "publicacao_anterior",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sucessoras",
                        to="divulgacao.publicacaodasinscricoes",
                    ),
                ),
                (
                    "versao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_das_inscricoes",
                        to="publicacoes.versaoconsolidada",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InscricaoNaPublicacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "situacao",
                    models.CharField(
                        choices=[
                            ("RECEBIDA", "Recebida"),
                            ("DEFERIDA", "Deferida"),
                            ("INDEFERIDA", "Indeferida"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_das_inscricoes",
                        to="inscricoes.inscricao",
                    ),
                ),
                (
                    "resultado",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_das_inscricoes",
                        to="resultados.resultadoetapa",
                    ),
                ),
                (
                    "publicacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="itens",
                        to="divulgacao.publicacaodasinscricoes",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="publicacaodasinscricoes",
            index=models.Index(
                fields=["edital", "publicado_em"], name="divulgacao__edital__6c66cb_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.UniqueConstraint(
                condition=models.Q(("publicacao_anterior__isnull", True)),
                fields=("edital",),
                name="uq_publicacao_das_inscricoes_raiz",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.UniqueConstraint(
                condition=models.Q(("publicacao_anterior__isnull", False)),
                fields=("publicacao_anterior",),
                name="uq_publicacao_das_inscricoes_sucessor",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("natureza", "PRELIMINAR"), _negated=True),
                    ("etapa_id__isnull", False),
                    _connector="OR",
                ),
                name="ck_preliminar_tem_etapa",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("natureza", "RECEBIDAS"), _negated=True),
                    ("etapa_id__isnull", True),
                    _connector="OR",
                ),
                name="ck_recebidas_sem_etapa",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("recurso_ate__isnull", True),
                    models.Q(("natureza", "PRELIMINAR"), ("admite_recurso", True)),
                    _connector="OR",
                ),
                name="ck_prazo_so_no_preliminar_que_admite",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("admite_recurso__isnull", True), ("natureza", "PRELIMINAR"), _connector="OR"
                ),
                name="ck_admite_recurso_so_no_preliminar",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaodasinscricoes",
            constraint=models.CheckConstraint(
                condition=models.Q(("quantidade__gte", 1)),
                name="ck_publicacao_das_inscricoes_nao_vazia",
            ),
        ),
        migrations.AddIndex(
            model_name="inscricaonapublicacao",
            index=models.Index(fields=["inscricao"], name="divulgacao__inscric_d5d33f_idx"),
        ),
        migrations.AddConstraint(
            model_name="inscricaonapublicacao",
            constraint=models.UniqueConstraint(
                fields=("publicacao", "inscricao"), name="uq_inscricao_por_publicacao"
            ),
        ),
        migrations.AddConstraint(
            model_name="inscricaonapublicacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("situacao", "INDEFERIDA"), _negated=True),
                    ("resultado__isnull", False),
                    _connector="OR",
                ),
                name="ck_indeferida_tem_resultado",
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
