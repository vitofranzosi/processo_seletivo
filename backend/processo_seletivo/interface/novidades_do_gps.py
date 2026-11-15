"""A página Novidades do GPS (168, FR-7401 a FR-7418, FR-7601 a FR-7606).

**Toda identidade da gestão entra**, como na Agenda: a página só diz o que mudou no produto, e a
nota que é de um público se esconde de quem não o integra (`D-004`). **Não há 404**: é listagem, e
filtro ou página inválidos caem no padrão.
"""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import identidade, navegacao
from processo_seletivo.novidades import catalogo, leitura

POR_PAGINA = 12
# Os destaques à vista antes do histórico; o resto abre num recolhido (UX-821): a seção não pode
# empurrar a linha do tempo para longe da primeira tela.
DESTAQUES_A_VISTA = 6
# Quantas mudanças além da principal o bloco nomeia; as outras ficam na contagem (FR-7604). Sem o
# teto, a implantação de uma quinzena virava um segundo histórico no topo da página.
DEMAIS_A_VISTA = 3
# O que abre o "Desde sua última visita" (FR-7604): a mudança de maior peso, e não a mais recente.
PESO = {relevancia: indice for indice, relevancia in enumerate(catalogo.RELEVANCIAS)}


def _link(destino, ator):
    """O endereço e o rótulo do destino, só a quem a barra o oferece (FR-7412)."""
    secao = navegacao.secao_da_rota(destino) if destino else None
    if secao is None or not secao.alcanca(ator):
        return "", ""
    return reverse(secao.rota), secao.rotulo


def _cartao(nota, ator, documentacao, capacidade=None):
    secao = navegacao.secao_da_rota(nota.destino) if nota.destino else None
    return {
        "nota": nota,
        # A capacidade a que a nota pertence (FR-7603): a correção de 13/11 é parte do Centro de
        # Controle, e não uma coisa solta.
        "capacidade": capacidade,
        # O link só a quem a barra o oferece (FR-7412): o destino que a autorização recusa é o
        # defeito que a barra foi desenhada para não ter.
        "destino": reverse(secao.rota) if secao and secao.alcanca(ator) else "",
        "rotulo_do_destino": secao.rotulo if secao else "",
        "saiba_mais": f"{documentacao}#{nota.documentacao}" if nota.documentacao else "",
    }


def _destaques(capacidades, notas, ator, documentacao):
    """As capacidades disponíveis para quem lê, com as notas que a pessoa alcança (FR-7602)."""
    por_id = {nota.id: nota for nota in notas}
    saida = []
    for capacidade in capacidades:
        if not leitura.disponivel(capacidade, ator):
            continue
        construida_por = [por_id[i] for i in capacidade.notas if i in por_id]
        if not construida_por:
            continue
        endereco, rotulo = _link(capacidade.destino, ator)
        saida.append(
            {
                "capacidade": capacidade,
                # Quantas atualizações a construíram, e desde quando — sem inventar um dia de
                # lançamento (`D-012`): a mais antiga é a primeira que a página conhece.
                "atualizacoes": len(construida_por),
                "desde": min(nota.data for nota in construida_por),
                "destino": endereco,
                "rotulo_do_destino": rotulo,
                "saiba_mais": f"{documentacao}#{capacidade.documentacao}"
                if capacidade.documentacao
                else "",
            }
        )
    return saida


def _meses(cartoes):
    meses = []
    for cartao in cartoes:
        data = cartao["nota"].data
        chave = (data.year, data.month)
        if not meses or meses[-1]["chave"] != chave:
            meses.append({"chave": chave, "data": data, "cartoes": []})
        meses[-1]["cartoes"].append(cartao)
    return meses


def _endereco(categoria="", pagina=1):
    parametros = {"categoria": categoria} if categoria else {}
    if pagina > 1:
        parametros["pagina"] = pagina
    consulta = urlencode(parametros)
    return reverse("interface:novidades") + (f"?{consulta}" if consulta else "")


