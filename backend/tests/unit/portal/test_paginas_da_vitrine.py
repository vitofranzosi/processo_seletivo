"""A ordem e as páginas da vitrine, sem banco.

**Por que existe.** A vitrine mostrava todas as seleções de uma vez, as encerradas da mais antiga
para a mais nova, e chamava de "encerrada" a que só tinha fechado as inscrições. Estes casos prendem
as três regras que saíram disso: o Edital sem desfecho próprio está em andamento, e não encerrado;
a encerrada mais recente vem primeiro, com desempate total; e o recorte em páginas leva a consulta
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


def encerrado(em):
    return SimpleNamespace(do_edital=True, em=dias(em), operacao="ENCERRADO")


def test_encerradas_vem_da_mais_recente_para_a_mais_antiga():
    """O critério é o ato que encerrou o Edital — não a ordem de chegada, nem o fim das inscrições,
    nem a vigência do conteúdo.

    A `3` é a publicada há mais tempo e a que foi encerrada por último: é a primeira do histórico.
    """
    catalogo = [
        selecao(1, ENCERRADO, fim=dias(-50), desfecho=encerrado(-40), vigente=-10),
        selecao(2, ENCERRADO, fim=dias(-90), desfecho=encerrado(-5), vigente=-60),
        selecao(3, ENCERRADO, fim=dias(-200), desfecho=encerrado(-1), vigente=-300),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == ["3", "2", "1"]


def test_cada_situacao_no_seu_lugar_e_com_a_sua_ordem():
    """Abertas e próximas pelo prazo mais próximo; depois o que está em andamento; o histórico
    por último entre os que tiveram inscrição."""
    catalogo = [
        selecao(1, ENCERRADO, fim=dias(-60), desfecho=encerrado(-1)),
        selecao(2, NAO_DESIGNADO),
        selecao(3, ABERTO, inicio=dias(-3), fim=dias(20)),
        selecao(4, FUTURO, inicio=dias(5), fim=dias(15)),
        selecao(5, ABERTO, inicio=dias(-3), fim=dias(2)),
        selecao(6, ENCERRADO, fim=dias(-90), desfecho=encerrado(-30)),
        selecao(7, leitura.EM_ANDAMENTO, fim=dias(-4)),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == [
        "5",
        "3",
        "4",
        "7",
        "1",
        "6",
        "2",
    ]


def test_o_empate_tem_ordem_e_ela_nao_depende_da_chegada():
    """Um Processo encerra vários Editais de uma vez: é o caso comum. Sem desempate total, a
    mesma seleção poderia sair em duas páginas e outra em nenhuma."""
    juntas = [
        selecao(numero, ENCERRADO, fim=dias(-30), desfecho=encerrado(-7))
        for numero in (11, 12, 13, 14)
    ]

    ida = numeros(leitura.ordenar_por_urgencia(juntas, AGORA))
    volta = numeros(leitura.ordenar_por_urgencia(list(reversed(juntas)), AGORA))

    assert ida == volta == ["14", "13", "12", "11"]


def test_sem_a_data_do_ato_o_historico_conta_do_fim_das_inscricoes():
    sem_data = SimpleNamespace(do_edital=True, em=None, operacao="ENCERRADO")

    assert leitura.encerrou_em(selecao(1, ENCERRADO, fim=dias(-50), desfecho=sem_data), AGORA) == (
        dias(-50)
    )


# ---------------------------------------------------------------------------
# Em andamento: fechou as inscrições e o Edital não acabou
# ---------------------------------------------------------------------------


def test_o_periodo_que_terminou_sem_desfecho_do_edital_esta_em_andamento():
    """O furo que este grupo fecha: "Inscrições encerradas" reunia o que segue e o que acabou."""
    terminou = Periodo(ENCERRADO, dias(-30), dias(-5))

    assert leitura.estado_na_vitrine(terminou, None) == leitura.EM_ANDAMENTO
    assert leitura.marca_da_selecao(terminou, None) == ("andamento", "Em andamento")
    # A ficha de divulgação descreve o período, e continua dizendo o dele.
    assert leitura.situacao_publica(terminou, None) == (ENCERRADO, "Encerrada")


def test_o_desfecho_do_edital_e_o_que_encerra():
    terminou = Periodo(ENCERRADO, dias(-30), dias(-5))
    aberto = Periodo(ABERTO, dias(-3), dias(9))

    for periodo in (terminou, aberto):
        assert leitura.estado_na_vitrine(periodo, encerrado(-1)) == ENCERRADO
        assert leitura.marca_da_selecao(periodo, encerrado(-1)) == (
            "encerrado_edital",
            "Edital encerrado",
        )


def test_o_edital_de_processo_encerrado_nao_esta_em_andamento():
    """Enquanto o período corre ele continua recebendo, e fica nas abertas; fechadas as
    inscrições, não há mais o que correr — "Em andamento" sobre "Processo seletivo encerrado em…"
    seriam duas coisas ditas da mesma seleção."""
    do_processo = SimpleNamespace(do_edital=False, em=dias(-1), operacao="ENCERRADO")
    terminou = Periodo(ENCERRADO, dias(-30), dias(-5))

    assert leitura.estado_na_vitrine(Periodo(ABERTO, dias(-3), dias(9)), do_processo) == ABERTO
    assert leitura.estado_na_vitrine(terminou, do_processo) == ENCERRADO
    assert leitura.marca_da_selecao(terminou, do_processo) == (ENCERRADO, "Encerrada")


def test_sob_o_desfecho_do_processo_o_edital_acabou_no_que_veio_por_ultimo():
    antes = SimpleNamespace(do_edital=False, em=dias(-40), operacao="ENCERRADO")
    depois = SimpleNamespace(do_edital=False, em=dias(-2), operacao="ENCERRADO")

    assert leitura.encerrou_em(selecao(1, ENCERRADO, fim=dias(-5), desfecho=antes), AGORA) == (
        dias(-5)
    )
    assert leitura.encerrou_em(selecao(2, ENCERRADO, fim=dias(-5), desfecho=depois), AGORA) == (
        dias(-2)
    )


def test_o_periodo_cancelado_segue_em_andamento_com_a_marca_propria():
    cancelado = Periodo(ENCERRADO, dias(-3), dias(30), cancelado=True)

    assert leitura.estado_na_vitrine(cancelado, None) == leitura.EM_ANDAMENTO
    assert leitura.marca_da_selecao(cancelado, None) == (ENCERRADO, "Período cancelado")


def em_andamento(numero, *, fim, **resumo):
    item = selecao(numero, leitura.EM_ANDAMENTO, fim=dias(fim))
    item["periodo"] = Periodo(ENCERRADO, None, dias(fim))
    item["acompanhamento"] = resumo or None
    return item


def test_em_andamento_o_recurso_aberto_vem_antes_e_o_prazo_mais_curto_primeiro():
    """É o único item do grupo que se pode perder."""
    catalogo = [
        em_andamento(1, fim=-2),
        em_andamento(2, fim=-40, mais_recente=dias(-1), prazo_unico=dias(6)),
        em_andamento(3, fim=-40, mais_recente=dias(-3), primeiro_prazo=dias(2)),
        em_andamento(4, fim=-40, mais_recente=dias(-1)),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == ["3", "2", "4", "1"]


def test_em_andamento_o_periodo_cancelado_nao_conta_do_fim_que_nao_valeu():
    """O fim declarado há meses não aconteceu: o que há é o conteúdo que declarou o cancelamento."""
    cancelado = selecao(1, leitura.EM_ANDAMENTO, fim=dias(-180), cancelado=True, vigente=-1)
    parado = em_andamento(2, fim=-30)

    assert numeros(leitura.ordenar_por_urgencia([parado, cancelado], AGORA)) == ["1", "2"]


def test_em_andamento_sem_publicacao_conta_do_fim_das_inscricoes():
    """O Edital recém-fechado não some atrás dos que publicaram há meses."""
    catalogo = [
        em_andamento(1, fim=-90, mais_recente=dias(-60)),
        em_andamento(2, fim=-2),
    ]

    assert numeros(leitura.ordenar_por_urgencia(catalogo, AGORA)) == ["2", "1"]


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
        pagina = leitura.paginar(itens, consulta(pagina=str(numero)), "fora-do-prazo")
        vistos.extend(pagina.itens)
        assert pagina.total == 23 and pagina.total_de_paginas == 3

    assert vistos == itens


def test_o_intervalo_dito_e_o_mostrado():
    pagina = leitura.paginar(list(range(23)), consulta(pagina="3"), "fora-do-prazo")

    assert (pagina.primeiro, pagina.ultimo, len(pagina.itens)) == (21, 23, 3)
    assert pagina.intervalo == "21–23"


def test_a_pagina_de_um_cartao_diz_um_numero_so():
    pagina = leitura.paginar(list(range(21)), consulta(pagina="3"), "fora-do-prazo")

    assert pagina.intervalo == "21"


def test_a_pagina_que_passa_da_ultima_mostra_a_ultima():
    """O endereço guardado continua mostrando seleções depois que o catálogo encolheu."""
    pagina = leitura.paginar(list(range(23)), consulta(pagina="99"), "fora-do-prazo")

    assert pagina.numero == 3 and pagina.itens == [20, 21, 22]
    assert pagina.seguinte == ""


def test_uma_pagina_so_nao_tem_navegacao():
    pagina = leitura.paginar(list(range(leitura.POR_PAGINA)), consulta(), "fora-do-prazo")

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
    pagina = leitura.paginar(list(range(35)), consulta(pagina="2"), "fora-do-prazo")

    assert pagina.anterior == "#fora-do-prazo"
    assert pagina.seguinte == "?pagina=3#fora-do-prazo"


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
