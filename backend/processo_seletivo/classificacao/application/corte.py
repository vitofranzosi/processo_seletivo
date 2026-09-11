"""Calcula a faixa que progride, a partir da ordem vigente e da regra publicada (014).

**Calcular não é emitir**, e é o desenho que a `015` fixou para a ordem: abrir a tela calcula e
mostra; não grava, não emite e não substitui. Um corte regenerado em silêncio quando a tela abre
mudaria, sozinho, quem participa da Etapa seguinte.

**Este módulo lê a ordem como ela foi emitida.** Não reordena, não recalcula pontuação e não aplica
critério de desempate novo — quem ordena é a `015`, e o corte é leitura dela.
"""

from processo_seletivo.classificacao.application.selectors import ato_vigente, estado_do_marco
from processo_seletivo.classificacao.domain import faixa
from processo_seletivo.classificacao.domain.nomes import nomes_do_marco
from processo_seletivo.classificacao.models import Corte, ItemDoCorte
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError

SEM_POSICAO = "considerado sem posição na ordem"


def geracao_vigente(*, edital, perfil_id, marco_id, lista_id=None):
    """As faixas da geração que ninguém sucedeu, da mais antiga para a mais nova.

    **Vigente é a geração, e não a faixa**: a raiz mais todas as continuações dela. Perguntar pela
    faixa sem sucessor devolveria a continuação e esconderia a raiz, que continua governando quem
    progrediu primeiro.
    """
    raiz = (
        Corte.objects.filter(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            raiz__isnull=True,
            sucessores__isnull=True,
        )
        .order_by("-emitido_em")
        .first()
    )
    if raiz is None:
        return []
    return [raiz, *Corte.objects.filter(raiz=raiz).order_by("emitido_em")]


def regra_do_marco(conteudo, *, perfil_id, marco_id):
    """A regra de corte publicada naquela versão, ou `None` quando o marco não corta."""
    nomes = nomes_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    return faixa.normalizar((nomes.get("marco") or {}).get("cutRule"))


def linha_do_quadro(conteudo, *, perfil_id, lista_id):
    """A linha do quadro de vagas do recorte — a da Modalidade, ou a geral quando não há lista.

    `lista_id` nulo lê a **linha geral**, e não é atalho: o recorte sem lista é a ampla
    concorrência, e a linha de `modalityId` nulo é onde a quantidade dela mora. A leitura vem do
    conteúdo publicado da versão que o ato citou, e não do relacional em elaboração — senão uma
    Retificação posterior mudaria o alvo de um corte já emitido.
    """
    from processo_seletivo.classificacao.domain.universo import por_identidade

    perfil = por_identidade((conteudo or {}).get("profiles"), perfil_id) or {}
    alvo = str(lista_id) if lista_id else None
    # **A lista da ampla concorrência lê a linha geral**, e não uma linha própria: é a mesma
    # identidade vista dos dois lados, e é o que a declaração do Perfil existe para dizer (D-014).
    ampla = perfil.get("generalCompetitionModalityId")
    if ampla and alvo == str(ampla):
        alvo = None
    for linha in perfil.get("vacancyTable") or []:
        declarada = str(linha.get("modalityId")) if linha.get("modalityId") else None
        if declarada == alvo:
            return linha
    return None


