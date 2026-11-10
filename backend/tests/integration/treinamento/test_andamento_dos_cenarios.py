"""O andamento diz o que cada providência é, nos cenários de treinamento da `134` (135).

O estudo do Centro de Controle (09/11) leu estes cenários pela derivação da `127`, e é neles que os
quatro defeitos apareceram: no C08 o protótipo destacou "Emitir a ordem — PPP" numa lista sem
inscritos; no C08 e no C12 a espera do definitivo oferecia publicar como preliminar o que já estava
publicado; no C06 o cartão e o resumo do Perfil contavam coisas diferentes com as mesmas palavras.
Cada caso monta o cenário pelo comando de carga, como a equipe faria, e lê o andamento de quem a
ficha nomeia. As mesmas regras, sem banco, estão em
`tests/unit/interface/test_andamento_o_que_cada_providencia_e.py`.
"""

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import providencias as pr
from processo_seletivo.treinamento import construcao as c
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

PPP = "PPP"
OFERTA = "publique como resultado preliminar"


@pytest.fixture
def seletor_ligado(settings):
    settings.INTERFACE_SELETOR_IDENTIDADE = True


@pytest.fixture
def cenario(treinamento):
    def montar(codigo):
        saida = carregar(codigo, autoridade=str(AUTORIDADE_DA_SUITE))
        assert f"{codigo}  CRIADO" in saida, saida
        return retomar(
            CenarioDeTreinamento.objects.get(codigo=codigo), autoridade=str(AUTORIDADE_DA_SUITE)
        )

    return montar


def _nivel(m, quem):
    andamento = a.do_edital(m.edital, m.ator(quem))
    assert andamento is not None
    return andamento, andamento.nivel_1


def _ordens(nivel):
    return [i for i in nivel.itens if i.natureza == a.ORDEM]


def _ordem_da_ppp(andamento):
    [perfil] = andamento.perfis
    ponto = next(p for p in perfil.pontos if p.tipo == a.ORDEM)
    lista = next(lista for lista, rotulo in perfil.listas if PPP in rotulo)
    return ponto.marco, lista, ponto.celula(lista)


def _celulas_do_resultado(andamento):
    [perfil] = andamento.perfis
    ponto = next(p for p in perfil.pontos if p.tipo == a.RESULTADO)
    return {rotulo: ponto.celula(lista) for lista, rotulo in perfil.listas}


# --- US1: a lista em que ninguém concorre (SC-1460, SC-1461) -----------------------------------


@pytest.mark.parametrize("codigo", ["C08", "C12", "C14"])
def test_a_ordem_da_ppp_em_que_ninguem_concorre_diz_isso_para_qualquer_papel(cenario, codigo):
    """SC-1460: zero providências de ordem da PPP sem a menção, para quem conduz e para quem só a
    lê como de outro papel; a célula continua *Pendente*, com a nota (FR-4671 a FR-4673)."""
    m = cenario(codigo)
    for quem, grupo in ((c.PRESIDENCIA, pr.SUA), (c.PUBLICACAO, pr.DE_OUTRO)):
        andamento, nivel = _nivel(m, quem)
        [ordem] = _ordens(nivel)
        assert ordem.listas == (PPP,), quem
        assert ordem.lista_vazia and ordem.grupo == grupo, quem
        assert ordem.ato == a.ATO_DA_ORDEM_VAZIA, quem
        _, _, celula = _ordem_da_ppp(andamento)
        assert celula.situacao == a.PENDENTE and celula.nota == a.NOTA_DA_LISTA_VAZIA, quem
    # A ordem da ampla, já emitida, não é providência e não ganha nota nenhuma.


def test_c04_a_ppp_com_inscritos_nao_menciona_lista_vazia(cenario):
    """SC-1461, US1 cenário 4: a mesma providência de antes, as duas listas numa linha só."""
    m = cenario("C04")
    for quem in (c.PRESIDENCIA, c.PUBLICACAO):
        andamento, nivel = _nivel(m, quem)
        [ordem] = _ordens(nivel)
        assert ordem.ato == "Emitir a ordem" and not ordem.lista_vazia
        assert ordem.listas == ("Ampla concorrência", PPP)
        _, _, celula = _ordem_da_ppp(andamento)
        assert (celula.situacao, celula.nota, celula.lista_vazia) == (a.PENDENTE, "", False)
        assert not any("ninguém concorreu" in item.ato for item in nivel.itens)


def test_c08_o_proximo_nesta_lista_diz_a_mesma_frase(cenario):
    """FR-4675: a transição lê a mesma célula, e mostra a mesma frase da providência."""
    m = cenario("C08")
    andamento, nivel = _nivel(m, c.PRESIDENCIA)
    marco, lista, _ = _ordem_da_ppp(andamento)
    desta, _, perfil = a.da_lista(andamento, marco["id"], lista, preferir=andamento.e_sua)
    [ordem] = _ordens(nivel)
    assert desta.ato == ordem.ato and desta.lista_vazia
    assert andamento.e_sua(desta, perfil)


