"""A configuração da agenda na gestão (167, T016, US1, UX-760, UX-765, UX-766, FR-7255)."""

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.models import AgendaDaEtapa
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def inscritas(edital_a):
    return inscrever(edital_a, 43)


def url(nome, edital, etapa):
    return reverse(f"interface:{nome}", args=[edital.id, etapa])


def formulario(dias=(("2026-11-23", (("08:00", "12:00"), ("13:00", "17:00"))),), **extra):
    dados = {"forma": "REMOTA", "duracao": "10", "intervalo": "5", "orientacoes": ""}
    for i, (dia, janelas) in enumerate(dias):
        dados[f"dia-{i}"] = dia
        for k, (inicio, fim) in enumerate(janelas):
            dados[f"dia-{i}-janela-{k}-inicio"] = inicio
            dados[f"dia-{i}-janela-{k}-fim"] = fim
    dados.update({"banca-0-id": "", "banca-0-nome": "Banca 1", "banca-0-acesso": "https://s/1"})
    dados.update(extra)
    return dados


def test_a_secao_vazia_diz_para_que_serve(presidente, edital_a, etapa_a2):
    """UX-765 e US1, cenário 1."""
    corpo = presidente.get(url("distribuicao", edital_a, etapa_a2)).content.decode()

    assert "Esta Etapa ainda não tem agenda." in corpo
    assert "antes de a lista de participantes estar fechada" in corpo
    assert url("agenda-configurar", edital_a, etapa_a2) in corpo


def test_a_secao_com_agenda_leva_a_montagem(presidente, edital_a, etapa_a2, inscritas):
    presidente.post(url("agenda-configurar", edital_a, etapa_a2), formulario())

    corpo = presidente.get(url("distribuicao", edital_a, etapa_a2)).content.decode()

    assert "Agenda em montagem" in corpo
    assert "faltam 11" in corpo
    assert url("agenda-montar", edital_a, etapa_a2) in corpo


def test_a_capacidade_responde_sem_gravar(presidente, edital_a, etapa_a2, inscritas):
    """US1, cenário 2: 32 horários e "faltam 11", nada gravado (UX-760)."""
    resposta = presidente.post(
        url("agenda-capacidade", edital_a, etapa_a2), formulario(), HTTP_HX_REQUEST="true"
    )
    corpo = resposta.content.decode()

    assert resposta.status_code == 200
    assert "Faltam 11 horários para as 43 pessoas." in corpo
    assert "16 atendimentos por banca × 1 banca" in corpo
    assert "Acrescentar Ter., 24/11" in corpo and "+32" in corpo
    assert "A Etapa anterior ainda não tem Resultado" in corpo
    assert not AgendaDaEtapa.objects.exists()


def test_a_capacidade_recusada_volta_200_com_o_alvo(presidente, edital_a, etapa_a2, inscritas):
    dados = formulario(dias=(("2026-11-23", (("12:00", "12:05"),)),))

    resposta = presidente.post(
        url("agenda-capacidade", edital_a, etapa_a2), dados, HTTP_HX_REQUEST="true"
    )

    assert resposta.status_code == 200
    assert resposta["HX-Retarget"] == "#calculo"
    assert "A janela 12:00–12:05 não comporta um atendimento de 10 minutos." in (
        resposta.content.decode()
    )


def test_o_atalho_acrescenta_o_dia_sem_gravar(presidente, edital_a, etapa_a2, inscritas):
    resposta = presidente.post(
        url("agenda-configurar", edital_a, etapa_a2),
        formulario(acao="atalho-dia"),
        HTTP_HX_REQUEST="true",
    )
    corpo = resposta.content.decode()

    assert 'value="2026-11-24"' in corpo
    assert "Cabem todas as 43 pessoas. Sobram 21 horários." in corpo
    assert not AgendaDaEtapa.objects.exists()


def test_a_recusa_lista_todos_os_problemas_e_nao_grava(presidente, edital_a, etapa_a2, inscritas):
    """UX-766: a lista inteira, com o que fazer."""
    dados = formulario(
        dias=(("2026-11-23", (("08:00", "12:00"), ("11:30", "14:00"))),),
        duracao="0",
        **{"banca-0-nome": ""},
    )

    resposta = presidente.post(url("agenda-configurar", edital_a, etapa_a2), dados)
    corpo = resposta.content.decode()

    assert resposta.status_code == 422
    assert "Informe a duração de cada atendimento, em minutos." in corpo
    assert "se sobrepõem. Ajuste uma delas." in corpo
    assert "Dê um nome a cada banca" in corpo
    assert not AgendaDaEtapa.objects.exists()


def test_salvar_leva_a_montagem(presidente, edital_a, etapa_a2, inscritas):
    resposta = presidente.post(url("agenda-configurar", edital_a, etapa_a2), formulario())

    assert resposta.status_code == 302
    assert resposta.url == url("agenda-montar", edital_a, etapa_a2)
    corpo = presidente.get(resposta.url).content.decode()
    assert "Configuração salva. A agenda continua em rascunho" in corpo


def test_sem_a_base_da_comissao_a_recusa_nomeia_o_que_falta(
    client, seletor_ligado, edital_a, etapa_a2
):
    """FR-7255: negado por padrão, na gramática das portas da `033`."""
    identificar(client, "elaine", ["elaborador"])

    resposta = client.get(url("agenda-configurar", edital_a, etapa_a2))

    assert resposta.status_code == 403
    assert not AgendaDaEtapa.objects.exists()


def test_fora_do_escopo_e_inexistente(client, seletor_ligado, edital_a, etapa_a2):
    identificar(client, "carlos", ["gestor"], escopo="outra")

    assert client.get(url("agenda-configurar", edital_a, etapa_a2)).status_code == 404


def test_etapa_ausente_da_versao_vigente_e_inexistente(presidente, edital_a):
    from uuid import uuid4

    assert presidente.get(url("agenda-configurar", edital_a, uuid4())).status_code == 404
