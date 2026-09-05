"""A proveniência do ato é conferida no banco, uma vez por ato (015, T125).

**A promessa e a entrega tinham divergido.** A `research.md` prometeu que a coerência conferiria
"que os Resultados citados na proveniência sejam os da Etapa enumerada pelo marco"; a `0001`
entregou verificação por posição, limitada a Inscrição × Edital × Perfil. Nenhuma das duas estava
errada isoladamente — o que faltava era o lugar certo de cumprir a promessa forte.

**Por que uma terceira trigger, e não ampliar a de posição.** Conferir os Resultados citados dentro
de `posicao_coerente` custaria a verificação global uma vez **por posição** — mil vezes num ato de
mil participantes, sempre com a mesma resposta. A proveniência é do ato: conferi-la no `INSERT` de
`AtoDeOrdenacao` custa uma execução, e a operação é `set-based` — nenhum laço, nenhuma consulta por
elemento.

`posicao_coerente` permanece como está, com o escopo que lhe cabe: a posição afirma coisas sobre
**uma** inscrição, e é isso que ela confere.

A `0001` não é reescrita. Migration aplicada não se reescreve, e a função nova nasce aqui inteira,
reversível por `DROP … IF EXISTS`.
"""

from django.db import migrations

CONFERIR = """
CREATE OR REPLACE FUNCTION check_ordering_act_provenance() RETURNS trigger AS $$
DECLARE
    divergentes integer;
BEGIN
    -- Cada Resultado citado precisa existir, pertencer ao Edital do ato e ter sido produzido numa
    -- Etapa que o marco enumera. `LEFT JOIN` com contagem do que não casou: uma varredura só,
    -- sem laço e sem consulta por elemento.
    SELECT count(*) INTO divergentes
    FROM jsonb_array_elements(NEW.universo -> 'stageResults') AS citado
    LEFT JOIN resultados_resultadoetapa AS resultado
        ON resultado.id = (citado ->> 'id')::uuid
       AND resultado.edital_id = NEW.edital_id
       AND resultado.etapa_id = (citado ->> 'stageId')::uuid
    WHERE resultado.id IS NULL;

    IF divergentes > 0 THEN
        RAISE EXCEPTION 'ordering act cites stage results that do not belong to its universe';
    END IF;

    -- O universo declara o que o ato afirma sobre si: Edital, Perfil, marco e versão precisam
    -- coincidir com as colunas. Sem isto, o resumo poderia descrever outro ato.
    IF (NEW.universo ->> 'editalId')::uuid IS DISTINCT FROM NEW.edital_id
       OR (NEW.universo ->> 'profileId')::uuid IS DISTINCT FROM NEW.perfil_id
       OR (NEW.universo ->> 'milestoneId')::uuid IS DISTINCT FROM NEW.marco_id
       OR (NEW.universo ->> 'versionId')::uuid IS DISTINCT FROM NEW.versao_id THEN
        RAISE EXCEPTION 'ordering act universe does not match the act it belongs to';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

CRIAR = """
CREATE TRIGGER ato_de_ordenacao_coerente
BEFORE INSERT ON classificacao_atodeordenacao
FOR EACH ROW EXECUTE FUNCTION check_ordering_act_provenance();
"""

DESFAZER = """
DROP TRIGGER IF EXISTS ato_de_ordenacao_coerente ON classificacao_atodeordenacao;
DROP FUNCTION IF EXISTS check_ordering_act_provenance();
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR)
    schema_editor.execute(CRIAR)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(DESFAZER)


class Migration(migrations.Migration):
    dependencies = [
        ("classificacao", "0001_initial"),
        ("resultados", "0004_resultado_por_ocorrencia"),
    ]

    operations = [migrations.RunPython(proteger, desproteger)]
