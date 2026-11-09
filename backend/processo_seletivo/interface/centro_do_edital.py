"""A página do Centro de Controle do Edital (136). Só leitura.

**Ao lado do detalhe, e não no lugar dele** (D-001). Durante a validação com operadores o detalhe
continua sendo a página do Edital; esta rota é nova, e os dois se ligam nos dois sentidos. Onde o
Centro mora de vez é a segunda decisão do estudo de 09/11, que só a troca do padrão (138) precisa.

**As mesmas funções do detalhe, na mesma ordem** (FR-4705, R-003). A porta, a segregação, o conjunto
de ações, as Retificações em curso, o andamento e os destinos do marco são lidos exatamente como
`views.detalhe` os lê. Uma segunda leitura divergiria da primeira na próxima mudança — é a lição da
`103` e da `104`. O que esta página faz de diferente é só a composição (`centro.py`).

**Nenhum ato.** Todo botão leva à tela real do ato, que continua sendo a que autoriza e a que
recusa: prever não é autorizar.
"""

from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import (
    acoes,
    andamento,
    atos_retificacao,
    centro,
    identidade,
    views,
)
from processo_seletivo.interface import providencias as prov


@require_http_methods(["GET"])
def centro_do_edital(request, edital_id):
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    # A porta do detalhe: inexistente e de outra unidade são o mesmo 404 (FR-4701).
    edital = views.obter_edital(actor=ator, edital_id=edital_id)
    if edital is None:
        raise Http404

    participantes = views.participantes_do_edital(edital)
    pendencias = views._pendencias(edital)
    segregacao = views.impede_por_segregacao(participantes, ator)
    conjunto = acoes.do_edital(edital, ator, pendencias=pendencias, segregacao=segregacao)
    em_curso = atos_retificacao.em_curso(edital, ator)
    dados = andamento.do_edital(edital, ator, em_curso=em_curso)
    if dados is None:
        # Antes da publicação, no cancelado ou com a derivação indisponível, não há andamento a
        # organizar: o detalhe desenha bem esse Edital, com a trilha e o bastão (D-002).
        return redirect("interface:detalhe", edital_id=edital.id)
    marcos = views._marcos_publicados(edital, ator)
    for perfil in dados.perfis:
        perfil.destinos = [
            item for item in marcos if str(item["perfil"].get("id")) == str(perfil.perfil.get("id"))
        ]
    documentos = views._documentos_publicados(edital)
    composto = centro.compor(
        edital,
        dados,
        documentos=documentos,
        em_curso=em_curso,
        alcance=andamento.Alcance.de(ator, edital),
    )
    return render(
        request,
        "interface/centro_do_edital.html",
        {
            "edital": edital,
            "centro": composto,
            "fase": centro.fase_consultada(composto, request.GET.get("fase")),
            "andamento": dados,
            "linha_das_inscricoes": andamento.linha_das_inscricoes(dados.inscricoes),
            "porque_nada": "" if composto.itens else prov.porque_nada(dados, edital),
            "documentos": documentos,
            "retificacoes_em_curso": em_curso,
            "participantes": participantes,
            "pendencias": pendencias,
            "grupo": acoes.hierarquia(conjunto),
            "pode_ver_avisos": views._pode_ver_avisos(ator, edital),
        },
    )
