"""A Mesa do avaliador: todas e somente as inscrições dela (US2).

A página é a mesma que a 011 deixou com um aviso; o que a `012` faz é substituir o aviso pela
lista. Quem chegou pela gestão continua sem Mesa — organizar o trabalho não é executá-lo.
"""

import pytest
from django.urls import reverse

from processo_seletivo.avaliacoes.application.selectors import POR_PAGINA
from tests.fixtures.comissao import alocar_em, inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def joao(gestor, processo_a, edital_a, comissao_de_a, etapa_a1):
    alocar_em(gestor, processo_a, comissao_de_a["joao"], edital_a, etapa_a1)
    return comissao_de_a["joao"]


@pytest.fixture
def mesa(edital_a, etapa_a1):
    return reverse("interface:minha-etapa", args=[edital_a.id, etapa_a1])


def distribuir_para(gestor, edital, etapa_id, membro, inscricoes, chave="mesa"):
    from processo_seletivo.avaliacoes.application.distribuicao import distribuir

    return distribuir(
        actor=gestor,
        processo_id=edital.processo_id,
        edital_id=edital.id,
        etapa_id=etapa_id,
        membro_ids=[membro.id],
        inscricao_ids=[i.id for i in inscricoes],
        idempotency_key=chave,
        correlation_id="teste",
    )


def test_a_mesa_lista_o_que_e_dele_e_conta(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    inscricoes = inscrever(edital_a, 3)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert "3 atribuições" in corpo
    assert "3 pendentes" in corpo
    for inscricao in inscricoes:
        assert inscricao.protocolo in corpo


def test_a_mesa_nao_mostra_inscricao_de_outro_avaliador(
    client, seletor_ligado, gestor, processo_a, edital_a, etapa_a1, joao, comissao_de_a, mesa
):
    """ "Todas **e somente**" é a metade que só se prova pela ausência (FR-020)."""
    from processo_seletivo.comissoes.domain.funcoes import Funcao
    from tests.fixtures.comissao import constituir

    ana = constituir(gestor, processo_a, [("ana", Funcao.MEMBRO)], prefixo="mesa")["ana"]
    alocar_em(gestor, processo_a, ana, edital_a, etapa_a1)
    minhas, dela = inscrever(edital_a, 1), inscrever(edital_a, 1, primeiro=80)
    distribuir_para(gestor, edital_a, etapa_a1, joao, minhas, chave="a")
    distribuir_para(gestor, edital_a, etapa_a1, ana, dela, chave="b")
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert minhas[0].protocolo in corpo
    assert dela[0].protocolo not in corpo


def test_o_filtro_separa_pendentes_de_concluidas(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    from processo_seletivo.avaliacoes.models import Atribuicao, Avaliacao

    inscricoes = inscrever(edital_a, 2)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    atribuicao = Atribuicao.objects.get(inscricao=inscricoes[0])
    Avaliacao.objects.create(
        atribuicao=atribuicao,
        identity_subject="joao",
        etapa_id=etapa_a1,
        inscricao_id=inscricoes[0].id,
    )
    identificar(client, "joao", [])

    pendentes = client.get(f"{mesa}?filtro=pendentes").content.decode()
    concluidas = client.get(f"{mesa}?filtro=concluidas").content.decode()

    # Rascunho **não** é concluída: pendente é a ausência de conclusão, e não a de avaliação.
    assert inscricoes[0].protocolo in pendentes
    assert inscricoes[1].protocolo in pendentes
    assert "Nenhuma inscrição sua corresponde" in concluidas


def test_a_mesa_pagina(client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa):
    """Quarenta e oito é comum; quinhentas não pode quebrar a tela (FR-022)."""
    inscricoes = inscrever(edital_a, POR_PAGINA + 3)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "joao", [])

    corpo = client.get(mesa).content.decode()

    assert "Página 1 de 2" in corpo
    assert "Próxima" in corpo


def test_alocado_sem_atribuicao_encontra_a_mesa_vazia(client, seletor_ligado, joao, mesa):
    """FR-023: alocação abre a porta da Etapa; a Atribuição abre a inscrição.

    O estado vazio explica que não há trabalho distribuído — e **não** fala em permissão, que
    diria a coisa errada.
    """
    identificar(client, "joao", [])

    resposta = client.get(mesa)
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Nenhuma inscrição foi distribuída a você" in corpo
    assert "permiss" not in corpo.lower()


def test_quem_chega_pela_gestao_nao_tem_mesa(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    """Organizar o trabalho não é executá-lo, e a página diz por qual porta o ator chegou."""
    inscricoes = inscrever(edital_a, 2)
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscricoes)
    identificar(client, "carlos", ["gestor"])

    corpo = client.get(mesa).content.decode()

    assert "chegou aqui pela gestão" in corpo
    assert "Minha Mesa" not in corpo
    assert inscricoes[0].protocolo not in corpo


def test_a_mesa_nao_e_armazenavel_pelo_navegador(
    client, seletor_ligado, gestor, edital_a, etapa_a1, joao, mesa
):
    distribuir_para(gestor, edital_a, etapa_a1, joao, inscrever(edital_a, 1))
    identificar(client, "joao", [])

    resposta = client.get(mesa)

    assert "no-store" in resposta["Cache-Control"]
