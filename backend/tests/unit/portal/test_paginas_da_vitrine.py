"""A ordem e as páginas da vitrine, sem banco.

**Por que existe.** A vitrine mostrava todas as seleções de uma vez, e as encerradas da mais antiga
para a mais nova: com dezenas de Editais fechados, a página era quase toda histórico, e o histórico
começava pelo que menos gente procura. Estes casos prendem as duas regras que saíram disso — a
encerrada mais recente primeiro, com desempate total, e o recorte em páginas que leva a consulta
consigo. Os casos de página estão em `tests/integration/portal/test_paginas_da_vitrine.py`.
"""

from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from processo_seletivo.inscricoes.domain.periodo import (
    ABERTO,
    ENCERRADO,
    FUTURO,
    NAO_DESIGNADO,
    Periodo,
)
from processo_seletivo.portal import leitura

FUSO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 13, 12, 0, tzinfo=FUSO)
OPCOES = {"unidades": ["Cefor"], "perfis": ["Enfermeiro"]}


def dias(quantos):
    return AGORA + timedelta(days=quantos)


def selecao(numero, estado, *, inicio=None, fim=None, cancelado=False, desfecho=None, vigente=-90):
    return {
        "edital_id": f"edital-{numero}",
        "numero": str(numero),
        "ano": "2026",
        "estado": estado,
        "periodo": Periodo(ENCERRADO if cancelado else estado, inicio, fim, cancelado=cancelado),
        "desfecho": desfecho,
        "vigente_desde": dias(vigente),
    }


def numeros(selecoes):
    return [item["numero"] for item in selecoes]


