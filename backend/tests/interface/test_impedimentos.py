"""A tela de confirmação é alcançável por URL direta e precisa dizer o que impede.

A lista de ações já filtra por permissão e situação — quem abre `/atos/<acao>` diretamente
recebia o mesmo formulário com "Confirmar", e a recusa só aparecia depois do clique. O command
continua sendo quem decide; isto é apenas a explicação antecipada.
"""

import pytest
from django.urls import reverse

from processo_seletivo.processos.models import Edital
from tests.interface.conftest import compor_rascunho, identificar


@pytest.fixture
def edital(api_client, manager_headers, process_payload):
    api_client.post("/api/v1/admin/processos", process_payload, format="json", **manager_headers)
    return Edital.objects.get()


def confirmar(client, edital, acao):
    return client.get(reverse("interface:ato", args=[edital.id, acao]))


@pytest.mark.django_db
@pytest.mark.integration
def test_sem_permissao_a_tela_explica_e_nao_oferece_confirmar(client, seletor_ligado, edital):
    identificar(client, "iris.auditora", ["auditor"])
    corpo = confirmar(client, edital, "submeter").content.decode()

    assert "Você não pode praticar este ato" in corpo
    assert "edital:submeter" in corpo
    assert "Confirmar: " not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_situacao_incompativel_diz_qual_e_a_exigida_e_qual_e_a_atual(
    client, seletor_ligado, edital
):
    """O Edital está em elaboração; homologar exige revisão."""
    identificar(client, "bruno.homologador", ["homologador"])
    corpo = confirmar(client, edital, "homologar").content.decode()

    assert "não cabe na situação atual" in corpo
    assert "Em revisão" in corpo and "Em elaboração" in corpo
    assert "Confirmar: " not in corpo


PERFIL_MINIMO = {
    "perfil-0-id": "dddddddd-0000-4000-8000-00000000f001",
    "perfil-0-code": "P1",
    "perfil-0-name": "Perfil",
    "perfil-0-immediateVacancies": "1",
    "perfil-0-reserveType": "NONE",
}
EVENTO_MINIMO = {
    "evento-0-id": "dddddddd-0000-4000-8000-00000000f002",
    "evento-0-type": "Inscrições",
    "evento-0-description": "Inscrições",
    "evento-0-startAt": "2026-10-01T09:00",
}


@pytest.mark.django_db
@pytest.mark.integration
def test_ato_cabivel_continua_oferecendo_confirmar(client, seletor_ligado, edital):
    """Sem Perfil e sem Evento o ato tem pendência impeditiva; o Edital precisa estar pronto."""
    identificar(client, "ana.elaboradora", ["elaborador"])
    compor_rascunho(client, edital, PERFIL_MINIMO, EVENTO_MINIMO)
    corpo = confirmar(client, edital, "submeter").content.decode()

    assert "Confirmar: Submeter para revisão" in corpo
    assert "não cabe na situação atual" not in corpo
    assert "Impedimento:" not in corpo


@pytest.mark.django_db
@pytest.mark.integration
def test_pendencia_impeditiva_tambem_retira_o_confirmar(client, seletor_ligado, edital):
    """A tela já dizia "Impedimento: ..." e mesmo assim oferecia o botão.

    A previsão é exata: a interface chama a mesma `validate_for_publication` que o command.
    """
    identificar(client, "ana.elaboradora", ["elaborador"])
    corpo = confirmar(client, edital, "submeter").content.decode()

    assert "Impedimento:" in corpo, "um Edital recém-criado não tem Perfil nem Evento"
    assert "Confirmar: " not in corpo
