"""O Resultado guarda a conclusão conforme a forma, e a conferência com a fonte acompanha (013).

**A dependência cruzada não é decorativa.** O SQL de `check_stage_result_source()` lê
`avaliacoes_avaliacao.forma` e `.sentido`, e o grafo de migrations do Django não infere isso da
ordem em que as tarefas foram escritas: sem a dependência declarada, uma instalação limpa poderia
aplicar esta migration antes de as colunas existirem, e a função sairia inválida.

**Por que a trigger é recriada por inteiro.** Ela hoje compara `fonte.pontuacao IS DISTINCT FROM
NEW.pontuacao`, e numa conclusão decisória os dois lados são nulos — `IS DISTINCT FROM` resolve nulo
contra nulo como **iguais**, e a conferência passaria a aprovar qualquer sentido em silêncio. A nova
compara forma, pontuação e sentido, os três, **incondicionalmente**: se as formas batem, alternar
seria redundante; se divergem, o primeiro teste já reprova.

`forma` nasce com `DEFAULT` e o `preserve_default=False` o remove em seguida, pelo mesmo caminho da
conclusão preservada — todo Resultado que existe hoje é pontuado, e escrever isso não afirma nada
que a linha já não dissesse.
"""

from django.db import migrations, models

CONFERIR = """
CREATE OR REPLACE FUNCTION check_stage_result_source() RETURNS trigger AS $$
DECLARE
    fonte RECORD;
BEGIN
    SELECT a.estado, a.forma, a.pontuacao, a.sentido,
           t.inscricao_id, t.etapa_id, t.edital_id, t.ativo
      INTO fonte
      FROM avaliacoes_avaliacao a
      JOIN avaliacoes_atribuicao t ON t.id = a.atribuicao_id
     WHERE a.id = NEW.avaliacao_id;

    IF NOT FOUND
       OR fonte.inscricao_id IS DISTINCT FROM NEW.inscricao_id
       OR fonte.etapa_id IS DISTINCT FROM NEW.etapa_id
       OR fonte.edital_id IS DISTINCT FROM NEW.edital_id
       OR fonte.forma IS DISTINCT FROM NEW.forma
       OR fonte.pontuacao IS DISTINCT FROM NEW.pontuacao
       OR fonte.sentido IS DISTINCT FROM NEW.sentido
       OR fonte.estado <> 'CONCLUIDA'
       OR NOT fonte.ativo THEN
        RAISE EXCEPTION 'stage result does not match its source evaluation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

CONFERIR_ANTERIOR = """
CREATE OR REPLACE FUNCTION check_stage_result_source() RETURNS trigger AS $$
DECLARE
    fonte RECORD;
BEGIN
    SELECT a.estado, a.pontuacao, t.inscricao_id, t.etapa_id, t.edital_id, t.ativo
      INTO fonte
      FROM avaliacoes_avaliacao a
      JOIN avaliacoes_atribuicao t ON t.id = a.atribuicao_id
     WHERE a.id = NEW.avaliacao_id;

    IF NOT FOUND
       OR fonte.inscricao_id IS DISTINCT FROM NEW.inscricao_id
       OR fonte.etapa_id IS DISTINCT FROM NEW.etapa_id
       OR fonte.edital_id IS DISTINCT FROM NEW.edital_id
       OR fonte.pontuacao IS DISTINCT FROM NEW.pontuacao
       OR fonte.estado <> 'CONCLUIDA'
       OR NOT fonte.ativo THEN
        RAISE EXCEPTION 'stage result does not match its source evaluation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def conferir_por_forma(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR)


def conferir_como_antes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR_ANTERIOR)


class Migration(migrations.Migration):
    dependencies = [
        ("avaliacoes", "0002_conclusao_por_forma"),
        ("inscricoes", "0003_cpf_na_submetida"),
        ("processos", "0001_initial"),
        ("resultados", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultadoetapa",
            name="forma",
            field=models.CharField(
                choices=[("PONTUADA", "Pontuada"), ("DECISORIA", "Decisoria")],
                default="PONTUADA",
                max_length=20,
            ),
            # O default preenche as linhas que já existem — todo Resultado gravado até aqui é
            # pontuado — e sai do esquema em seguida, para não afirmar para sempre que Resultado
            # sem forma é pontuado.
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="resultadoetapa",
            name="sentido",
            field=models.CharField(
                blank=True,
                choices=[("FAVORAVEL", "Favoravel"), ("DESFAVORAVEL", "Desfavoravel")],
                default="",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="resultadoetapa",
            name="pontuacao",
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True),
        ),
        migrations.AddConstraint(
            model_name="resultadoetapa",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("forma", "PONTUADA"), ("pontuacao__isnull", False), ("sentido", "")),
                    models.Q(
                        ("forma", "DECISORIA"),
                        ("pontuacao__isnull", True),
                        models.Q(("sentido", ""), _negated=True),
                    ),
                    _connector="OR",
                ),
                name="ck_resultado_completo_por_forma",
            ),
        ),
        migrations.RunPython(conferir_por_forma, conferir_como_antes),
    ]