def test_encerradas_vem_da_mais_recente_para_a_mais_antiga():
    """O critério é o fim das inscrições — não a ordem de chegada nem a vigência do conteúdo.

    A `3` é a publicada há mais tempo e a que fechou por último: é a primeira do histórico.
    """
    catalogo = [
        selecao(1, ENCERRADO, fim=dias(-40), vigente=-10),
        selecao(2, ENCERRADO, fim=dias(-5), vigente=-60),
        selecao(3, ENCERRADO, fim=dias(-1), vigente=-300),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == ["3", "2", "1"]


def test_abertas_continuam_pelo_prazo_mais_proximo_e_antes_do_historico():
    """A inversão é só do histórico: no que ainda recebe inscrição, o que fecha antes vem antes."""
    catalogo = [
        selecao(1, ENCERRADO, fim=dias(-1)),
        selecao(2, NAO_DESIGNADO),
        selecao(3, ABERTO, inicio=dias(-3), fim=dias(20)),
        selecao(4, FUTURO, inicio=dias(5), fim=dias(15)),
        selecao(5, ABERTO, inicio=dias(-3), fim=dias(2)),
        selecao(6, ENCERRADO, fim=dias(-30)),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == ["5", "3", "4", "1", "6", "2"]


def test_o_empate_tem_ordem_e_ela_nao_depende_da_chegada():
    """Um Processo publica vários Editais com o mesmo prazo: é o caso comum. Sem desempate total,
    a mesma seleção poderia sair em duas páginas e outra em nenhuma."""
    juntas = [selecao(numero, ENCERRADO, fim=dias(-7)) for numero in (11, 12, 13, 14)]

    ida = numeros(leitura.ordenar_por_urgencia(juntas, AGORA))
    volta = numeros(leitura.ordenar_por_urgencia(list(reversed(juntas)), AGORA))

    assert ida == volta == ["14", "13", "12", "11"]


def test_o_edital_encerrado_antes_do_prazo_conta_do_desfecho():
    """O que o tirou das abertas foi o ato, e não o fim do período — que nem chegou."""
    desfecho = SimpleNamespace(do_edital=True, em=dias(-2), operacao="CANCELADO")
    interrompido = selecao(1, ENCERRADO, inicio=dias(-20), fim=dias(10), desfecho=desfecho)
    interrompido["periodo"] = Periodo(ABERTO, dias(-20), dias(10))

    assert leitura.encerrou_em(interrompido, AGORA) == dias(-2)


def test_o_desfecho_depois_do_prazo_nao_rejuvenesce_o_historico():
    """Encerrar hoje um Edital cujas inscrições fecharam há um ano não o traz para a frente."""
    desfecho = SimpleNamespace(do_edital=True, em=dias(-1), operacao="ENCERRADO")
    antigo = selecao(1, ENCERRADO, fim=dias(-365), desfecho=desfecho)

    assert leitura.encerrou_em(antigo, AGORA) == dias(-365)


def test_o_desfecho_do_processo_nao_e_o_fim_das_inscricoes():
    desfecho = SimpleNamespace(do_edital=False, em=dias(-1), operacao="ENCERRADO")
    do_processo = selecao(1, ENCERRADO, fim=dias(-50), desfecho=desfecho)

    assert leitura.encerrou_em(do_processo, AGORA) == dias(-50)


def test_o_periodo_cancelado_conta_da_vigencia_do_conteudo_que_o_declara():
    """Ele não "encerrou em" data nenhuma, e as datas do período podem estar no futuro."""
    cancelado = selecao(1, ENCERRADO, inicio=dias(-3), fim=dias(30), cancelado=True, vigente=-4)

    assert leitura.encerrou_em(cancelado, AGORA) == dias(-4)


@pytest.mark.parametrize(
    "valor",
    ["", None, "abc", "0", "-3", "1.5", " ", "٣", "9" * 40, "2 OR 1=1"],
)
def test_pagina_irreconhecivel_e_a_primeira_e_nunca_erro(valor):
    assert leitura.pagina_pedida(valor) == 1


def test_pagina_reconhecida():
    assert leitura.pagina_pedida(" 3 ") == 3


def consulta(**parametros):
    return leitura.consulta_da_vitrine(parametros, OPCOES)


def test_a_pagina_reparte_sem_perder_nem_repetir():
    itens = list(range(1, 24))
    vistos = []
    for numero in (1, 2, 3):
        pagina = leitura.paginar(itens, consulta(pagina=str(numero)), "encerradas")
        vistos.extend(pagina.itens)
        assert pagina.total == 23 and pagina.total_de_paginas == 3

    assert vistos == itens


def test_o_intervalo_dito_e_o_mostrado():
    pagina = leitura.paginar(list(range(23)), consulta(pagina="3"), "encerradas")

    assert (pagina.primeiro, pagina.ultimo, len(pagina.itens)) == (21, 23, 3)
    assert pagina.intervalo == "21–23"


def test_a_pagina_de_um_cartao_diz_um_numero_so():
    pagina = leitura.paginar(list(range(21)), consulta(pagina="3"), "encerradas")

    assert pagina.intervalo == "21"


def test_a_pagina_que_passa_da_ultima_mostra_a_ultima():
    """O endereço guardado continua mostrando seleções depois que o catálogo encolheu."""
    pagina = leitura.paginar(list(range(23)), consulta(pagina="99"), "encerradas")

    assert pagina.numero == 3 and pagina.itens == [20, 21, 22]
    assert pagina.seguinte == ""


def test_uma_pagina_so_nao_tem_navegacao():
    pagina = leitura.paginar(list(range(leitura.POR_PAGINA)), consulta(), "encerradas")

    assert not pagina.varias
    assert pagina.anterior == "" and pagina.seguinte == ""


def test_lista_vazia_tem_uma_pagina_e_nenhum_intervalo():
    pagina = leitura.paginar([], consulta(busca="nada"), "resultado")

    assert (pagina.numero, pagina.primeiro, pagina.ultimo, pagina.varias) == (1, 0, 0, False)


def test_trocar_de_pagina_leva_a_consulta_e_a_ancora():
    pedido = consulta(busca="técnico", perfil="Enfermeiro", ordem="recentes", pagina="2")
    pagina = leitura.paginar(list(range(35)), pedido, "resultado")

    assert (
        pagina.seguinte == "?busca=t%C3%A9cnico&perfil=Enfermeiro&ordem=recentes&pagina=3#resultado"
    )
    # A primeira página não se escreve: o endereço dela é o da consulta, sem mais nada.
    assert pagina.anterior == "?busca=t%C3%A9cnico&perfil=Enfermeiro&ordem=recentes#resultado"


def test_sem_consulta_a_volta_a_primeira_e_so_a_ancora():
    pagina = leitura.paginar(list(range(35)), consulta(pagina="2"), "encerradas")

    assert pagina.anterior == "#encerradas"
    assert pagina.seguinte == "?pagina=3#encerradas"


def test_a_pagina_nao_e_filtro():
    """Folhear o histórico não desfaz os grupos nem abre os filtros recolhidos."""
    pedido = consulta(pagina="2")

    assert not pedido["ativa"] and not pedido["recolhidos_aplicados"]
    assert pedido["querystring"] == "pagina=2"
    assert consulta()["querystring"] == ""


def test_a_volta_da_selecao_leva_a_pagina_e_so_como_inteiro():
    volta = leitura.caminho_de_volta({"situacao": "encerrado", "pagina": "3"}, "/selecoes/")
    suja = leitura.caminho_de_volta({"pagina": "3&next=//fora"}, "/selecoes/")

    assert volta == "/selecoes/?situacao=encerrado&pagina=3"
    assert suja == "/selecoes/"
