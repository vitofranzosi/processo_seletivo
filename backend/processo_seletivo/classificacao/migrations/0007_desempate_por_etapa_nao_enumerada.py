"""A Etapa que um critério do marco compara entra na proveniência do ato (114, FR-3551).

Um marco pode somar só a Prova e desempatar pela maior nota na Entrevista. Desde a `114` o cálculo
lê os Resultados da Entrevista para o desempate, e o universo do ato os cita — é o que faz o recurso
que corrige essa nota obsoletar a ordem. A função da `0003` recusava todo Resultado de Etapa que o
marco não enumera, e o ato desse marco não se gravaria.

A conferência continua fechada: aceita a Etapa enumerada **ou** a que um critério
`MAIOR_PONTUACAO_NA_ETAPA` do mesmo marco compara, lido da versão citada pelo ato, e mais nenhuma.
Abrir para "qualquer Etapa do Edital" desfaria o que a `0003` existiu para fechar. É a mesma
resposta que `desempate.etapas_do_desempate` dá em Python, e o teste da trigger prende as duas.

**A citação da decisão de recurso acompanha** (114, D-005). A `0004` aceitava citar a providência a
jusante só no ato de marco que **enumera** a Etapa alcançada pelo recurso. Com a nota da Entrevista
dentro da ordem, a decisão que manda corrigi-la é pertinente ao marco que desempata por ela, e o ato
que a cumpre precisa poder citá-la — senão a definitiva daquele marco ficaria impedida para sempre
pela providência que nenhum ato dele consegue cumprir. A ampliação é a mesma: a Etapa enumerada ou
a comparada por critério, e nenhuma outra.

Migration aplicada não se reescreve: esta substitui as funções ligadas às triggers já existentes, e
a reversão restaura os textos da `0003` e da `0004`, copiados aqui e não importados — o módulo de
nome numérico não se importa limpo, e a cópia congela exatamente o estado que a reversão precisa
devolver.
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


CITAR_COM_DESEMPATE = """
CREATE OR REPLACE FUNCTION check_decision_citation_coherence() RETURNS trigger AS $$
DECLARE
    ato RECORD;
    peca RECORD;
    marco jsonb;
    etapa_alcancada UUID;