@require_http_methods(["GET"])
def novidades(request):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    try:
        notas = leitura.disponiveis(ator)
    except catalogo.CatalogoInvalido:
        # Não acontece em release que passou no CI. Se acontecer, a página diz, e o resto da gestão
        # continua de pé.
        leitura.logger.exception("novidades_indisponiveis")
        return render(request, "interface/novidades.html", {"indisponivel": True})

    desta_visita, visita_anterior = leitura.registrar_visita(request, ator, notas)
    documentacao = reverse("interface:documentacao")
    lido = catalogo.catalogo()
    destaques = _destaques(lido.capacidades, notas, ator, documentacao)
    disponiveis = {d["capacidade"].id: d["capacidade"] for d in destaques}
    dona = {
        nota: disponiveis[capacidade.id]
        for capacidade in lido.capacidades
        if capacidade.id in disponiveis
        for nota in capacidade.notas
    }
    por_id = {nota.id: nota for nota in notas}
    posicao = {nota.id: indice for indice, nota in enumerate(notas)}
    # Cada título do bloco leva ao cartão, na página da linha do tempo sem filtro em que ele está.
    recentes = (
        [
            {
                "nota": por_id[i],
                "endereco": f"{_endereco('', posicao[i] // POR_PAGINA + 1)}#{i}",
            }
            for i in desta_visita
            if i in por_id
        ]
        if visita_anterior
        else []
    )
    # A de maior peso abre o bloco; as demais vêm contadas por tipo, e listadas em linha (FR-7604).
    recentes.sort(key=lambda r: PESO[r["nota"].relevancia])
    principal, demais = (recentes[0], recentes[1:]) if recentes else (None, [])
    resumo_das_demais = [
        (c, sum(1 for r in demais if r["nota"].categoria is c)) for c in catalogo.CATEGORIAS
    ]

    categoria = request.GET.get("categoria", "")
    if categoria not in catalogo.POR_CODIGO:
        categoria = ""
    filtradas = [n for n in notas if not categoria or n.categoria.codigo == categoria]
    pagina = Paginator(filtradas, POR_PAGINA).get_page(request.GET.get("pagina"))
    # Os destaques só na primeira página, sem filtro: quem pagina ou filtra procura no histórico, e
    # não precisa rolar pela vitrine de novo.
    vitrine = destaques if pagina.number == 1 and not categoria else []
    filtros = [{"rotulo": "Todas", "codigo": "", "quantidade": len(notas)}] + [
        {
            "rotulo": c.plural,
            "codigo": c.codigo,
            "quantidade": sum(1 for n in notas if n.categoria is c),
        }
        for c in catalogo.CATEGORIAS
    ]
    for filtro in filtros:
        filtro["endereco"] = _endereco(filtro["codigo"])
    return render(
        request,
        "interface/novidades.html",
        {
            "meses": _meses(
                [_cartao(nota, ator, documentacao, dona.get(nota.id)) for nota in pagina]
            ),
            "recentes": recentes,
            "principal": principal,
            "demais": demais[:DEMAIS_A_VISTA],
            "outras": len(demais) - len(demais[:DEMAIS_A_VISTA]),
            "resumo_das_demais": [
                {"categoria": c, "quantidade": q} for c, q in resumo_das_demais if q
            ],
            "destaques": vitrine[:DESTAQUES_A_VISTA],
            "mais_destaques": vitrine[DESTAQUES_A_VISTA:],
            "primeira_visita": visita_anterior is None,
            "visita_anterior": visita_anterior,
            "filtros": filtros,
            "categoria": categoria,
            "pagina": pagina,
            "anteriores": _endereco(categoria, pagina.next_page_number())
            if pagina.has_next()
            else "",
            "seguintes": _endereco(categoria, pagina.previous_page_number())
            if pagina.has_previous()
            else "",
            "inicio": notas[-1].data if notas else None,
        },
    )