def test_c08_a_pagina_do_edital_diz_que_ninguem_concorre_no_nivel_1_e_na_matriz(
    cenario, client, seletor_ligado
):
    """O que a presidência lê no detalhe do Edital: o cartão e a matriz."""
    m = cenario("C08")
    identificar(client, c.PRESIDENCIA, [])
    pagina = client.get(reverse("interface:detalhe", args=[m.edital.id])).content.decode()
    assert "Emitir a ordem que declara que ninguém concorreu nesta lista" in pagina
    assert '<span class="nota-da-celula">lista em que ninguém concorre</span>' in pagina
    assert "sem inscritos" not in pagina


# --- US2: o que foi divulgado é dado (FR-4677) -------------------------------------------------


def test_a_celula_do_resultado_diz_o_que_o_publico_le_em_cada_cenario(cenario):
    esperado = {
        "C04": (a.NADA, a.NADA),
        "C08": (a.PRELIMINAR, a.NADA),
        "C12": (a.PRELIMINAR, a.NADA),
        "C14": (a.DEFINITIVO, a.NADA),
    }
    for codigo, (ampla, ppp) in esperado.items():
        andamento, _ = _nivel(cenario(codigo), c.PRESIDENCIA)
        celulas = _celulas_do_resultado(andamento)
        lido = tuple(
            next(cel.divulgado for rotulo, cel in celulas.items() if chave in rotulo)
            for chave in ("Ampla", PPP)
        )
        assert lido == (ampla, ppp), codigo


def test_o_preliminar_publicado_continua_sem_ser_feito(cenario):
    """D-002, FR-4678: o preliminar segue a pendência do definitivo; o definitivo é *Feito*."""
    andamento, _ = _nivel(cenario("C08"), c.PRESIDENCIA)
    ampla = next(cel for rot, cel in _celulas_do_resultado(andamento).items() if "Ampla" in rot)
    assert ampla.situacao == a.AGUARDA and ampla.nota == "resultado preliminar"


# --- US3: a razão da espera do definitivo (SC-1462) -------------------------------------------


@pytest.mark.parametrize("codigo", ["C08", "C12"])
def test_a_espera_do_definitivo_nao_oferece_publicar_como_preliminar(cenario, codigo):
    m = cenario(codigo)
    for quem in (c.PRESIDENCIA, c.PUBLICACAO):
        andamento, nivel = _nivel(m, quem)
        [espera] = [i for i in nivel.itens if i.natureza == a.RESULTADO and i.grupo == pr.EM_ESPERA]
        assert espera.ato == "Publicar o resultado definitivo"
        assert OFERTA not in espera.razao
        assert "prazo recursal" in espera.razao and "14/11/2026" in espera.razao
        assert espera.ate is not None
        for celula in _celulas_do_resultado(andamento).values():
            assert OFERTA not in celula.razao


def test_c08_na_previa_de_publicacao_a_mensagem_e_a_de_antes(cenario):
    """SC-1462, FR-4682: a aferição que a prévia e o comando leem continua oferecendo a escolha."""
    from processo_seletivo.classificacao.application.selectors import ato_vigente
    from processo_seletivo.divulgacao.domain import publicabilidade as p

    m = cenario("C08")
    andamento, _ = _nivel(m, c.PRESIDENCIA)
    marco, _, _ = _ordem_da_ppp(andamento)
    ato = ato_vigente(edital=m.edital, marco_id=str(marco["id"]), lista_id=None)
    afericao = p.aferir(
        edital=m.edital, marco_id=str(marco["id"]), ato=ato, natureza="DEFINITIVA", lista_id=None
    )
    assert afericao.codigo == p.JANELA_ABERTA
    assert afericao.mensagem == p.MENSAGENS[p.JANELA_ABERTA].format(fecha=p._quando(afericao.ate))
    assert afericao.mensagem.endswith("ou publique como resultado preliminar.")


def test_c08_a_previa_de_publicacao_mostra_a_mensagem_de_antes(cenario, client, seletor_ligado):
    """A tela de publicação, como o Publicador a abre."""
    from processo_seletivo.classificacao.application.selectors import ato_vigente

    m = cenario("C08")
    andamento, _ = _nivel(m, c.PRESIDENCIA)
    marco, _, _ = _ordem_da_ppp(andamento)
    ato = ato_vigente(edital=m.edital, marco_id=str(marco["id"]), lista_id=None)
    identificar(client, c.PUBLICACAO, ["publicador"])
    resposta = client.get(
        reverse("interface:previa-de-publicacao", args=[m.edital.id, marco["id"], ato.id])
    )
    assert resposta.status_code == 200
    assert OFERTA in resposta.content.decode()


# --- US4: a contagem do Perfil (SC-1464) ------------------------------------------------------


def test_c06_o_resumo_do_perfil_diz_o_escopo_e_os_numeros_sao_os_de_antes(cenario):
    m = cenario("C06")
    andamento, nivel = _nivel(m, c.PRESIDENCIA)
    assert pr.contagem(nivel) == "2 providências em aberto · 2 são suas"
    [perfil] = andamento.perfis
    resumo = a.resumo_do_perfil(perfil)
    assert resumo.endswith("· 1 providência em aberto nos marcos")