BEGIN
    SELECT a.edital_id, a.perfil_id, a.marco_id, a.versao_id
      INTO ato
      FROM classificacao_atodeordenacao a
     WHERE a.id = NEW.ato_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'decision citation refers to an ordering act that does not exist';
    END IF;

    SELECT d.especie,
           d.etapa_id,
           r.publicacao_atacada_id,
           r.resultado_atacado_id,
           i.edital_id,
           i.profile_id
      INTO peca
      FROM recursos_decisaorecurso d
      JOIN recursos_recurso r ON r.id = d.recurso_id
      JOIN inscricoes_inscricao i ON i.id = r.inscricao_id
     WHERE d.id = NEW.decisao_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'decision citation refers to a decision that does not exist';
    END IF;

    -- Só a quarta espécie produz ato a jusante. Citar um indeferimento, uma correção fixada ou uma
    -- reavaliação seria declarar cumprida uma providência que a decisão nunca determinou.
    IF peca.especie IS DISTINCT FROM 'PROVIDENCIA_A_JUSANTE' THEN
        RAISE EXCEPTION 'ordering act cites a decision that determined no downstream remedy';
    END IF;

    IF peca.edital_id IS DISTINCT FROM ato.edital_id
       OR peca.profile_id IS DISTINCT FROM ato.perfil_id THEN
        RAISE EXCEPTION 'ordering act cites a decision of another edital or profile';
    END IF;

    SELECT marco_publicado.conteudo INTO marco
      FROM publicacoes_versaoconsolidada AS versao
      CROSS JOIN LATERAL jsonb_array_elements(
          COALESCE(versao.content -> 'profiles', '[]'::jsonb)
      ) AS perfil_publicado(conteudo)
      CROSS JOIN LATERAL jsonb_array_elements(
          COALESCE(perfil_publicado.conteudo -> 'classificationMilestones', '[]'::jsonb)
      ) AS marco_publicado(conteudo)
     WHERE versao.id = ato.versao_id
       AND versao.edital_id = ato.edital_id
       AND perfil_publicado.conteudo ->> 'id' = ato.perfil_id::text
       AND marco_publicado.conteudo ->> 'id' = ato.marco_id::text;

    IF marco IS NULL THEN
        RAISE EXCEPTION 'ordering act milestone does not exist in its normative version';
    END IF;

    IF peca.publicacao_atacada_id IS NOT NULL THEN
        -- Contra a publicação: o marco pertinente é o daquela publicação, e mais nenhum.
        IF NOT EXISTS (
            SELECT 1
              FROM divulgacao_publicacaoresultado p
              JOIN classificacao_atodeordenacao a ON a.id = p.ato_id
             WHERE p.id = peca.publicacao_atacada_id
               AND a.marco_id = ato.marco_id
        ) THEN
            RAISE EXCEPTION 'ordering act cites a decision pertinent to another milestone';
        END IF;
        RETURN NEW;
    END IF;

    -- Contra o ResultadoEtapa: pertinente é qualquer marco que leia a Etapa alcançada. A Etapa
    -- vem da decisão quando ela a declara, e do Resultado atacado quando não — a quarta espécie
    -- não declara par, e é justamente ela que chega aqui.
    SELECT COALESCE(peca.etapa_id, res.etapa_id) INTO etapa_alcancada
      FROM resultados_resultadoetapa res
     WHERE res.id = peca.resultado_atacado_id;

    IF etapa_alcancada IS NULL THEN
        RAISE EXCEPTION 'decision citation cannot determine the stage it reaches';
    END IF;

    -- Pertinente é o marco cuja ordem **lê** a Etapa alcançada: a que ele enumera, ou a que um
    -- critério MAIOR_PONTUACAO_NA_ETAPA dele compara (114). É a mesma resposta de
    -- `desempate.etapas_que_a_ordem_le`, e a da conferência da proveniência logo acima nesta
    -- migration: o ato que cita a nota no universo pode citar a decisão que a corrigiu.
    IF NOT EXISTS (
        SELECT 1
          FROM jsonb_array_elements_text(
              COALESCE(marco -> 'stages', '[]'::jsonb)
          ) AS etapa_enumerada(id)
         WHERE etapa_enumerada.id = etapa_alcancada::text
    ) AND NOT EXISTS (
        SELECT 1
          FROM jsonb_array_elements(
              CASE WHEN jsonb_typeof(marco -> 'tiebreakers') = 'array'
                   THEN marco -> 'tiebreakers'
                   ELSE '[]'::jsonb
              END
          ) AS criterio(conteudo)
         WHERE criterio.conteudo ->> 'type' = 'MAIOR_PONTUACAO_NA_ETAPA'
           AND criterio.conteudo -> 'parameters' ->> 'stageId' = etapa_alcancada::text
    ) THEN
        RAISE EXCEPTION 'ordering act cites a decision pertinent to another milestone';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# Estado exato da função criada pela ``0004``.
