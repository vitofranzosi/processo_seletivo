"""A providência chega ao ato, e o ato volta ao Centro, nos cenários da `134` (139).

**Os cenários são os do estudo de continuidade** (10/11): o C06, em que fixar os participantes
estava a 1.681 px do topo do sorteio, e o C12, em que as chamadas estavam a 2.151 px do topo da
convocação. Aqui se prova que o endereço leva a um id **que a tela de destino tem** — a distância na
dobra se mede no navegador, e está em `specs/139-chegada-ao-ato-e-volta/verificacao.md`. As regras
sem banco estão em `tests/unit/interface/test_chegada_ao_ato.py`.
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.interface import andamento as a
from processo_seletivo.processos.models import Edital
from processo_seletivo.treinamento import construcao as k
from processo_seletivo.treinamento.models import CenarioDeTreinamento
from tests.fixtures.autoridades import AUTORIDADE_DA_SUITE
from tests.fixtures.treinamento import carregar, retomar
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.integration, pytest.mark.django_db]

RETORNO = '<p class="retorno-ao-centro">'


@pytest.fixture
def cenario(treinamento):
    treinamento.INTERFACE_SELETOR_IDENTIDADE = True

    def montar(codigo):
        saida = carregar(codigo, autoridade=str(AUTORIDADE_DA_SUITE))
        assert f"{codigo}  CRIADO" in saida, saida
        manifesto = CenarioDeTreinamento.objects.get(codigo=codigo)
        return Edital.objects.get(processo=manifesto.processo)

    return montar


def _centro(client, edital):
    resposta = client.get(reverse("interface:detalhe", args=[edital.id]))
    assert resposta.status_code == 200
    return resposta


def _chega_ao_alvo(client, url):
    """O endereço tem fragmento, e a tela de destino tem o id: o navegador rola até ele."""
    caminho, _, ancora = url.partition("#")
    assert ancora, url
    corpo = client.get(caminho).content.decode()
    assert f'id="{ancora}"' in corpo, (url, ancora)
    return corpo


def _sem_fragmento(itens):
    return [(i.ato, i.situacao, i.responsavel, i.grupo, i.url.split("#")[0]) for i in itens]


# ---------------------------------------------------------------------------------------------
# C06 — sorteio antes do congelamento
# ---------------------------------------------------------------------------------------------


def test_c06(client, cenario):
    """Um cenário por caso: a carga custa perto de um minuto, e dois no mesmo banco colidem."""
    edital = cenario("C06")
    identificar(client, k.PRESIDENCIA, [])
    marco_id, ppp = c06_fixar_os_participantes_chega_aos_recortes(client, edital)
    c06_depois_de_congelar_a_ampla_a_ppp_e_link_e_o_bloco_volta_ao_centro(
        client, edital, marco_id, ppp
    )


def c06_fixar_os_participantes_chega_aos_recortes(client, edital):
    """SC-1490, FR-4760, FR-4762, FR-4766: as duas listas juntadas chegam aos recortes, e cada
    recorte tem o seu id."""
    centro = _centro(client, edital).context["centro"]
    url = centro.destaque.item.p.url
    assert url.endswith("#titulo-recortes"), url
    corpo = _chega_ao_alvo(client, url)
    assert 'id="recorte-ampla"' in corpo
    assert len(re.findall(r'<article class="recorte" id="recorte-[^"]+">', corpo)) == 2

    # Cada lista, na célula dela, leva ao seu recorte — e é a juntada que leva à seção.
    m = retomar(CenarioDeTreinamento.objects.get(codigo="C06"), autoridade=str(AUTORIDADE_DA_SUITE))
    [perfil] = a.do_edital(edital, m.ator(k.PRESIDENCIA)).perfis
    relacao = next(p for p in perfil.pontos if p.tipo == a.RELACAO)
    for lista, _ in perfil.listas:
        url = relacao.celula(lista).url
        assert url.endswith(f"#{a.ancora_do_recorte(lista)}"), url
        assert f'id="{a.ancora_do_recorte(lista)}"' in corpo
    ppp = next(lista for lista, rotulo in perfil.listas if "PPP" in rotulo)
    return relacao.marco["id"], ppp


def c06_depois_de_congelar_a_ampla_a_ppp_e_link_e_o_bloco_volta_ao_centro(
    client, edital, marco_id, ppp
):
    """FR-4768, FR-4769, SC-1492: o "Ainda neste marco" leva ao recorte da PPP, e o bloco termina
    no Centro."""
    resposta = client.post(
        reverse("interface:publicar-relacao-do-sorteio", args=[edital.id, marco_id]),
        {"chave_idempotencia": "c06-139-ampla", "lista_id": ""},
        follow=True,
    )
    corpo = resposta.content.decode()
    assert "Relação publicada e congelada" in corpo, corpo[:2000]

    ainda = corpo.split('<p class="ainda-neste-marco">', 1)[1].split("</p>", 1)[0]
    link = re.search(r'<a href="([^"]+)">[^<]*\(PPP\) — congelar a relação</a>', ainda)
    assert link, ainda
    assert link.group(1).endswith(f"#{a.ancora_do_recorte(ppp)}"), link.group(1)
    assert f'id="{link.group(1).partition("#")[2]}"' in corpo

    centro = reverse("interface:detalhe", args=[edital.id])
    assert f'{RETORNO}<a href="{centro}">Voltar ao Centro de Controle do Edital</a></p>' in corpo


# ---------------------------------------------------------------------------------------------
# C12 — conferência documental
# ---------------------------------------------------------------------------------------------


def test_c12(client, cenario):
    edital = cenario("C12")
    identificar(client, k.PRESIDENCIA, [])
    centro = _centro(client, edital).context["centro"]
    itens = [*centro.suas]
    conferir = [i for i in itens if i.p.ato.startswith("Conferir os documentos")]
    assert conferir, [i.p.ato for i in itens]
    corpo = _chega_ao_alvo(client, conferir[0].p.url)
    assert conferir[0].p.url.endswith("#chamadas")
    assert "Chamadas praticadas" in corpo
