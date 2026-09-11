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
    for linha in perfil.get("vacancyTable") or []:
        declarada = str(linha.get("modalityId")) if linha.get("modalityId") else None
        if declarada == alvo:
            return linha
    return None


def calcular_corte(
    *, edital, perfil_id, marco_id, lista_id=None, at=None, desde=0, faixa_anterior=None
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
    conteudo = ato.versao.content
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
    progrediram, excedentes, primeira, ultima = faixa.calcular(
        [(str(ident), posicao) for ident, posicao, _ in posicoes],
        alvo=alvo,
        excedente=regra.get("surplusCount") or 0,
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
        "versao": ato.versao,
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


__all__ = ["calcular_corte", "geracao_vigente", "linha_do_quadro", "regra_do_marco"]
