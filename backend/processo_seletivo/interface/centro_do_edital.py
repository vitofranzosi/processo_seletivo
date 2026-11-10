"""O Centro de Controle do Edital (136): a página do Edital quando há andamento (138). Só leitura.

**Na rota do Edital** (138, FR-4860). A `136` o pôs numa rota própria, ao lado do detalhe, durante
a validação com operadores. Em 10/11/2026 o usuário dispensou a validação e decidiu que o Centro
mora na rota do Edital (D-001 da `138`): `views.detalhe` lê o Edital uma vez e chama `desenhar`
quando a derivação devolve andamento, e o detalhe quando não devolve.

**A leitura é a do detalhe, uma só** (FR-4705 da `136`, FR-4861 da `138`). A porta, a segregação, o
conjunto de ações, as Retificações em curso, o andamento e os destinos do marco chegam prontos em
`views.LeituraDoEdital`. Este módulo não importa `views`: só compõe (`centro.py`) e desenha.

**Nenhum ato.** Todo botão leva à tela real do ato, que continua sendo a que autoriza e a que
recusa: prever não é autorizar.
"""

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from processo_seletivo.interface import acoes, andamento, centro
from processo_seletivo.interface import providencias as prov


def desenhar(request, leitura):
    """O Centro, a partir da leitura do Edital. Quem chama garante que há andamento."""
    edital, dados = leitura.edital, leitura.andamento
    composto = centro.compor(
        edital,
        dados,
        documentos=leitura.documentos,
        em_curso=leitura.em_curso,
        alcance=dados.alcance,
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
            "porque_nada": "" if composto.tem_algo else prov.porque_nada(dados, edital),
            # A principal do conjunto é o ato do Edital, e vem cheia como no detalhe — a não ser
            # que a pessoa tenha o que fazer, e então a principal é isso (127, FR-4088).
            "peso_da_principal": "secundario" if composto.tem_sua else "",
            "documentos": leitura.documentos,
            "retificacoes_em_curso": leitura.em_curso,
            "participantes": leitura.participantes,
            "pendencias": leitura.pendencias,
            "grupo": acoes.hierarquia(leitura.conjunto),
            "pode_ver_avisos": leitura.pode_ver_avisos,
            # O que só o detalhe oferecia ao Edital publicado, nas mesmas condições (138, FR-4871).
            "pode_conversar_com_o_assistente": leitura.pode_conversar_com_o_assistente,
            "conducao_do_imutavel": leitura.conducao_do_imutavel,
            # O retorno do ato que acabou de acontecer (138, FR-4865): publicar e encerrar chegam
            # aqui.
            "conferencia_do_ato": leitura.conferencia_do_ato,
        },
    )


@require_http_methods(["GET"])
def centro_do_edital(request, edital_id):
    """O endereço da `136`, que leva à página do Edital com os mesmos parâmetros (138, FR-4863).

    **Sem porta própria** (D-003 da `138`). A resposta é a mesma para qualquer identificador, e a
    página de destino aplica a dela: o Edital de outra unidade e o inexistente dão o mesmo 404 lá.
    O fragmento não chega ao servidor; o navegador o reaplica depois do redirecionamento.
    """
    destino = reverse("interface:detalhe", args=[edital_id])
    consulta = request.META.get("QUERY_STRING", "")
    return redirect(f"{destino}?{consulta}" if consulta else destino)
