"""O horário na área do candidato (167, T046, FR-7228, FR-7229, US3 cenários 8 e 9).

Publicado: o dia e a hora em destaque, a duração, a banca, o botão da sala e as orientações; o
endereço da sala só para a própria pessoa, e nunca o de outra inscrição. Antes da publicação: "ainda
não foi publicado", com o período do cronograma. E consultas que não crescem com as pessoas.
"""

from datetime import date, time

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from processo_seletivo.agendamento.application import configurar
from processo_seletivo.agendamento.domain.horarios import Banca
from tests.fixtures.agenda_da_etapa import (
    DUAS_HORAS,
    SEG,
    configuracao,
    montar_completa,
    publicar_agenda,
)
from tests.fixtures.comissao import inscrever
from tests.fixtures.divulgacao import entrar_como_titular

pytestmark = [pytest.mark.django_db]

SALA_1 = "https://sala.exemplo/1"
SALA_2 = "https://sala.exemplo/2"
DUAS_BANCAS = (
    Banca("nova-1", "Banca 1", SALA_1, 1),
    Banca("nova-2", "Banca 2", SALA_2, 2),
)


@pytest.fixture
def inscricoes(edital_a):
    return inscrever(edital_a, 4)


def _area(client, inscricao):
    entrar_como_titular(client, inscricao)
    resposta = client.get(reverse("portal:acompanhamento", args=[inscricao.id]))
    assert resposta.status_code == 200
    return resposta.content.decode()


def test_publicado_mostra_dia_hora_duracao_sala_e_orientacoes(
    client, gestor, edital_a, etapa_a2, inscricoes
):
    """US3, cenário 8."""
    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)

    corpo = _area(client, inscricoes[0])

    assert "Seu horário: Prova didática" in corpo
    assert "Segunda-feira, 23/11/2026, às <strong>08:00</strong>" in corpo
    assert "10 minutos" in corpo
    assert f'href="{SALA_1}"' in corpo and "Entrar na sala virtual" in corpo
    assert "Tenha o documento." in corpo


def test_a_sala_de_outra_banca_nao_chega_a_quem_nao_e_dela(
    client, gestor, edital_a, etapa_a2, inscricoes
):
    """FR-7229: com duas bancas, cada pessoa vê a sua sala — e a banca, porque há mais de uma."""
    montar_completa(
        gestor,
        edital_a,
        etapa_a2,
        config=configuracao(dias=((SEG, DUAS_HORAS),), bancas=DUAS_BANCAS),
    )
    ato = publicar_agenda(gestor, edital_a, etapa_a2)
    por_inscricao = {h.inscricao_id: h for h in ato.horarios.all()}

    for inscricao in inscricoes:
        corpo = _area(client, inscricao)
        minha = por_inscricao[inscricao.id]
        outra = SALA_2 if minha.banca_nome == "Banca 1" else SALA_1
        assert f"<dd>{minha.banca_nome}</dd>" in corpo
        assert outra not in corpo


def test_antes_da_publicacao_diz_que_nao_foi_publicado_com_o_periodo(
    client, gestor, edital_a, etapa_a1, inscricoes
):
    """US3, cenário 9: a primeira Etapa tem Evento em 01/09/2026."""
    configurar.salvar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a1,
        configuracao=configuracao(dias=((date(2026, 9, 1), ((time(8), time(9)),)),)),
    )

    corpo = _area(client, inscricoes[0])

    assert "ainda não foi publicado" in corpo
    assert "A Etapa acontece em 01/09/2026, pelo cronograma." in corpo
    assert "Entrar na sala virtual" not in corpo
    assert "sala.exemplo" not in corpo


def test_sem_agenda_nao_ha_bloco(client, edital_a, inscricoes):
    corpo = _area(client, inscricoes[0])

    assert "Seu horário" not in corpo


def test_o_numero_de_consultas_da_agenda_e_fixo(client, gestor, edital_a, etapa_a2, inscricoes):
    montar_completa(gestor, edital_a, etapa_a2)
    publicar_agenda(gestor, edital_a, etapa_a2)
    entrar_como_titular(client, inscricoes[0])
    endereco = reverse("portal:acompanhamento", args=[inscricoes[0].id])
    client.get(endereco)

    with CaptureQueriesContext(connection) as consultas:
        client.get(endereco)

    # As agendas do Edital, as publicações delas e o vigente desta inscrição.
    agenda = [q for q in consultas.captured_queries if "agendamento_" in q["sql"]]
    assert len(agenda) == 3, [q["sql"] for q in agenda]
