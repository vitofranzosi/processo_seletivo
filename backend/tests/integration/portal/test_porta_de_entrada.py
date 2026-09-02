"""Há sempre por onde entrar, e sempre por onde voltar à área.

Percorrendo a jornada no navegador, a vitrine não oferecia nenhum "Entrar": quem já se inscreveu e
volta para conferir precisava clicar em *Inscrever-se nesta vaga* numa vaga qualquer — a única porta
— ou saber o endereço de cor. E, com sessão aberta, o cabeçalho trazia só o nome e o botão *Sair*:
nada levava a "Minhas inscrições".

Um sistema em que a pessoa não encontra o próprio lugar perde candidato antes de qualquer
formulário.
"""

import pytest
from django.urls import reverse

from tests.fixtures.candidato import MARIA, identificar

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def test_a_vitrine_oferece_entrar_para_quem_nao_esta_identificado(client):
    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert reverse("portal:acesso") in corpo
    assert "Entrar" in corpo


def test_com_sessao_o_cabecalho_leva_as_inscricoes(client, candidatos_registrados):
    identificar(client, MARIA)

    corpo = client.get(reverse("portal:vitrine")).content.decode()

    assert "Minhas inscrições" in corpo
    assert reverse("portal:inscricoes") in corpo
    assert "Entrar" not in corpo, "quem já está dentro não é convidado a entrar de novo"


def test_a_porta_acompanha_a_pessoa_pelas_paginas_publicas(client, selecao):
    """A vitrine e o detalhe da seleção são onde o candidato chega vindo de fora."""
    corpo = client.get(reverse("portal:selecao", args=[selecao.id])).content.decode()

    assert reverse("portal:acesso") in corpo


def test_as_telas_do_acesso_nao_convidam_a_entrar(client):
    """Um "Entrar" no cabeçalho da própria tela de entrar aponta para onde a pessoa já está."""
    for rota in ("portal:acesso", "portal:acesso-codigo"):
        corpo = client.get(reverse(rota), follow=True).content.decode()
        cabecalho = corpo.split("</header>")[0]
        assert "Entrar</a>" not in cabecalho, rota
