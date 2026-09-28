"""O que uma Retificação alterou, dito em linguagem do domínio (024, FR-130, D-005).

**Por que existe.** `AlteracaoNormativa.target_path` é endereçamento estrutural —
`/profiles/id=<uuid>/immediateVacancies`. É a forma certa para o sistema localizar o que mudou, e
a forma errada para dizer a alguém o que mudou: é vocabulário nosso, não do domínio, e o Princípio I
manda que a página fale a língua do Edital.

**O que este módulo devolve, e o que ele recusa devolver.** Devolve *onde* — a entidade alterada,
pelo rótulo que ela tem no conteúdo-base — e *qual campo*. **Não** devolve valor anterior nem valor
novo: quem quer o texto exato do ato abre o documento da Retificação, que está na mesma linha do
histórico. A tela de homologação da gestão precisa do antes e do depois, porque quem aprova
confere valores; quem se candidata precisa saber **que** as vagas daquele Perfil mudaram.

**Caminho não reconhecido não produz linha.** É a `D-009` aplicada ao caso mais fácil de errar:
inventar um rótulo genérico para um caminho que não se sabe ler afirmaria algo sobre o Edital. Uma
alteração a menos na lista é honesta; uma linha que diz a coisa errada, não.

**O silêncio tem um custo, e ele é cobrado contra o contrato.** Calar o desconhecido só é honesto
se o conhecido cobrir o que uma Retificação pode alterar. Até 27/09 não cobria: 45 dos 84 campos
que `editais/domain/mutabilidade` declara retificáveis não viravam linha — o percentual da cota, o
quadro de vagas, o prazo recursal, o método do sorteio —, e o contador dizia "(1)" onde o ato
alterara dois campos (`doc/achado-o-que-mudou-cala-campos-retificaveis.md`). O dicionário agora é
chaveado como o contrato, por `(coleção, caminho relativo)`, e `test_alteracoes_legiveis` sintetiza
um caminho para cada par retificável e exige linha: campo novo sem tradução reprova no dia em que
nasce, e não no dia em que alguém o procura no portal.

**Os rótulos acrescentados em 27/09 são os da tela da Retificação** (`interface/retificacao.py`),
para que quem retifica e quem se inscreve leiam o mesmo nome. Os anteriores ficaram como estavam, e
alguns divergem da tela — "Denominação" × "Nome da Etapa", "Obrigatoriedade" × "Obrigatório". O
guardião cobra a existência da linha, e não o nome; unificá-los está registrado no achado. O módulo
não importa os rótulos de lá: domínio não importa de `interface`, e a cópia é o preço dessa
fronteira.
"""

from processo_seletivo.editais.domain import mutabilidade
from processo_seletivo.publicacoes.domain.changes import resolve_path
from processo_seletivo.publicacoes.domain.colecoes import FORMA_DA_COLECAO

# A posição de acréscimo da gramática: `/attachments/-` é "no fim desta coleção".
ACRESCIMO = "-"

OPERACOES = {"ADD": "acrescentado", "REPLACE": "alterado", "REMOVE": "removido"}

# Como cada coleção normativa se chama numa página pública, e por qual campo cada elemento dela se
# reconhece. O nome do elemento vem do **conteúdo-base** — é o que aquela versão dizia, que é o que
# quem lê precisa reconhecer. `None` no campo do nome é elemento sem nome próprio, e quem o nomeia é
# `_nome_proprio`.
COLECOES = {
    "profiles": ("Perfil", "name"),
    "schedule": ("Evento do cronograma", "description"),
    "stages": ("Etapa", "name"),
    "sections": ("Seção", "title"),
    "attachments": ("Anexo", "label"),
    "documentRequirements": ("Documento exigido", "name"),
    "competitionModalities": ("Modalidade de concorrência", "name"),
    # Pelo rótulo, e não pelo tipo: o tipo é `DATA` ou `INTEIRO`, vocabulário nosso, e nomeava o
    # fato como "Fato declarado “DATA”" em todo acréscimo e remoção.
    "declaredFacts": ("Fato declarado", "label"),
    "classificationMilestones": ("Marco de classificação", "name"),
    # O critério não tem nome: o que o distingue dos vizinhos é a ordem em que se aplica.
    "tiebreakers": ("Critério de desempate", None),
    # A linha também não: ela é a lista de concorrência a que dá vagas, e o nome vem da Modalidade
    # que ela aponta — ou da ampla, que é a linha sem Modalidade (025, D-002).
    "vacancyTable": ("Linha do quadro de vagas", None),
}


