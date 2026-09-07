"""A citação da decisão pelo ato de ordenação — e a coerência dela, conferida no banco (018, T-015).

**Por que a pertinência é conferida aqui, e não só no comando.** Uma gravação direta que ligasse uma
decisão pertinente ao marco `M1` a um ato do marco `M2` do mesmo Edital liberaria indevidamente a
publicação definitiva de `M2` — sem que ninguém tivesse corrigido o vício reconhecido. É o mesmo
argumento de `check_ordering_act_provenance`: a citação é proveniência, e proveniência que só o
comando confere é proveniência que qualquer outro caminho de escrita desfaz.

O caminho por `jsonb_array_elements` para achar o marco na versão publicada é o **mesmo** que a
`0003` já percorre. Reusá-lo é o que mantém as duas conferências dizendo a mesma coisa sobre onde a
norma mora.

O que `citacao_coerente` confere:

```text
espécie          a decisão é PROVIDENCIA_A_JUSANTE — as outras não geram ato a jusante
Edital           a decisão e o ato pertencem ao mesmo Edital
Perfil           o Perfil da Inscrição que recorreu é o do ato
Marco            o marco do ato enumera a Etapa alcançada pelo recurso, nos DOIS ramos
                 de objeto atacado: contra a publicação, é o marco dela; contra o
                 ResultadoEtapa, é o marco que enumera a Etapa daquele Resultado
```

**Os dois ramos, e não um.** Uma decisão sobre recurso contra `ResultadoEtapa` alcança a Etapa
daquele Resultado, e o marco pertinente é qualquer um que a enumere; uma decisão sobre recurso
contra publicação alcança o marco daquela publicação. Conferir só o segundo deixaria o primeiro
passar para qualquer marco do Edital.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models

COERENCIA = """
CREATE OR REPLACE FUNCTION reject_decision_citation_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'decision citations are append-only';
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER citacao_append_only
BEFORE UPDATE OR DELETE ON classificacao_citacaodedecisao
FOR EACH ROW EXECUTE FUNCTION reject_decision_citation_mutation();

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
CREATE TRIGGER citacao_coerente
BEFORE INSERT ON classificacao_citacaodedecisao
FOR EACH ROW EXECUTE FUNCTION check_decision_citation_coherence();
"""

REVERTER = """
DROP TRIGGER IF EXISTS citacao_coerente ON classificacao_citacaodedecisao;
DROP FUNCTION IF EXISTS check_decision_citation_coherence();
DROP TRIGGER IF EXISTS citacao_append_only ON classificacao_citacaodedecisao;
DROP FUNCTION IF EXISTS reject_decision_citation_mutation();
"""


def proteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(COERENCIA)


def desproteger(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(REVERTER)


class Migration(migrations.Migration):
    dependencies = [
        ("classificacao", "0003_ato_coerente_com_marco"),
        ("recursos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CitacaoDeDecisao",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "ato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="citacoes",
                        to="classificacao.atodeordenacao",
                    ),
                ),
                (
                    "decisao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="citacoes",
                        to="recursos.decisaorecurso",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="citacaodedecisao",
            constraint=models.UniqueConstraint(
                fields=("ato", "decisao"), name="uq_citacao_ato_decisao"
            ),
        ),
        migrations.AddIndex(
            model_name="citacaodedecisao",
            index=models.Index(fields=["decisao"], name="classificac_decisao_91ad1f_idx"),
        ),
        migrations.RunPython(proteger, desproteger),
    ]
