"""A Etapa que um critério do marco compara entra na proveniência do ato (114, FR-3551).

Um marco pode somar só a Prova e desempatar pela maior nota na Entrevista. Desde a `114` o cálculo
lê os Resultados da Entrevista para o desempate, e o universo do ato os cita — é o que faz o recurso
que corrige essa nota obsoletar a ordem. A função da `0003` recusava todo Resultado de Etapa que o
marco não enumera, e o ato desse marco não se gravaria.

A conferência continua fechada: aceita a Etapa enumerada **ou** a que um critério
`MAIOR_PONTUACAO_NA_ETAPA` do mesmo marco compara, lido da versão citada pelo ato, e mais nenhuma.
Abrir para "qualquer Etapa do Edital" desfaria o que a `0003` existiu para fechar. É a mesma
resposta que `desempate.etapas_do_desempate` dá em Python, e o teste da trigger prende as duas.

Migration aplicada não se reescreve: esta substitui a função ligada à trigger já existente, e a
reversão restaura o texto da `0003`, copiado aqui e não importado — o módulo de nome numérico não se
importa limpo, e a cópia congela exatamente o estado que a reversão precisa devolver.
"""

from django.db import migrations

CONFERIR_COM_DESEMPATE = """
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
    -- precisa pertencer à enumeração do marco encontrado acima **ou ser a que um critério
    -- MAIOR_PONTUACAO_NA_ETAPA dele compara** (114): a nota que desempata é entrada da ordem.
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
       )
       AND NOT EXISTS (
            -- O `CASE`, e não só o `COALESCE`: este disjunto é novo, e o PostgreSQL não promete
            -- avaliá-lo depois do anterior. Um `tiebreakers` publicado como `null` faria
            -- `jsonb_array_elements` levantar "cannot extract elements from a scalar" na emissão
            -- de um ato legítimo, que só cita Etapas enumeradas.
            SELECT 1
            FROM jsonb_array_elements(
                CASE WHEN jsonb_typeof(marco -> 'tiebreakers') = 'array'
                     THEN marco -> 'tiebreakers'
                     ELSE '[]'::jsonb
                END
            ) AS criterio(conteudo)
            WHERE criterio.conteudo ->> 'type' = 'MAIOR_PONTUACAO_NA_ETAPA'
              AND criterio.conteudo -> 'parameters' ->> 'stageId' = citado ->> 'stageId'
       );

    IF divergentes > 0 THEN
        RAISE EXCEPTION 'ordering act cites stage results that do not belong to its milestone';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# Estado exato da função criada pela ``0003``.
RESTAURAR_0003 = """
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


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR_COM_DESEMPATE)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(RESTAURAR_0003)


class Migration(migrations.Migration):
    dependencies = [("classificacao", "0006_corte")]

    operations = [migrations.RunPython(proteger, desproteger)]
