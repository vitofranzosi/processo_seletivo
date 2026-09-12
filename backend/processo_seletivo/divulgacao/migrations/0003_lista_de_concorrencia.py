"""A dimensão da lista de concorrência na divulgação (021, D-015, FR-068).

Três atos raiz num marco — ampla concorrência, PPI e PcD — exigem três publicações, e
`uq_publicacao_raiz_por_marco` recusava a segunda. A constraint parte em duas parciais, e a
primeira mantém nome e garantia para a publicação sem lista: toda publicação já existente tem
`lista_id NULL`, e continua sob exatamente a regra que já a governava.

**E a trigger de coerência passa a conhecer a lista.** Ela existe para afirmar que o ato citado é a
autoridade sobre os eixos, e a lista virou um eixo: sem esta alteração, uma publicação declarando
`lista_id` da PPI poderia citar o ato da PcD e o banco aceitaria — a garantia dos outros três eixos
valeria, e a do quarto seria promessa da aplicação.
"""

from django.db import migrations, models

COERENCIA_COM_LISTA = """
CREATE OR REPLACE FUNCTION check_result_publication_coherence() RETURNS trigger AS $$
DECLARE
    origem RECORD;
    anterior RECORD;
BEGIN
    -- O ato citado é a autoridade sobre os eixos; a publicação apenas os declara.
    SELECT a.edital_id, a.perfil_id, a.marco_id, a.lista_id
      INTO origem
      FROM classificacao_atodeordenacao a
     WHERE a.id = NEW.ato_id;

    IF NOT FOUND
       OR origem.edital_id IS DISTINCT FROM NEW.edital_id
       OR origem.perfil_id IS DISTINCT FROM NEW.perfil_id
       OR origem.marco_id IS DISTINCT FROM NEW.marco_id
       OR origem.lista_id IS DISTINCT FROM NEW.lista_id THEN
        RAISE EXCEPTION 'result publication does not match the ordering act it cites';
    END IF;

    IF NEW.publicacao_anterior_id IS NOT NULL THEN
        SELECT p.edital_id, p.perfil_id, p.marco_id, p.lista_id, p.natureza
          INTO anterior
          FROM divulgacao_publicacaoresultado p
         WHERE p.id = NEW.publicacao_anterior_id;

        IF NOT FOUND
           OR anterior.edital_id IS DISTINCT FROM NEW.edital_id
           OR anterior.perfil_id IS DISTINCT FROM NEW.perfil_id
           OR anterior.marco_id IS DISTINCT FROM NEW.marco_id
           OR anterior.lista_id IS DISTINCT FROM NEW.lista_id THEN
            RAISE EXCEPTION 'result publication succeeds a publication of another milestone';
        END IF;

        IF anterior.natureza = 'DEFINITIVA' AND NEW.natureza = 'PRELIMINAR' THEN
            RAISE EXCEPTION 'result publication nature regresses from final to preliminary';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

COERENCIA_SEM_LISTA = """
CREATE OR REPLACE FUNCTION check_result_publication_coherence() RETURNS trigger AS $$
DECLARE
    origem RECORD;
    anterior RECORD;
BEGIN
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
"""


def alcancar_a_lista(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(COERENCIA_COM_LISTA)


def esquecer_a_lista(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(COERENCIA_SEM_LISTA)


class Migration(migrations.Migration):
    dependencies = [
        ("classificacao", "0005_origem_e_lista"),
        ("divulgacao", "0002_declaracao"),
        ("processos", "0002_teto_de_inscricoes"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="publicacaoresultado",
            name="uq_publicacao_raiz_por_marco",
        ),
        migrations.AddField(
            model_name="publicacaoresultado",
            name="lista_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddConstraint(
            model_name="publicacaoresultado",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("lista_id__isnull", True), ("publicacao_anterior__isnull", True)
                ),
                fields=("edital", "perfil_id", "marco_id"),
                name="uq_publicacao_raiz_por_marco",
            ),
        ),
        migrations.AddConstraint(
            model_name="publicacaoresultado",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("lista_id__isnull", False), ("publicacao_anterior__isnull", True)
                ),
                fields=("edital", "perfil_id", "marco_id", "lista_id"),
                name="uq_publicacao_raiz_por_marco_e_lista",
            ),
        ),
        # Depois das constraints: a coluna precisa existir antes de a função a ler.
        migrations.RunPython(alcancar_a_lista, esquecer_a_lista),
    ]
