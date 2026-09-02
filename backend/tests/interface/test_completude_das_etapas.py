"""O quanto falta, lido de fora da Etapa — os quatro estados que o cartão precisa distinguir.

A tela dizia "115 pendentes de 255" numa frase corrida, e com isso respondia uma pergunta só. A
outra — qual destas Etapas nem começou — ficava para a aritmética de quem lê, e é justamente a que
se faz olhando a lista inteira.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.selectors import _completude
from tests.fixtures.mesa import concluir_como, distribuir_para, inscricoes_de, montar_banca
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def cenario(gestor, api_client, manager_headers):
    return montar_banca(gestor, api_client, manager_headers, seed=31, codigo="CP")


@pytest.fixture
def cinco(cenario, gestor):
    """Cinco para o joão. A ana fica alocada e sem nenhuma — o quarto estado."""
    inscricoes = inscricoes_de(cenario, 5, primeiro=3100)
    distribuir_para(cenario, gestor, ["joao"], inscricoes, chave="cp")
    return inscricoes


def cartao(client, subject):
    identificar(client, subject, [])
    return client.get(reverse("interface:minhas-etapas")).content.decode()


def test_o_cartao_diz_quanto_falta_e_o_quanto_ja_andou(client, seletor_ligado, cenario, cinco):
    """As duas perguntas na mesma linha: o que se age, e o que se compara."""
    concluir_como(cenario, "joao", cinco[0])
    concluir_como(cenario, "joao", cinco[1])

    corpo = cartao(client, "joao")

    assert "3</strong>" in corpo and "pendentes" in corpo
    assert "40%" in corpo
    assert "2 de 5" in corpo
    assert "width:40%" in corpo


def test_a_etapa_nao_comecada_nao_se_parece_com_a_quase_pronta(
    client, seletor_ligado, cenario, cinco
):
    """Zero por cento é uma notícia, e "5 pendentes de 5" a dava sem dizê-la."""
    corpo = cartao(client, "joao")

    assert "0%" in corpo
    assert "width:0%" in corpo
    assert "Concluída" not in corpo


def test_terminar_e_um_estado_e_nao_a_ausencia_de_pendencias(
    client, seletor_ligado, cenario, cinco
):
    """ "0 pendentes" diria o mesmo pela ausência; quem terminou merece a palavra."""
    for inscricao in cinco:
        concluir_como(cenario, "joao", inscricao)

    corpo = cartao(client, "joao")

    assert "Concluída" in corpo
    assert "100%" in corpo
    assert "medidor completo" in corpo
    # E a palavra ocupa o lugar do número: "0 pendentes" seria a mesma notícia dita ao contrário.
    assert corpo.split('class="restante">')[1].startswith("Concluída")


def test_alocada_sem_distribuicao_diz_isso_em_vez_de_calar(client, seletor_ligado, cenario, cinco):
    """A ana responde pela Etapa e não recebeu inscrição nenhuma.

    Esconder a linha deixava o cartão dela idêntico ao de quem não sabe informar.
    """
    corpo = cartao(client, "ana")

    assert "Nenhuma inscrição distribuída a você ainda." in corpo
    assert "%" not in corpo.split('class="medidor')[0].split("Análise documental")[-1]


@pytest.mark.parametrize(
    ("total", "concluidas", "esperado"),
    [
        (255, 0, 0),
        (255, 1, 1),  # arredondaria para 0%, e daria por não começada a que já andou
        (255, 254, 99),  # arredondaria para 100%, e daria por encerrada a que ainda deve uma
        (255, 255, 100),
        (255, 140, 55),
        (0, 0, 0),
    ],
)
def test_o_percentual_reserva_os_extremos_para_os_extremos(total, concluidas, esperado):
    assert _completude(total, concluidas)["percentual"] == esperado
