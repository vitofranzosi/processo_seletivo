"""A cobertura do conteúdo publicado: todo campo mostrado, ou excluído com o motivo (`R-015`).

**Por que uma tabela, e um guardião sobre ela** (`SC-533`). O conteúdo publicado cresce a cada
feature que muda o Edital. Sem esta tabela, um campo novo ficaria invisível ao assistente em
silêncio — a resposta não o mostraria, e ninguém saberia que deixou de mostrar.
`tests/unit/duvidas/test_cobertura.py` exige três coisas:

- todo caminho folha do conteúdo publicado do corpus está aqui;
- todo campo dos esquemas publicados declarados em `editais/domain/validation.py` está aqui;
- a versão do esquema é a registrada abaixo. Feature que muda o conteúdo publicado sobe a versão
  (`shared/canonical.py`), e é isso que obriga a classificar o campo novo.

E confere a tabela contra as respostas: o que ela diz que uma pergunta mostra, alguma resposta do
corpus mostra de fato.

**Quatro classes.** As perguntas que mostram o campo num cartão; `LOCALIZACAO`, quando o campo é o
nome do lugar do cartão (o código e o nome do Perfil, o título da seção); `REGRA`, quando o campo
decide o que a resposta mostra sem ser mostrado; e `EXCLUIDO`, com o motivo.
"""

from __future__ import annotations

#: A versão do conteúdo publicado que esta tabela classifica (`shared/canonical.py`).
VERSAO_DO_ESQUEMA = 17

LOCALIZACAO = "LOCALIZACAO"
#: O campo decide **o que** a resposta mostra, sem ser mostrado: a aplicabilidade do documento, o
#: Evento que é o período de inscrições.
REGRA = "REGRA"


def excluido(motivo: str) -> tuple[str, str]:
    return ("EXCLUIDO", motivo)


IDENTIDADE = excluido("identidade interna da entidade: não é informação para quem lê")
ORDEM = excluido("ordem de exibição: as respostas já saem nessa ordem")
HASH = excluido("integridade do artefato, conferida na publicação; não é informação para quem lê")
CODIGO_INTERNO = excluido("código interno do sistema; o rótulo legível é o que a resposta mostra")
OPACO = excluido(
    "opaco: o documento publicado não o imprime (`docs/libras/auditoria-sistema.md`, §6), e "
    "mostrá-lo seria dizer o que o ato não diz"
)
SEM_PERGUNTA = excluido(
    "nenhuma das doze perguntas trata disto; registrado para a revisão do catálogo com o setor "
    "de seleção (070, T046)"
)

