"""A Programação na Mesa e a próxima entrevista em Minhas atividades (179, US2).

A Mesa ganha a visão por horário, que é a primeira quando a agenda está publicada; a lista por
inscrição continua a mesma. Minhas atividades diz a próxima entrevista (FR-8211, FR-8212, FR-8214).
"""

import re

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.application import atos_individuais, leitura
from tests.fixtures.avaliacoes_com_agenda import agenda, atribuir, comissao, por_sessao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


def _mesa(edital, etapa, **params):
    url = reverse("interface:minha-etapa", args=[edital.id, etapa])
    return url + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")


@pytest.fixture
def ana_com_banca(gestor, edital_a, etapa_a2):
    """Seis pessoas em duas bancas; a Ana avalia as da Banca 01, o Bruno as da Banca 02."""
    inscrever(edital_a, 6)
    agenda(gestor, edital_a, etapa_a2, quantas_bancas=2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana", "bruno"])
    banca1, banca2 = (v for _, v in sorted(por_sessao(edital_a, etapa_a2).items()))
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], banca1, chave="ana")
    atribuir(gestor, edital_a, etapa_a2, [membros["bruno"]], banca2, chave="bruno")
    return banca1, banca2


def test_a_programacao_e_a_primeira_visao_com_agenda_publicada(
    client, seletor_ligado, edital_a, etapa_a2, ana_com_banca
):
    banca1, banca2 = ana_com_banca
    identificar(client, "ana", [])
    corpo = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert 'aria-current="page">Programação</a>' in corpo
    assert "Segunda-feira, 23/11/2026" in corpo
    assert "08:00–08:10" in corpo
    assert "Banca 01" in corpo and "Banca 02" not in corpo
    assert 'href="https://sala.exemplo/1"' in corpo and "Entrar na sala" in corpo
    assert "Avaliação não iniciada" in corpo
    for pessoa in banca1:
        assert pessoa.protocolo in corpo
    for pessoa in banca2:
        assert pessoa.protocolo not in corpo
    horas = re.findall(r"<strong>(\d\d:\d\d)–", corpo)
    assert horas == sorted(horas)


def test_por_inscricao_continua_a_lista_de_hoje(
    client, seletor_ligado, edital_a, etapa_a2, ana_com_banca
):
    identificar(client, "ana", [])
    corpo = client.get(_mesa(edital_a, etapa_a2, visao="inscricoes")).content.decode()
    assert 'aria-current="page">Por inscrição</a>' in corpo
    assert "Inscrições atribuídas a você nesta Etapa" in corpo
    assert "Entrar na sala" not in corpo
    assert "visao=inscricoes&filtro=nao-iniciadas" in corpo


def test_antes_da_publicacao_a_programacao_avisa(
    client, seletor_ligado, gestor, edital_a, etapa_a2
):
    pessoas = inscrever(edital_a, 2)
    agenda(gestor, edital_a, etapa_a2, publicar=False)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="ana")
    identificar(client, "ana", [])
    padrao = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert 'aria-current="page">Por inscrição</a>' in padrao
    programacao = client.get(_mesa(edital_a, etapa_a2, visao="programacao")).content.decode()
    assert "A agenda desta Etapa ainda não foi publicada" in programacao


def test_sem_agenda_a_mesa_e_a_de_hoje(client, seletor_ligado, gestor, edital_a, etapa_a2):
    pessoas = inscrever(edital_a, 2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="ana")
    identificar(client, "ana", [])
    corpo = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert "visoes-da-mesa" not in corpo
    assert "Inscrições atribuídas a você nesta Etapa" in corpo


def test_a_remarcacao_aparece_com_a_marca(
    client, seletor_ligado, gestor, edital_a, etapa_a2, ana_com_banca
):
    banca1, _ = ana_com_banca
    agenda_ = leitura.agenda_da_etapa(edital_a, etapa_a2)
    livre = leitura.montagem(edital_a, etapa_a2, agenda_).livres[-1]
    atos_individuais.remarcar(
        actor=gestor,
        edital=edital_a,
        etapa_id=etapa_a2,
        inscricao_id=banca1[0].id,
        inicio=livre.inicio,
        banca_id=livre.banca_id,
        motivo="falha de conexão",
        idempotency_key="remarcar-mesa",
    )
    identificar(client, "ana", [])
    corpo = client.get(_mesa(edital_a, etapa_a2)).content.decode()
    assert "remarcada em" in corpo


def test_os_filtros_valem_na_programacao(client, seletor_ligado, edital_a, etapa_a2, ana_com_banca):
    identificar(client, "ana", [])
    corpo = client.get(_mesa(edital_a, etapa_a2, filtro="concluidas")).content.decode()
    assert "Entrar na sala" not in corpo
    assert "Nenhuma entrevista sua com horário publicado" in corpo


def test_minhas_atividades_diz_a_proxima_entrevista(
    client, seletor_ligado, edital_a, etapa_a2, ana_com_banca
):
    identificar(client, "ana", [])
    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()
    i = corpo.find("Avaliar")
    assert "próxima entrevista 23/11 às 08:00, Banca 01" in corpo, corpo[i - 300 : i + 900]
    assert reverse("interface:minha-etapa", args=[edital_a.id, etapa_a2]) in corpo


def test_sem_entrevista_futura_a_linha_nao_fala_de_entrevista(
    client, seletor_ligado, gestor, edital_a, etapa_a2
):
    pessoas = inscrever(edital_a, 2)
    membros = comissao(gestor, edital_a, etapa_a2, ["ana"])
    atribuir(gestor, edital_a, etapa_a2, [membros["ana"]], pessoas, chave="ana")
    identificar(client, "ana", [])
    corpo = client.get(reverse("interface:minhas-etapas")).content.decode()
    assert "próxima entrevista" not in corpo
