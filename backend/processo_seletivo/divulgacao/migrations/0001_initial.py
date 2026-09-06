"""As três tabelas da divulgação, suas quatro constraints e suas quatro triggers.

**Três triggers de imutabilidade, absolutas.** Publicação, situação divulgada e documento nascem e
não mudam mais — nem por quem tem privilégio. Toda sucessão é linha nova (FR-040).

**Uma trigger de coerência**, no molde de `resultado_etapa_coerente` (013) e de
`ato_de_ordenacao_coerente` (015): ela impede que a linha **nasça errada**, enquanto as três acima
impedem que ela **mude depois**. Num registro append-only, congelar o erro é pior do que deixá-lo
mudar.

O que ela confere no `INSERT`, e por quê:

1. **Os três eixos da publicação coincidem com os do `AtoDeOrdenacao` citado.** Isto não é
   redundância com `uq_publicacao_raiz_por_marco`: os eixos são colunas da publicação, e a
   constraint opera **sobre elas** — não sobre o ato. Uma linha que declare um marco e cite o ato
   de outro passa pela constraint sem ser vista, porque o par que ela ocupa é o do marco
   declarado; bastaria variar o eixo declarado para inserir quantas raízes se quisesse sobre o
   mesmo ato, e a cadeia deixaria de significar o que afirma (FR-038, FR-042).
2. **O predecessor, quando há, pertence ao mesmo `(edital, perfil_id, marco_id)`** — uma cadeia
   que atravessasse marcos não descreveria sucessão nenhuma.
3. **`PRELIMINAR` não sucede `DEFINITIVA`.** A ordem entre naturezas tem sentido único (D-007).

As três dependem de **outra linha**, e é por isso que a verificação é trigger e não
`CheckConstraint`.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_result_publication_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'result publications are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER publicacao_resultado_append_only
BEFORE UPDATE OR DELETE ON divulgacao_publicacaoresultado
FOR EACH ROW EXECUTE FUNCTION reject_result_publication_mutation();

CREATE OR REPLACE FUNCTION reject_disclosed_status_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'disclosed statuses are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER situacao_divulgada_append_only
BEFORE UPDATE OR DELETE ON divulgacao_situacaodivulgada
FOR EACH ROW EXECUTE FUNCTION reject_disclosed_status_mutation();

CREATE OR REPLACE FUNCTION reject_result_document_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'result documents are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER documento_do_resultado_append_only
BEFORE UPDATE OR DELETE ON divulgacao_documentodoresultado
FOR EACH ROW EXECUTE FUNCTION reject_result_document_mutation();

CREATE OR REPLACE FUNCTION check_result_publication_coherence() RETURNS trigger AS $$
DECLARE
    origem RECORD;
    anterior RECORD;
BEGIN
    -- O ato citado é a autoridade sobre os eixos; a publicação apenas os declara.
    SELECT a.edital_id, a.perfil_id, a.marco_id
      INTO origem
      FROM classificacao_atodeordenacao a
     WHERE a.id = NEW.ato_id;

    IF NOT FOUND
       OR origem.edital_id IS DISTINCT FROM NEW.edital_id
       OR origem.perfil_id IS DISTINCT FROM NEW.perfil_id
       OR origem.marco_id IS DISTINCT FROM NEW.marco_id THEN
        RAISE EXCEPTION 'result publication does not match the ordering act it cites';
    END IF;

    IF NEW.publicacao_anterior_id IS NOT NULL THEN
        SELECT p.edital_id, p.perfil_id, p.marco_id, p.natureza
          INTO anterior
          FROM divulgacao_publicacaoresultado p
         WHERE p.id = NEW.publicacao_anterior_id;

        IF NOT FOUND
           OR anterior.edital_id IS DISTINCT FROM NEW.edital_id
           OR anterior.perfil_id IS DISTINCT FROM NEW.perfil_id
           OR anterior.marco_id IS DISTINCT FROM NEW.marco_id THEN
            RAISE EXCEPTION 'result publication succeeds a publication of another milestone';
        END IF;

        IF anterior.natureza = 'DEFINITIVA' AND NEW.natureza = 'PRELIMINAR' THEN
            RAISE EXCEPTION 'result publication nature regresses from final to preliminary';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER publicacao_resultado_coerente
BEFORE INSERT ON divulgacao_publicacaoresultado
FOR EACH ROW EXECUTE FUNCTION check_result_publication_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS publicacao_resultado_coerente ON divulgacao_publicacaoresultado;
DROP FUNCTION IF EXISTS check_result_publication_coherence();
DROP TRIGGER IF EXISTS documento_do_resultado_append_only ON divulgacao_documentodoresultado;
DROP FUNCTION IF EXISTS reject_result_document_mutation();
DROP TRIGGER IF EXISTS situacao_divulgada_append_only ON divulgacao_situacaodivulgada;
DROP FUNCTION IF EXISTS reject_disclosed_status_mutation();
DROP TRIGGER IF EXISTS publicacao_resultado_append_only ON divulgacao_publicacaoresultado;
DROP FUNCTION IF EXISTS reject_result_publication_mutation();
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
        ("classificacao", "0003_ato_coerente_com_marco"),
        ("inscricoes", "0004_valor_de_fato"),
        ("processos", "0002_teto_de_inscricoes"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicacaoResultado",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("perfil_id", models.UUIDField()),
                ("marco_id", models.UUIDField()),
                (
                    "natureza",
                    models.CharField(
                        choices=[
                            ("PRELIMINAR", "Resultado preliminar"),
                            ("DEFINITIVA", "Resultado definitivo"),
                        ],
                        max_length=20,
                    ),
                ),
                ("conteudo_publico", models.BinaryField()),
                ("conteudo_publico_hash", models.CharField(db_index=True, max_length=64)),
                ("publicado_por", models.CharField(max_length=255)),
                ("publicado_em", models.DateTimeField()),
                ("signatario_id", models.UUIDField()),
                ("signatario_nome", models.CharField(max_length=255)),
                ("signatario_cargo", models.CharField(max_length=255)),
                (
                    "ato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_de_resultado",
                        to="classificacao.atodeordenacao",
                    ),
                ),
                (
                    "edital",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="publicacoes_de_resultado",
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
                        to="divulgacao.publicacaoresultado",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DocumentoDoResultado",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("bytes", models.BinaryField()),
                ("content_type", models.CharField(default="application/pdf", max_length=100)),
                ("documento_hash", models.CharField(db_index=True, max_length=64)),
                (
                    "publicacao",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="documento",
                        to="divulgacao.publicacaoresultado",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SituacaoDivulgada",
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
                            ("CLASSIFICADA", "Classificada"),
                            ("SEM_POSICAO", "Sem posição"),
                        ],
                        max_length=20,
                    ),
                ),
                ("posicao", models.PositiveIntegerField(blank=True, null=True)),
                ("compartilhada", models.BooleanField(default=False)),
                ("pontuacao", models.CharField(blank=True, default="", max_length=32)),
                ("motivo", models.TextField(blank=True, default="")),
                (
                    "inscricao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="situacoes_divulgadas",
                        to="inscricoes.inscricao",
                    ),
                ),
                (
                    "publicacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="situacoes",
                        to="divulgacao.publicacaoresultado",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="publicacaoresultado",
            index=models.Index(
                fields=["edital", "perfil_id", "marco_id"], name="divulgacao__edital__92a218_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaoresultado",
            constraint=models.UniqueConstraint(
                condition=models.Q(("publicacao_anterior__isnull", True)),
                fields=("edital", "perfil_id", "marco_id"),
                name="uq_publicacao_raiz_por_marco",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaoresultado",
            constraint=models.UniqueConstraint(
                condition=models.Q(("publicacao_anterior__isnull", False)),
                fields=("publicacao_anterior",),
                name="uq_publicacao_sucessora_unica",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaoresultado",
            constraint=models.UniqueConstraint(
                fields=("ato", "natureza"), name="uq_publicacao_por_ato_natureza"
            ),
        ),
        migrations.AddIndex(
            model_name="situacaodivulgada",
            index=models.Index(fields=["inscricao"], name="divulgacao__inscric_599ed5_idx"),
        ),
        migrations.AddConstraint(
            model_name="situacaodivulgada",
            constraint=models.UniqueConstraint(
                fields=("publicacao", "inscricao"), name="uq_situacao_por_publicacao_inscricao"
            ),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