#: Padrão de caminho → classe. `*` é qualquer item de coleção; `/**` cobre a subárvore inteira.
COBERTURA = {
    # ---- identificação do Edital
    "/schemaVersion": excluido("versão do esquema, controle interno da forma canônica"),
    "/editalId": IDENTIDADE,
    "/processoId": IDENTIDADE,
    "/processoCode": CODIGO_INTERNO,
    "/processoTitle": LOCALIZACAO,
    "/number": LOCALIZACAO,
    "/year": LOCALIZACAO,
    "/title": LOCALIZACAO,
    "/description": SEM_PERGUNTA,
    # ---- inscrição e matrícula
    "/maxInscricoesPorCandidato": ("P-06",),
    "/matriculationRequest": ("P-10",),
    "/matriculationRequest/moment": ("P-10",),
    "/matriculationRequest/declarationText": ("P-10",),
    "/drawMethod/**": ("P-09",),
    # ---- Perfis
    "/profiles/*/id": IDENTIDADE,
    "/profiles/*/code": LOCALIZACAO,
    "/profiles/*/name": LOCALIZACAO,
    "/profiles/*/description": ("P-03",),
    "/profiles/*/requirements": ("P-04",),
    "/profiles/*/immediateVacancies": ("P-03",),
    "/profiles/*/reserveType": ("P-03",),
    "/profiles/*/reserveLimit": ("P-03",),
    "/profiles/*/generalCompetitionModalityId": excluido(
        "a ampla concorrência é a linha do quadro sem modalidade (`FR-1427`); este vínculo não "
        "muda o que se diz ao leitor"
    ),
    "/profiles/*/locality": ("P-03",),
    "/profiles/*/workload": ("P-03",),
    "/profiles/*/compensation": ("P-03",),
    "/profiles/*/duties": SEM_PERGUNTA,
    "/profiles/*/classificationInformation": OPACO,
    "/profiles/*/classificationInformation/**": OPACO,
    "/profiles/*/callInformation": OPACO,
    "/profiles/*/callInformation/**": OPACO,
    "/profiles/*/callForm": ("P-10",),
    "/profiles/*/vacancyReversion": ("P-03",),
    "/profiles/*/vacancyReversion/kind": ("P-03",),
    "/profiles/*/vacancyTable/*/id": IDENTIDADE,
    "/profiles/*/vacancyTable/*/modalityId": LOCALIZACAO,
    "/profiles/*/vacancyTable/*/immediateVacancies": ("P-03",),
    "/profiles/*/competitionModalities/*/id": IDENTIDADE,
    "/profiles/*/competitionModalities/*/code": LOCALIZACAO,
    "/profiles/*/competitionModalities/*/name": LOCALIZACAO,
    "/profiles/*/competitionModalities/*/description": ("P-03",),
    "/profiles/*/competitionModalities/*/normativeRule": ("P-03",),
    "/profiles/*/competitionModalities/*/normativeRule/foundation": ("P-03",),
    "/profiles/*/competitionModalities/*/normativeRule/id": IDENTIDADE,
    "/profiles/*/competitionModalities/*/normativeRule/version": excluido(
        "versão interna da regra da modalidade; o documento não a imprime"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/effectiveFrom": excluido(
        "vigência interna da regra da modalidade; o documento não a imprime"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/percentage": excluido(
        "o percentual é a origem do cálculo; a resposta mostra as vagas que o quadro publicou"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/calculation": excluido(
        "regra do cálculo das vagas; a resposta mostra o quadro publicado, que é o resultado dela"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/rounding/**": excluido(
        "arredondamento do cálculo das vagas; a resposta mostra o quadro publicado"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/rounding": excluido(
        "arredondamento do cálculo das vagas; a resposta mostra o quadro publicado"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/distribution": excluido(
        "distribuição interna do cálculo; a resposta mostra o quadro publicado"
    ),
    "/profiles/*/competitionModalities/*/normativeRule/callRules": SEM_PERGUNTA,
    "/profiles/*/declaredFacts": LOCALIZACAO,
    "/profiles/*/declaredFacts/*/id": IDENTIDADE,
    "/profiles/*/declaredFacts/*/code": CODIGO_INTERNO,
    "/profiles/*/declaredFacts/*/label": LOCALIZACAO,
    "/profiles/*/declaredFacts/*/type": excluido("tipo interno do fato declarado"),
    "/profiles/*/classificationMilestones": ("P-07",),
    "/profiles/*/classificationMilestones/*/id": IDENTIDADE,
    "/profiles/*/classificationMilestones/*/code": CODIGO_INTERNO,
    "/profiles/*/classificationMilestones/*/name": ("P-07", "P-09"),
    "/profiles/*/classificationMilestones/*/orderProduction": ("P-07", "P-09"),
    "/profiles/*/classificationMilestones/*/stages": ("P-07", "P-09"),
    "/profiles/*/classificationMilestones/*/operation": ("P-07",),
    "/profiles/*/classificationMilestones/*/normalization": ("P-07",),
    "/profiles/*/classificationMilestones/*/rounding/**": ("P-07",),
    "/profiles/*/classificationMilestones/*/rounding": ("P-07",),
    "/profiles/*/classificationMilestones/*/appealWindow": ("P-08",),
    "/profiles/*/classificationMilestones/*/appealWindow/**": ("P-08",),
    "/profiles/*/classificationMilestones/*/drawMethod": ("P-09",),
    "/profiles/*/classificationMilestones/*/drawMethod/**": ("P-09",),
    "/profiles/*/classificationMilestones/*/cutRule/**": ("P-07",),
    "/profiles/*/classificationMilestones/*/tiebreakers": ("P-07",),
    "/profiles/*/classificationMilestones/*/tiebreakers/**": ("P-07",),
    # ---- cronograma
    "/schedule/*/id": IDENTIDADE,
    "/schedule/*/type": LOCALIZACAO,
    "/schedule/*/description": ("P-01", "P-02", "P-08"),
    "/schedule/*/startAt": ("P-01", "P-02", "P-08"),
    "/schedule/*/endAt": ("P-01", "P-02", "P-08"),
    "/schedule/*/order": ORDEM,
    "/schedule/*/status": ("P-01", "P-02"),
    "/schedule/*/location": ("P-01", "P-02", "P-08"),
    "/schedule/*/isRegistrationPeriod": REGRA,
    # ---- documentos exigidos
    "/documentRequirements/*/id": IDENTIDADE,
    "/documentRequirements/*/key": CODIGO_INTERNO,
    "/documentRequirements/*/name": LOCALIZACAO,
    "/documentRequirements/*/instructions": ("P-05",),
    "/documentRequirements/*/required": ("P-05",),
    "/documentRequirements/*/order": ORDEM,
    "/documentRequirements/*/profileId": REGRA,
    "/documentRequirements/*/modalityId": REGRA,
    "/documentRequirements/*/modalityCode": REGRA,
    "/documentRequirements/*/attachmentId": ("P-05",),
    # ---- Etapas
    "/stages/*/id": IDENTIDADE,
    "/stages/*/name": ("P-07",),
    "/stages/*/order": ORDEM,
    "/stages/*/weight": ("P-07",),
    "/stages/*/eliminatory": ("P-07",),
    "/stages/*/classificatory": ("P-07",),
    "/stages/*/minimumScore": ("P-07",),
    "/stages/*/maximumScore": ("P-07",),
    "/stages/*/forma": ("P-07",),
    "/stages/*/evaluationsPerRegistration": excluido(
        "quantas avaliações cada inscrição recebe é organização interna da banca"
    ),
    "/stages/*/rotuloFavoravel": ("P-07",),
    "/stages/*/rotuloDesfavoravel": ("P-07",),
    "/stages/*/scheduleEventId": excluido(
        "vínculo entre Etapa e Evento; a data da Etapa aparece pelo cronograma"
    ),
    # ---- seções e anexos
    "/sections/*/id": IDENTIDADE,
    "/sections/*/key": excluido("chave interna do catálogo de seções; o título é o que se mostra"),
    "/sections/*/title": LOCALIZACAO,
    "/sections/*/order": ORDEM,
    "/sections/*/type": excluido("a seção gerada não tem texto no conteúdo; a textual, sim"),
    "/sections/*/source": excluido("a seção gerada é composta pelo documento a partir dos dados"),
    "/sections/*/content": (
        "P-01",
        "P-03",
        "P-04",
        "P-05",
        "P-06",
        "P-07",
        "P-08",
        "P-09",
        "P-10",
        "P-11",
    ),
    "/attachments/*/id": IDENTIDADE,
    "/attachments/*/label": ("P-12",),
    "/attachments/*/order": ORDEM,
    "/attachments/*/artifactId": excluido(
        "identifica o arquivo do anexo; vira o link, e não texto"
    ),
    "/attachments/*/artifactHash": HASH,
}


#: Mostrados só em condição que o corpus não exercita: o guardião não exige vê-los numa resposta.
CONDICIONAIS = {
    "/schedule/*/status": "só sai quando o Evento foi declarado cancelado; o corpus não tem",
}


def classe(caminho_generalizado: str):
    """A classe do caminho, pelo padrão exato ou pela subárvore (`/**`) mais próxima."""
    if caminho_generalizado in COBERTURA:
        return COBERTURA[caminho_generalizado]
    partes = caminho_generalizado.split("/")
    while len(partes) > 1:
        partes = partes[:-1]
        candidato = "/".join(partes) + "/**"
        if candidato in COBERTURA:
            return COBERTURA[candidato]
    return None
