"""A tela do relatório do Edital: a ação, a página e as portas (099, FR-2513 a FR-2515)."""

import pytest
from django.urls import reverse

from tests.fixtures.relatorio import montar_cenario
from tests.interface.conftest import identificar

pytestmark = pytest.mark.django_db


@pytest.fixture
def cenario(db):
    return montar_cenario(final="pendente")


def test_a_gestao_ve_a_acao_e_a_pagina_com_a_camada_executiva(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital", args=[cenario.edital.id])

    detalhe = client.get(reverse("interface:detalhe", args=[cenario.edital.id]))
    assert url in detalhe.content.decode()

    pagina = client.get(url)
    corpo = pagina.content.decode()
    assert pagina.status_code == 200
    assert "no-store" in pagina["Cache-Control"]
    for trecho in (
        "Relatório do Edital 61/2026",
        "Encerrado em 20/10/2026",
        "Situação das providências",
        "Visão geral",
        "inscrições por vaga",
        "Resultados por perfil de vaga",
        "Professor de Informática",
        "Baixar PDF",
    ):
        assert trecho in corpo, trecho
    assert reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id]) in corpo


def test_a_presidencia_do_processo_tambem_alcanca(client, seletor_ligado, cenario):
    identificar(client, "paulo.presidente", ["elaborador"])
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 200


def test_quem_e_da_unidade_sem_a_base_recebe_a_recusa_explicada(client, seletor_ligado, cenario):
    """FR-2514 e a gramática da `033`: 403 que diz o que falta, e não 404."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 403
    assert "Peça" in resposta.content.decode()
    detalhe = client.get(reverse("interface:detalhe", args=[cenario.edital.id]))
    assert "Relatório do Edital" not in detalhe.content.decode()


def test_outra_unidade_recebe_nao_encontrado(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"], escopo="outra-unidade")
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[cenario.edital.id]))
    assert resposta.status_code == 404


def test_edital_nao_publicado_tem_a_acao_indisponivel_e_recusa(client, seletor_ligado, edital):
    """Caso-limite: antes da publicação a ação aparece desabilitada, com o motivo."""
    identificar(client, "gustavo.gestor", ["gestor"])
    detalhe = client.get(reverse("interface:detalhe", args=[edital.id])).content.decode()
    assert "O relatório fica disponível quando o Edital for publicado." in detalhe
    resposta = client.get(reverse("interface:relatorio-do-edital", args=[edital.id]))
    assert resposta.status_code == 409


def test_a_emissao_so_aceita_envio(client, seletor_ligado, cenario):
    identificar(client, "gustavo.gestor", ["gestor"])
    resposta = client.get(reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id]))
    assert resposta.status_code == 405


def test_a_lista_de_processos_nao_oferece_o_relatorio(client, seletor_ligado, cenario):
    """A ação é do detalhe: na lista, ela custaria uma consulta à comissão por linha."""
    identificar(client, "paulo.presidente", ["elaborador"])
    lista = client.get(reverse("interface:lista")).content.decode()
    assert reverse("interface:relatorio-do-edital", args=[cenario.edital.id]) not in lista


def test_so_a_falha_de_serializacao_vira_tente_de_novo(
    client, seletor_ligado, cenario, monkeypatch
):
    """Erro de banco que não é concorrência sobe como defeito, e não como "baixe de novo"."""
    from django.db import IntegrityError, OperationalError

    from processo_seletivo.interface import relatorio_pdf

    identificar(client, "gustavo.gestor", ["gestor"])
    url = reverse("interface:relatorio-do-edital-pdf", args=[cenario.edital.id])

    class Serializacao(Exception):
        sqlstate = "40001"

    def concorrente(*args, **kwargs):
        raise OperationalError("could not serialize access") from Serializacao()

    monkeypatch.setattr(relatorio_pdf, "compor", concorrente)
    assert client.post(url).status_code == 409

    def defeito(*args, **kwargs):
        raise IntegrityError("defeito")

    monkeypatch.setattr(relatorio_pdf, "compor", defeito)
    client.raise_request_exception = True
    with pytest.raises(IntegrityError):
        client.post(url)