# Quais coleções moram dentro de qual, lido da forma que a gramática de endereçamento declara. Sem
# isto, um campo do elemento que se chame como uma coleção — `stages` do marco, que é lista de
# identidades — seria lido como descida para dentro dela.
def _filhas():
    """`{coleção que contém (None para o Edital): {coleções dentro dela}}`."""
    filhas = {}
    for colecao, forma in FORMA_DA_COLECAO.items():
        nomes = [segmento for segmento in forma.strip("/").split("/") if segmento != "*"]
        if nomes:
            filhas.setdefault(nomes[-2] if len(nomes) > 1 else None, set()).add(colecao)
    return filhas


_FILHAS = _filhas()

# Os campos, por coleção. O que não estiver aqui não vira linha — ver a docstring do módulo.
CAMPOS = {
    "profiles": {
        "code": "Código",
        "name": "Denominação",
        "description": "Descrição",
        "requirements": "Requisitos",
        "immediateVacancies": "Vagas imediatas",
        "reserveType": "Cadastro reserva",
        "reserveLimit": "Limite do cadastro reserva",
        "locality": "Localidade",
        "duties": "Atribuições",
        "workload": "Carga horária",
        "compensation": "Remuneração",
        "generalCompetitionModalityId": "Modalidade que é a ampla concorrência",
        "callForm": "Forma de comunicar a convocação",
        "vacancyReversion/kind": "Gatilho da reversão de vaga reservada",
        # O objeto que nasce por Retificação (016, D-007): `REPLACE` sobre o `null` publicado.
        "vacancyReversion": "Reversão de vaga reservada",
    },
    "schedule": {
        "type": "Tipo",
        "description": "Descrição",
        "startAt": "Início",
        "endAt": "Término",
        "order": "Ordem",
        "location": "Local",
        "isRegistrationPeriod": "Período de inscrições",
    },
    "stages": {
        "name": "Denominação",
        "order": "Ordem",
        "weight": "Peso",
        "eliminatory": "Caráter eliminatório",
        "classificatory": "Caráter classificatório",
        "minimumScore": "Nota mínima",
        "maximumScore": "Nota máxima",
        "forma": "Forma de conclusão",
        "evaluationsPerRegistration": "Avaliações por inscrição",
        "rotuloFavoravel": "Rótulo favorável",
        "rotuloDesfavoravel": "Rótulo desfavorável",
    },
    "sections": {"title": "Título", "content": "Texto", "order": "Ordem"},
    "attachments": {
        "label": "Rótulo",
        "order": "Ordem editorial",
        "artifactId": "Arquivo",
        # A conferência anda junto do arquivo e não é decisão própria. Mostrá-la como linha
        # separada diria duas vezes a mesma substituição, uma delas em SHA-256 — é a correção que
        # a `020` já fez na tela da gestão, e que não vale a pena refazer aqui.
        "artifactHash": None,
    },
    "documentRequirements": {
        "name": "Nome",
        "instructions": "Instruções",
        "required": "Obrigatoriedade",
        "order": "Ordem",
        "attachmentId": "Modelo",
        # O recorte, nas três formas: o exato por Perfil e por Modalidade, e o transversal da 044
        # (FR-721). O campo é nomeado, e não o valor, como toda linha deste resumo (D-008). Os dois
        # primeiros ficaram fora até 26/09, e o resumo calava justamente a alteração que mais pesa
        # para quem se inscreve: a conferência de 25/09 retificou o laudo para valer só no C1, e o
        # portal listou 6 das 7 alterações. Os rótulos são os da tela da gestão.
        "profileId": "Exigido apenas do Perfil",
        "modalityId": "Exigido apenas da modalidade",
        "modalityCode": "Modalidade em todos os Perfis",
    },
    "competitionModalities": {
        "code": "Código",
        "name": "Denominação",
        "description": "Descrição",
        # A regra da cota tem quatro partes que se retificam e quatro que não (026). O caminho
        # inteiro é a chave: `normativeRule` sozinho não diria qual das quatro mudou.
        "normativeRule/percentage": "Percentual (%)",
        "normativeRule/foundation": "Fundamento normativo",
        "normativeRule/version": "Versão do fundamento",
        "normativeRule/effectiveFrom": "Vigente desde",
    },
    "vacancyTable": {
        "immediateVacancies": "Vagas imediatas",
        "modalityId": "Lista de concorrência",
    },
    "declaredFacts": {"label": "Rótulo exibido ao candidato"},
    "classificationMilestones": {
        "name": "Denominação do marco",
        "orderProduction": "Como a ordem é produzida",
        "operation": "Como as pontuações se combinam",
        "normalization": "Normalização antes de combinar",
        "rounding/scale": "Casas decimais da pontuação",
        "rounding/mode": "Como arredondar",
        "appealWindow/admits": "Admite recurso",
        "appealWindow/durationDays": "Prazo em dias",
        "appealWindow/unit": "Contagem do prazo",
        "drawMethod/algorithm": "Algoritmo do sorteio",
        "drawMethod/source": "Fonte pública da semente",
        "drawMethod/occurrence": "Ocorrência que fixará a semente",
        "drawMethod/occurrenceAt": "Quando a ocorrência acontece",
        "drawMethod/derivation": "Como a ocorrência decorre da data programada",
        "drawMethod/normalization/rule": "Regra de normalização",
        "drawMethod/normalization/text": "Normalização, como se publica",
        "drawMethod/substitutionRule/rule": "Regra de substituição",
        "drawMethod/substitutionRule/text": "Substituição, como se publica",
        "drawMethod/qualifyingStageId": "Etapa que habilita ao sorteio",
        "cutRule/targetCount": "Quantos progridem",
        "cutRule/surplusCount": "Suplentes alcançados na mesma faixa",
        "cutRule/tieOutcome": "Empate na última posição",
        # Os objetos que nascem por Retificação (048, FR-785; 021, FR-014): um `REPLACE` sobre o
        # `null` publicado, com o objeto inteiro. Os nomes são os da tela de composição, que é
        # onde a Retificação que os faz nascer manda a pessoa ler.
        "cutRule": "Regra de corte",
        "appealWindow": "Recurso contra o resultado",
        "drawMethod": "Método do sorteio",
    },
    "tiebreakers": {"order": "Ordem de aplicação"},
}

