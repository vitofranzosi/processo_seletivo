"""Confere cada Resultado citado contra o marco e contra a sua identidade completa (015, T125).

A ``0002`` colocou a conferência no lugar certo — uma vez no ``INSERT`` do ato —, mas a primeira
versão da função conferia apenas que o Resultado existia no Edital e na Etapa **declarada pelo
próprio item citado**. Ela não lia o marco. Assim, um Resultado real de qualquer outra Etapa do
Edital atravessava, e ``registrationId`` e ``versionId`` podiam descrever outra origem.

Migration aplicada não se reescreve. Esta substitui a função ligada à trigger já existente e a
reversão restaura integralmente a função da ``0002``. A conferência continua ``set-based`` e roda
uma vez por ato, independentemente da quantidade de posições.
"""

from django.db import migrations

CONFERIR_COM_MARCO = """
CREATE OR REPLACE FUNCTION check_ordering_act_provenance() RETURNS trigger AS $$
DECLARE
    marco jsonb;
    divergentes integer;
BEGIN
    -- O resumo precisa primeiro descrever as próprias colunas do ato. Esta precedência preserva
    -- uma mensagem precisa mesmo quando o identificador adulterado também impediria achar o marco.
    IF (NEW.universo ->> 'editalId')::uuid IS DISTINCT FROM NEW.edital_id
       OR (NEW.universo ->> 'profileId')::uuid IS DISTINCT FROM NEW.perfil_id
       OR (NEW.universo ->> 'milestoneId')::uuid IS DISTINCT FROM NEW.marco_id
       OR (NEW.universo ->> 'versionId')::uuid IS DISTINCT FROM NEW.versao_id THEN
        RAISE EXCEPTION 'ordering act universe does not match the act it belongs to';
    END IF;

    -- A regra é lida da versão histórica citada pelo ato. Perfil e marco são identidades
    -- publicadas; não dependem das linhas mutáveis do rascunho.
    SELECT marco_publicado.conteudo INTO marco
    FROM publicacoes_versaoconsolidada AS versao
    CROSS JOIN LATERAL jsonb_array_elements(
        COALESCE(versao.content -> 'profiles', '[]'::jsonb)
    ) AS perfil_publicado(conteudo)
    CROSS JOIN LATERAL jsonb_array_elements(
        COALESCE(perfil_publicado.conteudo -> 'classificationMilestones', '[]'::jsonb)
    ) AS marco_publicado(conteudo)
    WHERE versao.id = NEW.versao_id
      AND versao.edital_id = NEW.edital_id
      AND perfil_publicado.conteudo ->> 'id' = NEW.perfil_id::text
      AND marco_publicado.conteudo ->> 'id' = NEW.marco_id::text;

    IF marco IS NULL THEN
        RAISE EXCEPTION 'ordering act milestone does not exist in its normative version';
    END IF;

    -- O item citado não é autoridade sobre a sua própria identidade. Todos os campos que ligam
    -- o Resultado à proveniência precisam coincidir com a linha append-only, e a Etapa dessa linha
    -- precisa pertencer à enumeração do marco encontrado acima.
    SELECT count(*) INTO divergentes
    FROM jsonb_array_elements(
        COALESCE(NEW.universo -> 'stageResults', '[]'::jsonb)
    ) AS citado
    LEFT JOIN resultados_resultadoetapa AS resultado
        ON resultado.id = (citado ->> 'id')::uuid
       AND resultado.edital_id = NEW.edital_id
       AND resultado.inscricao_id = (citado ->> 'registrationId')::uuid
       AND resultado.etapa_id = (citado ->> 'stageId')::uuid
       AND resultado.versao_id = (citado ->> 'versionId')::uuid
    WHERE resultado.id IS NULL
       OR NOT EXISTS (
            SELECT 1
            FROM jsonb_array_elements_text(
                COALESCE(marco -> 'stages', '[]'::jsonb)
            ) AS etapa_enumerada(id)
            WHERE etapa_enumerada.id = citado ->> 'stageId'
       );

    IF divergentes > 0 THEN
        RAISE EXCEPTION 'ordering act cites stage results that do not belong to its milestone';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# Estado exato da função criada pela ``0002``. A reversão devolve a aplicação à migration anterior
# sem remover a trigger que aquela migration é responsável por possuir.
RESTAURAR_0002 = """
CREATE OR REPLACE FUNCTION check_ordering_act_provenance() RETURNS trigger AS $$
DECLARE
    divergentes integer;
BEGIN
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


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR_COM_MARCO)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(RESTAURAR_0002)


class Migration(migrations.Migration):
    dependencies = [("classificacao", "0002_ato_coerente")]

    operations = [migrations.RunPython(proteger, desproteger)]
