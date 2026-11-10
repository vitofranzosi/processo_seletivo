"""A providência leva ao lugar do ato na tela de destino (139, FR-4760 a FR-4767).

O estudo de continuidade operacional (10/11) mediu a passagem do Centro às telas dos atos: a
providência abria a tela no topo, e o ato estava a 1.681 px no sorteio e a 2.151 px na
convocação. O endereço ganha um fragmento, e nada mais: a situação, o ato e o responsável são os
de antes. Aqui, as regras sem banco; nos cenários da `134`, em
`tests/integration/treinamento/test_chegada_e_volta_nos_cenarios.py`.
"""

import pytest

from processo_seletivo.interface import andamento as a
from processo_seletivo.interface import providencias as p
from processo_seletivo.interface.templatetags.interface_extras import ancora_do_recorte
from tests.unit.interface.test_providencias import prov

LISTA = "6f1c1b7e-0000-4000-8000-000000000001"


# --- as âncoras -------------------------------------------------------------------------------


def test_o_recorte_da_ampla_tem_ancora_propria_e_o_da_lista_leva_o_id():
    """FR-4762: a ampla não tem identificador de lista; a lista é um UUID, e não colide com ela."""
    assert a.ancora_do_recorte(None) == a.ancora_do_recorte("") == "recorte-ampla"
    assert a.ancora_do_recorte(LISTA) == f"recorte-{LISTA}"


def test_a_tela_le_a_mesma_ancora_que_a_derivacao():
    """FR-4762: o filtro da tela do sorteio é a mesma função, e não uma segunda redação."""
    for lista in (None, "", LISTA):
        assert ancora_do_recorte(lista) == a.ancora_do_recorte(lista)


def test_sem_endereco_o_fragmento_nao_cria_link():
    assert a.com_ancora("", "chamadas") == ""
    assert a.com_ancora("/c", "") == "/c"
    assert a.com_ancora("/c?lista=1", "chamadas") == "/c?lista=1#chamadas"


@pytest.mark.parametrize(
    ("uma", "outra", "comum"),
    [
        ("chamadas", "chamadas", "chamadas"),
        ("recorte-ampla", f"recorte-{LISTA}", "titulo-recortes"),
        # A terceira lista de um marco com cotas se junta a uma juntada que já leva aos recortes.
        ("titulo-recortes", f"recorte-{LISTA}", "titulo-recortes"),
        ("chamada-1", "chamada-4", "chamadas"),
        ("chamadas", "chamada-2", "chamadas"),
        ("titulares", "pendentes", ""),
        ("recorte-ampla", "titulo-ocorrencia", ""),
        ("", "chamadas", ""),
    ],
)
def test_a_ancora_comum_de_duas_providencias_da_mesma_tela(uma, outra, comum):
    """FR-4766."""
    assert a.ancora_comum(uma, outra) == comum


# --- o caminho comum de duas listas (FR-4766) ------------------------------------------------


def test_duas_listas_do_sorteio_juntadas_chegam_aos_recortes_e_nao_a_conducao():
    """O caminho comum da `127` comparava o endereço inteiro: com o fragmento de cada recorte, as
    duas listas iriam para a condução do marco, e não para a tela delas."""
    itens = [
        prov(
            "Congelar a relação",
            sua=True,
            lista="Ampla",
            url="/sorteio#recorte-ampla",
            url_do_marco="/m",
        ),
        prov(
            "Congelar a relação",
            sua=True,
            lista="PPP",
            url=f"/sorteio?lista={LISTA}#recorte-{LISTA}",
            url_do_marco="/m",
        ),
    ]
    [item] = p.Nivel1(itens).itens
    assert item.url == "/sorteio#titulo-recortes"
    assert item.listas == ("Ampla", "PPP")


def test_telas_diferentes_continuam_indo_a_conducao_do_marco():
    itens = [
        prov("Publicar o resultado", sua=True, lista="Ampla", url="/a#x", url_do_marco="/m"),
        prov("Publicar o resultado", sua=True, lista="PPP", url="/b#x", url_do_marco="/m"),
    ]
    assert p.Nivel1(itens).itens[0].url == "/m"


