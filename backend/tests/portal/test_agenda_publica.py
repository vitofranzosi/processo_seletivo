"""A agenda publicada na página pública (167, T045, FR-7225 a FR-7227, SC-2394, `D-009`).

A seção "Agendas" na seleção; a agenda por dia; a busca pelo protocolo e pelo nome — e só pelo
protocolo na Etapa restrita por Modalidade —; nada de sala, CPF, e-mail, telefone ou Modalidade no
HTML; sem tabela; e um número de consultas que não cresce com as pessoas.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.agendamento.application import conferir
from tests.fixtures.agenda_da_etapa import montar_completa, publicar_agenda
from tests.fixtures.comissao import inscrever

pytestmark = [pytest.mark.django_db]

SALA = "https://sala.exemplo/1"


@pytest.fixture
def inscricoes(edital_a):
    return inscrever(edital_a, 5)


@pytest.fixture
def publicada(gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)
    return publicar_agenda(gestor, edital_a, etapa_a2)


def _pagina(client, ato, busca=None):
    endereco = reverse("portal:agenda-da-etapa", args=[ato.agenda_id])
    resposta = client.get(endereco, {"busca": busca} if busca is not None else {})
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_a_selecao_lista_a_agenda_publicada(client, edital_a, publicada):
    corpo = client.get(reverse("portal:selecao", args=[edital_a.id])).content.decode()

    assert 'id="agendas-titulo">Agendas<' in corpo
    assert reverse("portal:agenda-da-etapa", args=[publicada.agenda_id]) in corpo
    assert "Em 23/11/2026" in corpo


def test_sem_publicacao_a_selecao_nao_tem_agendas_e_a_pagina_e_404(
    client, gestor, edital_a, etapa_a2, inscricoes
):
    from processo_seletivo.agendamento.application import leitura

    montar_completa(gestor, edital_a, etapa_a2)
    agenda = leitura.agenda_da_etapa(edital_a, etapa_a2)

    corpo = client.get(reverse("portal:selecao", args=[edital_a.id])).content.decode()
    assert 'id="agendas-titulo"' not in corpo
    resposta = client.get(reverse("portal:agenda-da-etapa", args=[agenda.id]))
    assert resposta.status_code == 404


def test_a_agenda_por_dia_com_nome_e_protocolo(client, publicada, inscricoes):
    corpo = _pagina(client, publicada)

    assert "Segunda-feira, 23/11/2026" in corpo
    for inscricao in inscricoes:
        assert inscricao.nome in corpo and inscricao.protocolo in corpo
    assert "08:00" in corpo and "09:00" in corpo
    assert "Número de inscrição ou nome" in corpo


def test_nada_de_sala_cpf_email_ou_telefone_e_sem_tabela(client, publicada, inscricoes):
    """SC-2394, FR-7226, e a lista pública sem `<table>`."""
    corpo = _pagina(client, publicada)

    assert SALA not in corpo and "sala.exemplo" not in corpo
    for inscricao in inscricoes:
        assert inscricao.email not in corpo
    assert "111.444.777-35" not in corpo and "11144477735" not in corpo
    assert "<table" not in corpo


def test_a_busca_pelo_protocolo_inteiro_pelo_fim_e_pelo_nome(client, publicada, inscricoes):
    alvo = inscricoes[2]

    for termo in (alvo.protocolo, alvo.protocolo[-4:], "candidata 3", "CANDIDATA 3"):
        corpo = _pagina(client, publicada, termo)
        assert "1 horário encontrado." in corpo, termo
        assert alvo.protocolo in corpo
        assert inscricoes[0].protocolo not in corpo

    corpo = _pagina(client, publicada, "INS-1999-9999")
    assert "Nenhum horário com esse número ou nome." in corpo


def test_na_etapa_restrita_so_o_protocolo_e_a_busca_so_por_ele(
    client, gestor, edital_a, etapa_a2, inscricoes, monkeypatch
):
    """`D-009`: a agenda da Etapa por Modalidade não publica o nome, e o nome não acha ninguém."""
    monkeypatch.setattr(conferir, "restrita", lambda etapa: True)
    montar_completa(gestor, edital_a, etapa_a2)
    ato = publicar_agenda(gestor, edital_a, etapa_a2)

    corpo = _pagina(client, ato)
    assert all(inscricao.nome not in corpo for inscricao in inscricoes)
    assert all(inscricao.protocolo in corpo for inscricao in inscricoes)
    assert "Número de inscrição<" in corpo or "Número de inscrição</label>" in corpo
    assert "ou nome" not in corpo

    corpo = _pagina(client, ato, "Candidata 3")
    assert "Nenhum horário com esse número." in corpo
    corpo = _pagina(client, ato, inscricoes[2].protocolo)
    assert "1 horário encontrado." in corpo


def test_o_numero_de_consultas_nao_cresce_com_as_pessoas(client, publicada, inscricoes):
    endereco = reverse("portal:agenda-da-etapa", args=[publicada.agenda_id])
    client.get(endereco)
    with CaptureQueriesContext(connection) as consultas:
        client.get(endereco)
    # Duas leituras: o ato com o Edital, e os vigentes com a inscrição e o ato — e as da moldura.
    agenda = [q for q in consultas.captured_queries if "agendamento_" in q["sql"]]
    assert len(agenda) == 2, [q["sql"] for q in agenda]
