"""A jornada de quem preside sem papel sistêmico — o ator central da 011.

Estes testes nasceram de um percurso manual: a presidente conseguia fazer tudo, e o sistema lhe
dizia que ela não podia nada. As telas herdadas decidiam por `ator.permissions`, e a base
contextual que a 011 criou não existia para elas.
"""

import pytest
from django.urls import reverse

from tests.fixtures.comissao import alocar_em
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


@pytest.fixture
def presidente(client, seletor_ligado, comissao_de_a):
    identificar(client, "maria", [])
    return client


def test_a_lista_nao_diz_que_a_presidente_nao_tem_papel(presidente, processo_a):
    """L1: "Sua conta não possui nenhum papel de responsabilidade" era falso para ela."""
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" not in corpo
    assert "Você preside a comissão" in corpo


def test_a_lista_oferece_a_comissao_a_quem_a_integra(presidente, processo_a):
    corpo = presidente.get(reverse("interface:lista")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo


def test_quem_nao_tem_vinculo_continua_recebendo_a_orientacao(client, seletor_ligado, processo_a):
    """A garantia da 002 permanece para quem de fato não tem nada."""
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:lista")).content.decode()

    assert "Sem permissões" in corpo


def test_a_presidente_sem_alocacao_nao_e_mandada_pedir_acesso(presidente):
    """L2: ela já integra a comissão — mandá-la pedir para ser registrada é dizer o oposto."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" not in corpo
    assert "Comissões que você integra" in corpo


def test_minhas_etapas_leva_a_presidente_ate_a_comissao_dela(presidente, processo_a):
    """L3: o acesso existia; a rota não."""
    corpo = presidente.get(reverse("interface:minhas-etapas")).content.decode()

    assert reverse("interface:comissao", args=[processo_a.id]) in corpo
    assert reverse("interface:alocacoes", args=[processo_a.id]) in corpo


def test_quem_nao_tem_nada_continua_recebendo_a_orientacao_em_minhas_etapas(
    client, seletor_ligado
):
    identificar(client, "servidor.novo", [])

    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()

    assert "não possui papel de responsabilidade nem atribuição" in corpo


def test_o_seletor_nao_oferece_quem_ja_esta_alocado(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L4: oferecer quem já está era a tela produzindo o próprio 409."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    seletor = corpo.split(f'id="membro-{etapa_a1}"')[1].split("</select>")[0]
    assert str(comissao_de_a["joao"].id) not in seletor
    assert str(comissao_de_a["maria"].id) in seletor


def test_etapa_com_a_comissao_toda_alocada_diz_isso(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    for membro in comissao_de_a.values():
        alocar_em(gestor, processo_a, membro, edital_a, etapa_a1)

    corpo = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()

    assert "Toda a comissão já está alocada nesta Etapa" in corpo


def test_as_remocoes_dizem_de_quem_e_de_onde(
    presidente, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L5: quatro botões com o mesmo nome acessível são indistinguíveis por leitor de tela."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)

    alocacoes = presidente.get(
        reverse("interface:alocacoes", args=[processo_a.id])
    ).content.decode()
    comissao = presidente.get(
        reverse("interface:comissao", args=[processo_a.id])
    ).content.decode()

    assert 'aria-label="Remover joao da Etapa Análise documental"' in alocacoes
    assert 'aria-label="Remover joao da comissão"' in comissao


def test_a_confirmacao_de_atribuicao_nao_usa_estilo_de_alerta(
    client, seletor_ligado, gestor, processo_a, edital_a, comissao_de_a, etapa_a1
):
    """L8: a frase que confirma a atribuição parecia um problema a resolver."""
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    identificar(client, "joao", [])

    corpo = client.get(
        reverse("interface:atribuicao", args=[edital_a.id, etapa_a1])
    ).content.decode()

    trecho = corpo.split("Você está alocado nesta Etapa")[0][-120:]
    assert 'class="sucesso"' in trecho