def calcular_corte(
    *,
    edital,
    perfil_id,
    marco_id,
    lista_id=None,
    at=None,
    desde=0,
    faixa_anterior=None,
    quantidade=None,
):
    """A proposta de faixa: quem progride, quem fica fora, e o universo que a delimita.

    `desde` e `faixa_anterior` só chegam preenchidos na continuação, e é o que a faz começar depois
    da última posição já alcançada em vez de recomeçar do primeiro.
    """
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        raise DomainError(
            "sem_ato_vigente",
            "Este recorte não tem ordem emitida: não há o que cortar.",
            409,
        )
    # **A norma é a vigente, e a ordem é a emitida.** O ato congela as posições; a regra e o quadro
    # vêm da versão em vigor **agora**, que é o que a frase que governa esta feature diz: "a partir
    # da ordem vigente e da regra publicada". Ler a regra de `ato.versao` fazia a geração sucessora
    # nascer obsoleta sempre que a Retificação alcançasse o quadro sem tocar no marco — o alvo
    # derivado recalculava o número antigo e a comparação com a versão vigente acusava a
    # divergência que a própria sucessão deveria fechar.
    versao = effective_version(edital_id=edital.id, at=at)
    conteudo = versao.content
    regra = regra_do_marco(conteudo, perfil_id=perfil_id, marco_id=marco_id)
    if regra is None:
        raise DomainError(
            "marco_sem_regra_de_corte",
            "Este marco não declara regra de corte: o Edital não publicou quantos progridem.",
            409,
        )
    # **Não se corta sobre ordem obsoleta** (FR-198): seria selecionar quem progride por uma ordem
    # que o próprio sistema já sabe estar para trás.
    estado = estado_do_marco(edital=edital, marco_id=marco_id, at=at, lista_id=lista_id)
    if estado.get("obsoleto"):
        causas = "; ".join(item.get("descricao", "") for item in estado.get("divergencias") or [])
        raise DomainError(
            "ato_obsoleto",
            f"A ordem deste recorte está obsoleta, e o corte sairia dela. {causas}".strip(),
            409,
        )
    alvo, origem = _alvo(regra, conteudo, perfil_id=perfil_id, lista_id=lista_id)
    posicoes = list(
        ato.posicoes.all().values_list("inscricao_id", "posicao", "motivo").order_by("posicao")
    )
    # **A continuação não herda o teto da primeira emissão** (FR-204). O alvo e o excedente
    # publicados formam a faixa **inicial**; a continuação vai até onde quem emite declarou, e o
    # Edital não publica teto nenhum para ela — ele diz "até que se preencha", e quantas vagas foram
    # preenchidas é conta da `016`. Limitar a continuação a `alvo + excedente` era exatamente o teto
    # que a `FR-204` deixou de ter, herdado por dentro do cálculo.
    tamanho = int(alvo) if quantidade is None else int(quantidade)
    excedente = int(regra.get("surplusCount") or 0) if quantidade is None else 0
    progrediram, excedentes, primeira, ultima = faixa.calcular(
        [(str(ident), posicao) for ident, posicao, _ in posicoes],
        alvo=tamanho,
        excedente=excedente,
        desfecho=regra.get("tieOutcome"),
        desde=desde,
    )
    dentro, excedente_por_empate = set(progrediram), set(excedentes)
    itens = [
        {
            "inscricao_id": str(ident),
            "posicao": posicao,
            "consequencia": (
                ItemDoCorte.Consequencia.PROGREDIU
                if str(ident) in dentro
                else ItemDoCorte.Consequencia.FORA_DA_FAIXA
            ),
            "motivo": _motivo(str(ident), posicao, motivo, dentro, primeira, ultima, desde),
            "excedente_por_empate": str(ident) in excedente_por_empate,
        }
        for ident, posicao, motivo in posicoes
    ]
    return {
        "ato": ato,
        "versao": versao,
        "regra": regra,
        "alvo": alvo,
        "origem_do_alvo": origem,
        "excedente": int(regra.get("surplusCount") or 0),
        "primeira_posicao": primeira,
        "ultima_posicao": ultima,
        "itens": itens,
        "progrediram": len(dentro),
        "fora": len(itens) - len(dentro),
        "universo": {
            "editalId": str(edital.id),
            "profileId": str(perfil_id),
            "milestoneId": str(marco_id),
            "listId": str(lista_id) if lista_id else None,
            "orderingActId": str(ato.id),
            "versionId": str(ato.versao_id),
            "cutRule": regra,
            "target": {"count": alvo, **origem},
            "surplus": int(regra.get("surplusCount") or 0),
            "previousCutId": str(faixa_anterior.id) if faixa_anterior is not None else None,
        },
    }


def _alvo(regra, conteudo, *, perfil_id, lista_id):
    if regra.get("targetKind") != faixa.ALVO_DO_QUADRO:
        return faixa.alvo_apurado(regra)
    linha = linha_do_quadro(conteudo, perfil_id=perfil_id, lista_id=lista_id)
    # **A conferência por recorte mora aqui, e não na publicação** — é onde a lista é conhecida. A
    # publicação exige a linha geral; exigir também uma por Modalidade declarada tornaria
    # impublicável o Edital que declara "Ampla concorrência" como Modalidade, que por norma nunca
    # tem linha reservada (025, FR-176, R-006).
    if linha is None:
        raise DomainError(
            "recorte_sem_linha_de_quadro",
            "A regra deriva o alvo do quadro de vagas, e este recorte não tem linha publicada.",
            409,
        )
    return faixa.alvo_apurado(
        regra,
        quantidade_do_quadro=linha.get("immediateVacancies"),
        linha_do_quadro=str(linha.get("id")) if linha.get("id") else None,
    )


