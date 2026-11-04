"""Os documentos da convocação: a lista da chamada, as apresentações e as conferências (115).

**Nascem append-only, nas duas camadas**: as triggers abaixo recusam a mutação mesmo de quem tem
privilégio, e o papel de runtime não recebe `UPDATE` nem `DELETE` — o segundo vem de
`TABELAS_APPEND_ONLY`, e é por isso que o provisionamento precisa rodar de novo depois desta
migration.

**As triggers de coerência conferem o que `CHECK` não alcança**, porque `CHECK` não atravessa
tabelas:

- o item da lista pertence à **raiz** da chamada e à inscrição dela, e nasce no instante dela
  (D-009);
- a referência aponta documento da **mesma inscrição**, do requisito certo, com o hash da origem, e
  nunca outra referência (FR-3576, FR-3619);
- a conferência julga apresentação do **mesmo item**, e copia o hash dela.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

import processo_seletivo.convocacao.models
import processo_seletivo.inscricoes.storage

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_call_document_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'call documents are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER item_da_convocacao_append_only
BEFORE UPDATE OR DELETE ON convocacao_itemdalistadaconvocacao
FOR EACH ROW EXECUTE FUNCTION reject_call_document_mutation();
CREATE TRIGGER apresentacao_append_only
BEFORE UPDATE OR DELETE ON convocacao_apresentacaodedocumento
FOR EACH ROW EXECUTE FUNCTION reject_call_document_mutation();
CREATE TRIGGER conferencia_append_only
BEFORE UPDATE OR DELETE ON convocacao_conferenciadedocumento
FOR EACH ROW EXECUTE FUNCTION reject_call_document_mutation();

CREATE OR REPLACE FUNCTION check_call_list_item_coherence() RETURNS trigger AS $$
DECLARE
    alvo RECORD;
BEGIN
    SELECT c.inscricao_id, c.convocacao_anterior_id, c.criado_em
      INTO alvo
      FROM convocacao_convocacao c
     WHERE c.id = NEW.chamada_id;
    IF NOT FOUND OR alvo.convocacao_anterior_id IS NOT NULL THEN
        RAISE EXCEPTION 'call document list belongs to the root of the call';
    END IF;
    IF alvo.inscricao_id IS DISTINCT FROM NEW.inscricao_id THEN
        RAISE EXCEPTION 'call document list for another registration';
    END IF;
    IF alvo.criado_em IS DISTINCT FROM NEW.gravada_em THEN
        RAISE EXCEPTION 'call document list recorded at another instant than the call';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER item_da_convocacao_coerente
BEFORE INSERT ON convocacao_itemdalistadaconvocacao
FOR EACH ROW EXECUTE FUNCTION check_call_list_item_coherence();

CREATE OR REPLACE FUNCTION check_call_document_coherence() RETURNS trigger AS $$
DECLARE
    item RECORD;
    documento RECORD;
    origem RECORD;
BEGIN
    SELECT i.inscricao_id, i.requisito_id, i.aproveita_requisito_id, i.chamada_id
      INTO item
      FROM convocacao_itemdalistadaconvocacao i
     WHERE i.id = NEW.item_id;
    IF NEW.documento_da_inscricao_id IS NOT NULL THEN
        SELECT d.inscricao_id, d.requirement_id, d.content_hash
          INTO documento
          FROM inscricoes_documentosubmetido d
         WHERE d.id = NEW.documento_da_inscricao_id;
        IF documento.inscricao_id IS DISTINCT FROM item.inscricao_id THEN
            RAISE EXCEPTION 'reused document from another registration';
        END IF;
        IF documento.requirement_id IS DISTINCT FROM item.aproveita_requisito_id
           AND documento.requirement_id IS DISTINCT FROM item.requisito_id THEN
            RAISE EXCEPTION 'reused document of a requirement the item does not reuse';
        END IF;
        IF documento.content_hash IS DISTINCT FROM NEW.content_hash THEN
            RAISE EXCEPTION 'reused document with another hash';
        END IF;
    END IF;
    IF NEW.apresentacao_de_origem_id IS NOT NULL THEN
        SELECT a.arquivo, a.content_hash, oi.inscricao_id, oi.requisito_id, oi.chamada_id
          INTO origem
          FROM convocacao_apresentacaodedocumento a
          JOIN convocacao_itemdalistadaconvocacao oi ON oi.id = a.item_id
         WHERE a.id = NEW.apresentacao_de_origem_id;
        IF origem.arquivo = '' THEN
            RAISE EXCEPTION 'a reference never points to another reference';
        END IF;
        IF origem.inscricao_id IS DISTINCT FROM item.inscricao_id
           OR origem.requisito_id IS DISTINCT FROM item.requisito_id
           OR origem.chamada_id = item.chamada_id THEN
            RAISE EXCEPTION 'reused presentation from another registration, requirement or call';
        END IF;
        IF origem.content_hash IS DISTINCT FROM NEW.content_hash THEN
            RAISE EXCEPTION 'reused presentation with another hash';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER apresentacao_coerente
BEFORE INSERT ON convocacao_apresentacaodedocumento
FOR EACH ROW EXECUTE FUNCTION check_call_document_coherence();

CREATE OR REPLACE FUNCTION check_call_review_coherence() RETURNS trigger AS $$
DECLARE
    julgada RECORD;
BEGIN
    IF NEW.apresentacao_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT a.item_id, a.content_hash INTO julgada
      FROM convocacao_apresentacaodedocumento a
     WHERE a.id = NEW.apresentacao_id;
    IF julgada.item_id IS DISTINCT FROM NEW.item_id THEN
        RAISE EXCEPTION 'review of a presentation of another item';
    END IF;
    IF julgada.content_hash IS DISTINCT FROM NEW.hash_conferido THEN
        RAISE EXCEPTION 'review with another hash than the presentation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER conferencia_coerente
BEFORE INSERT ON convocacao_conferenciadedocumento
FOR EACH ROW EXECUTE FUNCTION check_call_review_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS conferencia_coerente ON convocacao_conferenciadedocumento;
DROP FUNCTION IF EXISTS check_call_review_coherence();
DROP TRIGGER IF EXISTS apresentacao_coerente ON convocacao_apresentacaodedocumento;
DROP FUNCTION IF EXISTS check_call_document_coherence();
DROP TRIGGER IF EXISTS item_da_convocacao_coerente ON convocacao_itemdalistadaconvocacao;
DROP FUNCTION IF EXISTS check_call_list_item_coherence();
DROP TRIGGER IF EXISTS conferencia_append_only ON convocacao_conferenciadedocumento;
DROP TRIGGER IF EXISTS apresentacao_append_only ON convocacao_apresentacaodedocumento;
DROP TRIGGER IF EXISTS item_da_convocacao_append_only ON convocacao_itemdalistadaconvocacao;
DROP FUNCTION IF EXISTS reject_call_document_mutation();
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
        ("convocacao", "0004_referencia_da_publicacao"),
        ("inscricoes", "0007_imutabilidade_da_enviada"),
        ("publicacoes", "0012_imutabilidade_da_homologacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApresentacaoDeDocumento",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("numero", models.PositiveIntegerField()),
                (
                    "arquivo",
                    models.FileField(
                        blank=True,
                        max_length=255,
                        storage=processo_seletivo.inscricoes.storage.ArmazenamentoPrivado(),
                        upload_to=processo_seletivo.convocacao.models.caminho_da_apresentacao,
                    ),
                ),
                ("nome_original", models.CharField(blank=True, max_length=255)),
                ("tamanho", models.PositiveBigIntegerField(default=0)),
                ("content_hash", models.CharField(max_length=64)),
                ("apresentado_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("apresentado_em", models.DateTimeField()),
                (
                    "apresentacao_de_origem",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aproveitamentos",
                        to="convocacao.apresentacaodedocumento",
                    ),
                ),
                (
                    "documento_da_inscricao",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="apresentacoes_que_o_aproveitam",
                        to="inscricoes.documentosubmetido",
                    ),
                ),
            ],
            options={
                "ordering": ["item", "numero"],
            },
        ),
        migrations.CreateModel(
            name="ItemDaListaDaConvocacao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("requisito_id", models.UUIDField()),
                ("chave", models.CharField(max_length=100)),
                (
                    "situacao",
                    models.CharField(
                        choices=[
                            ("OBRIGATORIO", "Obrigatorio"),
                            ("FACULTATIVO", "Facultativo"),
                            ("NAO_SE_APLICA", "Nao Se Aplica"),
                        ],
                        max_length=16,
                    ),
                ),
                ("forma_do_recorte", models.CharField(max_length=40)),
                ("perfil_id", models.UUIDField(blank=True, null=True)),
                ("modalidade_id", models.UUIDField(blank=True, null=True)),
                ("modalidade_codigo", models.CharField(blank=True, default="", max_length=100)),
                ("aproveita_requisito_id", models.UUIDField(blank=True, null=True)),
                ("gravada_em", models.DateTimeField()),
                (
                    "chamada",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="itens_da_lista",
                        to="convocacao.convocacao",
                    ),
                ),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="itens_da_lista_da_convocacao",
                        to="inscricoes.inscricao",
                    ),
                ),
                (
                    "versao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="publicacoes.versaoconsolidada",
                    ),
                ),
            ],
            options={
                "ordering": ["gravada_em", "id"],
            },
        ),
        migrations.CreateModel(
            name="ConferenciaDeDocumento",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("hash_conferido", models.CharField(blank=True, max_length=64)),
                (
                    "resultado",
                    models.CharField(
                        choices=[
                            ("CONFORME", "Conforme"),
                            ("PENDENTE", "Pendente"),
                            ("NAO_SE_APLICA", "Não se aplica"),
                        ],
                        max_length=16,
                    ),
                ),
                ("motivo", models.TextField(blank=True)),
                ("motivo_da_substituicao", models.TextField(blank=True)),
                ("conferido_por", models.CharField(max_length=255)),
                ("unidade_de_atuacao", models.CharField(max_length=100)),
                ("conferido_em", models.DateTimeField()),
                (
                    "apresentacao",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conferencias",
                        to="convocacao.apresentacaodedocumento",
                    ),
                ),
                (
                    "conferencia_anterior",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="convocacao.conferenciadedocumento",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="conferencias",
                        to="convocacao.itemdalistadaconvocacao",
                    ),
                ),
            ],
            options={
                "ordering": ["conferido_em", "id"],
            },
        ),
        migrations.AddField(
            model_name="apresentacaodedocumento",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="apresentacoes",
                to="convocacao.itemdalistadaconvocacao",
            ),
        ),
        migrations.AddConstraint(
            model_name="itemdalistadaconvocacao",
            constraint=models.UniqueConstraint(
                fields=("chamada", "requisito_id"), name="uq_item_da_convocacao_por_requisito"
            ),
        ),
        migrations.AddConstraint(
            model_name="itemdalistadaconvocacao",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("situacao__in", ["OBRIGATORIO", "FACULTATIVO", "NAO_SE_APLICA"])
                ),
                name="ck_item_da_convocacao_situacao",
            ),
        ),
        migrations.AddConstraint(
            model_name="conferenciadedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(("resultado__in", ["CONFORME", "PENDENTE", "NAO_SE_APLICA"])),
                name="ck_conferencia_resultado",
            ),
        ),
        migrations.AddConstraint(
            model_name="conferenciadedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("resultado", "CONFORME"),
                    models.Q(("motivo", ""), _negated=True),
                    _connector="OR",
                ),
                name="ck_conferencia_motivo",
            ),
        ),
        migrations.AddConstraint(
            model_name="conferenciadedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("resultado", "CONFORME"), _negated=True),
                    ("apresentacao__isnull", False),
                    _connector="OR",
                ),
                name="ck_conferencia_conforme_com_apresentacao",
            ),
        ),
        migrations.AddConstraint(
            model_name="conferenciadedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("apresentacao__isnull", True),
                    models.Q(("hash_conferido", ""), _negated=True),
                    _connector="OR",
                ),
                name="ck_conferencia_hash",
            ),
        ),
        migrations.AddConstraint(
            model_name="apresentacaodedocumento",
            constraint=models.UniqueConstraint(
                fields=("item", "numero"), name="uq_apresentacao_por_item_e_numero"
            ),
        ),
        migrations.AddConstraint(
            model_name="apresentacaodedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        models.Q(("arquivo", ""), _negated=True),
                        ("documento_da_inscricao__isnull", True),
                        ("apresentacao_de_origem__isnull", True),
                    ),
                    models.Q(
                        ("arquivo", ""),
                        ("documento_da_inscricao__isnull", False),
                        ("apresentacao_de_origem__isnull", True),
                    ),
                    models.Q(
                        ("arquivo", ""),
                        ("documento_da_inscricao__isnull", True),
                        ("apresentacao_de_origem__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="ck_apresentacao_arquivo_ou_referencia",
            ),
        ),
        migrations.AddConstraint(
            model_name="apresentacaodedocumento",
            constraint=models.CheckConstraint(
                condition=models.Q(("content_hash", ""), _negated=True),
                name="ck_apresentacao_com_hash",
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
