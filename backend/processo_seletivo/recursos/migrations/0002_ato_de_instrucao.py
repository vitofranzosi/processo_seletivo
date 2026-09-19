"""A tabela do ato de instrução, suas duas constraints e suas duas triggers (036, FR-527).

**Nasce append-only, nas duas camadas que a Constituição exige**, e nenhuma delas é contornável em
desenvolvimento: a trigger recusa a mutação mesmo de quem tem privilégio, e o papel de runtime não
recebe `UPDATE` nem `DELETE` — este segundo vem de `TABELAS_APPEND_ONLY`, em
`seguranca/papeis.py`, e é por isso que `make preparar` precisa rodar **de novo** depois desta
migration. Sem a segunda passada a falha aparece longe da causa, num arquivo sorteado.

**A trigger de coerência confere o que `CHECK` não alcança**, e é por isso que ela é trigger:
`CHECK` não atravessa tabelas em PostgreSQL. Duas perguntas, e cada uma fecha um vazamento
diferente:

1. **o documento instruído pertence à Inscrição da peça.** Sem isto, uma gravação direta anexaria o
   documento de **uma** pessoa ao recurso de **outra** — que é, num só passo, o dado de terceiro que
   a `FR-535` proíbe atravessar e a ampliação de acesso que a `FR-105` da `018` proíbe. A camada de
   aplicação já confere; esta guarda vale para o resto — um comando de manutenção, um shell, um
   caminho que ninguém escreveu ainda;
2. **instrução de parecer só existe sobre peça que ataca Resultado.** Recurso contra a publicação
   não contesta a avaliação de ninguém, e ali não há parecer a instruir: a linha afirmaria um anexo
   que não existe, e numa tabela append-only ela entraria uma vez e ficaria.

O que ela deliberadamente **não** confere é o estado da peça. O alcance morre com a decisão por ser
**derivado** — não há nada a fechar, e uma trigger que recusasse instruir peça decidida duplicaria,
no banco, uma regra que a ausência de estado persistido já garante. Recusar ali é conforto de
mensagem, e mora na aplicação, onde a frase pode explicar o que terminou.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

PROTEGER = """
CREATE OR REPLACE FUNCTION reject_instruction_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'instruction acts are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER ato_de_instrucao_append_only
BEFORE UPDATE OR DELETE ON recursos_atodeinstrucao
FOR EACH ROW EXECUTE FUNCTION reject_instruction_mutation();

CREATE OR REPLACE FUNCTION check_instruction_coherence() RETURNS trigger AS $$
DECLARE
    peca RECORD;
    anexo RECORD;
BEGIN
    SELECT r.inscricao_id, r.resultado_atacado_id
      INTO peca
      FROM recursos_recurso r
     WHERE r.id = NEW.recurso_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'instruction cites an appeal that does not exist';
    END IF;

    IF NEW.documento_id IS NOT NULL THEN
        SELECT d.inscricao_id
          INTO anexo
          FROM inscricoes_documentosubmetido d
         WHERE d.id = NEW.documento_id;
        IF NOT FOUND OR anexo.inscricao_id IS DISTINCT FROM peca.inscricao_id THEN
            RAISE EXCEPTION 'instruction attaches a document of another registration';
        END IF;
    ELSIF peca.resultado_atacado_id IS NULL THEN
        RAISE EXCEPTION 'instruction cites an opinion on an appeal that attacks no stage result';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER ato_de_instrucao_coerente
BEFORE INSERT ON recursos_atodeinstrucao
FOR EACH ROW EXECUTE FUNCTION check_instruction_coherence();
"""

DESPROTEGER = """
DROP TRIGGER IF EXISTS ato_de_instrucao_coerente ON recursos_atodeinstrucao;
DROP FUNCTION IF EXISTS check_instruction_coherence();
DROP TRIGGER IF EXISTS ato_de_instrucao_append_only ON recursos_atodeinstrucao;
DROP FUNCTION IF EXISTS reject_instruction_mutation();
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
        ("inscricoes", "0004_valor_de_fato"),
        ("recursos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AtoDeInstrucao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "especie",
                    models.CharField(
                        choices=[("PARECER", "Parecer"), ("DOCUMENTO", "Documento")], max_length=20
                    ),
                ),
                ("razao", models.TextField(blank=True)),
                ("instruido_por", models.CharField(max_length=255)),
                ("instruido_em", models.DateTimeField()),
                (
                    "documento",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="instrucoes_que_o_citam",
                        to="inscricoes.documentosubmetido",
                    ),
                ),
                (
                    "recurso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="instrucoes",
                        to="recursos.recurso",
                    ),
                ),
            ],
            options={
                "ordering": ["instruido_em", "id"],
                "indexes": [
                    models.Index(fields=["recurso"], name="recursos_at_recurso_82d07a_idx")
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("especie__in", ("PARECER", "DOCUMENTO"))),
                        name="ck_instrucao_especie",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            models.Q(("documento__isnull", False), ("especie", "DOCUMENTO")),
                            models.Q(("documento__isnull", True), ("especie", "PARECER")),
                            _connector="OR",
                        ),
                        name="ck_instrucao_anexo_por_especie",
                    ),
                ],
            },
        ),
        migrations.RunPython(proteger, desproteger),
    ]