# Os campos de topo do Edital: alterados sem passar por coleção nenhuma.
CAMPOS_DO_EDITAL = {
    "title": "Título do Edital",
    "description": "Descrição do Edital",
    "number": "Número",
    "year": "Ano",
    "processoTitle": "Título do Processo",
    "processoCode": "Código do Processo",
    "maxInscricoesPorCandidato": "Teto de inscrições por candidato",
    "matriculationRequest/declarationText": "Declaração do Requerimento de Matrícula",
    # O método comum ao Edital (030, FR-429): nove campos, espelhando os do marco.
    "drawMethod/algorithm": "Algoritmo do sorteio comum",
    "drawMethod/source": "Fonte pública da semente",
    "drawMethod/occurrence": "Ocorrência que fixará a semente",
    "drawMethod/occurrenceAt": "Quando a ocorrência acontece",
    "drawMethod/derivation": "Como a ocorrência decorre da data programada",
    "drawMethod/normalization/rule": "Regra de normalização",
    "drawMethod/normalization/text": "Normalização, como se publica",
    "drawMethod/substitutionRule/rule": "Regra de substituição",
    "drawMethod/substitutionRule/text": "Substituição, como se publica",
}

# A mesma raiz com o nome que o contrato lhe dá, para que um dicionário só responda pelas duas.
CAMPOS[mutabilidade.RAIZ] = CAMPOS_DO_EDITAL


