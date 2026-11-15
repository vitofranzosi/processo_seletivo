"""A montagem na gestão (167, T026, US2, UX-761, UX-762, UX-764)."""

import re

import pytest
from django.urls import reverse

from processo_seletivo.agendamento.application import configurar, leitura
from processo_seletivo.agendamento.models import Agendamento
from tests.fixtures.agenda_da_etapa import configuracao
from tests.fixtures.comissao import inscrever
from tests.interface.conftest import identificar

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def presidente(client, seletor_ligado):
    identificar(client, "carlos", ["gestor"])
    return client


@pytest.fixture
def inscritas(edital_a):
    return inscrever(edital_a, 5)


@pytest.fixture
def agenda(gestor, edital_a, etapa_a2, inscritas):
    return configurar.salvar(
        actor=gestor, edital=edital_a, etapa_id=etapa_a2, configuracao=configuracao()
    ).agenda


def url(nome, edital, etapa):
    return reverse(f"interface:{nome}", args=[edital.id, etapa])


def _horarios(edital, etapa):
    return leitura.montagem(edital, etapa, leitura.agenda_da_etapa(edital, etapa)).horarios


def _chave(horario):
    return f"{horario.banca_id}@{horario.inicio.isoformat()}"


def test_sem_configuracao_leva_a_configurar(presidente, edital_a, etapa_a2):
    resposta = presidente.get(url("agenda-montar", edital_a, etapa_a2))

    assert resposta.status_code == 302
    assert resposta.url == url("agenda-configurar", edital_a, etapa_a2)


def test_um_resumo_so_abas_e_a_acao_que_falta(presidente, edital_a, etapa_a2, agenda):
    corpo = presidente.get(url("agenda-montar", edital_a, etapa_a2)).content.decode()

    assert corpo.count('class="medidor') == 1
    assert "<strong>0</strong> de 5 com horário" in corpo
    assert 'Seg., 23/11 <span class="contagem">0/4</span>' in corpo
    # UX-764: a ação principal aparece uma vez; UX-761: a grade não repete texto de ação.
    assert corpo.count("Preencher automaticamente") == 1
    grade = corpo[corpo.index('class="grade-compacta"') : corpo.index("</table>")]
    assert "Agendar" not in grade and "Liberar" not in grade
    assert grade.count("Livre") == 4


def test_o_painel_da_pessoa_e_o_do_horario_livre(presidente, edital_a, etapa_a2, inscritas, agenda):
    """UX-762: escolher a pessoa e depois o horário, ou o contrário, sem arrastar."""
    pessoa = presidente.get(
        url("agenda-painel", edital_a, etapa_a2),
        {"pessoa": inscritas[0].id},
        HTTP_HX_REQUEST="true",
    ).content.decode()
    horario = presidente.get(
        url("agenda-painel", edital_a, etapa_a2),
        {"horario": _chave(_horarios(edital_a, etapa_a2)[0])},
        HTTP_HX_REQUEST="true",
    ).content.decode()

    assert "Escolha um horário livre" in pessoa and 'name="horario"' in pessoa
    assert "Quem vai para este horário?" in horario and "Agendar aqui" in horario
    assert horario.count('name="inscricao"') == 5


def test_a_previa_no_painel_nao_grava_e_a_aplicacao_grava(presidente, edital_a, etapa_a2, agenda):
    previa = presidente.post(url("agenda-preencher", edital_a, etapa_a2), HTTP_HX_REQUEST="true")
    corpo = previa.content.decode()

    assert "Prévia: nada foi gravado" in corpo
    assert "4 pessoas recebem horário. 1 continua sem horário." in corpo
    assert "Ver quem vai para cada horário (4)" in corpo
    assert not Agendamento.objects.exists()

    assinatura = re.search(r'name="assinatura" value="([0-9a-f]+)"', corpo).group(1)
    resposta = presidente.post(
        url("agenda-preencher", edital_a, etapa_a2), {"assinatura": assinatura}
    )

    assert resposta.status_code == 302
    assert Agendamento.objects.count() == 4
    depois = presidente.get(resposta.url).content.decode()
    assert "4 pessoas receberam horário." in depois
    # Sem horário livre, "Preencher automaticamente" sai do alto (UX-764).
    assert "Preencher automaticamente" not in depois


def test_a_assinatura_velha_mostra_a_previa_nova(presidente, edital_a, etapa_a2, agenda):
    resposta = presidente.post(
        url("agenda-preencher", edital_a, etapa_a2), {"assinatura": "0" * 64}
    )

    assert resposta.status_code == 409
    corpo = resposta.content.decode()
    assert "A agenda mudou desde a prévia. Veja a prévia nova antes de aplicar." in corpo
    assert "Prévia: nada foi gravado" in corpo


def test_agendar_mudar_e_liberar_pelos_formularios(
    presidente, edital_a, etapa_a2, inscritas, agenda
):
    horarios = _horarios(edital_a, etapa_a2)
    agendar = url("agenda-agendar", edital_a, etapa_a2)

    primeiro = presidente.post(
        agendar, {"inscricao": inscritas[0].id, "horario": _chave(horarios[0])}
    )
    mudanca = presidente.post(
        agendar, {"inscricao": inscritas[0].id, "horario": _chave(horarios[2]), "mudanca": "1"}
    )

    assert primeiro.status_code == mudanca.status_code == 302
    assert Agendamento.objects.get().inicio == horarios[2].inicio
    corpo = presidente.get(mudanca.url).content.decode()
    assert "Candidata 1 passou de Seg., 23/11, 08:00 para Seg., 23/11, 08:30." in corpo

    liberada = presidente.post(
        url("agenda-liberar", edital_a, etapa_a2), {"inscricao": inscritas[0].id}
    )

    assert liberada.status_code == 302
    assert not Agendamento.objects.exists()


def test_o_horario_ocupado_volta_com_a_frase_e_a_grade_relida(
    presidente, edital_a, etapa_a2, inscritas, agenda
):
    horario = _chave(_horarios(edital_a, etapa_a2)[0])
    agendar = url("agenda-agendar", edital_a, etapa_a2)
    presidente.post(agendar, {"inscricao": inscritas[0].id, "horario": horario})

    resposta = presidente.post(agendar, {"inscricao": inscritas[1].id, "horario": horario})

    assert resposta.status_code == 409
    corpo = resposta.content.decode()
    assert "Esse horário acabou de ser ocupado" in corpo
    assert "Candidata 1" in corpo