def test_a_mesma_secao_em_duas_listas_se_mantem():
    itens = [
        prov("Conferir", sua=True, lista="Ampla", url="/c#chamadas"),
        prov("Conferir", sua=True, lista="PPP", url="/c?lista=2#chamadas"),
    ]
    assert p.Nivel1(itens).itens[0].url == "/c#chamadas"


# --- a convocação (FR-4763 a FR-4765, FR-4767) -----------------------------------------------


def convocacao(**fatos):
    base = {"apuracao": a.Celula(a.FEITO), "url": "/convocacao?lista=1"}
    base.update(fatos)
    return a.situacoes_da_convocacao(base)


def _urls(providencias):
    return {c.ato: c.url for c in providencias}


def test_cada_providencia_da_convocacao_leva_a_secao_do_seu_ato():
    _, providencias = convocacao(
        pendentes=1,
        vencidos=1,
        decidir=2,
        primeira_pronta=3,
        conferir=1,
        url_da_conferencia="/convocacao?lista=1",
        titulares=2,
        em_curso=1,
    )
    assert _urls(providencias) == {
        "Emitir 1 comunicação": "/convocacao?lista=1#pendentes",
        "Registrar o não atendimento de 1 convocação vencida": "/convocacao?lista=1#vencidos",
        "Registrar o desfecho de 2 convocações prontas": "/convocacao?lista=1#chamada-3",
        "Conferir os documentos de 1 convocação": "/convocacao?lista=1#chamadas",
        "Convocar 2 titulares": "/convocacao?lista=1#titulares",
        "Resposta de 1 convocação": "/convocacao?lista=1#chamadas",
    }


def test_o_desfecho_sem_a_posicao_da_pronta_leva_as_chamadas():
    _, [desfecho] = convocacao(decidir=1)
    assert desfecho.url == "/convocacao?lista=1#chamadas"


def test_chamar_da_fila_leva_a_fila():
    _, [chamar] = convocacao(faltando=1, fila=2)
    assert chamar.url == "/convocacao?lista=1#fila"


def test_sem_consulta_nenhuma_providencia_ganha_endereco():
    """Quem não tem consulta continua sem link: o fragmento não cria um."""
    _, providencias = convocacao(url="", pendentes=1, decidir=1, primeira_pronta=1, titulares=1)
    assert {c.url for c in providencias} == {""}


def test_o_fragmento_nao_muda_situacao_ato_responsavel_nem_ordem():
    """FR-4767: tirado o fragmento, as providências são as de um endereço sem ele."""
    fatos = {"pendentes": 1, "vencidos": 2, "decidir": 1, "primeira_pronta": 2, "titulares": 1}
    resumo, providencias = convocacao(**fatos)

    def sem_fragmento(c):
        return (c.situacao, c.ato, c.responsavel, c.razao, c.contagem, c.url.split("#")[0])

    assert [sem_fragmento(c) for c in providencias] == [
        (
            a.PENDENTE,
            "Emitir 1 comunicação",
            a.CONDUZ,
            "o prazo não começou a correr",
            1,
            "/convocacao?lista=1",
        ),
        (
            a.PENDENTE,
            "Registrar o não atendimento de 2 convocações vencidas",
            a.CONDUZ,
            "",
            2,
            "/convocacao?lista=1",
        ),
        (
            a.PENDENTE,
            "Registrar o desfecho de 1 convocação pronta",
            a.CONDUZ,
            "os documentos obrigatórios estão conferidos",
            1,
            "/convocacao?lista=1",
        ),
        (a.PENDENTE, "Convocar 1 titular", a.CONDUZ, "", 1, "/convocacao?lista=1"),
    ]
    assert resumo.ato == "Emitir 1 comunicação"


def test_o_impedimento_e_o_feito_ficam_sem_fragmento():
    resumo, _ = convocacao(
        impedimento={"codigo": "forma_de_comunicacao_nao_declarada", "detalhe": "Falta a forma."}
    )
    assert resumo.url == "/convocacao?lista=1"
    feito, providencias = convocacao(convocadas=2, desfechadas=2)
    assert (feito.situacao, feito.url, providencias) == (a.FEITO, "/convocacao?lista=1", [])