def _motivo(ident, posicao, motivo_da_ordem, dentro, primeira, ultima, desde):
    """A causa em uma frase — e quem ficou fora precisa dela mais do que quem entrou (FR-194)."""
    if ident in dentro:
        return ""
    if posicao is None:
        return motivo_da_ordem or SEM_POSICAO
    if desde and posicao <= desde:
        return f"alcançado por faixa anterior, na posição {posicao}"
    alcance = ultima if ultima is not None else primeira - 1
    return f"posição {posicao}, além da última alcançada por esta faixa ({alcance})"


__all__ = [
    "calcular_corte",
    "divergencias_da_reproducao",
    "estado_do_corte",
    "geracao_vigente",
    "linha_do_quadro",
    "regra_do_marco",
    "reproduzir_corte",
]


def estado_do_corte(*, edital, perfil_id, marco_id, lista_id=None, at=None):
    """A geração vigente ao lado do que a norma diz agora — sem escrever nenhuma das duas (014).

    Devolve `obsoleto` e as **causas nomeadas**, e nunca "divergências": a `018` já pagou esse preço
    uma vez, quando a divergência genérica escondia o reingresso e quem lia não sabia o que havia
    mudado (FR-216).

    **São quatro causas, e três delas não custam consulta nova** — o ato vigente e a versão já são
    lidos para o estado da ordem. A quarta é a mesma pergunta que a tela do marco já faz.
    """
    geracao = geracao_vigente(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
    )
    if not geracao:
        return {"geracao": [], "obsoleto": False, "causas": []}
    raiz = geracao[0]
    causas = []
    vigente = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if vigente is None or str(vigente.id) != str(raiz.ato_id):
        causas.append(
            {
                "tipo": "ordem_sucedida",
                "descricao": (
                    "A ordem que este corte leu foi sucedida. A faixa continua vigente e "
                    "produzindo efeito até que a geração sucessora seja emitida."
                ),
            }
        )
    versao = effective_version(edital_id=edital.id, at=at)
    regra_agora = regra_do_marco(versao.content, perfil_id=perfil_id, marco_id=marco_id)
    if regra_agora != (raiz.universo or {}).get("cutRule"):
        causas.append(
            {
                "tipo": "regra_alterada",
                "descricao": (
                    "A regra de corte publicada mudou desde esta emissão: o alvo, o excedente, o "
                    "desfecho do empate ou a Etapa governada já não são os que a faixa congelou."
                ),
            }
        )
    causas.extend(_quadro_alterado(raiz, versao, perfil_id=perfil_id, lista_id=lista_id))
    causas.extend(_reingressou(edital, geracao))
    return {"geracao": geracao, "obsoleto": bool(causas), "causas": causas}


def _quadro_alterado(raiz, versao, *, perfil_id, lista_id):
    """A linha do quadro que o alvo derivado leu mudou de quantidade.

    Só é detectável porque o ato guardou o `rowId`: a quantidade sozinha não identifica a linha de
    onde veio, e sem a identidade a comparação não saberia dizer se **aquela** linha mudou.
    """
    alvo = (raiz.universo or {}).get("target") or {}
    if alvo.get("source") != "VACANCY_TABLE_ROW":
        return []
    linha = linha_do_quadro(versao.content, perfil_id=perfil_id, lista_id=lista_id)
    # **A identidade entra na comparação, e não só a quantidade.** Sem ela, uma Retificação que
    # substitua a linha por outra com o mesmo número deixaria a geração em dia — e a fonte
    # normativa que o ato cita já não seria a que existe. É para isso que o `rowId` foi gravado.
    mesma_linha = linha is not None and str(linha.get("id") or "") == str(alvo.get("rowId") or "")
    if mesma_linha and linha.get("immediateVacancies") == alvo.get("count"):
        return []
    return [
        {
            "tipo": "quadro_alterado",
            "descricao": (
                "A linha do quadro de vagas de onde este corte tirou o alvo mudou, ou deixou de "
                "existir na versão vigente."
            ),
        }
    ]


