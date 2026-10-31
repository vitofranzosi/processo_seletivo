"""Os acessos na trilha da unidade, no modo institucional (108, US3, `D-002`).

Aqui, e não com os demais casos da página, porque é aqui que moram o provedor simulado e as pessoas
institucionais da `106`. Os atos são os das funções da `106` e da `107` — conceder, revogar,
suspender —, e a sessão do Auditor é aberta pela entrada institucional de verdade, que grava a
própria `ENTRADA` na trilha: é ela que prova que sessão não aparece.
"""

import re

import pytest
from django.urls import reverse
from django.utils import timezone

from processo_seletivo.seguranca import acessos as catalogo
from processo_seletivo.seguranca.application import acessos, suspensao
from processo_seletivo.seguranca.domain import Actor
from tests.seguranca.apoio import entrar, pessoa, vincular

pytestmark = pytest.mark.django_db

URL = reverse("interface:trilha-da-unidade")


@pytest.fixture
def fiscal(client, provedor):
    """O Auditor do `cefor`, pessoa institucional, com a sessão aberta neste cliente."""
    alguem = pessoa("fiscal", nome="Fábio Fiscal", email="fabio@ifes.edu.br")
    vincular(alguem, "cefor", "auditor")
    entrar(client, "fiscal", nome="Fábio Fiscal", email="fabio@ifes.edu.br")
    return alguem


def _admin_da_unidade(escopo="cefor"):
    alguem = pessoa(f"admin-{escopo}", nome=f"Carlos Admin {escopo}")
    return Actor(alguem.username, escopo, frozenset({catalogo.GERIR, catalogo.CONSULTAR}))


def _admin_institucional():
    alguem = pessoa("adm-inst", nome="Irene Institucional")
    return Actor(alguem.username, catalogo.ESCOPO_INSTITUCIONAL, frozenset({catalogo.ADMINISTRAR}))


def _lista(client):
    corpo = client.get(URL).content.decode()
    if '<ol class="auditoria"' not in corpo:
        return corpo, []
    lista = corpo.split('<ol class="auditoria"')[1].split("</ol>")[0]
    return corpo, re.findall(r"<li>(.*?)</li>", lista, re.S)


def test_a_concessao_e_a_revogacao_na_unidade_aparecem_com_os_nomes(client, fiscal):
    bea = pessoa("bea", nome="Beatriz Prado", email="beatriz.prado@ifes.edu.br")
    admin = _admin_da_unidade()
    agora = timezone.now()
    vinculo = acessos.conceder(
        admin, pessoa=bea, escopo="cefor", papel="elaborador", motivo="Memorando 12/2026", now=agora
    )
    acessos.revogar(admin, vinculo=vinculo, motivo="Mudou de setor", now=timezone.now())

    corpo, itens = _lista(client)

    assert len(itens) == 2, "a entrada do Auditor é sessão, e não aparece"
    revogacao, concessao = itens
    assert "Revogação de acesso" in revogacao and "“Mudou de setor”" in revogacao
    assert "Concessão de acesso" in concessao and "“Memorando 12/2026”" in concessao
    for item in itens:
        assert "Beatriz Prado, como Elaborador" in item
        assert "por <strong>Carlos Admin cefor</strong>" in item
    # SC-1024: nem o identificador interno, nem o e-mail de quem recebeu.
    assert "pessoa-" not in corpo.split('<main id="conteudo"')[1]
    assert "beatriz.prado@ifes.edu.br" not in corpo


def test_a_concessao_institucional_do_administrador_da_unidade_aparece_e_a_de_outra_nao(
    client, fiscal, campus_a
):
    instituicao = _admin_institucional()
    carla = pessoa("carla", nome="Carla Souza")
    dora = pessoa("dora", nome="Dora Lima")
    acessos.conceder(
        instituicao,
        pessoa=carla,
        escopo="cefor",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="Portaria 40/2026",
        now=timezone.now(),
    )
    acessos.conceder(
        instituicao,
        pessoa=dora,
        escopo="campus-a",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="Portaria 41/2026",
        now=timezone.now(),
    )
    # A suspensão é global, gravada no institucional: fica fora (`D-003`).
    suspensao.suspender(instituicao, pessoa=dora, motivo="Apuração", now=timezone.now())

    corpo, itens = _lista(client)

    assert len(itens) == 1
    (item,) = itens
    assert "Carla Souza, como Administrador de acessos da unidade" in item
    assert "por <strong>Irene Institucional</strong>" in item
    assert "Portaria 40/2026" in item
    assert "Dora Lima" not in corpo and "Apuração" not in corpo


def test_o_filtro_de_acessos_traz_os_dois_escopos(client, fiscal):
    instituicao = _admin_institucional()
    admin = _admin_da_unidade()
    acessos.conceder(
        instituicao,
        pessoa=pessoa("carla", nome="Carla Souza"),
        escopo="cefor",
        papel=catalogo.ADMINISTRADOR_DE_ACESSOS,
        motivo="Portaria 40/2026",
        now=timezone.now(),
    )
    acessos.conceder(
        admin,
        pessoa=pessoa("bea", nome="Beatriz Prado"),
        escopo="cefor",
        papel="publicador",
        motivo="Memorando 13/2026",
        now=timezone.now(),
    )

    corpo = client.get(URL + "?assunto=acessos").content.decode()
    lista = corpo.split('<ol class="auditoria"')[1].split("</ol>")[0]
    assert lista.count("Concessão de acesso") == 2
    so_unidade = client.get(URL + "?assunto=unidade").content.decode()
    assert "Nenhum ato corresponde ao filtro." in so_unidade


def test_o_administrador_institucional_sem_unidade_nao_le(client, provedor):
    """Quem só tem o escopo institucional não tem unidade a ler (`D-003`).

    A recusa aqui vem da falta de `auditoria:consultar`, que nenhum papel institucional concede. A
    recusa pelo escopo, com o Auditor no institucional, só se monta pelo seletor de demonstração, e
    está em `tests/interface/test_trilha_da_unidade.py`.
    """
    alguem = pessoa("adm-inst", nome="Irene Institucional")
    vincular(alguem, catalogo.ESCOPO_INSTITUCIONAL, catalogo.ADMINISTRADOR_INSTITUCIONAL)
    entrar(client, "adm-inst", nome="Irene Institucional")

    assert client.get(URL).status_code == 403
