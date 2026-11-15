"""A página Novidades do GPS (168, FR-7401 a FR-7418).

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


def _cartao(nota, ator, documentacao):
    secao = navegacao.secao_da_rota(nota.destino) if nota.destino else None
    return {
        "nota": nota,
        # O link só a quem a barra o oferece (FR-7412): o destino que a autorização recusa é o
        # defeito que a barra foi desenhada para não ter.
        "destino": reverse(secao.rota) if secao and secao.alcanca(ator) else "",
        "rotulo_do_destino": secao.rotulo if secao else "",
        "saiba_mais": f"{documentacao}#{nota.documentacao}" if nota.documentacao else "",
    }


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

    categoria = request.GET.get("categoria", "")
    if categoria not in catalogo.POR_CODIGO:
        categoria = ""
    filtradas = [n for n in notas if not categoria or n.categoria.codigo == categoria]
    pagina = Paginator(filtradas, POR_PAGINA).get_page(request.GET.get("pagina"))
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
            "meses": _meses([_cartao(nota, ator, documentacao) for nota in pagina]),
            "recentes": recentes,
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