def _reingressou(edital, geracao):
    """Alguém voltou ao universo **do ato de ordenação** que a faixa leu (FR-218, FR-230).

    **A medida é o ato, e não "o universo do corte"**, e a diferença é a feature inteira: todo
    participante considerado está no universo do corte, de modo que medir ali faria **qualquer**
    deferimento obsoletá-lo — inclusive o de quem já está dentro da faixa. Somado ao bloqueio de
    trabalho novo, isso pararia a Etapa para exigir uma geração sucessora idêntica à anterior. No
    77/2026, em que o recurso é julgado na própria Etapa que o corte governa, esse seria o caso
    normal, e não a exceção.

    "Alcançar o ato" tem duas metades, e as duas são conferidas: a pessoa estar entre os
    participantes que ele congelou, **e** o Resultado superado ser de uma das Etapas que produziram
    a ordem. Sem a segunda, o deferimento na Etapa governada obsoletaria o corte — que é justamente
    o que a `FR-230` proíbe.
    """
    from processo_seletivo.resultados.models import ResultadoEtapa

    universo = geracao[0].ato.universo or {}
    participantes = [str(item) for item in (universo.get("participants") or [])]
    # **As Etapas que produziram a ordem, e só elas.** É aqui que a `FR-230` vira código: um
    # deferimento na Etapa **governada** não move posição nenhuma, e obsoletar por causa dele
    # pararia a Etapa para exigir uma geração sucessora idêntica à anterior. Num ato de sorteio a
    # coleção é vazia — a ordem não vem de Etapa nenhuma —, e por isso reingresso algum o obsoleta.
    etapas_da_ordem = {
        str(item.get("stageId"))
        for item in (universo.get("stageResults") or [])
        if isinstance(item, dict) and item.get("stageId")
    }
    if not participantes or not etapas_da_ordem:
        return []
    reingressaram = ResultadoEtapa.vigentes.filter(
        edital=edital,
        inscricao_id__in=participantes,
        etapa_id__in=etapas_da_ordem,
        resultado_anterior__isnull=False,
    ).exists()
    if not reingressaram:
        return []
    return [
        {
            "tipo": "participante_reingressou",
            "descricao": (
                "Um participante reingressou no universo da ordem por decisão recursal deferida: "
                "a faixa pode não ser mais a que a norma produz."
            ),
        }
    ]


def reproduzir_corte(corte):
    """A faixa calculada de novo, **a partir do universo declarado** — e não do estado de hoje.

    Registrar o que foi usado e chegar de novo ao mesmo resultado são coisas distintas, e a
    Constituição pede a segunda. Por isso nada aqui consulta a regra vigente, o quadro vigente ou o
    ato vigente: a regra vem do `universo` que o corte congelou, as posições vêm do ato que ele
    citou, e o alvo vem do número que ele apurou — inclusive quando derivado, porque a linha do
    quadro pode ter mudado desde então (FR-199).

    **A posição gravada no item nunca é entrada do motor**, pela mesma razão que a `015` já
    registrou para a ordem: usá-la faria a reprodução confirmar a si mesma.
    """
    universo = corte.universo or {}
    regra = universo.get("cutRule") or {}
    alvo = (universo.get("target") or {}).get("count") or 0
    desde = 0
    if corte.faixa_anterior_id is not None:
        desde = corte.faixa_anterior.ultima_posicao or 0
    posicoes = [
        (str(inscricao_id), posicao)
        for inscricao_id, posicao in corte.ato.posicoes.all()
        .values_list("inscricao_id", "posicao")
        .order_by("posicao")
    ]
    progrediram, excedentes, primeira, ultima = faixa.calcular(
        posicoes,
        alvo=alvo,
        excedente=universo.get("surplus") or 0,
        desfecho=regra.get("tieOutcome"),
        desde=desde,
    )
    return {
        "progrediram": progrediram,
        "excedentes": excedentes,
        "primeira_posicao": primeira,
        "ultima_posicao": ultima,
    }


def divergencias_da_reproducao(corte, *, reproduzido=None):
    """O que a reprodução encontra de diferente do que o ato gravou — vazio quando reproduz.

    A continuação limita a faixa à quantidade que quem emitiu declarou (`FR-203`), e essa quantidade
    **não** está no universo: ela é decisão de quem emite, e não norma publicada. Por isso a
    comparação de uma continuação é do **prefixo**: a reprodução diz até onde a faixa poderia ir, e
    o ato diz até onde ela foi.
    """
    reproduzido = reproduzido or reproduzir_corte(corte)
    gravados = [
        str(item)
        for item in corte.itens.filter(consequencia=ItemDoCorte.Consequencia.PROGREDIU)
        .order_by("posicao")
        .values_list("inscricao_id", flat=True)
    ]
    calculados = reproduzido["progrediram"]
    if corte.faixa_anterior_id is not None:
        calculados = calculados[: len(gravados)]
    if gravados == calculados:
        return []
    return [
        {
            "tipo": "faixa_divergente",
            "descricao": (
                "A reprodução a partir do universo declarado não chega à mesma faixa que o ato "
                "gravou."
            ),
        }
    ]
