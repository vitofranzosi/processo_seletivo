"""O caminho até o trabalho, seguido **só por links** — que é como uma pessoa chega.

Este arquivo existe por causa de uma lacuna que atravessou a implementação inteira sem aparecer:
nenhuma tela do sistema tinha link para a distribuição de uma Etapa. A 012 estava pronta, testada
e inalcançável — e não apareceu porque toda verificação chegava lá por `reverse()`, que não é um
caminho, e todo roteiro chegava montando a URL.

A regra que estes testes impõem é simples: **partindo de onde a pessoa cai ao entrar, e clicando
apenas no que a tela oferece, chega-se ao trabalho.**
"""

import re

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


def links(cliente, url):
    """Os endereços que a tela oferece — e nada mais."""
    corpo = cliente.get(url).content.decode()
    return re.findall(r'href="([^"#][^"]*)"', corpo)


@pytest.fixture
def cenario(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    inscrever(edital_a, 2, primeiro=900)
    return {"processo": processo_a, "edital": edital_a, "etapa": etapa_a1}


def test_a_presidencia_chega_a_distribuicao_seguindo_links(client, seletor_ligado, cenario):
    """Da tela em que a presidência cai ao entrar, sem digitar URL nenhuma."""
    identificar(client, "maria", [])

    da_entrada = links(client, reverse("interface:minhas-etapas"))
    alocacoes = next(u for u in da_entrada if u.endswith("/alocacoes"))

    da_alocacao = links(client, alocacoes)
    distribuicao = next(u for u in da_alocacao if "/distribuicao/" in u)

    resposta = client.get(distribuicao)

    assert resposta.status_code == 200
    assert "Inscrições, uma a uma" in resposta.content.decode()


def test_o_gestor_chega_a_distribuicao_seguindo_links(client, seletor_ligado, cenario):
    """E quem entra pelo papel administrativo cai na lista, e chega pelo mesmo elo."""
    identificar(client, "carlos", ["gestor"])

    da_lista = links(client, reverse("interface:lista"))
    alocacoes = next(u for u in da_lista if u.endswith("/alocacoes"))
    distribuicao = next(u for u in links(client, alocacoes) if "/distribuicao/" in u)

    assert client.get(distribuicao).status_code == 200


def test_da_distribuicao_se_alcanca_o_resto_da_012(client, seletor_ligado, cenario):
    """Impedimentos, trilha e conclusões pendem da distribuição — e caíam junto com ela."""
    identificar(client, "maria", [])
    distribuicao = reverse("interface:distribuicao", args=[cenario["edital"].id, cenario["etapa"]])

    oferecidos = links(client, distribuicao)

    for trecho in ("/impedimentos", "/trilha", "/conclusoes"):
        assert any(trecho in u for u in oferecidos), trecho


def test_o_avaliador_chega_a_sua_mesa_seguindo_links(client, seletor_ligado, cenario):
    """A porta de quem executa já existia, e continua existindo."""
    identificar(client, "joao", [])

    da_entrada = links(client, reverse("interface:minhas-etapas"))
    mesa = next(u for u in da_entrada if "/minhas-etapas/" in u)

    resposta = client.get(mesa)

    assert resposta.status_code == 200
    assert "Minha Mesa" in resposta.content.decode()


def test_quem_nao_gere_nao_recebe_o_elo(client, seletor_ligado, cenario):
    """O link não é enfeite: ele leva a uma tela que só a gestão e a presidência alcançam."""
    identificar(client, "joao", [])

    alocacoes = reverse("interface:alocacoes", args=[cenario["processo"].id])

    assert client.get(alocacoes).status_code == 404


def test_quem_pode_gerir_ve_o_caminho_mesmo_sem_integrar_a_comissao(
    client, seletor_ligado, cenario
):
    """A permissão existia e o caminho não: o gestor não membro não recebia link nenhum.

    `comissao:gerir` autoriza constituir a comissão e alocar; a lista só oferecia esses links a
    quem tivesse vínculo. Quem constitui a comissão é justamente quem ainda não a integra.
    """
    identificar(client, "carlos", ["gestor"])

    oferecidos = links(client, reverse("interface:lista"))

    assert any(u.endswith("/comissao") for u in oferecidos)
    assert any(u.endswith("/alocacoes") for u in oferecidos)