RESTAURAR_0004 = """
CREATE OR REPLACE FUNCTION check_decision_citation_coherence() RETURNS trigger AS $$
DECLARE
    ato RECORD;
    peca RECORD;
    marco jsonb;
    etapa_alcancada UUID;
BEGIN
    SELECT a.edital_id, a.perfil_id, a.marco_id, a.versao_id
      INTO ato
      FROM classificacao_atodeordenacao a
     WHERE a.id = NEW.ato_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'decision citation refers to an ordering act that does not exist';
    END IF;

    SELECT d.especie,
           d.etapa_id,
           r.publicacao_atacada_id,
           r.resultado_atacado_id,
           i.edital_id,
           i.profile_id
      INTO peca
      FROM recursos_decisaorecurso d
      JOIN recursos_recurso r ON r.id = d.recurso_id
      JOIN inscricoes_inscricao i ON i.id = r.inscricao_id
     WHERE d.id = NEW.decisao_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'decision citation refers to a decision that does not exist';
    END IF;

    -- Só a quarta espécie produz ato a jusante. Citar um indeferimento, uma correção fixada ou uma
    -- reavaliação seria declarar cumprida uma providência que a decisão nunca determinou.
    IF peca.especie IS DISTINCT FROM 'PROVIDENCIA_A_JUSANTE' THEN
        RAISE EXCEPTION 'ordering act cites a decision that determined no downstream remedy';
    END IF;

    IF peca.edital_id IS DISTINCT FROM ato.edital_id
       OR peca.profile_id IS DISTINCT FROM ato.perfil_id THEN
        RAISE EXCEPTION 'ordering act cites a decision of another edital or profile';
    END IF;

    SELECT marco_publicado.conteudo INTO marco
      FROM publicacoes_versaoconsolidada AS versao
      CROSS JOIN LATERAL jsonb_array_elements(
          COALESCE(versao.content -> 'profiles', '[]'::jsonb)
      ) AS perfil_publicado(conteudo)
      CROSS JOIN LATERAL jsonb_array_elements(
          COALESCE(perfil_publicado.conteudo -> 'classificationMilestones', '[]'::jsonb)
      ) AS marco_publicado(conteudo)
     WHERE versao.id = ato.versao_id
       AND versao.edital_id = ato.edital_id
       AND perfil_publicado.conteudo ->> 'id' = ato.perfil_id::text
       AND marco_publicado.conteudo ->> 'id' = ato.marco_id::text;

    IF marco IS NULL THEN
        RAISE EXCEPTION 'ordering act milestone does not exist in its normative version';
    END IF;

    IF peca.publicacao_atacada_id IS NOT NULL THEN
        -- Contra a publicação: o marco pertinente é o daquela publicação, e mais nenhum.
        IF NOT EXISTS (
            SELECT 1
              FROM divulgacao_publicacaoresultado p
              JOIN classificacao_atodeordenacao a ON a.id = p.ato_id
             WHERE p.id = peca.publicacao_atacada_id
               AND a.marco_id = ato.marco_id
        ) THEN
            RAISE EXCEPTION 'ordering act cites a decision pertinent to another milestone';
        END IF;
        RETURN NEW;
    END IF;

    -- Contra o ResultadoEtapa: pertinente é qualquer marco que enumere a Etapa alcançada. A Etapa
    -- vem da decisão quando ela a declara, e do Resultado atacado quando não — a quarta espécie
    -- não declara par, e é justamente ela que chega aqui.
    SELECT COALESCE(peca.etapa_id, res.etapa_id) INTO etapa_alcancada
      FROM resultados_resultadoetapa res
     WHERE res.id = peca.resultado_atacado_id;

    IF etapa_alcancada IS NULL THEN
        RAISE EXCEPTION 'decision citation cannot determine the stage it reaches';
    END IF;

    IF NOT EXISTS (
        SELECT 1
          FROM jsonb_array_elements_text(
              COALESCE(marco -> 'stages', '[]'::jsonb)
          ) AS etapa_enumerada(id)
         WHERE etapa_enumerada.id = etapa_alcancada::text
    ) THEN
        RAISE EXCEPTION 'ordering act cites a decision pertinent to another milestone';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CONFERIR_COM_DESEMPATE)
    schema_editor.execute(CITAR_COM_DESEMPATE)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(RESTAURAR_0003)
    schema_editor.execute(RESTAURAR_0004)


class Migration(migrations.Migration):
    dependencies = [("classificacao", "0006_corte")]

    operations = [migrations.RunPython(proteger, desproteger)]