def alteracao_legivel(conteudo_base, alteracao):
    """Uma alteração dita em português, ou `None` quando não se sabe lê-la.

    `alteracao` é qualquer objeto com `target_path` e `operation` — a `AlteracaoNormativa`
    persistida serve, e um par simples também, o que mantém o módulo testável sem banco.

    O caminho se lê em duas partes: **onde** — a descida pelas coleções, uma entidade por nível,
    de `/profiles/id=…` até `/tiebreakers/id=…` — e **qual campo**, que é o que sobra, lido
    inteiro. Ler só o primeiro segmento do que sobra calava os campos compostos: `normativeRule`
    sozinho não diz se mudou o percentual ou o fundamento.
    """
    caminho = (getattr(alteracao, "target_path", "") or "").strip()
    operacao = OPERACOES.get(getattr(alteracao, "operation", ""), "alterado")
    if not caminho.startswith("/"):
        return None

    segmentos = caminho.strip("/").split("/")
    nomes = []
    colecao = mutabilidade.RAIZ
    contem = conteudo_base
    pai = None
    while len(segmentos) >= 2 and segmentos[0] in _FILHAS.get(pai, ()) and segmentos[0] in COLECOES:
        colecao, seletor, *segmentos = segmentos
        nomes.append(_nome_da_entidade(contem, colecao, seletor))
        contem = _elemento(contem, colecao, seletor)
        pai = colecao

    # O elemento inteiro: ele entrou ou saiu do Edital.
    if nomes and not segmentos:
        return {"onde": " — ".join(nomes), "campo": "", "operacao": operacao}

    campo = _rotulo_do_campo(colecao, "/".join(segmentos))
    if campo is None:
        return None
    return {"onde": " — ".join(nomes) or "O Edital", "campo": campo, "operacao": operacao}


def alteracoes_legiveis(conteudo_base, alteracoes):
    """As que se sabe ler, na ordem em que o ato as declarou."""
    lidas = (alteracao_legivel(conteudo_base, item) for item in alteracoes)
    return [item for item in lidas if item is not None]


def _rotulo_do_campo(colecao, campo):
    """`None` significa "não vira linha" — tanto o campo desconhecido quanto o deliberadamente
    omitido. Os dois casos têm a mesma consequência na tela, e distingui-los aqui só serviria para
    o chamador ter de tratar dois."""
    return CAMPOS.get(colecao, {}).get(campo)


def _elemento(conteudo, colecao, seletor):
    """O elemento no conteúdo-base, ou `None` quando ele não está lá — acrescentado agora, ou
    conteúdo-base sem ele."""
    if seletor == ACRESCIMO or not isinstance(conteudo, dict):
        return None
    valor = resolve_path(conteudo, f"/{colecao}/{seletor}")
    return valor if isinstance(valor, dict) else None


def _nome_da_entidade(conteudo, colecao, seletor):
    """`Perfil “Professor de Informática”`, lido do conteúdo-base.

    O rótulo vem daquela versão, e não do banco: é o que o Edital dizia quando a Retificação foi
    escrita, que é o que quem lê o histórico precisa reconhecer. Sem nome legível — porque o
    elemento está sendo acrescentado agora, ou porque o conteúdo-base não o tem — devolve só o
    tipo, que já diz mais do que um UUID.

    `conteudo` é quem **contém** a coleção: o Edital para o Perfil, o Perfil para a Modalidade.
    """
    rotulo, campo_do_nome = COLECOES[colecao]
    elemento = _elemento(conteudo, colecao, seletor)
    if elemento is None:
        return rotulo
    if campo_do_nome is None:
        return _nome_proprio(conteudo, colecao, elemento, rotulo)
    nome = str(elemento.get(campo_do_nome) or "").strip()
    return f"{rotulo} “{nome}”" if nome else rotulo


def _nome_proprio(conteudo, colecao, elemento, rotulo):
    """O nome do elemento que não tem campo de nome."""
    if colecao == "tiebreakers":
        ordem = elemento.get("order")
        return f"{rotulo} nº {ordem}" if isinstance(ordem, int) else rotulo
    # A linha do quadro: o nome da Modalidade que ela aponta, procurada no mesmo Perfil. Sem
    # Modalidade, ela é a linha geral — e é assim que a tela da Retificação a chama.
    modalidade = elemento.get("modalityId")
    if modalidade is None:
        return f"{rotulo} “Ampla concorrência”"
    for candidata in conteudo.get("competitionModalities") or []:
        if isinstance(candidata, dict) and str(candidata.get("id")) == str(modalidade):
            nome = str(candidata.get("name") or "").strip()
            return f"{rotulo} “{nome}”" if nome else rotulo
    return rotulo
